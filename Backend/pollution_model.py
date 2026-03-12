"""
AI Pollution Prediction Model
Linear Regression (scikit-learn) predicts PM2.5 from
temperature, humidity, traffic density, and hour of day.
"""

import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures

_model = None
_poly = None


def _generate_training_data(n=500):
    np.random.seed(42)
    data, targets = [], []
    for _ in range(n):
        temp = np.random.uniform(15, 45)
        humidity = np.random.uniform(20, 95)
        traffic = np.random.uniform(10, 100)
        hour = np.random.randint(0, 24)

        base = 15
        traffic_eff = traffic * 0.45
        temp_eff = max(0, (temp - 25) * 0.8)
        humidity_eff = -humidity * 0.05
        if 8 <= hour <= 10:
            hour_eff = 25
        elif 17 <= hour <= 20:
            hour_eff = 30
        elif 0 <= hour <= 5:
            hour_eff = 10
        else:
            hour_eff = 5

        pm25 = max(5, base + traffic_eff + temp_eff + humidity_eff + hour_eff + np.random.normal(0, 8))
        data.append([temp, humidity, traffic, hour])
        targets.append(pm25)
    return np.array(data), np.array(targets)


def train_model():
    global _model, _poly
    X, y = _generate_training_data()
    _poly = PolynomialFeatures(degree=2, include_bias=False)
    X_poly = _poly.fit_transform(X)
    _model = LinearRegression()
    _model.fit(X_poly, y)
    score = _model.score(X_poly, y)
    return {"status": "trained", "r2_score": round(score, 4), "n_samples": len(y)}


def predict_pollution(temperature, humidity, traffic, hour):
    global _model, _poly
    if _model is None:
        train_model()
    features = np.array([[temperature, humidity, traffic, hour]])
    features_poly = _poly.transform(features)
    predicted = max(5, round(float(_model.predict(features_poly)[0]), 1))

    if predicted <= 12:
        cat, col = "Good", "#34c759"
    elif predicted <= 35.4:
        cat, col = "Moderate", "#ffd60a"
    elif predicted <= 55.4:
        cat, col = "Unhealthy for Sensitive Groups", "#ff9f0a"
    elif predicted <= 150.4:
        cat, col = "Unhealthy", "#ff3b30"
    else:
        cat, col = "Very Unhealthy", "#8e0000"

    return {
        "predicted_pm25": predicted,
        "category": cat,
        "color": col,
        "input": {"temperature": temperature, "humidity": humidity, "traffic": traffic, "hour": hour},
    }


def predict_hourly_forecast(temperature, humidity, traffic, start_hour, hours=6):
    forecast = []
    for i in range(hours + 1):
        h = (start_hour + i) % 24
        t_adj = traffic
        if 17 <= h <= 20:
            t_adj = min(100, traffic * 1.4)
        elif 0 <= h <= 5:
            t_adj = max(10, traffic * 0.4)
        pred = predict_pollution(temperature, humidity, t_adj, h)
        forecast.append({"hour": h, "label": f"+{i}h" if i > 0 else "Now", **pred})
    return forecast


if __name__ == "__main__":
    import json
    print("Training:", json.dumps(train_model(), indent=2))
    print("Predict:", json.dumps(predict_pollution(31, 68, 70, 18), indent=2))
