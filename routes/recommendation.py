from flask import Blueprint, request, jsonify
from agri_wiz import AgriWiz
from utils.location_data import LiveLocationManager as LocationManager
from utils.weather_api import WeatherService, WeatherAPI
from utils.yield_estimation import YieldEstimator
import logging
from datetime import datetime
import os
from concurrent.futures import ThreadPoolExecutor

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create instances
agri_wiz = AgriWiz()
location_manager = LocationManager(openweather_api_key=os.getenv('OPENWEATHER_API_KEY'))
try:
    weather_service = WeatherService()
except Exception as e:
    logger.warning(f"WeatherService initialization failed: {e}")
    weather_service = None
weather_api = WeatherAPI()
yield_estimator = YieldEstimator()

# Create the recommendation blueprint
recommendation_bp = Blueprint("recommendation", __name__, url_prefix="/api")

@recommendation_bp.route("/recommendations", methods=["GET"])
def get_recommendations():
    """Get crop recommendations based on location (required parameter)"""
    try:
        # Location parameter is now required
        location = request.args.get("location")
        
        if not location:
            return jsonify({"error": "Location parameter is required"}), 400
        
        # Location-based recommendations using real-time data
        logger.debug(f"Getting location-based recommendations for: {location}")
        
        # Get weather forecast for real-time data
        weather_forecast = None
        if weather_service:
            weather_forecast = weather_service.get_weather_forecast(location)
        
        # Determine current season based on location and date
        current_month = datetime.now().strftime("%B").lower()
        current_season = None
        
        # Use location-specific season mapping if available
        if "seasons" in location_info and location_info["seasons"]:
            for season, months in location_info["seasons"].items():
                if current_month in [month.lower() for month in months]:
                    current_season = season
                    break
        
        # Fallback to general Indian agricultural seasons
        if not current_season:
            month_num = datetime.now().month
            if month_num in [12, 1, 2]:  # Dec, Jan, Feb
                current_season = "rabi"  # Winter crops
            elif month_num in [6, 7, 8, 9]:  # Jun, Jul, Aug, Sep
                current_season = "kharif"  # Monsoon crops
            else:
                current_season = "summer"  # Summer crops
        
        # Extract location-based environmental data
        soil_type = 'N/A'
        climate = 'N/A'
        humidity = 'N/A'
        rainfall = 'N/A'
        soil_fertility = 'N/A'
        soil_ph = 'N/A'
        water_availability = 'N/A'
        temperature = 'N/A'
        
        # Use real-time weather data when available
        if weather_forecast and "averages" in weather_forecast:
            avg_temp = weather_forecast["averages"].get("temperature")
            avg_humid = weather_forecast["averages"].get("humidity")
            avg_rain = weather_forecast["averages"].get("rainfall")
            
            if avg_temp is not None:
                temperature = avg_temp
            if avg_humid is not None:
                humidity = "high" if avg_humid > 70 else "medium" if avg_humid > 40 else "low"
            if avg_rain is not None:
                rainfall = "high" if avg_rain > 100 else "medium" if avg_rain > 25 else "low"
        
        # Use location data as fallback for weather parameters
        if humidity is None:
            humidity = location_info.get("humidity", "medium")
        if rainfall is None:
            rainfall = location_info.get("rainfall", "medium")
        
        # Get soil fertility from location data
        soil_fertility = location_info.get("soil_fertility", "medium")
        
        # Additional real-time parameters
        soil_ph = location_info.get("soil_ph", "6.5-7.5")
        water_availability = location_info.get("water_availability", "medium")
        
        logger.info(f"Using real-time parameters for {location}: "
                   f"soil_type={soil_type}, climate={climate}, season={current_season}, "
                   f"humidity={humidity}, rainfall={rainfall}, soil_fertility={soil_fertility}, "
                   f"temperature={temperature}°C")
        
        # Get enhanced recommendations using location-based method
        recommendations, location_details = agri_wiz.get_recommendations_by_location(
            location, humidity, soil_fertility, temperature=temperature
        )
        
        if recommendations is None:
            return jsonify({"error": f"Unable to generate recommendations for {location}. {location_details}"}), 404
        
        # Enhanced response with real-time data integration
        response_data = {
            "recommendations": recommendations,
            "location_details": {
                "location_name": location,
                "soil_type": soil_type,
                "climate": climate,
                "season": current_season,
                "rainfall": rainfall,
                "humidity": humidity,
                "soil_fertility": soil_fertility,
                "soil_ph": soil_ph,
                "water_availability": water_availability,
                "temperature": temperature,
                "data_sources": {
                    "weather_api": bool(weather_forecast),
                    "location_database": True,
                    "real_time_season": True
                },
                "last_updated": datetime.now().isoformat()
            },
            "metadata": {
                "total_recommendations": len(recommendations),
                "analysis_type": "location_based_real_time",
                "confidence_level": "high" if weather_forecast else "medium"
            }
        }
        
        return jsonify(response_data)
            
    except Exception as e:
        logger.error(f"Error in recommendations endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

@recommendation_bp.route("/recommendation/crop/<crop_name>", methods=["GET"])
def get_crop_details(crop_name):
    """Get detailed information about a specific crop"""
    try:
        crop_details = agri_wiz.get_crop_details(crop_name)
        
        if crop_details is None:
            return jsonify({"error": f"Crop '{crop_name}' not found"}), 404
        
        return jsonify({
            "crop_details": crop_details
        })
    except Exception as e:
        logger.error(f"Error getting crop details: {str(e)}")
        return jsonify({"error": str(e)}), 500

@recommendation_bp.route("/recommendation/calendar/<location>", methods=["GET"])
def get_crop_calendar(location):
    """Get crop calendar for a specific location"""
    try:
        calendar = agri_wiz.get_crop_calendar(location)
        
        if calendar is None:
            return jsonify({"error": f"Location '{location}' not found"}), 404
        
        return jsonify({
            "location": location,
            "crop_calendar": calendar
        })
    except Exception as e:
        logger.error(f"Error getting crop calendar: {str(e)}")
        return jsonify({"error": str(e)}), 500

@recommendation_bp.route("/recommendation/season", methods=["GET"])
def get_current_season():
    """Get current season information"""
    try:
        current_season = agri_wiz.get_current_season()
        
        return jsonify({
            "current_season": current_season,
            "season_info": {
                "winter": "December - February",
                "spring": "March - May", 
                "summer": "June - August",
                "rainy": "September - November"
            }
        })
    except Exception as e:
        logger.error(f"Error getting current season: {str(e)}")
        return jsonify({"error": str(e)}), 500

@recommendation_bp.route("/recommendations/live", methods=["GET"])
def get_live_recommendations():
    """Get crop recommendations based on real-time weather and soil data for a location."""
    location = request.args.get("location")
    lat = request.args.get("lat")
    lon = request.args.get("lon")

    if not (lat and lon):
        return jsonify({"error": "Coordinates required."}), 400
    lat = float(lat)
    lon = float(lon)

    # Fetch live weather and soil data concurrently
    with ThreadPoolExecutor() as executor:
        weather_future = executor.submit(location_manager.get_live_weather, lat, lon)
        soil_future = executor.submit(location_manager.get_live_soil_data, lat, lon)
        weather = weather_future.result()
        soil = soil_future.result()
    print("weather", weather)
    print("soil", soil)
    if not weather:
        return jsonify({"error": "Could not fetch live weather data.", "weather": weather}), 500
    if not soil:
        return jsonify({"error": "Could not fetch live soil data.", "soil": soil}), 500

    # 2. Extract values from weather and soil structures
    temperature = weather.get("main", {}).get("temp", 25)
    humidity = weather.get("main", {}).get("humidity", 60)
    rainfall = weather.get("rain", {}).get("1h", 0)
    # Extract soil pH from solid grid query result structure
    ph_layer = next((layer for layer in soil.get("properties", {}).get("layers", []) if layer["name"] == "phh2o"), None)
    soil_ph = None
    if ph_layer:
        # Use mean or Q0.5 if available, else fallback
        soil_ph = ph_layer["depths"][0]["values"].get("mean")
        if soil_ph is None:
            soil_ph = ph_layer["depths"][0]["values"].get("Q0.5", 6.5)
    if soil_ph is None:
        soil_ph = 6.5

    # 3. For each crop, check suitability and predict yield
    recommendations = []
    for crop in agri_wiz.crop_data:
        crop_name = crop.get("crop_name")
        if not crop_name or not isinstance(crop_name, str):
            continue  # Skip crops without a valid name
        ai_confidence = 80  # Placeholder, can be improved
        risk = "Low Risk"
        profit = "High Profit"
        recommendation_label = "Recommended"
        # Predict yield
        conditions = {
            "temperature": temperature,
            "rainfall": rainfall,
            "humidity": humidity,
            "soil_ph": soil_ph,
            "soil_fertility": "high",  # Placeholder, can be improved
            "water_availability": "high",  # Placeholder
            "season": "summer"  # Placeholder, can use month
        }
        yield_info = yield_estimator.predict_yield(crop_name, conditions)
        estimated_yield = yield_info.get("estimated_yield", None)
        # Revenue (mock calculation)
        price_per_unit = crop.get("market_price", 2000)
        revenue = None
        if estimated_yield:
            revenue = estimated_yield * price_per_unit
        # Risk and profit (mock logic)
        if ai_confidence > 90:
            recommendation_label = "Highly Recommended"
        elif ai_confidence > 80:
            recommendation_label = "Recommended"
        else:
            recommendation_label = "Consider"
        if estimated_yield and estimated_yield < 10:
            risk = "Medium Risk"
            profit = "Medium Profit"
        if estimated_yield and estimated_yield < 5:
            risk = "High Risk"
            profit = "Low Profit"
        # Build response
        recommendations.append({
            "crop_name": crop_name,
            "ai_confidence": f"{ai_confidence}%",
            "yield": f"{estimated_yield} tons/hectare" if estimated_yield else "N/A",
            "revenue": f"₹{int(revenue):,}" if revenue else "N/A",
            "duration": crop.get("duration", "N/A"),
            "price_per_unit": f"₹{price_per_unit}/quintal",
            "profit": profit,
            "risk": risk,
            "recommendation_label": recommendation_label
        })
    # Sort by estimated yield descending
    recommendations = sorted(recommendations, key=lambda x: float(x["yield"].split()[0]) if x["yield"] != "N/A" else 0, reverse=True)
    return jsonify({"recommendations": recommendations, "weather": weather, "soil": soil, "location": location or f"{lat},{lon}"})
