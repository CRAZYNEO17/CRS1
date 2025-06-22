# routes/state_crops.py
from flask import Blueprint, request, jsonify # type: ignore

# Import from the project root
from agri_wiz import AgriWiz
from location_data import LocationManager

# Create instance
agri_wiz = AgriWiz()

state_crops_bp = Blueprint("state_crops", __name__, url_prefix="/api")

@state_crops_bp.route("/api/state-crops/<location>", methods=["GET"])
def get_state_crops(location):
    """Get crop and soil data specific to a state/location"""
    try:
        # Initialize location manager to get state info
        location_manager = LocationManager()
        location_info = location_manager.get_location_info(location)

        if not location_info:
            return jsonify({"error": "Location not found"}), 404

        # Get recommended crops for this location
        recommendations, details = agri_wiz.get_recommendations_by_location(location)
        
        # Get state-specific crop calendar
        crop_calendar = agri_wiz.get_crop_calendar(location)

        response = {
            "state_info": {
                "name": location,
                "climate": location_info.get("climate", ""),
                "common_soil_types": location_info.get("common_soil_types", []),
                "annual_rainfall": location_info.get("rainfall", ""),
                "major_seasons": list(location_info.get("seasons", {}).keys())
            },
            "soil_parameters": {
                "types": location_info.get("common_soil_types", []),
                "fertility": location_info.get("soil_fertility", ""),
                "ph_range": "6.0-7.5",  # Default range, update based on actual data
                "characteristics": {
                    "texture": "Medium to Fine",
                    "drainage": "Good",
                    "water_holding": "Medium to High"
                }
            },
            "recommended_crops": recommendations if recommendations else [],
            "crop_calendar": crop_calendar,
            "location_details": details
        }

        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
