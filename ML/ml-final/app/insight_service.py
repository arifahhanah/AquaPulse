from typing import Optional
from datetime import datetime, timedelta
from app.data_processor import process, DEFAULT_THRESHOLD_WARNING, DEFAULT_THRESHOLD_DANGER, DEFAULT_MAX_CAPACITY
from app.llm_service import call_llm

# ── State global throttle ──────────────────────────
_last_llm_call: Optional[datetime] = None
_last_llm_result: tuple = (
    "Belum ada insight.",
    "Pantau kondisi secara rutin."
)
LLM_INTERVAL_SECONDS = 5  # ganti 5 atau 10 sesuai kebutuhan

# ──────────────────────────────────────────────────

def normalize_date(date) -> Optional[str]:
    if not date:
        return None
    return str(date)[:10]


async def run_insight(
    period: str,
    readings: list,
    date: Optional[str] = None,
    threshold_warning: float = DEFAULT_THRESHOLD_WARNING,
    threshold_danger: float = DEFAULT_THRESHOLD_DANGER,
    max_capacity: float = DEFAULT_MAX_CAPACITY,
) -> dict:
    global _last_llm_call, _last_llm_result

    date = normalize_date(date)

    result = process(readings, date, threshold_warning, threshold_danger, max_capacity)

    if result.get("is_empty"):
        return {
            "trend": "stabil",
            "warning": 0,
            "danger": 0,
            "water_level_change": 0.0,
            "avg_height": 0.0,
            "cm_to_overflow": 0.0,
            "estimated_overflow": None,
            "summary": "Tidak ada data sensor yang valid.",
            "recommendation": "Cek koneksi sensor dan pastikan data terkirim.",
        }

    stats = result.get("stats") or {}
    sensor_text = result.get("sensor_text", "")

    # ── Throttle: cek apakah sudah waktunya panggil LLM ──
    now = datetime.now()
    should_call_llm = (
        _last_llm_call is None or
        (now - _last_llm_call).total_seconds() >= LLM_INTERVAL_SECONDS
    )

    if should_call_llm:
        try:
            summary, recommendation = await call_llm(
                period, date, stats, sensor_text,
                threshold_warning, threshold_danger, max_capacity,
            )
            _last_llm_result = (summary, recommendation)
            _last_llm_call = now
        except Exception as e:
            summary = f"LLM tidak tersedia: {str(e)}"
            recommendation = "Gunakan monitoring manual sementara LLM tidak aktif."
            _last_llm_result = (summary, recommendation)
    else:
        # pakai hasil LLM terakhir
        summary, recommendation = _last_llm_result

    return {
        "trend": stats.get("trend", "stabil"),
        "warning": stats.get("warning_count", 0),
        "danger": stats.get("danger_count", 0),
        "water_level_change": stats.get("water_level_change", 0.0),
        "avg_height": stats.get("avg_height", 0.0),
        "cm_to_overflow": stats.get("cm_to_overflow") or 0.0,
        "estimated_overflow": stats.get("estimated_overflow"),
        "summary": summary,
        "recommendation": recommendation,
    }