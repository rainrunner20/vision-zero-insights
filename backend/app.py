"""Read-only crash-data research API with a restricted demo prediction endpoint.

No public administrative data upload is exposed. Use an authorized,
offline database import instead of posting tokens through the browser.
"""
import logging
import os
from math import isfinite

from flask import Flask, jsonify, request
from flask_cors import CORS

from db import get_recent_crashes, get_crashes_in_bbox

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024

allowed = [
    origin.strip() for origin in os.getenv(
        "VISIONZERO_ALLOWED_ORIGINS", "http://localhost:5173"
    ).split(",") if origin.strip()
]
CORS(app, resources={r"/api/*": {"origins": allowed}})


@app.get("/")
@app.get("/health")
def health():
    # Process liveness, not proof that the database or model is available.
    return jsonify(status="ok", purpose="research-prototype")


@app.get("/api/crashes")
def crashes():
    try:
        count = min(max(int(request.args.get("limit", "200")), 1), 500)
    except ValueError:
        return jsonify(error="Limit must be an integer."), 400

    try:
        return jsonify(get_recent_crashes(limit=count))
    except Exception:
        app.logger.exception("Crash query failed")
        return jsonify(error="Crash data is temporarily unavailable."), 503


@app.get("/api/crashes/bbox")
def crashes_bbox():
    try:
        min_lon, min_lat, max_lon, max_lat = [
            float(request.args[field]) for field in (
                "min_lon", "min_lat", "max_lon", "max_lat"
            )
        ]
        values = (min_lon, min_lat, max_lon, max_lat)
        if not all(isfinite(v) for v in values) or not (
            -180 <= min_lon < max_lon <= 180 and
            -90 <= min_lat < max_lat <= 90
        ):
            raise ValueError("Invalid bounding box.")
    except (KeyError, ValueError, TypeError):
        return jsonify(error="Supply valid min_lon, min_lat, max_lon and max_lat."), 400

    try:
        return jsonify(get_crashes_in_bbox(min_lon, min_lat, max_lon, max_lat, limit=500))
    except Exception:
        app.logger.exception("Bounding-box query failed")
        return jsonify(error="Crash data is temporarily unavailable."), 503


@app.post("/api/predict")
def predict():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify(error="Expected a JSON object."), 400

    borough = payload.get("borough")
    factor = payload.get("contributing_factor_vehicle_1")
    permitted = {"MANHATTAN", "QUEENS", "BROOKLYN", "BRONX", "STATEN ISLAND"}
    if borough not in permitted or not isinstance(factor, str) or not (1 <= len(factor.strip()) <= 128):
        return jsonify(error="Provide a borough and a contributing factor (1-128 characters)."), 400

    try:
        # The historical model trained on borough + contributing_factor only.
        # crash_date is not a learned feature in the existing model.
        from model import predict_severity
        severity = predict_severity({"borough": borough, "contributing_factor": factor.strip()})
        if severity not in {"low", "high"}:
            raise ValueError("Model unavailable")
        return jsonify(predicted_severity=severity, is_clinically_validated=False)
    except Exception:
        app.logger.exception("Research model unavailable")
        return jsonify(error="Prediction model is temporarily unavailable."), 503


if __name__ == "__main__":
    app.run(debug=False)
