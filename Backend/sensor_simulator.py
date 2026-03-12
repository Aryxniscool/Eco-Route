"""
IoT Air Quality Sensor Simulator for Jabalpur
Generates realistic pollution readings for 25 locations across the city.
"""
import requests
import time
import random, math
from datetime import datetime
API_URL = "http://127.0.0.1:8000/sensors/update"

SENSOR_LOCATIONS = [
    {"name": "Jabalpur City Center",      "lat": 23.1815, "lon": 79.9864, "base_pm25": 65,  "type": "urban"},
    {"name": "Madan Mahal",               "lat": 23.2000, "lon": 79.9500, "base_pm25": 40,  "type": "residential"},
    {"name": "Adhartal",                  "lat": 23.1650, "lon": 80.0200, "base_pm25": 75,  "type": "commercial"},
    {"name": "Gorakhpur Industrial Area", "lat": 23.1700, "lon": 79.9200, "base_pm25": 130, "type": "industrial"},
    {"name": "Dumna Nature Reserve",      "lat": 23.1298, "lon": 79.9450, "base_pm25": 20,  "type": "green"},
    {"name": "Wright Town",               "lat": 23.2100, "lon": 80.0000, "base_pm25": 55,  "type": "urban"},
    {"name": "Rani Durgavati University", "lat": 23.1550, "lon": 79.9700, "base_pm25": 30,  "type": "green"},
    {"name": "Napier Town",               "lat": 23.1750, "lon": 79.9550, "base_pm25": 50,  "type": "residential"},
    {"name": "Vijay Nagar",               "lat": 23.1900, "lon": 79.9750, "base_pm25": 60,  "type": "urban"},
    {"name": "Garha",                     "lat": 23.2050, "lon": 79.9350, "base_pm25": 70,  "type": "commercial"},
    {"name": "Ranjhi",                    "lat": 23.2200, "lon": 79.9650, "base_pm25": 85,  "type": "industrial"},
    {"name": "Gwarighat",                 "lat": 23.1400, "lon": 79.9300, "base_pm25": 35,  "type": "green"},
    {"name": "Tilwara Ghat",              "lat": 23.1350, "lon": 79.9600, "base_pm25": 38,  "type": "green"},
    {"name": "South Civil Lines",         "lat": 23.1680, "lon": 79.9420, "base_pm25": 45,  "type": "residential"},
    {"name": "Sanjeevani Nagar",          "lat": 23.1950, "lon": 79.9900, "base_pm25": 55,  "type": "residential"},
    {"name": "Khamaria",                  "lat": 23.1530, "lon": 80.0100, "base_pm25": 95,  "type": "industrial"},
    {"name": "Shakti Nagar",              "lat": 23.2080, "lon": 79.9800, "base_pm25": 58,  "type": "urban"},
    {"name": "Patan",                     "lat": 23.1450, "lon": 79.9850, "base_pm25": 42,  "type": "residential"},
    {"name": "Gohalpur",                  "lat": 23.2300, "lon": 80.0050, "base_pm25": 48,  "type": "residential"},
    {"name": "Bargi Hills",              "lat": 23.1100, "lon": 79.9700, "base_pm25": 22,  "type": "green"},
    {"name": "Jabalpur Cantt",            "lat": 23.1620, "lon": 79.9580, "base_pm25": 38,  "type": "residential"},
    {"name": "Russel Chowk",              "lat": 23.1780, "lon": 79.9680, "base_pm25": 72,  "type": "commercial"},
    {"name": "Marhatal",                  "lat": 23.1850, "lon": 79.9400, "base_pm25": 62,  "type": "urban"},
    {"name": "Kamla Nehru Nagar",         "lat": 23.1970, "lon": 79.9550, "base_pm25": 52,  "type": "residential"},
    {"name": "Bhedaghat Road",            "lat": 23.1200, "lon": 79.9900, "base_pm25": 28,  "type": "green"},
]


def _time_factor():
    hour = datetime.now().hour
    if 8 <= hour <= 10 or 17 <= hour <= 20:
        return 1.3
    elif 11 <= hour <= 16:
        return 1.1
    elif 6 <= hour <= 7:
        return 0.9
    else:
        return 0.7


def _type_multiplier(zone_type):
    return {"industrial": 1.4, "commercial": 1.15, "urban": 1.0, "residential": 0.85, "green": 0.6}.get(zone_type, 1.0)


def _compute_aqi(pm25):
    if pm25 <= 12:
        return int(pm25 / 12 * 50)
    elif pm25 <= 35.4:
        return int(50 + (pm25 - 12) / 23.4 * 50)
    elif pm25 <= 55.4:
        return int(100 + (pm25 - 35.4) / 20 * 50)
    elif pm25 <= 150.4:
        return int(150 + (pm25 - 55.4) / 95 * 100)
    elif pm25 <= 250.4:
        return int(250 + (pm25 - 150.4) / 100 * 100)
    else:
        return int(min(500, 350 + (pm25 - 250.4) / 100 * 150))


def generate_sensor_reading(location):
    tf = _time_factor()
    tm = _type_multiplier(location["type"])
    noise = random.gauss(0, location["base_pm25"] * 0.15)
    pm25 = max(5, location["base_pm25"] * tf * tm + noise)
    pm10 = pm25 * random.uniform(1.4, 2.0)
    no2 = pm25 * random.uniform(0.8, 1.5) + random.uniform(-5, 10)
    aqi = _compute_aqi(pm25)
    return {
        "name": location["name"],
        "lat": location["lat"],
        "lon": location["lon"],
        "zone_type": location["type"],
        "pm25": round(pm25, 1),
        "pm10": round(pm10, 1),
        "no2": round(max(0, no2), 1),
        "aqi": aqi,
        "timestamp": datetime.now().isoformat(),
    }


def generate_all_sensors():
    return [generate_sensor_reading(loc) for loc in SENSOR_LOCATIONS]


def get_nearest_sensor(lat, lon):
    best, best_dist = None, float("inf")
    for loc in SENSOR_LOCATIONS:
        d = math.hypot(loc["lat"] - lat, loc["lon"] - lon)
        if d < best_dist:
            best_dist, best = d, loc
    return generate_sensor_reading(best)

if __name__ == "__main__":
    while True:
        readings = generate_all_sensors()

        try:
            requests.post(API_URL, json={"sensors": readings})
            print(f"Sent {len(readings)} sensor readings")
        except:
            print("Backend not running")

        time.sleep(10)
