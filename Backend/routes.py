"""
API Route Handlers for EcoRoute Backend
"""

from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel
from datetime import datetime
import httpx

from sensor_simulator import generate_all_sensors, get_nearest_sensor
from pollution_model import predict_pollution, predict_hourly_forecast
from route_optimizer import generate_demo_routes, rank_routes

router = APIRouter()

# ── In-memory store for community reports ──
community_reports = []

# ── OpenRouteService config ──
ORS_API_KEY = ""  # Add your API key here
ORS_BASE_URL = "https://api.openrouteservice.org/v2/directions"

TRANSPORT_PROFILES = {
    "walk": "foot-walking",
    "cycle": "cycling-regular",
    "drive": "driving-car",
}


# ──────── Route API ────────
@router.get("/route")
async def get_route(
    origin_lat: float = Query(..., description="Origin latitude"),
    origin_lon: float = Query(..., description="Origin longitude"),
    dest_lat: float = Query(..., description="Destination latitude"),
    dest_lon: float = Query(..., description="Destination longitude"),
    mode: str = Query("walk", description="Transport mode: walk, cycle, drive"),
):
    """
    Get 2-3 routes between origin and destination,
    scored by pollution exposure and distance.
    """
    profile = TRANSPORT_PROFILES.get(mode, "foot-walking")

    # Try OpenRouteService API
    if ORS_API_KEY:
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(
                    f"{ORS_BASE_URL}/{profile}",
                    params={
                        "api_key": ORS_API_KEY,
                        "start": f"{origin_lon},{origin_lat}",
                        "end": f"{dest_lon},{dest_lat}",
                        "alternative_routes[share_factor]": 0.6,
                        "alternative_routes[target_count]": 3,
                    },
                )
                if resp.status_code == 200:
                    data = resp.json()
                    routes = data.get("features", [])
                    if routes:
                        return rank_routes(routes)
        except Exception as e:
            print(f"ORS API error: {e}")

    # Fallback: generate demo routes
    return generate_demo_routes(origin_lat, origin_lon, dest_lat, dest_lon)


# ──────── Pollution API ────────
@router.get("/pollution")
async def get_pollution(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
):
    """
    Get pollution data for a specific location.
    Uses simulated sensor network (or OpenAQ when key is configured).
    """
    reading = get_nearest_sensor(lat, lon)
    return {
        "aqi": reading["aqi"],
        "pm25": reading["pm25"],
        "pm10": reading["pm10"],
        "no2": reading["no2"],
        "location": reading["name"],
        "zone_type": reading["zone_type"],
        "timestamp": reading["timestamp"],
    }


# ──────── Sensor Grid API ────────
@router.get("/sensors")
async def get_sensors():
    """Get readings from all simulated IoT sensors."""
    return {"sensors": generate_all_sensors(), "count": 25}


# ──────── AI Prediction API ────────
class PredictionRequest(BaseModel):
    temperature: float = 31
    humidity: float = 68
    traffic: float = 70
    hour: int = 18

@router.post("/predict_pollution")
async def predict(req: PredictionRequest):
    """Predict PM2.5 level using the ML model."""
    result = predict_pollution(req.temperature, req.humidity, req.traffic, req.hour)
    return result


# ──────── Hourly Forecast API ────────
class ForecastRequest(BaseModel):
    temperature: float = 31
    humidity: float = 68
    traffic: float = 70
    start_hour: int = 15
    hours: int = 6

@router.post("/forecast")
async def forecast(req: ForecastRequest):
    """Get multi-hour pollution forecast."""
    return {"forecast": predict_hourly_forecast(
        req.temperature, req.humidity, req.traffic, req.start_hour, req.hours
    )}


# ──────── Community Reports API ────────
class PollutionReport(BaseModel):
    lat: float
    lon: float
    description: str
    severity: str = "moderate"  # low, moderate, high
    reporter: str = "anonymous"

@router.post("/report_pollution")
async def report_pollution(report: PollutionReport):
    """Submit a crowdsourced pollution report."""
    entry = {
        "id": len(community_reports) + 1,
        "lat": report.lat,
        "lon": report.lon,
        "description": report.description,
        "severity": report.severity,
        "reporter": report.reporter,
        "timestamp": datetime.now().isoformat(),
    }
    community_reports.append(entry)
    return {"status": "submitted", "report": entry}


@router.get("/community_reports")
async def get_community_reports():
    """Get all community pollution reports."""
    return {"reports": community_reports, "count": len(community_reports)}
