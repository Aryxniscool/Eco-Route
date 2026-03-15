@router.get("/live_conditions")
async def live_conditions(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
):
    """Get real-time AQI from WAQI and weather from Open-Meteo."""

    waqi_token = os.getenv("WAQI_TOKEN")
    if not waqi_token:
        raise HTTPException(status_code=500, detail="WAQI_TOKEN not configured")

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            aqi_res, weather_res = await asyncio.gather(
                client.get(
                    f"https://api.waqi.info/feed/geo:{lat};{lon}/?token={waqi_token}"
                ),
                client.get(
                    f"https://api.open-meteo.com/v1/forecast"
                    f"?latitude={lat}&longitude={lon}"
                    f"&current=temperature_2m,relative_humidity_2m,wind_speed_10m"
                ),
            )

        aqi_data = aqi_res.json()
        weather_data = weather_res.json()

        # Guard: WAQI returns status "ok" on success
        if aqi_data.get("status") != "ok":
            raise HTTPException(status_code=502, detail="WAQI API error")

        iaqi = aqi_data["data"].get("iaqi", {})
        current = weather_data.get("current", {})

        return {
            "aqi":         aqi_data["data"].get("aqi"),
            "pm25":        iaqi.get("pm25", {}).get("v"),
            "no2":         iaqi.get("no2",  {}).get("v"),
            "pm10":        iaqi.get("pm10", {}).get("v"),
            "temperature": current.get("temperature_2m"),
            "humidity":    current.get("relative_humidity_2m"),
            "wind_speed":  current.get("wind_speed_10m"),
            "station":     aqi_data["data"].get("city", {}).get("name", "Unknown"),
            "timestamp":   datetime.now().isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Live conditions fetch failed: {str(e)}")