#!/usr/bin/env python
# Agri Wiz - Enhanced Crop Recommendation System
# Incorporating data from ICAR, Agricultural Universities, and IMD

import os
import json
import csv
from datetime import datetime
from location_data import LocationManager
from scheme_manager import SchemeManager
from weather_api import WeatherService
from yield_estimation import YieldEstimator

class AgriWiz:
    def __init__(self):
        self.crop_data = []
        self.location_manager = LocationManager()
        self.scheme_manager = SchemeManager()
        self.weather_service = WeatherService()
        self.yield_estimator = YieldEstimator()
        self.load_crop_data()
        
    def load_crop_data(self):
        """Load enhanced crop data from the CSV file."""
        try:
            if os.path.exists("data/raw/crop_data.csv"):
                with open("data/raw/crop_data.csv", "r") as file:
                    reader = csv.DictReader(file)
                    self.crop_data = list(reader)
                print(f"Loaded {len(self.crop_data)} crops from database with enhanced parameters.")
            else:
                print("Crop database not found.")
        except Exception as e:
            print(f"Error loading crop data: {e}")

    def create_sample_data(self):
        """Create sample crop data if no data file exists."""
        self.crop_data = [
            {"crop_name": "Rice", "soil_types": "clay,loamy,alluvial", "climates": "tropical,subtropical", "seasons": "summer,rainy", "water_needs": "high", "humidity_preference": "high", "soil_fertility": "medium,high"},
            {"crop_name": "Wheat", "soil_types": "loamy,sandy loam,alluvial", "climates": "temperate,subtropical", "seasons": "winter,spring", "water_needs": "medium", "humidity_preference": "low,medium", "soil_fertility": "medium,high"},
            {"crop_name": "Corn", "soil_types": "loamy,sandy,alluvial", "climates": "temperate,subtropical", "seasons": "summer", "water_needs": "medium", "humidity_preference": "medium", "soil_fertility": "medium,high"},
            {"crop_name": "Cotton", "soil_types": "loamy,black soil", "climates": "subtropical,tropical", "seasons": "summer,rainy", "water_needs": "medium", "humidity_preference": "medium", "soil_fertility": "high"},
            {"crop_name": "Sugarcane", "soil_types": "loamy,clay,black soil", "climates": "tropical,subtropical", "seasons": "spring", "water_needs": "high", "humidity_preference": "high", "soil_fertility": "high"},
            {"crop_name": "Potato", "soil_types": "loamy,sandy loam", "climates": "temperate", "seasons": "winter,spring", "water_needs": "medium", "humidity_preference": "medium", "soil_fertility": "medium,high"},
            {"crop_name": "Tomato", "soil_types": "loamy,sandy loam", "climates": "temperate,subtropical", "seasons": "summer,spring", "water_needs": "medium", "humidity_preference": "medium", "soil_fertility": "medium,high"},
            {"crop_name": "Soybean", "soil_types": "loamy,clay loam", "climates": "temperate,subtropical", "seasons": "summer", "water_needs": "medium", "humidity_preference": "medium", "soil_fertility": "medium"},
            {"crop_name": "Barley", "soil_types": "loamy,clay loam", "climates": "temperate", "seasons": "winter,spring", "water_needs": "low", "humidity_preference": "low", "soil_fertility": "low,medium"},
            {"crop_name": "Oats", "soil_types": "loamy,sandy loam", "climates": "temperate", "seasons": "spring,fall", "water_needs": "medium", "humidity_preference": "medium", "soil_fertility": "medium"},
            {"crop_name": "Chickpea", "soil_types": "sandy loam,loamy", "climates": "subtropical", "seasons": "winter", "water_needs": "low", "humidity_preference": "low", "soil_fertility": "low,medium"},
            {"crop_name": "Mustard", "soil_types": "loamy,clay", "climates": "subtropical", "seasons": "winter", "water_needs": "low", "humidity_preference": "low", "soil_fertility": "medium"},
            {"crop_name": "Groundnut", "soil_types": "sandy,loamy,red", "climates": "tropical,subtropical", "seasons": "rainy", "water_needs": "medium", "humidity_preference": "medium", "soil_fertility": "medium"},
            {"crop_name": "Sunflower", "soil_types": "loamy,sandy loam", "climates": "temperate,subtropical", "seasons": "spring,summer", "water_needs": "medium", "humidity_preference": "low,medium", "soil_fertility": "medium"},
            {"crop_name": "Mango", "soil_types": "loamy,alluvial,laterite", "climates": "tropical", "seasons": "summer", "water_needs": "medium", "humidity_preference": "medium,high", "soil_fertility": "medium"},
            {"crop_name": "Banana", "soil_types": "loamy,alluvial", "climates": "tropical", "seasons": "rainy", "water_needs": "high", "humidity_preference": "high", "soil_fertility": "high"},
            # Adding new crops with humidity and soil fertility parameters
            {"crop_name": "Coffee", "soil_types": "loamy,volcanic", "climates": "tropical,subtropical", "seasons": "rainy", "water_needs": "medium", "humidity_preference": "high", "soil_fertility": "medium,high"},
            {"crop_name": "Tea", "soil_types": "loamy,acidic", "climates": "tropical,subtropical", "seasons": "rainy", "water_needs": "high", "humidity_preference": "high", "soil_fertility": "medium"},
            {"crop_name": "Cashew", "soil_types": "sandy,red,laterite", "climates": "tropical", "seasons": "summer", "water_needs": "low", "humidity_preference": "medium", "soil_fertility": "low,medium"},
            {"crop_name": "Coconut", "soil_types": "sandy,loamy,laterite", "climates": "tropical", "seasons": "rainy", "water_needs": "medium", "humidity_preference": "high", "soil_fertility": "medium"},
            {"crop_name": "Orange", "soil_types": "loamy,sandy loam", "climates": "subtropical", "seasons": "winter", "water_needs": "medium", "humidity_preference": "medium", "soil_fertility": "medium,high"},
            {"crop_name": "Apple", "soil_types": "loamy,sandy loam", "climates": "temperate", "seasons": "spring", "water_needs": "medium", "humidity_preference": "low,medium", "soil_fertility": "medium,high"},
            {"crop_name": "Grape", "soil_types": "sandy,loamy", "climates": "mediterranean,temperate", "seasons": "spring,summer", "water_needs": "low,medium", "humidity_preference": "low", "soil_fertility": "medium"},
            {"crop_name": "Onion", "soil_types": "loamy,sandy loam", "climates": "temperate,subtropical", "seasons": "winter", "water_needs": "medium", "humidity_preference": "low,medium", "soil_fertility": "medium"},
            {"crop_name": "Garlic", "soil_types": "loamy,sandy loam", "climates": "temperate", "seasons": "winter", "water_needs": "medium", "humidity_preference": "low", "soil_fertility": "medium"},
            {"crop_name": "Turmeric", "soil_types": "loamy,sandy loam", "climates": "tropical", "seasons": "rainy", "water_needs": "high", "humidity_preference": "high", "soil_fertility": "high"},
            {"crop_name": "Ginger", "soil_types": "loamy,sandy loam", "climates": "tropical", "seasons": "rainy", "water_needs": "high", "humidity_preference": "high", "soil_fertility": "high"},
            {"crop_name": "Chili Pepper", "soil_types": "loamy,sandy loam", "climates": "tropical,subtropical", "seasons": "summer", "water_needs": "medium", "humidity_preference": "medium,high", "soil_fertility": "medium,high"},
            {"crop_name": "Cardamom", "soil_types": "loamy,forest", "climates": "tropical", "seasons": "rainy", "water_needs": "high", "humidity_preference": "high", "soil_fertility": "high"},
            {"crop_name": "Black Pepper", "soil_types": "loamy,forest", "climates": "tropical", "seasons": "rainy", "water_needs": "high", "humidity_preference": "high", "soil_fertility": "medium,high"}
        ]
        self.save_crop_data()
    
    def save_crop_data(self):
        """Save crop data to CSV file."""
        try:
            os.makedirs("data/raw", exist_ok=True)
            with open("data/raw/crop_data.csv", "w", newline="") as file:
                fieldnames = ["crop_name", "soil_types", "climates", "seasons", "water_needs", 
                             "humidity_preference", "soil_fertility"]
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.crop_data)
            print("Crop data saved successfully.")
        except Exception as e:
            print(f"Error saving crop data: {e}")
    
    def add_crop(self, crop_data):
        """Add a new crop to the database."""
        self.crop_data.append(crop_data)
        self.save_crop_data()
        print(f"Added {crop_data['crop_name']} to the database.")
    
    def get_recommendations(self, soil_type, climate, season, rainfall=None, humidity=None, soil_fertility=None, 
                          soil_ph=None, temperature=None, water_availability=None):
        """Enhanced get recommendations with additional parameters."""
        recommendations = []
        scored_recommendations = []
        
        for crop in self.crop_data:
            score = 0
            max_score = 0
            
            # Core parameters (required matches) - 3 points each
            if any(s.strip().lower() == soil_type.lower() for s in crop["soil_types"].split(",")):
                score += 3
            max_score += 3
            
            if any(c.strip().lower() == climate.lower() for c in crop["climates"].split(",")):
                score += 3
            max_score += 3
            
            if any(s.strip().lower() == season.lower() for s in crop["seasons"].split(",")):
                score += 3
            max_score += 3
            
            # Optional parameters - 2 points each
            if humidity and "humidity_preference" in crop:
                max_score += 2
                if any(h.strip().lower() == humidity.lower() for h in crop["humidity_preference"].split(",")):
                    score += 2
            
            if soil_fertility and "soil_fertility" in crop:
                max_score += 2
                if any(f.strip().lower() == soil_fertility.lower() for f in crop["soil_fertility"].split(",")):
                    score += 2
            
            # Advanced parameters - 1 point each
            if soil_ph and "ph_range" in crop:
                max_score += 1
                try:
                    ph_min, ph_max = map(float, crop["ph_range"].split("-"))
                    if ph_min <= float(soil_ph) <= ph_max:
                        score += 1
                except (ValueError, AttributeError):
                    pass
            
            if temperature and "temperature_range" in crop:
                max_score += 1
                try:
                    temp_min, temp_max = map(float, crop["temperature_range"].split("-"))
                    if temp_min <= float(temperature) <= temp_max:
                        score += 1
                except (ValueError, AttributeError):
                    pass
            
            # Calculate match percentage
            match_percentage = (score / max_score * 100) if max_score > 0 else 0
            
            if match_percentage >= 60:  # Include crops with at least 60% match
                crop_info = {
                    "crop": crop,
                    "match_percentage": match_percentage,
                    "score_details": {
                        "total_score": score,
                        "max_possible": max_score
                    }
                }
                scored_recommendations.append(crop_info)
        
        # Sort by match percentage and extract crop data
        scored_recommendations.sort(key=lambda x: x["match_percentage"], reverse=True)
        recommendations = [item["crop"] for item in scored_recommendations]
        
        return recommendations, scored_recommendations
    
    def get_recommendations_by_location(self, location_name, humidity=None, soil_fertility=None, 
                                      soil_ph=None, temperature=None):
        """Enhanced location-based recommendations with weather and yield estimates."""
        location_info = self.location_manager.get_location_info(location_name)
        
        if not location_info:
            return None, "Location information not found."
        
        # Get weather forecast
        weather_forecast = self.weather_service.get_weather_forecast(location_name)
        
        # Get current season for location
        current_month = datetime.now().strftime("%B").lower()
        current_season = None
        
        for season, months in location_info["seasons"].items():
            if current_month in months:
                current_season = season
                break
        
        if not current_season:
            current_season = "summer"  # Default to summer if season not found
        
        # Get recommendations based on location data
        soil_type = location_info["common_soil_types"][0] if location_info["common_soil_types"] else "loamy"
        climate = location_info["climate"]
        rainfall = location_info["rainfall"]
        
        # Use weather data if available
        if weather_forecast:
            avg_temp = weather_forecast["averages"]["temperature"]
            avg_humid = weather_forecast["averages"]["humidity"]
            avg_rain = weather_forecast["averages"]["rainfall"]
            
            if temperature is None and avg_temp is not None:
                temperature = avg_temp
            if humidity is None and avg_humid is not None:
                humidity = "high" if avg_humid > 70 else "medium" if avg_humid > 40 else "low"
            if rainfall is None and avg_rain is not None:
                rainfall = "high" if avg_rain > 2 else "medium" if avg_rain > 0.5 else "low"
        
        # Use location data if parameter not provided
        location_humidity = location_info.get("humidity", None)
        if humidity is None and location_humidity:
            humidity = location_humidity
            
        recommendations = []
        scored_recommendations = []
        
        for crop in self.crop_data:
            score = 0
            max_score = 0
            
            # Check soil type compatibility
            crop_soils = [s.strip() for s in crop["soil_types"].split(",")]
            if any(soil in crop_soils for soil in location_info["common_soil_types"]):
                score += 2
            max_score += 2
            
            # Check climate compatibility
            crop_climates = [c.strip() for c in crop["climates"].split(",")]
            if climate in crop_climates:
                score += 3
            elif any(c in ["subtropical", "temperate"] for c in crop_climates):
                score += 1
            max_score += 3
            
            # Check season suitability
            crop_seasons = [s.strip() for s in crop["seasons"].split(",")]
            if current_season in crop_seasons:
                score += 2
            max_score += 2
            
            # Check humidity preference if available
            if humidity and "humidity_preference" in crop:
                crop_humidity = [h.strip() for h in crop["humidity_preference"].split(",")]
                if humidity in crop_humidity:
                    score += 1
                max_score += 1
            
            # Check soil fertility if available
            if soil_fertility and "soil_fertility" in crop:
                crop_fertility = [f.strip() for f in crop["soil_fertility"].split(",")]
                if soil_fertility in crop_fertility:
                    score += 1
                max_score += 1
            
            # Calculate match percentage
            match_percentage = (score / max_score * 100) if max_score > 0 else 0
            
            if match_percentage >= 40:  # Only include crops with at least 40% match
                scored_recommendations.append({
                    "crop": crop,
                    "match_percentage": match_percentage
                })
        
        # Sort by match percentage and extract crop data
        scored_recommendations.sort(key=lambda x: x["match_percentage"], reverse=True)
        recommendations = [item["crop"] for item in scored_recommendations]
        
        # Prepare location details for display
        details = {
            "soil_type": ", ".join(location_info["common_soil_types"]),
            "climate": climate,
            "season": current_season,
            "rainfall": rainfall,
            "humidity": humidity,
            "soil_fertility": soil_fertility
        }
        
        return recommendations, details

    def get_schemes_for_crop(self, crop_name: str, state: str, land_area: float = 0.0) -> dict:
        """Get government schemes and subsidies relevant to a specific crop."""
        schemes = self.scheme_manager.get_relevant_schemes(crop_name, state, land_area)
        subsidies = {}
        
        # Get relevant subsidies
        if crop_name.lower() in ["rice", "wheat", "maize", "barley"]:
            subsidies["seeds"] = self.scheme_manager.get_subsidy_info("seeds", "cereals")
        elif crop_name.lower() in ["chickpea", "pigeon pea", "green gram", "black gram"]:
            subsidies["seeds"] = self.scheme_manager.get_subsidy_info("seeds", "pulses")
        elif crop_name.lower() in ["groundnut", "soybean", "sunflower", "mustard"]:
            subsidies["seeds"] = self.scheme_manager.get_subsidy_info("seeds", "oilseeds")
        
        # Add machinery and irrigation subsidies if applicable
        subsidies["machinery"] = self.scheme_manager.get_subsidy_info("farm_machinery")
        subsidies["irrigation"] = self.scheme_manager.get_subsidy_info("irrigation")
        
        return {
            "schemes": schemes,
            "subsidies": subsidies
        }

    def get_crop_details(self, crop_name):
        """Get detailed information about a specific crop."""
        for crop in self.crop_data:
            if crop["crop_name"].lower() == crop_name.lower():
                return {
                    "name": crop["crop_name"],
                    "growing_period": crop.get("growing_period_days", "N/A"),
                    "yield_potential": crop.get("yield_potential_qt_per_ha", "N/A"),
                    "major_nutrients": crop.get("major_nutrients_required", "N/A"),
                    "pest_resistance": crop.get("pest_resistance", "N/A"),
                    "disease_resistance": crop.get("disease_resistance", "N/A"),
                    "market_demand": crop.get("market_demand", "N/A"),
                    "soil_types": crop["soil_types"],
                    "climates": crop["climates"],
                    "seasons": crop["seasons"],
                    "water_needs": crop["water_needs"],
                    "humidity_preference": crop.get("humidity_preference", "N/A"),
                    "soil_fertility": crop.get("soil_fertility", "N/A"),
                    "ph_range": crop.get("ph_range", "N/A"),
                    "temperature_range": crop.get("temperature_range", "N/A"),
                    "rainfall_range": crop.get("rainfall_range_mm", "N/A")
                }
        return None

    def get_crop_calendar(self, location_name):
        """Get crop calendar based on location's seasons."""
        location_info = self.location_manager.get_location_info(location_name)
        if not location_info:
            return None
            
        calendar = {}
        for season, months in location_info["seasons"].items():
            suitable_crops = []
            for crop in self.crop_data:
                if season in crop["seasons"].split(","):
                    suitable_crops.append({
                        "name": crop["crop_name"],
                        "growing_period": crop.get("growing_period_days", "N/A"),
                        "water_needs": crop["water_needs"]
                    })
            calendar[season] = {
                "months": months,
                "suitable_crops": suitable_crops
            }
        return calendar

    def get_current_season(self):
        """Determine current season based on month."""
        month = datetime.now().month
        if month in [12, 1, 2]:
            return "winter"
        elif month in [3, 4, 5]:
            return "spring"
        elif month in [6, 7, 8]:
            return "summer"
        else:  # months 9, 10, 11
            return "rainy"

    def main_menu(self):
        # ... (rest of the CLI code unchanged)
        pass

# CLI mode
agri_wiz = AgriWiz()

print("\n" + "="*50)
print("🌱 Welcome to Agri Wiz - Crop Recommendation System 🌱")
print("="*50)
print("\nTip: Run with --gui argument to use the graphical interface")

agri_wiz.main_menu()

if __name__ == "__main__":
    agri_wiz = AgriWiz()
    agri_wiz.main_menu()