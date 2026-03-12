"""
EcoRoute Backend — FastAPI Application
Run with: uvicorn main:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from routes import router
from pollution_model import train_model

# ── Create app ──
app = FastAPI(
    title="EcoRoute API",
    description="Climate-tech navigation backend for healthier urban routing",
    version="1.0.0",
)

# ── CORS (allow frontend to call API) ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Include all API routes ──
app.include_router(router)


# ── Train ML model on startup ──
@app.on_event("startup")
async def startup():
    result = train_model()
    print(f"ML Model trained: R2={result['r2_score']}, samples={result['n_samples']}")


# ── Health check ──
@app.get("/")
async def root():
    return {
        "name": "EcoRoute API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": [
            "GET  /route?origin_lat=&origin_lon=&dest_lat=&dest_lon=&mode=walk",
            "GET  /pollution?lat=&lon=",
            "GET  /sensors",
            "POST /predict_pollution",
            "POST /forecast",
            "POST /report_pollution",
            "GET  /community_reports",
        ],
    }


# ── Serve frontend (optional — if index.html is in parent dir) ──
frontend_path = os.path.join(os.path.dirname(__file__), "..", "index.html")
if os.path.exists(frontend_path):
    @app.get("/app")
    async def serve_frontend():
        return FileResponse(frontend_path)
