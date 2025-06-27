from flask import Blueprint, jsonify
from utils.weather_api import WeatherAPI

weather_bp = Blueprint("weather", __name__, url_prefix="/api")
weather_api = WeatherAPI()

@weather_bp.route("/weather/<location>", methods=["GET"])
def get_weather(location):
    """Get weather data for a location"""
    try:
        weather_data = weather_api.get_weather_data(location)
        if weather_data:
            return jsonify(weather_data)
        return jsonify({"error": "Could not fetch weather data"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500 