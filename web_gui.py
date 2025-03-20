#!/usr/bin/env python
from flask import Flask, render_template, request, jsonify, url_for
from agri_wiz import AgriWiz
from weather_api import WeatherAPI, get_humidity_level, get_rainfall_level
import os

app = Flask(__name__, static_url_path='/static', static_folder='static')
agri_wiz = AgriWiz()
weather_api = WeatherAPI()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/locations')
def get_locations():
    locations = agri_wiz.location_manager.get_all_locations()
    return jsonify(locations)

@app.route('/api/weather/<location>')
def get_weather(location):
    try:
        weather_data = weather_api.get_weather_data(location)
        season = agri_wiz.location_manager.get_current_season_for_location(location)
        if not season:
            season = agri_wiz.get_current_season()
        
        return jsonify({
            'temperature': weather_data.get('temperature', 25),
            'humidity': weather_data.get('humidity', 60),
            'rainfall': weather_data.get('rainfall', 0),
            'season': season,
            'humidity_level': get_humidity_level(weather_data.get('humidity', 60)),
            'rainfall_level': get_rainfall_level(weather_data.get('rainfall', 0))
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'temperature': 25,  # Provide default values
            'humidity': 60,
            'rainfall': 0,
            'season': 'summer',
            'humidity_level': 'medium',
            'rainfall_level': 'low'
        })

@app.route('/api/recommendations', methods=['POST'])
def get_recommendations():
    data = request.json
    try:
        if 'location' in data and data['location']:
            enhanced_recommendations, details = agri_wiz.get_recommendations_by_location(
                data['location'],
                data.get('humidity'),
                data.get('soil_fertility')
            )
            
            if enhanced_recommendations is None:
                return jsonify({'error': details}), 400
                
            # Extract just the crop info for the frontend
            recommendations = [rec["crop"] for rec in enhanced_recommendations]
            return jsonify({
                'recommendations': recommendations,
                'details': {
                    'soil_type': details['soil_type'],
                    'climate': details['climate'],
                    'season': details['season'],
                    'rainfall': details['rainfall'],
                    'humidity': details['humidity'],
                    'soil_fertility': details['soil_fertility']
                }
            })
        else:
            recommendations, scored_recommendations = agri_wiz.get_recommendations(
                data['soil_type'],
                data['climate'],
                data['season'],
                data.get('rainfall'),
                data.get('humidity'),
                data.get('soil_fertility')
            )
            return jsonify({'recommendations': recommendations})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/crops')
def get_crops():
    return jsonify(agri_wiz.crop_data)

@app.route('/api/crops', methods=['POST'])
def add_crop():
    crop_data = request.json
    try:
        agri_wiz.add_crop(crop_data)
        return jsonify({'message': 'Crop added successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/yield/estimate', methods=['POST'])
def estimate_yield():
    data = request.json
    try:
        conditions = {
            "temperature": float(data['temperature']),
            "rainfall": float(data['rainfall']),
            "humidity": float(data['humidity']),
            "soil_ph": float(data.get('soil_ph', 6.5)),
            "soil_fertility": data['soil_fertility'],
            "water_availability": data['water_availability'],
            "season": data.get('season', 'summer')
        }
        
        crop_name = data['crop_name'].lower()
        yield_estimate = agri_wiz.yield_estimator.predict_yield(crop_name, conditions)
        
        if "error" not in yield_estimate:
            # Get optimization suggestions
            optimization = agri_wiz.yield_estimator.get_optimization_suggestions(crop_name, conditions)
            yield_estimate['optimization'] = optimization
            
            # Get yield factors
            factors = agri_wiz.yield_estimator.get_yield_factors(crop_name)
            yield_estimate['factors'] = factors
            
            return jsonify(yield_estimate)
        else:
            return jsonify(yield_estimate), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/yield/models')
def get_yield_models():
    """Get list of available yield prediction models"""
    try:
        models = list(agri_wiz.yield_estimator.models.keys())
        return jsonify({'models': models})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/schemes')
def get_all_schemes():
    """Get all available schemes"""
    try:
        return jsonify(agri_wiz.scheme_manager.get_all_schemes())
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/schemes/search', methods=['POST'])
def search_schemes():
    """Search for schemes based on criteria"""
    data = request.json
    try:
        if data.get('search_type') == 'category':
            schemes = agri_wiz.scheme_manager.get_schemes_by_category(data['category'])
            return jsonify({'schemes': schemes})
        else:
            crop = data.get('crop', '')
            state = data.get('state', '')
            land_area = float(data['land_area']) if data.get('land_area') else None
            
            scheme_info = agri_wiz.get_schemes_for_crop(crop, state, land_area)
            return jsonify(scheme_info)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/schemes/categories')
def get_scheme_categories():
    """Get list of available scheme categories"""
    try:
        categories = agri_wiz.scheme_manager.get_categories()
        return jsonify({'categories': categories})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    app.run(debug=True, port=5000)