from flask import Blueprint, request, jsonify
from agri_wiz import AgriWiz

crops_bp = Blueprint("crops", __name__, url_prefix="/api")
agri_wiz = AgriWiz()

@crops_bp.route("/crops", methods=["GET"])
def get_crops():
    """Get all available crops"""
    return jsonify(agri_wiz.crop_data)

@crops_bp.route("/crops", methods=["POST"])
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
        for field in required_fields:
            if field not in crop_data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        agri_wiz.add_crop(crop_data)
        return jsonify({"message": "Crop added successfully", "crop": crop_data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500 