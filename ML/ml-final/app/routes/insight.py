from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.insight_service import run_insight
from app.config import settings
from app.data_processor import (
    DEFAULT_THRESHOLD_WARNING,
    DEFAULT_THRESHOLD_DANGER,
    DEFAULT_MAX_CAPACITY,
)

router = APIRouter()


# =========================
# SENSOR MODEL
# =========================
class SensorReading(BaseModel):
    timestamp: str
    water_level: float
    distance: Optional[float] = None
    water_raw: Optional[float] = None
    status: Optional[str] = "normal"


# =========================
# REQUEST MODEL
# =========================
class InsightRequest(BaseModel):
    period: str = "realtime"
    readings: List[SensorReading]
    date: Optional[str] = None
    # FIX: bisa override threshold per-request, default dari settings
    threshold_warning: float = settings.THRESHOLD_WARNING
    threshold_danger: float = settings.THRESHOLD_DANGER
    max_capacity: float = settings.MAX_CAPACITY


# =========================
# RESPONSE MODEL
# =========================
class InsightResponse(BaseModel):
    trend: str = "stabil"
    warning: int = 0
    danger: int = 0
    water_level_change: float = 0.0
    avg_height: float = 0.0
    cm_to_overflow: float = 0.0
    estimated_overflow: Optional[str] = None
    summary: str = ""
    recommendation: str = "Pantau kondisi secara rutin."


# =========================
# REALTIME ENDPOINT
# =========================
@router.post("/", response_model=InsightResponse)
async def get_insight(request: InsightRequest):
    """Endpoint insight realtime — kirim array readings dari IoT."""
    if not request.readings:
        raise HTTPException(status_code=400, detail="Data sensor tidak boleh kosong.")

    result = await run_insight(
        period=request.period,
        readings=[r.model_dump() for r in request.readings],
        date=request.date,
        threshold_warning=request.threshold_warning,
        threshold_danger=request.threshold_danger,
        max_capacity=request.max_capacity,
    )
    return result


# =========================
# DAILY ENDPOINT
# =========================
@router.post("/daily", response_model=InsightResponse)
async def get_daily_insight(request: InsightRequest):
    """Endpoint insight harian — summary dan rekomendasi per hari."""
    if not request.readings:
        raise HTTPException(status_code=400, detail="Data sensor tidak boleh kosong.")

    result = await run_insight(
        period="daily",
        readings=[r.model_dump() for r in request.readings],
        date=request.date,
        threshold_warning=request.threshold_warning,
        threshold_danger=request.threshold_danger,
        max_capacity=request.max_capacity,
    )
    return result
