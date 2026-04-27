from datetime import datetime, timedelta
from typing import Optional

DEFAULT_THRESHOLD_WARNING = 8.0
DEFAULT_THRESHOLD_DANGER = 10.0
DEFAULT_MAX_CAPACITY = 12.0

LEVEL_MIN_VALID = 0.0
LEVEL_MAX_VALID = 500.0

# Status dari DB IoT: "bahaya" dan "warning"
# Dinormalisasi ke format internal: normal / warning / bahaya
STATUS_MAP = {
    "normal": "normal",
    "warning": "warning",
    "siaga1": "warning",
    "bahaya": "bahaya",
    "danger": "bahaya",
    "siaga2": "bahaya",
}


# ─── 1. CLEANING ─────────────────────────────────────────────────────────────

def _normalize_timestamp(ts) -> Optional[str]:
    if not ts:
        return None
    try:
        return datetime.fromisoformat(
            str(ts).replace("Z", "+00:00")
        ).strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        try:
            s = str(ts).strip()[:19]
            datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
            return s
        except Exception:
            return None


def clean_readings(readings: list) -> tuple:
    clean = []
    rejected = []

    for r in readings:
        reasons = []

        ts = _normalize_timestamp(r.get("timestamp") or r.get("created_at"))
        if not ts:
            reasons.append(f"timestamp tidak valid: '{r.get('timestamp')}'")

        raw_level = r.get("water_level")
        level = None
        if raw_level is None:
            reasons.append("water_level kosong")
        else:
            try:
                level = float(raw_level)
            except (ValueError, TypeError):
                reasons.append(f"water_level bukan angka: '{raw_level}'")
            else:
                if not (LEVEL_MIN_VALID <= level <= LEVEL_MAX_VALID):
                    reasons.append(f"water_level di luar range: {level}")
                    level = None

        raw_status = str(r.get("status", "")).lower().strip()
        status = STATUS_MAP.get(raw_status, "normal")

        if ts is None or level is None:
            rejected.append({**r, "_reject_reasons": reasons})
        else:
            clean.append({
                "timestamp": ts,
                "water_level": level,
                "distance": r.get("distance"),
                "water_raw": r.get("water_raw"),
                "status": status,
            })

    return clean, rejected


# ─── 2. PREPROCESSING ────────────────────────────────────────────────────────

def preprocess_readings(readings: list, date: Optional[str] = None) -> list:
    if date:
        readings = [r for r in readings if r["timestamp"].startswith(date)]

    readings = sorted(readings, key=lambda r: r["timestamp"])

    seen = set()
    unique = []
    for r in readings:
        key = (r["timestamp"], r["water_level"])
        if key not in seen:
            seen.add(key)
            unique.append(r)

    return unique


# ─── 3. KALKULASI ────────────────────────────────────────────────────────────

def hitung_trend(readings: list) -> str:
    if len(readings) < 2:
        return "stabil"

    first = readings[0]["water_level"]
    last = readings[-1]["water_level"]
    diff = last - first

    if diff > 0.3:
        return "naik"
    if diff < -0.3:
        return "turun"
    return "stabil"


def hitung_avg(readings: list) -> float:
    if not readings:
        return 0.0
    return round(sum(r["water_level"] for r in readings) / len(readings), 4)


def hitung_perubahan(readings: list) -> float:
    if len(readings) < 2:
        return 0.0
    n = len(readings)
    w = max(2, n // 10)
    awal = sum(r["water_level"] for r in readings[:w]) / w
    akhir = sum(r["water_level"] for r in readings[-w:]) / w
    return round(akhir - awal, 4)


def hitung_siaga(readings: list) -> tuple:
    warning_count = sum(1 for r in readings if r["status"] == "warning")
    danger_count = sum(1 for r in readings if r["status"] == "bahaya")
    return warning_count, danger_count


def prediksi_overflow(readings: list, max_capacity: float) -> dict:
    if not readings:
        return {
            "cm_to_overflow": None,
            "estimated_overflow": None,
            "rate_per_minute": None,
        }

    last = readings[-1]["water_level"]
    sisa = round(max_capacity - last, 4)

    # FIX: gunakan key "overflow_status" konsisten, bukan campuran
    if last >= max_capacity:
        return {
            "cm_to_overflow": 0.0,
            "overflow_status": "SUDAH OVERFLOW",
            "estimated_overflow": "SUDAH OVERFLOW",
            "rate_per_minute": None,
        }

    rate = None
    estimasi = None

    try:
        t1 = datetime.strptime(readings[0]["timestamp"], "%Y-%m-%d %H:%M:%S")
        t2 = datetime.strptime(readings[-1]["timestamp"], "%Y-%m-%d %H:%M:%S")
        menit = (t2 - t1).total_seconds() / 60

        if menit > 0:
            delta = readings[-1]["water_level"] - readings[0]["water_level"]
            rate = round(delta / menit, 6)
            if rate > 0 and sisa > 0:
                estimasi = (t2 + timedelta(minutes=sisa / rate)).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
    except Exception:
        pass

    return {
        "cm_to_overflow": sisa,
        "estimated_overflow": estimasi,
        "rate_per_minute": rate,
    }


def format_untuk_llm(readings: list) -> str:
    n = len(readings)
    sample = readings if n <= 20 else (
        readings[:5]
        + readings[n // 2 - 2: n // 2 + 3]
        + readings[-5:]
    )
    lines = [
        f"- [{r['timestamp']}] {r['water_level']} cm | {r['status']}"
        for r in sample
    ]
    if n > 20:
        lines.insert(5, f"  ... ({n - 20} data lainnya) ...")
    return "\n".join(lines)


# ─── PIPELINE UTAMA ──────────────────────────────────────────────────────────

def process(
    readings: list,
    date: Optional[str] = None,
    threshold_warning: float = DEFAULT_THRESHOLD_WARNING,
    threshold_danger: float = DEFAULT_THRESHOLD_DANGER,
    max_capacity: float = DEFAULT_MAX_CAPACITY,
) -> dict:

    clean, rejected = clean_readings(readings)
    clean = preprocess_readings(clean, date)

    if not clean:
        return {
            "clean_readings": [],
            "rejected": rejected,
            "stats": None,
            "sensor_text": "",
            "is_empty": True,
        }

    warning, bahaya = hitung_siaga(clean)
    overflow = prediksi_overflow(clean, max_capacity)
    last = clean[-1]

    stats = {
        "trend": hitung_trend(clean),
        "avg_height": hitung_avg(clean),
        "water_level_change": hitung_perubahan(clean),
        "warning_count": warning,
        "danger_count": bahaya,
        "total_readings": len(clean),
        "first_level": clean[0]["water_level"],
        "last_level": last["water_level"],
        "first_timestamp": clean[0]["timestamp"],
        "last_timestamp": last["timestamp"],
        "alarm_active": last.get("alarm_active", False),
        "pump_status": last.get("pump_status", False),
        **overflow,
    }

    return {
        "clean_readings": clean,
        "rejected": rejected,
        "stats": stats,
        "sensor_text": format_untuk_llm(clean),
        "is_empty": False,
    }
