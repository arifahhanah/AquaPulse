"""
test.py
───────
Mode 1 — dummy data (tidak perlu DB, tidak perlu service jalan):
    python test.py

Mode 2 — dari MySQL langsung (perlu DB & service jalan):
    python test.py db
"""

import sys
import requests

BASE_URL = "http://localhost:8001"

# Sesuaikan threshold dengan skala sensor fisik kamu
# Dari screenshot DB, water_level ~10 cm
THRESHOLD_WARNING = 8.0
THRESHOLD_DANGER  = 10.0
MAX_CAPACITY      = 12.0

BASE_BODY = {
    "period":            "daily",
    "threshold_warning": THRESHOLD_WARNING,
    "threshold_danger":  THRESHOLD_DANGER,
    "max_capacity":      MAX_CAPACITY,
}

# ─── Data Dummy (sesuai schema DB IoT) ───────────────────────────────────────
# Schema DB: id, timestamp, water_level, distance, water_raw, status, created_at
# Status dari DB: "bahaya" (akan dinormalisasi → siaga2 otomatis)

READINGS_BAHAYA = [
    {"timestamp": "2026-04-26 06:00:00", "water_level": 5.1,  "distance": 6.9,  "water_raw": 0, "status": "normal"},
    {"timestamp": "2026-04-26 07:00:00", "water_level": 5.8,  "distance": 6.2,  "water_raw": 0, "status": "normal"},
    {"timestamp": "2026-04-26 08:00:00", "water_level": 6.5,  "distance": 5.5,  "water_raw": 0, "status": "normal"},
    {"timestamp": "2026-04-26 09:00:00", "water_level": 7.2,  "distance": 4.8,  "water_raw": 0, "status": "normal"},
    {"timestamp": "2026-04-26 10:00:00", "water_level": 8.1,  "distance": 3.9,  "water_raw": 0, "status": "warning"},
    {"timestamp": "2026-04-26 11:00:00", "water_level": 8.9,  "distance": 3.1,  "water_raw": 0, "status": "warning"},
    {"timestamp": "2026-04-26 12:00:00", "water_level": 10.2, "distance": 1.8,  "water_raw": 0, "status": "bahaya"},
    {"timestamp": "2026-04-26 13:00:00", "water_level": 10.7, "distance": 1.3,  "water_raw": 0, "status": "bahaya"},
]

READINGS_NORMAL = [
    # Mirip data screenshot DB yang asli
    {"timestamp": "2026-04-26 19:19:07", "water_level": 10.1229, "distance": 6.8715, "water_raw": 0, "status": "bahaya"},
    {"timestamp": "2026-04-26 19:19:09", "water_level": 10.4487, "distance": 6.5513, "water_raw": 0, "status": "bahaya"},
    {"timestamp": "2026-04-26 19:19:17", "water_level": 10.4487, "distance": 6.5513, "water_raw": 0, "status": "bahaya"},
    {"timestamp": "2026-04-26 19:19:19", "water_level": 10.7688, "distance": 6.2317, "water_raw": 0, "status": "bahaya"},
]

READINGS_TURUN = [
    {"timestamp": "2026-04-27 06:00:00", "water_level": 10.5, "distance": 1.5, "water_raw": 0, "status": "bahaya"},
    {"timestamp": "2026-04-27 08:00:00", "water_level": 9.8,  "distance": 2.2, "water_raw": 0, "status": "warning"},
    {"timestamp": "2026-04-27 10:00:00", "water_level": 8.5,  "distance": 3.5, "water_raw": 0, "status": "warning"},
    {"timestamp": "2026-04-27 12:00:00", "water_level": 7.2,  "distance": 4.8, "water_raw": 0, "status": "normal"},
    {"timestamp": "2026-04-27 14:00:00", "water_level": 6.0,  "distance": 6.0, "water_raw": 0, "status": "normal"},
]

READINGS_KOTOR = [
    {"timestamp": "2026-04-28 06:00:00", "water_level": 5.0,   "distance": 7.0,  "water_raw": 0, "status": "normal"},
    {"timestamp": "",                     "water_level": 6.0,   "distance": 6.0,  "water_raw": 0, "status": "normal"},   # timestamp kosong
    {"timestamp": "2026-04-28 08:00:00", "water_level": -1.0,  "distance": 5.0,  "water_raw": 0, "status": "normal"},   # level negatif
    {"timestamp": "2026-04-28 09:00:00", "water_level": 999.0, "distance": 1.0,  "water_raw": 0, "status": "normal"},   # out of range
    {"timestamp": "2026-04-28 10:00:00", "water_level": 7.5,   "distance": 4.5,  "water_raw": 0, "status": "rusak"},    # status invalid
    {"timestamp": "2026-04-28 11:00:00", "water_level": 8.2,   "distance": 3.8,  "water_raw": 0, "status": "warning"},
    {"timestamp": "2026-04-28 12:00:00", "water_level": 9.5,   "distance": 2.5,  "water_raw": 0, "status": "warning"},
    {"timestamp": "2026-04-28 13:00:00", "water_level": 10.3,  "distance": 1.7,  "water_raw": 0, "status": "bahaya"},
]


# ─── Helper ───────────────────────────────────────────────────────────────────

def print_result(label: str, result: dict):
    print(f"\n{'='*65}")
    print(f"  {label}")
    print(f"{'='*65}")
    print(f"  Trend              : {result.get('trend')}")
    print(f"  Siaga 1            : {result.get('warning')} kali")
    print(f"  Siaga 2            : {result.get('danger')} kali")
    print(f"  Perubahan level    : {result.get('water_level_change', 0):+.4f} cm")
    print(f"  Rata-rata level    : {result.get('avg_height', 0):.4f} cm")
    print(f"  Sisa ke overflow   : {result.get('cm_to_overflow')} cm")
    print(f"  Estimasi overflow  : {result.get('estimated_overflow') or '-'}")
    
    print(f"\n  Summary:")
    print(f"  {result.get('summary')}")
    print(f"\n  Rekomendasi:")
    print(f"  {result.get('recommendation')}")


def post(label: str, url: str, body: dict):
    print(f"\n[TEST] {label}")
    try:
        res = requests.post(url, json=body, timeout=60)
        if res.status_code == 200:
            print_result(label, res.json())
        else:
            print(f"  ERROR {res.status_code}: {res.text}")
    except requests.exceptions.ConnectionError:
        print("  ERROR: ML service tidak jalan!")
        print("         Jalankan: uvicorn app.main:app --reload --port 8000")
        sys.exit(1)
    except Exception as e:
        print(f"  ERROR: {e}")


# ─── Mode 1: Dummy ────────────────────────────────────────────────────────────

def run_dummy():
    print("\n" + "="*65)
    print("  MODE: DUMMY DATA")
    print(f"  Threshold: warning={THRESHOLD_WARNING} cm | danger={THRESHOLD_DANGER} cm | max={MAX_CAPACITY} cm")
    print("="*65)

    print("\n[0] Health check...")
    try:
        res = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"  → {res.json()}")
    except requests.exceptions.ConnectionError:
        print("  ERROR: Service tidak jalan! Jalankan dulu:")
        print("         uvicorn app.main:app --reload --port 8000")
        sys.exit(1)

    post("TREN NAIK — warning & bahaya (2026-04-26)",
         f"{BASE_URL}/insight/daily?date=2026-04-26",
         {**BASE_BODY, "readings": READINGS_BAHAYA})

    post("DATA SEPERTI SCREENSHOT DB — semua bahaya (2026-04-26)",
         f"{BASE_URL}/insight/daily?date=2026-04-26",
         {**BASE_BODY, "readings": READINGS_NORMAL})

    post("TREN TURUN — dari bahaya ke normal (2026-04-27)",
         f"{BASE_URL}/insight/daily?date=2026-04-27",
         {**BASE_BODY, "readings": READINGS_TURUN})

    post("DATA KOTOR — test cleaning (2026-04-28)",
         f"{BASE_URL}/insight/daily?date=2026-04-28",
         {**BASE_BODY, "readings": READINGS_KOTOR})

    post("TIDAK ADA DATA — tanggal tidak ada",
         f"{BASE_URL}/insight/daily?date=2099-01-01",
         {**BASE_BODY, "readings": READINGS_BAHAYA})

    print(f"\n{'='*65}")
    print("  SEMUA TEST SELESAI")
    print(f"{'='*65}\n")


# ─── Mode 2: Dari MySQL ───────────────────────────────────────────────────────

def run_from_db():
    try:
        import pymysql
        import pymysql.cursors
    except ImportError:
        print("ERROR: pymysql belum diinstall. Jalankan: pip install pymysql")
        sys.exit(1)

    # ── Sesuaikan dengan koneksi MySQL kamu ──────────────────────────────────
    DB_CONFIG = {
        "host":        "10.57.237.215",
        "port":        3306,
        "user":        "root",
        "password":    "123",           # ← isi password MySQL kamu
        "db":          "water_levels",  # ← isi nama database kamu
        "cursorclass": pymysql.cursors.DictCursor,
    }
    TABLE     = "water_levels"   # ← sesuaikan nama tabel
    TEST_DATE = "2026-04-26"    # ← sesuaikan tanggal yang ada datanya

    print("\n" + "="*65)
    print("  MODE: DARI MYSQL LANGSUNG")
    print(f"  DB    : {DB_CONFIG['db']} @ {DB_CONFIG['host']}")
    print(f"  Tabel : {TABLE}")
    print(f"  Tanggal: {TEST_DATE}")
    print(f"  Threshold: warning={THRESHOLD_WARNING} | danger={THRESHOLD_DANGER} | max={MAX_CAPACITY}")
    print("="*65)

    print("\n[1] Konek ke MySQL...")
    try:
        conn = pymysql.connect(**DB_CONFIG)
        print("  → Berhasil!")
    except Exception as e:
        print(f"  ERROR: {e}")
        sys.exit(1)

    print("\n[2] Ambil data dari DB...")
    with conn:
        with conn.cursor() as cur:
            cur.execute(f"""
                SELECT
                    id,
                    DATE_FORMAT(timestamp,  '%%Y-%%m-%%d %%H:%%i:%%s') AS timestamp,
                    water_level,
                    distance,
                    water_raw,
                    status,
                    DATE_FORMAT(created_at, '%%Y-%%m-%%d %%H:%%i:%%s') AS created_at
                FROM `{TABLE}`
                WHERE DATE(timestamp) = %s
                ORDER BY timestamp ASC
            """, (TEST_DATE,))
            rows = cur.fetchall()

    print(f"  → {len(rows)} baris ditemukan")
    if not rows:
        print(f"  Tidak ada data untuk {TEST_DATE}. Ganti TEST_DATE di test.py")
        sys.exit(0)
    print(f"  Contoh data pertama: {rows[0]}")

    print("\n[3] Kirim ke ML service...")
    post(
        f"DATA MYSQL — {TEST_DATE}",
        f"{BASE_URL}/insight/daily?date={TEST_DATE}",
        {**BASE_BODY, "readings": list(rows)},
    )

    print(f"\n{'='*65}")
    print("  TEST SELESAI")
    print(f"{'='*65}\n")


# ─── Main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "dummy"
    if mode == "db":
        run_from_db()
    else:
        run_dummy()
