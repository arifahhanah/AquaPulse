"""
prompts.py — semua prompt LLM ada di sini.
Pakai str.replace() bukan str.format() untuk hindari konflik {{ }} JSON.
"""
from typing import Optional

SYSTEM_PROMPT = """Kamu adalah sistem analisis monitoring level air pada wadah/penampung air kecil.

Konteks:
- Pompa MENGALIRKAN air MASUK ke wadah (bukan menyedot keluar)
- Jika level tinggi → pompa harus DIMATIKAN agar tidak meluap
- Jika level normal → pompa boleh dinyalakan

OUTPUT WAJIB: JSON satu baris tanpa markdown, tanpa penjelasan:
{"summary": "...", "recommendation": "..."}

ATURAN SUMMARY (2-3 kalimat):
- Sebutkan level awal dan akhir dalam cm
- Sebutkan tren (naik/turun/stabil)
- Sebutkan jumlah siaga 1 dan siaga 2
- Sebutkan estimasi overflow jika ada

ATURAN REKOMENDASI (cek dari atas, pakai yang pertama cocok):
- Jika level >= MAXCAP → "OVERFLOW TERJADI. Segera kurangi volume air."
- Jika danger → "BAHAYA: Level mencapai TDANG cm, Pompa dimatikan"
- Jika warning>0 DAN trend naik → "PERINGATAN: Level naik mendekati batas bahaya TDANG cm. Sisa SISA cm menuju overflow."
- Jika warning>0 DAN trend stabil → "Level di zona siaga 1. Pantau dan jangan nyalakan pompa."
- Jika warning>0 DAN trend turun → "Level siaga 1 mulai turun. Kondisi membaik."
- Jika normal DAN trend naik → "Level normal tapi tren naik. Pantau agar tidak mencapai TWARN cm."
- Jika normal DAN trend turun → "Kondisi aman, tren turun."
- Jika normal DAN trend stabil → "Kondisi aman dan stabil."

ATURAN KETAT:
- Output HANYA JSON satu baris
- Jangan gunakan null atau string kosong
- Bahasa Indonesia"""


def build_system_prompt(
    threshold_warning: float,
    threshold_danger: float,
    max_capacity: float,
    cm_to_overflow,
    estimated_overflow: Optional[str],
) -> str:
    return (
        SYSTEM_PROMPT
        .replace("MAXCAP", str(max_capacity))
        .replace("SISA", str(cm_to_overflow))
        .replace("ESTOV", str(estimated_overflow or "tidak dapat diprediksi"))
        .replace("TWARN", str(threshold_warning))
        .replace("TDANG", str(threshold_danger))
    )


def build_user_prompt(
    period: str,
    date: Optional[str],
    stats: dict,
    sensor_text: str,
    threshold_warning: float,
    threshold_danger: float,
    max_capacity: float,
) -> str:
    estimated = stats.get("estimated_overflow")
    rate = stats.get("rate_per_minute")

    if estimated == "SUDAH OVERFLOW":
        overflow_text = "SUDAH OVERFLOW"
    elif estimated and rate:
        overflow_text = f"{estimated} (laju: {rate:+.6f} cm/menit)"
    else:
        overflow_text = "Tidak dapat diprediksi"

    return (
        f"Periode   : {period} harian{f' - {date}' if date else ''}\n"
        f"Total data: {stats['total_readings']} pembacaan\n"
        f"\n"
        f"KONFIGURASI:\n"
        f"- Warning  : {threshold_warning} cm\n"
        f"- Danger   : {threshold_danger} cm\n"
        f"- Kapasitas maksimal : {max_capacity} cm\n"
        f"\n"
        f"STATISTIK:\n"
        f"- Tren               : {stats['trend']}\n"
        f"- Level awal         : {stats['first_level']:.4f} cm ({stats['first_timestamp']})\n"
        f"- Level akhir        : {stats['last_level']:.4f} cm ({stats['last_timestamp']})\n"
        f"- Perubahan level    : {stats['water_level_change']:+.4f} cm\n"
        f"- Rata-rata level    : {stats['avg_height']:.4f} cm\n"
        f"- Kejadian warning   : {stats['warning_count']} kali\n"
        f"- Kejadian danger    : {stats['danger_count']} kali\n"
        f"\n"
        f"PREDIKSI OVERFLOW:\n"
        f"- Sisa menuju overflow: {stats['cm_to_overflow']:.4f} cm\n"
        f"- Estimasi            : {overflow_text}\n"
        f"\n"
        f"SAMPEL DATA SENSOR:\n"
        f"{sensor_text}\n"
        f"\n"
        f'Tulis JSON satu baris: {{"summary": "...", "recommendation": "..."}}'
    )
