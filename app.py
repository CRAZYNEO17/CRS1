#!/usr/bin/env python
# REST API Server for Agri Wiz
from flask import Flask, request, jsonify
from agri_wiz import AgriWiz
from weather_api import WeatherAPI
import logging
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

app = Flask(__name__)
agri_wiz = AgriWiz()
weather_api = WeatherAPI()


@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "version": "1.0.0"})


@app.route("/api/crops", methods=["GET"])
def get_crops():
    """Get all available crops"""
    return jsonify(agri_wiz.crop_data)


@app.route("/api/crops", methods=["POST"])
def add_crop():
    """Add a new crop"""
    try:
        crop_data = request.json
        required_fields = [
            "crop_name",
            "soil_types",
            "climates",
            "seasons",
            "water_needs",
            "humidity_preference",
            "soil_fertility",
        ]

        # Validate required fields
        for field in required_fields:
            if field not in crop_data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        agri_wiz.add_crop(crop_data)
        return jsonify({"message": "Crop added successfully", "crop": crop_data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/recommendations", methods=["GET"])
def get_recommendations():
    """Get crop recommendations based on parameters"""
    try:
        soil_type = request.args.get("soil_type")
        climate = request.args.get("climate")
        season = request.args.get("season")
        rainfall = request.args.get("rainfall")
        humidity = request.args.get("humidity")
        soil_fertility = request.args.get("soil_fertility")

        if not all([soil_type, climate, season]):
            return jsonify(
                {"error": "soil_type, climate, and season are required"}
            ), 400

        recommendations, scored_recommendations = agri_wiz.get_recommendations(
            soil_type, climate, season, rainfall, humidity, soil_fertility
        )

        return jsonify(
            {
                "recommendations": recommendations,
                "scored_recommendations": scored_recommendations,
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/recommendations/location/<location>", methods=["GET"])
def get_recommendations_by_location(location):
    """Get crop recommendations based on location"""
    try:
        humidity = request.args.get("humidity")
        soil_fertility = request.args.get("soil_fertility")

        recommendations, details = agri_wiz.get_recommendations_by_location(
            location, humidity, soil_fertility
        )

        if recommendations is None:
            return jsonify({"error": details}), 404

        return jsonify(
            {"recommendations": recommendations, "location_details": details}
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/weather/<location>", methods=["GET"])
def get_weather(location):
    """Get weather data for a location"""
    try:
        weather_data = weather_api.get_weather_data(location)
        if weather_data:
            return jsonify(weather_data)
        return jsonify({"error": "Could not fetch weather data"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/yield/estimate", methods=["POST"])
def estimate_yield():
    """Estimate crop yield based on parameters"""
    try:
        data = request.json
        required_fields = [
            "crop_name",
            "temperature",
            "rainfall",
            "humidity",
            "soil_ph",
            "soil_fertility",
            "water_availability",
            "season",
        ]

        # Validate required fields
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        yield_estimate = agri_wiz.yield_estimator.predict_yield(data["crop_name"], data)

        if "error" in yield_estimate:
            return jsonify({"error": yield_estimate["error"]}), 400

        return jsonify(yield_estimate)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/schemes", methods=["GET"])
def get_schemes():
    """Get government schemes based on parameters"""
    try:
        crop_name = request.args.get("crop")
        state = request.args.get("state")
        land_area = request.args.get("land_area")
        category = request.args.get("category")

        if category:
            schemes = agri_wiz.scheme_manager.get_schemes_by_category(category)
            return jsonify({"schemes": schemes})

        if not all([crop_name, state]):
            return jsonify({"error": "crop and state are required"}), 400

        scheme_info = agri_wiz.get_schemes_for_crop(
            crop_name, state, float(land_area) if land_area else None
        )

        return jsonify(scheme_info)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
