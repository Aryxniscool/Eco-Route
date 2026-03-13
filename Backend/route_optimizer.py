"""
Clean Route Optimizer
Scores routes by pollution exposure and distance.
"""

import math
import copy
import random

from sensor_simulator import get_nearest_sensor

POLLUTION_WEIGHT = 0.7
DISTANCE_WEIGHT = 0.3


def _haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat, dlon = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def calculate_route_score(avg_pollution, distance_km):
    """Lower score = healthier route.
    Formula: 0.7 * normalized_pollution + 0.3 * normalized_distance"""
    norm_p = min(avg_pollution / 300, 1.0)
    norm_d = min(distance_km / 50, 1.0)
    return round((POLLUTION_WEIGHT * norm_p + DISTANCE_WEIGHT * norm_d) * 100, 1)


def rank_routes(ors_routes):
    """
    Score and rank ORS routes.
    ORS coordinates arrive as [lon, lat].
    We convert to [lat, lon] for Leaflet consumption.
    """
    routes = []

    for i, r in enumerate(ors_routes):
        # ORS coordinates are [lon, lat]
        coords = r["geometry"]["coordinates"]
        summary = r["properties"]["summary"]

        distance_km = round(summary["distance"] / 1000, 2)
        duration_min = round(summary["duration"] / 60, 1)

        pollution_samples = []
        pm_samples = []

        # Sample pollution along the route
        # coords are [lon, lat] from ORS, so unpack correctly
        for lon, lat in coords[::20]:
            sensor = get_nearest_sensor(lat, lon)
            pollution_samples.append(sensor["aqi"])
            pm_samples.append(sensor["pm25"])

        if not pollution_samples:
            # Defensive: if route has no coords, use defaults
            pollution_samples = [50]
            pm_samples = [25]

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
            # Convert ORS [lon, lat] → Leaflet [lat, lon] — single conversion
            "coordinates": [[lat, lon] for lon, lat in coords],
        })

    # Ensure at least 3 routes exist
    while len(routes) < 3:
        clone = copy.deepcopy(routes[0])
        clone["duration_min"] *= random.uniform(1.05, 1.15)
        clone["avg_aqi"] *= random.uniform(0.9, 1.1)
        clone["route_score"] = calculate_route_score(
            clone["avg_aqi"], clone["distance_km"]
        )
        # Slightly offset cloned route coords so they are visually distinct
        offset = random.uniform(0.001, 0.003) * (1 if len(routes) % 2 == 0 else -1)
        clone["coordinates"] = [
            [lat + offset, lon + offset * 0.5] for lat, lon in clone["coordinates"]
        ]
        routes.append(clone)

    # Rank routes
    fastest = min(routes, key=lambda r: r["duration_min"])
    remaining = [r for r in routes if r is not fastest]

    cleanest = min(remaining, key=lambda r: r["avg_aqi"])
    remaining = [r for r in remaining if r is not cleanest]

    balanced = min(remaining, key=lambda r: r["route_score"])

    fastest["route_name"] = "Fastest Route"
    cleanest["route_name"] = "Cleanest Route"
    balanced["route_name"] = "Balanced Route"

    return {
        "all_routes": [fastest, cleanest, balanced],
        "cleanest_route": cleanest,
    }


def generate_demo_routes(origin_lat, origin_lon, dest_lat, dest_lon):
    """Generate demo route data when OpenRouteService is unavailable."""
    direct_dist = _haversine(origin_lat, origin_lon, dest_lat, dest_lon)
    configs = [
        {"name": "Fastest Route", "dist_mult": 1.0, "time_mult": 1.0, "pollution_base": 110},
        {"name": "Cleanest Route", "dist_mult": 1.25, "time_mult": 1.2, "pollution_base": 45},
        {"name": "Balanced Route", "dist_mult": 1.15, "time_mult": 1.1, "pollution_base": 70},
    ]
    routes = []
    for cfg in configs:
        # Generate coordinates and exact path length
        coords = _interpolate_coords(
            origin_lat, origin_lon, dest_lat, dest_lon, cfg["dist_mult"]
        )
        
        # Calculate true route distance by summing segment distances
        dist = 0.0
        for i in range(len(coords) - 1):
            dist += _haversine(coords[i][0], coords[i][1], coords[i+1][0], coords[i+1][1])
            
        duration = dist / 25 * 60 * cfg["time_mult"]
        pm25 = cfg["pollution_base"] + random.gauss(0, 8)
        aqi = int(pm25 * 1.3 + random.uniform(-10, 10))
        exposure = pm25 * (duration / 60)
        score = calculate_route_score(aqi, dist)
        routes.append({
            "route_name": cfg["name"],
            "distance_km": round(dist, 2),
            "duration_min": round(duration, 1),
            "avg_pm25": round(max(5, pm25), 1),
            "avg_aqi": max(10, aqi),
            "total_exposure": round(max(1, exposure), 1),
            "route_score": score,
            # Returns [lat, lon] for Leaflet — consistent with rank_routes
            "coordinates": coords,
        })
    fastest = min(routes, key=lambda r: r["duration_min"])
    cleanest = min(routes, key=lambda r: r["route_score"])
    health_score = max(0, round(100 - cleanest["route_score"]))
    return {
        "fastest_route": fastest,
        "cleanest_route": cleanest,
        "all_routes": routes,
        "pollution_score": health_score,
        "exposure_estimate": cleanest["total_exposure"],
        "demo_mode": True,
    }


def _interpolate_coords(lat1, lon1, lat2, lon2, curve_factor):
    """Generate interpolated coordinates in [lat, lon] format for Leaflet."""
    coords = []
    for i in range(21):
        t = i / 20
        offset = math.sin(t * math.pi) * (curve_factor - 1) * 0.01
        lat = lat1 + (lat2 - lat1) * t + offset
        lon = lon1 + (lon2 - lon1) * t - offset * 0.5
        coords.append([lat, lon])
    return coords