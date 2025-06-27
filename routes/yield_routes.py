from flask import Blueprint, request, jsonify
from agri_wiz import AgriWiz

yield_routes_bp = Blueprint("yield_routes", __name__, url_prefix="/api")
agri_wiz = AgriWiz()

@yield_routes_bp.route("/yield/estimate", methods=["POST"])
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
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        yield_estimate = agri_wiz.yield_estimator.predict_yield(data["crop_name"], data)
        if "error" in yield_estimate:
            return jsonify({"error": yield_estimate["error"]}), 400
        return jsonify(yield_estimate)
    except Exception as e:
        return jsonify({"error": str(e)}), 500 