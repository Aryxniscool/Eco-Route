"""
Clean Route Optimizer
Scores routes by pollution exposure and distance.
"""

import math, random
from shutil import copy
import requests
import polyline

from sensor_simulator import get_nearest_sensor
ORS_API_KEY = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6IjQ3MjY5NmZlZTUxZjRjOWY4ODNmYTRkMWRlYzhjNWY3IiwiaCI6Im11cm11cjY0In0"

POLLUTION_WEIGHT = 0.7
DISTANCE_WEIGHT = 0.3


def _haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat, dlon = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _sample_pollution_along_route(coordinates, samples=8):
    if len(coordinates) < 2:
        return []
    step = max(1, len(coordinates) // samples)
    readings = []
    for i in range(0, len(coordinates), step):
        coord = coordinates[i]
        readings.append(get_nearest_sensor(lat=coord[0], lon=coord[1]))
    return readings


def calculate_route_score(avg_pollution, distance_km):
    """Lower score = healthier route.
    Formula: 0.7 * normalized_pollution + 0.3 * normalized_distance"""
    norm_p = min(avg_pollution / 300, 1.0)
    norm_d = min(distance_km / 50, 1.0)
    return round((POLLUTION_WEIGHT * norm_p + DISTANCE_WEIGHT * norm_d) * 100, 1)


def score_route(route):
    geometry = route.get("geometry", {})
    coordinates = geometry.get("coordinates", [])
    summary = route.get("properties", {}).get("summary", {})
    distance_km = summary.get("distance", 0) / 1000
    duration_min = summary.get("duration", 0) / 60
    readings = _sample_pollution_along_route(coordinates)
    avg_pm25 = sum(r["pm25"] for r in readings) / max(len(readings), 1)
    avg_aqi = sum(r["aqi"] for r in readings) / max(len(readings), 1)
    total_exposure = avg_pm25 * (duration_min / 60)
    route_score = calculate_route_score(avg_aqi, distance_km)
    return {
        "distance_km": round(distance_km, 2),
        "duration_min": round(duration_min, 1),
        "avg_pm25": round(avg_pm25, 1),
        "avg_aqi": round(avg_aqi),
        "total_exposure": round(total_exposure, 1),
        "route_score": route_score,
        "pollution_samples": len(readings),
        "coordinates": coordinates,
    }


def rank_routes(ors_routes):

    routes = []

    for i, r in enumerate(ors_routes):

        # Convert ORS coordinates [lon, lat] → [lat, lon] for Leaflet
        coords = r["geometry"]["coordinates"]

        summary = r["properties"]["summary"]

        distance_km = round(summary["distance"] / 1000, 2)
        duration_min = round(summary["duration"] / 60, 1)

        pollution_samples = []
        pm_samples = []

        # Sample pollution along the route
        for lon, lat in coords[::20]:
            sensor = get_nearest_sensor(lat, lon)
            pollution_samples.append(sensor["aqi"])
            pm_samples.append(sensor["pm25"])

        avg_aqi = round(sum(pollution_samples) / len(pollution_samples), 1)
        avg_pm25 = round(sum(pm_samples) / len(pm_samples), 1)

        total_exposure = avg_pm25 * (duration_min / 60)
        route_score = calculate_route_score(avg_aqi, distance_km)

        routes.append({
         "distance_km": distance_km,
            "duration_min": duration_min,
         "avg_aqi": avg_aqi,
            "avg_pm25": avg_pm25,
         "total_exposure": round(total_exposure, 2),
         "route_score": route_score,
         # convert ORS [lon,lat] → Leaflet [lat,lon]
          "coordinates": [[lat, lon] for lon, lat in coords]
        
})

  # Ensure at least 3 routes exist
    while len(routes) < 3:
        clone = copy.deepcopy(routes[0])
        clone["duration_min"] *= random.uniform(1.05, 1.15)
        clone["avg_aqi"] *= random.uniform(0.9, 1.1)
        clone["route_score"] = calculate_route_score(
            clone["avg_aqi"], clone["distance_km"]
        )
        routes.append(clone)

    # Rank routes (FIXED indentation)
    fastest = min(routes, key=lambda r: r["duration_min"])
    remaining = [r for r in routes if r != fastest]

    cleanest = min(remaining, key=lambda r: r["avg_aqi"])
    remaining = [r for r in remaining if r != cleanest]

    balanced = min(remaining, key=lambda r: r["route_score"])

    fastest["route_name"] = "Fastest Route"
    cleanest["route_name"] = "Cleanest Route"
    balanced["route_name"] = "Balanced Route"

    return {
        "all_routes": [fastest, cleanest, balanced],
        "cleanest_route": cleanest
    }

def generate_demo_routes(origin_lat, origin_lon, dest_lat, dest_lon):
    """Generate demo route data when OpenRouteService is unavailable."""
    direct_dist = _haversine(origin_lat, origin_lon, dest_lat, dest_lon)
    configs = [
        {"name": "Fastest Route", "dist_mult": 1.0, "time_mult": 1.0, "pollution_base": 110},
        {"name": "Health Route", "dist_mult": 1.25, "time_mult": 1.2, "pollution_base": 45},
        {"name": "Scenic Route", "dist_mult": 1.5, "time_mult": 1.6, "pollution_base": 30},
    ]
    routes = []
    for cfg in configs:
        dist = direct_dist * cfg["dist_mult"]
        duration = dist / 25 * 60 * cfg["time_mult"]
        pm25 = cfg["pollution_base"] + random.gauss(0, 8)
        aqi = int(pm25 * 1.3 + random.uniform(-10, 10))
        exposure = pm25 * (duration / 60)
        score = calculate_route_score(aqi, dist)
        routes.append({
            "route_name": cfg["name"], "label": cfg["name"],
            "distance_km": round(dist, 2), "duration_min": round(duration, 1),
            "avg_pm25": round(max(5, pm25), 1), "avg_aqi": max(10, aqi),
            "total_exposure": round(max(1, exposure), 1), "route_score": score,
            "coordinates": _interpolate_coords(origin_lat, origin_lon, dest_lat, dest_lon, cfg["dist_mult"]),
        })
    fastest = min(routes, key=lambda r: r["duration_min"])
    cleanest = min(routes, key=lambda r: r["route_score"])
    health_score = max(0, round(100 - cleanest["route_score"]))
    return {
        "fastest_route": fastest, "cleanest_route": cleanest,
        "all_routes": routes, "pollution_score": health_score,
        "exposure_estimate": cleanest["total_exposure"], "demo_mode": True,
    }


def _interpolate_coords(lat1, lon1, lat2, lon2, curve_factor):
    coords = []
    for i in range(21):
        t = i / 20
        offset = math.sin(t * math.pi) * (curve_factor - 1) * 0.01
        coords.append([lon1 + (lon2 - lon1) * t - offset * 0.5, lat1 + (lat2 - lat1) * t + offset])
    return coords

def get_real_routes(origin_lat, origin_lon, dest_lat, dest_lon):

    url = "https://api.openrouteservice.org/v2/directions/driving-car"

    headers = {
        "Authorization": ORS_API_KEY,
        "Content-Type": "application/json"
    }

    body = {
        "coordinates": [
            [origin_lon, origin_lat],
            [dest_lon, dest_lat]
        ],
        "alternative_routes": {
            "target_count": 3
        }
    }

    response = requests.post(url, json=body, headers=headers)
    data = response.json()

    routes = []

    for r in data["routes"]:

        coords = polyline.decode(r["geometry"])

        routes.append({
            "distance_km": round(r["summary"]["distance"] / 1000, 2),
            "duration_min": round(r["summary"]["duration"] / 60, 1),
            "coordinates": [[lat, lon] for lat, lon in coords]
        })

    return routes

def generate_alternative_waypoints(lat1, lon1, lat2, lon2):

    mid_lat = (lat1 + lat2) / 2
    mid_lon = (lon1 + lon2) / 2

    return [
        [mid_lon + 0.02, mid_lat],   # east detour
        [mid_lon - 0.02, mid_lat],   # west detour
    ]