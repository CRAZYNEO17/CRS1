# routes/schemes.py
from flask import Blueprint, request, jsonify # type: ignore
import logging

# Import from the project root
from agri_wiz import AgriWiz
from utils.location_data import LiveLocationManager as LocationManager

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create instances
agri_wiz = AgriWiz()

schemes_bp = Blueprint("schemes", __name__, url_prefix="/api")

@schemes_bp.route("/schemes", methods=["GET"])
def get_schemes():
  """Get government schemes based on parameters"""
  try:
    crop_name = request.args.get("crop")
    state = request.args.get("state")
    land_area = request.args.get("land_area")
    category = request.args.get("category")
    location = request.args.get("location")

    # Log the value of 'location' for debugging
    logger.debug(f"Received request parameters: crop={crop_name}, state={state}, location={location}, category={category}")

    # Handle category-based scheme requests
    if category:
      logger.debug(f"Fetching schemes for category: {category}")
      schemes = agri_wiz.scheme_manager.get_schemes_by_category(category)
      return jsonify({"schemes": schemes})

    # Handle location-based scheme requests
    if location:
      logger.debug(f"Fetching location info and schemes for: {location}")
      import os
      location_manager = LocationManager(openweather_api_key=os.getenv('OPENWEATHER_API_KEY'))
      location_info = location_manager.get_location_info(location)
      if not location_info:
        logger.warning(f"Location not found: {location}")
        return jsonify({"error": f"Location '{location}' not found"}), 404
        
      # The location is used as the state for scheme lookup
      detected_state = location
      
      # Get recommendations, crop calendar, and schemes
      recommendations, details = agri_wiz.get_recommendations_by_location(location)
      crop_calendar = agri_wiz.get_crop_calendar(location)
      
      # Use the newly implemented get_schemes_for_state method
      try:
        state_schemes = agri_wiz.scheme_manager.get_schemes_for_state(detected_state)
        logger.debug(f"Found {len(state_schemes)} schemes for state: {detected_state}")
      except Exception as scheme_error:
        logger.error(f"Error fetching schemes for state: {scheme_error}")
        state_schemes = []

      # Build comprehensive response with all relevant data
      response = {
        "state_info": {
          "name": detected_state,
          "climate": location_info.get("climate", ""),
          "common_soil_types": location_info.get("common_soil_types", []),
          "annual_rainfall": location_info.get("rainfall", ""),
          "major_seasons": list(location_info.get("seasons", {}).keys())
        },
        "soil_parameters": {
          "types": location_info.get("common_soil_types", []),
          "fertility": location_info.get("soil_fertility", ""),
          "ph_range": "6.0-7.5", # Default range, could be location-specific in future
          "characteristics": {
            "texture": "Medium to Fine",
            "drainage": "Good",
            "water_holding": "Medium to High"
          }
        },
        "recommended_crops": recommendations if recommendations else [],
        "crop_calendar": crop_calendar,
        "schemes": state_schemes,
        "location_details": details
      }
      return jsonify(response)

    # Handle crop and state based scheme requests
    if not all([crop_name, state]):
      logger.warning("Missing required parameters for scheme lookup")
      return jsonify({"error": "Either 'location' or both 'crop' and 'state' are required"}), 400

    logger.debug(f"Fetching schemes for crop: {crop_name} in state: {state}")
    if land_area is None:
      logger.warning("Missing required parameter: land_area")
      return jsonify({"error": "'land_area' is required for crop and state based scheme lookup"}), 400
    try:
      land_area_float = float(land_area)
    except ValueError:
      logger.warning("Invalid value for land_area; must be a number")
      return jsonify({"error": "'land_area' must be a valid number"}), 400
    scheme_info = agri_wiz.get_schemes_for_crop(
      crop_name, state, land_area_float
    )
    return jsonify(scheme_info)

  except Exception as e:
    logger.error(f"Error in get_schemes endpoint: {str(e)}")
    return jsonify({"error": str(e)}), 500

@schemes_bp.route("/schemes/all", methods=["GET"])
def get_all_schemes():
  """Get all available government schemes"""
  try:
    all_schemes = agri_wiz.scheme_manager.get_all_schemes()
    return jsonify({"schemes": all_schemes})
  except Exception as e:
    logger.error(f"Error in get_all_schemes endpoint: {str(e)}")
    return jsonify({"error": str(e)}), 500

@schemes_bp.route("/schemes/categories", methods=["GET"])
def get_scheme_categories():
  """Get all scheme categories"""
  try:
    categories = agri_wiz.scheme_manager.get_categories()
    return jsonify({"categories": categories})
  except Exception as e:
    logger.error(f"Error in get_scheme_categories endpoint: {str(e)}")
    return jsonify({"error": str(e)}), 500
