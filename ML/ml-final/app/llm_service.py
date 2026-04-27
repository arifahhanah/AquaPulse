import json
import re
from groq import AsyncGroq
from app.config import settings
from app.prompts import build_system_prompt, build_user_prompt

# FIX: gunakan AsyncGroq agar compatible dengan FastAPI async
_client = AsyncGroq(api_key=settings.GROQ_API_KEY)


# ─────────────────────────────────────────────
# JSON PARSER ROBUST
# ─────────────────────────────────────────────

def _extract_json(text: str) -> dict:
    """Extract JSON object dari respons LLM (hapus markdown dll)."""
    if not text:
        return {}

    # Hapus markdown code block
    cleaned = re.sub(r"```(?:json)?", "", text, flags=re.IGNORECASE)
    cleaned = cleaned.replace("```", "").strip()

    try:
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start != -1 and end != -1:
            return json.loads(cleaned[start:end + 1])
    except json.JSONDecodeError:
        pass

    return {}


# ─────────────────────────────────────────────
# MAIN LLM CALL
# ─────────────────────────────────────────────

async def call_llm(
    period: str,
    date,
    stats: dict,
    sensor_text: str,
    threshold_warning: float,
    threshold_danger: float,
    max_capacity: float,
) -> tuple:
    """Panggil Groq LLM dan kembalikan (summary, recommendation)."""

    system_prompt = build_system_prompt(
        threshold_warning=threshold_warning,
        threshold_danger=threshold_danger,
        max_capacity=max_capacity,
        cm_to_overflow=stats.get("cm_to_overflow"),
        estimated_overflow=stats.get("estimated_overflow"),
    )

    user_prompt = build_user_prompt(
        period, date, stats, sensor_text,
        threshold_warning, threshold_danger, max_capacity,
    )

    try:
        response = await _client.chat.completions.create(
            model=settings.GROQ_MODEL,
            temperature=0.2,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )

        raw = response.choices[0].message.content or ""
        parsed = _extract_json(raw)

        if parsed:
            summary = str(parsed.get("summary", "")).strip()
            recommendation = str(parsed.get("recommendation", "")).strip()
            if summary and recommendation:
                return summary, recommendation

        return (
            "Insight tidak valid dari LLM, gunakan data statistik.",
            "Pantau kondisi air secara berkala dan aktifkan alert manual.",
        )

    except Exception as e:
        return (
            f"LLM error: {str(e)}",
            "Gunakan mode monitoring manual sementara.",
        )
