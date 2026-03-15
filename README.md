# 🌿 EcoRoute — AI-Powered Clean Air Navigation

> **Navigate cities. Breathe cleaner. Live longer.**

EcoRoute is a full-stack climate-tech web application that recommends the **healthiest travel route** — not just the fastest one. It compares three route options in real time, scoring each by pollution exposure using live AQI data, ML predictions, and IoT sensor readings.

🔗 **[Live Demo](https://eco-route-ruby.vercel.app)** · 📦 **[Backend API](https://eco-route.onrender.com/docs)**

---

![EcoRoute Dark Mode](Images/DarkMode.png)

---

## ✨ Features

### 🗺️ Smart Route Planning

EcoRoute calculates and compares three route options:

| Route | Description |
|---|---|
| 🔴 **Fastest Route** | Shortest travel time — may pass through high-pollution zones |
| 🟡 **Balanced Route** | Compromise between speed and air quality |
| 🟢 **Cleanest Route** | Lowest pollution exposure — the recommended route |

Scored using: `Route Score = 0.7 × Pollution Exposure + 0.3 × Distance`

![Route Comparison](Images/RouteComparision.png)

---

### 🌫️ Live Air Quality Map

- Real-time AQI from 25 IoT sensors across Jabalpur (simulated grid)
- Live AQI data from WAQI monitoring stations
- Visual pollution clouds across the city
- Interactive map with AQI, PM2.5, NO₂, and Green Zone overlays

![Live AQI Map](Images/LiveAirQualityMapDark.png)

---

### 🧠 AI Air Quality Prediction

EcoRoute uses a scikit-learn ML model (Linear Regression) to predict PM2.5 levels based on:
- Temperature
- Humidity
- Traffic density
- Hour of day

Includes a 6-hour forecast to help plan journeys in advance.

![AI Prediction](Images/AiPollutionPredictor.png)

---

### 📊 Pollution Exposure Analysis

For every route EcoRoute calculates:
- Average AQI
- PM2.5 concentration
- Total pollution exposure during travel
- Health score and asthma advisory

![Pollution Analysis](Images/PollutionExposureAnalysis1.png)
![Pollution Analysis](Images/PollutionExposureAnalysis2.png)

---

### 🧑‍🤝‍🧑 Community Pollution Reporting

Users can contribute real-time pollution reports, recording:
- Location of the report
- Type of pollution (smoke, dust, waste burning, traffic congestion)
- Severity level (Low / Moderate / High)
- Timestamp of the observation

![Community Reports](Images/CommunityReports.png)

---

### 🌗 Light & Dark Mode

Full theme support for better usability and accessibility.

| Light Mode | Dark Mode |
|---|---|
| ![Light Mode](Images/LightMode.png) | ![Dark Mode](Images/DarkMode.png) |

---

## 🏗️ Tech Stack

**Frontend**
- HTML5, CSS3, JavaScript (Vanilla)
- Leaflet.js — interactive map visualisation

**Backend**
- Python 3.11
- FastAPI — REST API framework
- scikit-learn — ML pollution prediction (Linear Regression)
- httpx — async API calls

**APIs & Data**
- [OpenRouteService](https://openrouteservice.org/) — real routing with alternative routes
- [WAQI API](https://aqicn.org/api/) — live air quality index data
- [Open-Meteo](https://open-meteo.com/) — real-time weather (free, no key needed)
- Simulated IoT sensor grid — 25 sensors across Jabalpur zones

**Deployment**
- Backend: [Render](https://render.com)
- Frontend: [Vercel](https://vercel.com)

---

## 📂 Project Structure

```
EcoRoute/
├── Frontend/
│   └── index.html              # Full single-page app
├── Backend/
│   ├── main.py                 # FastAPI entry point
│   ├── routes.py               # All API route handlers
│   ├── pollution_model.py      # scikit-learn ML model
│   ├── route_optimizer.py      # Route scoring logic
│   ├── sensor_simulator.py     # IoT sensor grid simulation
│   └── requirements.txt        # Python dependencies
├── Images/                     # Screenshots
└── README.md
```

---

## 🚀 Running Locally

**Backend**

```bash
cd Backend
pip install -r requirements.txt
uvicorn main:app --reload
```

API runs at `http://localhost:8000`  
Interactive docs at `http://localhost:8000/docs`

**Frontend**

Open `Frontend/index.html` directly in your browser, or use the Live Server extension in VS Code.

---

## 🔑 Environment Variables

Set these in your Render dashboard under **Environment**:

| Variable | Description |
|---|---|
| `WAQI_TOKEN` | API token from [aqicn.org/data-platform/token](https://aqicn.org/data-platform/token) |
| `ORS_API_KEY` | API key from [openrouteservice.org](https://openrouteservice.org) |

---

## 🌐 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Health check |
| GET | `/route` | Get 3 scored routes between two points |
| GET | `/pollution` | Pollution data for a location |
| GET | `/sensors` | All 25 IoT sensor readings |
| GET | `/live_conditions` | Real-time AQI + weather data |
| POST | `/predict_pollution` | ML-based PM2.5 prediction |
| POST | `/forecast` | 6-hour pollution forecast |
| POST | `/report_pollution` | Submit a community report |
| GET | `/community_reports` | Get all community reports |

Full interactive docs: [eco-route.onrender.com/docs](https://eco-route.onrender.com/docs)

---

## 📈 Future Improvements

- [ ] Real IoT sensor integration (replace simulation)
- [ ] Wearable device support for personal exposure tracking
- [ ] Multi-city support beyond Jabalpur
- [ ] Personalised health recommendations (asthma, age, activity level)
- [ ] Historical AQI trend analysis
- [ ] PWA support for offline use
- [ ] Real-time traffic + AQI co-optimisation

---

## 🏆 Background

Built for the **CodeKumbh Hackathon** by Team **CodeBlooded**.

After the hackathon we properly deployed the project, integrated real air quality data from live WAQI monitoring stations, fixed coordinate bugs, secured API keys, and built a production-ready backend on Render.

EcoRoute aims to make cities healthier by helping people choose cleaner paths and reduce pollution exposure in daily travel. Small routing decisions can lead to big health improvements for millions of people.

---

## 👨‍💻 Author

**Aryan Khanna** — Student Developer

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Aryan_Khanna-0077B5?style=flat&logo=linkedin)](https://www.linkedin.com/in/aryan-khanna-a12a5737a/)
[![GitHub](https://img.shields.io/badge/GitHub-Aryxniscool-181717?style=flat&logo=github)](https://github.com/Aryxniscool)

---

## 📄 License

MIT License — free to use, modify, and distribute.
