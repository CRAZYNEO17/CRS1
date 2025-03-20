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
            if os.path.exists("crop_data.csv"):
                with open("crop_data.csv", "r") as file:
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
            with open("crop_data.csv", "w", newline="") as file:
                fieldnames = ["crop_name", "soil_types", "climates", "seasons", "water_needs", "humidity_preference", "soil_fertility"]
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

    def get_schemes_for_crop(self, crop_name: str, state: str, land_area: float = None) -> dict:
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
        while True:
            print("\nPlease select an option:")
            print("1. Get crop recommendations")
            print("2. Get recommendations by location")
            print("3. Add new crop to database")
            print("4. View all crops in database")
            print("5. Manage locations")
            print("6. View government schemes and subsidies")
            print("7. View weather forecast")
            print("8. Estimate crop yields")
            print("9. Exit")
            
            choice = input("Enter your choice (1-9): ")
            
            if choice == "7":
                print("\n--- Weather Forecast ---")
                location = input("Enter location: ")
                forecast = self.weather_service.get_weather_forecast(location)
                
                if forecast:
                    print("\nWeather Forecast:")
                    print(f"Average Temperature: {forecast['averages']['temperature']:.1f}°C")
                    print(f"Average Humidity: {forecast['averages']['humidity']:.0f}%")
                    print(f"Total Rainfall: {forecast['averages']['rainfall']:.1f}mm")
                    
                    print("\nDaily Forecast:")
                    for day in forecast["daily_forecasts"]:
                        print(f"\n{day['date']}:")
                        print(f"  Temperature: {day['temperature']:.1f}°C")
                        print(f"  Humidity: {day['humidity']:.0f}%")
                        print(f"  Rainfall: {day['rainfall']:.1f}mm")
                else:
                    print("Weather forecast not available for this location.")
            
            elif choice == "8":
                print("\n--- Crop Yield Estimation ---")
                crop_name = input("Enter crop name: ")
                location = input("Enter location: ")
                
                # Get location and weather data
                location_info = self.location_manager.get_location_info(location)
                weather_forecast = self.weather_service.get_weather_forecast(location)
                
                if location_info and weather_forecast:
                    conditions = {
                        "temperature": weather_forecast["averages"]["temperature"],
                        "rainfall": weather_forecast["averages"]["rainfall"] * 30,  # Monthly estimate
                        "humidity": weather_forecast["averages"]["humidity"],
                        "soil_ph": float(input("Enter soil pH (default 6.5): ") or 6.5),
                        "soil_fertility": input("Enter soil fertility (low/medium/high) [default: medium]: ") or "medium",
                        "water_availability": input("Enter water availability (low/medium/high) [default: medium]: ") or "medium",
                        "season": self.get_current_season()
                    }
                    
                    # Get yield estimate
                    yield_estimate = self.yield_estimator.predict_yield(crop_name, conditions)
                    
                    if "error" not in yield_estimate:
                        print(f"\nEstimated Yield: {yield_estimate['estimated_yield']} {yield_estimate['unit']}")
                        print(f"Confidence Interval: {yield_estimate['confidence_interval'][0]} - {yield_estimate['confidence_interval'][1]} {yield_estimate['unit']}")
                        
                        # Get optimization suggestions
                        optimization = self.yield_estimator.get_optimization_suggestions(crop_name, conditions)
                        if "error" not in optimization:
                            print("\nOptimization Suggestions:")
                            for suggestion in optimization["suggestions"]:
                                print(f"- {suggestion['suggestion']}")
                                print(f"  Potential yield improvement: {suggestion['potential_improvement']} {yield_estimate['unit']}")
                    else:
                        print(f"Error: {yield_estimate['error']}")
                else:
                    print("Location or weather data not available.")
            
            elif choice == "9":
                print("\nThank you for using Agri Wiz! Happy farming! 🌾")
                break
            
            else:
                # Handle other menu options as before
                print("\nPlease select an option:")
                print("1. Get crop recommendations")
                print("2. Get recommendations by location")
                print("3. Add new crop to database")
                print("4. View all crops in database")
                print("5. Manage locations")
                print("6. View government schemes and subsidies")
                print("7. Exit")
                
                choice = input("Enter your choice (1-7): ")
                
                if choice == "1":
                    print("\n--- Crop Recommendation ---")
                    location = input("Enter your location (optional): ")
                    
                    # If location provided, try to get soil and climate defaults
                    soil_defaults = []
                    climate_default = ""
                    if location:
                        soil_defaults = self.location_manager.get_soil_recommendations(location)
                        climate_default = self.location_manager.get_climate(location)
                        
                        if soil_defaults or climate_default:
                            print(f"\nFound data for location: {location}")
                            if soil_defaults:
                                print(f"Common soil types: {', '.join(soil_defaults)}")
                            if climate_default:
                                print(f"Climate: {climate_default}")
                    
                    soil_type = input("Enter soil type (clay/loamy/sandy/black soil): ")
                    climate = input("Enter climate (tropical/subtropical/temperate): ") if not climate_default else input(f"Enter climate (tropical/subtropical/temperate) [default: {climate_default}]: ") or climate_default
                    
                    # Get season or use current season
                    use_current = input("Use current season? (y/n): ").lower()
                    if use_current == "y":
                        if location:
                            season = self.location_manager.get_current_season_for_location(location) or self.get_current_season()
                        else:
                            season = self.get_current_season()
                        print(f"Current season detected as: {season}")
                    else:
                        season = input("Enter season (summer/winter/rainy/spring/fall): ")
                    
                    rainfall = input("Enter rainfall level (low/medium/high) [optional]: ")
                    humidity = input("Enter humidity level (low/medium/high) [optional]: ")
                    soil_fertility = input("Enter soil fertility (low/medium/high) [optional]: ")
                    soil_ph = input("Enter soil pH level [optional]: ")
                    temperature = input("Enter temperature [optional]: ")
                    water_availability = input("Enter water availability [optional]: ")
                    
                    recommendations, scored_recommendations = self.get_recommendations(soil_type, climate, season, rainfall, humidity, soil_fertility, soil_ph, temperature, water_availability)
                    
                    print("\n--- Recommended Crops ---")
                    if recommendations:
                        print(f"Found {len(recommendations)} suitable crops for your conditions:")
                        for i, crop in enumerate(recommendations, 1):
                            print(f"{i}. {crop['crop_name']} (Water needs: {crop['water_needs']}, "
                                  f"Humidity: {crop.get('humidity_preference', 'N/A')}, "
                                  f"Soil fertility: {crop.get('soil_fertility', 'N/A')})")
                    else:
                        print("No crops match your exact criteria. Consider these alternatives:")
                        # Provide some close matches with fewer criteria matching
                        alternatives = []
                        for crop in self.crop_data:
                            matches = 0
                            total_parameters = 3  # Core parameters
                            
                            # Check core parameters
                            if any(s.strip().lower() == soil_type.lower() for s in crop["soil_types"].split(",")):
                                matches += 1
                            if any(c.strip().lower() == climate.lower() for c in crop["climates"].split(",")):
                                matches += 1
                            if any(s.strip().lower() == season.lower() for s in crop["seasons"].split(",")):
                                matches += 1
                            
                            # Check optional parameters if provided
                            if humidity and "humidity_preference" in crop:
                                total_parameters += 1
                                if any(h.strip().lower() == humidity.lower() for h in crop["humidity_preference"].split(",")):
                                    matches += 1
                            
                            if soil_fertility and "soil_fertility" in crop:
                                total_parameters += 1
                                if any(f.strip().lower() == soil_fertility.lower() for f in crop["soil_fertility"].split(",")):
                                    matches += 1
                            
                            # Calculate match percentage
                            match_percentage = (matches / total_parameters) * 100
                            
                            if match_percentage >= 60:  # At least 60% match
                                alternatives.append((crop, matches, match_percentage))
                        
                        # Sort alternatives by match percentage
                        alternatives.sort(key=lambda x: x[2], reverse=True)
                        
                        for i, (crop, matches, percentage) in enumerate(alternatives[:5], 1):
                            print(f"{i}. {crop['crop_name']} - {percentage:.0f}% match")
                            print(f"   Water needs: {crop['water_needs']}, "
                                  f"Humidity: {crop.get('humidity_preference', 'N/A')}, "
                                  f"Soil fertility: {crop.get('soil_fertility', 'N/A')}")
                
                elif choice == "2":
                    print("\n--- Location-Based Recommendations ---")
                    
                    # Show available locations
                    print("\nAvailable locations in database:")
                    locations = self.location_manager.get_all_locations()
                    for i, loc in enumerate(locations, 1):
                        print(f"{i}. {loc.replace('_', ' ').title()}")
                        
                    location = input("\nEnter your location: ")
                    humidity = input("Enter humidity level (low/medium/high) [optional]: ")
                    soil_fertility = input("Enter soil fertility (low/medium/high) [optional]: ")
                    soil_ph = input("Enter soil pH level [optional]: ")
                    temperature = input("Enter temperature [optional]: ")
                    
                    recommendations, details = self.get_recommendations_by_location(location, humidity, soil_fertility, soil_ph, temperature)
                    
                    if recommendations is None:
                        print(f"\n{details}")
                        continue
                        
                    print(f"\nUsing location data:")
                    print(f"  - Soil Type: {details['soil_type']}")
                    print(f"  - Climate: {details['climate']}")
                    print(f"  - Season: {details['season']}")
                    print(f"  - Rainfall: {details['rainfall']}")
                    if details['humidity']:
                        print(f"  - Humidity: {details['humidity']}")
                    if details['soil_fertility']:
                        print(f"  - Soil Fertility: {details['soil_fertility']}")
                    if details['soil_ph']:
                        print(f"  - Soil pH: {details['soil_ph']}")
                    if details['temperature']:
                        print(f"  - Temperature: {details['temperature']}")
                    
                    print("\n--- Recommended Crops ---")
                    if recommendations:
                        print(f"Found {len(recommendations)} suitable crops for your location:")
                        for i, crop in enumerate(recommendations, 1):
                            print(f"{i}. {crop['crop_name']} (Water needs: {crop['water_needs']}, "
                                  f"Humidity: {crop.get('humidity_preference', 'N/A')}, "
                                  f"Soil fertility: {crop.get('soil_fertility', 'N/A')})")
                    else:
                        print("No crops match your location criteria exactly.")
                        print("Try adjusting optional parameters or use option 1 for manual input.")
                    
                    # After displaying recommendations, show relevant schemes
                    print("\n--- Available Government Schemes ---")
                    for crop_name, schemes in details['schemes_by_crop'].items():
                        print(f"\nSchemes for {crop_name}:")
                        for scheme in schemes:
                            print(f"- {scheme['name']}: {scheme['description']}")
                            if 'benefits' in scheme:
                                print("  Benefits:")
                                for benefit in scheme['benefits']:
                                    print(f"  * {benefit}")
                        print()
                
                elif choice == "3":
                    print("\n--- Add New Crop ---")
                    crop_name = input("Enter crop name: ")
                    soil_types = input("Enter suitable soil types (comma-separated): ")
                    climates = input("Enter suitable climates (comma-separated): ")
                    seasons = input("Enter suitable seasons (comma-separated): ")
                    water_needs = input("Enter water needs (low/medium/high): ")
                    humidity = input("Enter humidity preference (low/medium/high, comma-separated): ")
                    soil_fertility = input("Enter soil fertility needs (low/medium/high, comma-separated): ")
                    
                    new_crop = {
                        "crop_name": crop_name,
                        "soil_types": soil_types,
                        "climates": climates,
                        "seasons": seasons,
                        "water_needs": water_needs,
                        "humidity_preference": humidity,
                        "soil_fertility": soil_fertility
                    }
                    
                    self.add_crop(new_crop)
                
                elif choice == "4":
                    print("\n--- All Crops in Database ---")
                    for i, crop in enumerate(self.crop_data, 1):
                        print(f"{i}. {crop['crop_name']}")
                        print(f"   Soil Types: {crop['soil_types']}")
                        print(f"   Climates: {crop['climates']}")
                        print(f"   Seasons: {crop['seasons']}")
                        print(f"   Water Needs: {crop['water_needs']}")
                        if "humidity_preference" in crop:
                            print(f"   Humidity Preference: {crop['humidity_preference']}")
                        if "soil_fertility" in crop:
                            print(f"   Soil Fertility: {crop['soil_fertility']}")
                        print()
                
                elif choice == "5":
                    print("\n--- Manage Locations ---")
                    print("1. View all locations")
                    print("2. Add new location")
                    
                    loc_choice = input("Enter your choice (1-2): ")
                    
                    if loc_choice == "1":
                        print("\n--- All Locations in Database ---")
                        locations = self.location_manager.get_all_locations()
                        
                        for i, loc_name in enumerate(locations, 1):
                            loc_info = self.location_manager.get_location_info(loc_name)
                            print(f"{i}. {loc_name.replace('_', ' ').title()}")
                            print(f"   Climate: {loc_info['climate']}")
                            print(f"   Soil Types: {', '.join(loc_info['common_soil_types'])}")
                            print(f"   Rainfall: {loc_info['rainfall']}")
                            if "humidity" in loc_info:
                                print(f"   Humidity: {loc_info['humidity']}")
                            print(f"   Seasons: {', '.join(loc_info['seasons'].keys())}")
                            print()
                    
                    elif loc_choice == "2":
                        print("\n--- Add New Location ---")
                        location_name = input("Enter location name: ")
                        soil_types = input("Enter common soil types (comma-separated): ").split(",")
                        soil_types = [s.strip() for s in soil_types]
                        climate = input("Enter climate: ")
                        rainfall = input("Enter rainfall level (low/medium/high): ")
                        humidity = input("Enter humidity level (low/medium/high): ")
                        
                        # Season data
                        print("\nNow enter the months for each season (comma-separated):")
                        winter_months = input("Winter months: ").lower().split(",")
                        winter_months = [m.strip() for m in winter_months]
                        summer_months = input("Summer months: ").lower().split(",")
                        summer_months = [m.strip() for m in summer_months]
                        rainy_months = input("Rainy/Monsoon months: ").lower().split(",")
                        rainy_months = [m.strip() for m in rainy_months]
                        spring_months = input("Spring months: ").lower().split(",")
                        spring_months = [m.strip() for m in spring_months]
                        fall_months = input("Fall/Autumn months: ").lower().split(",")
                        fall_months = [m.strip() for m in fall_months]
                        
                        seasons = {}
                        if winter_months[0]: seasons["winter"] = winter_months
                        if summer_months[0]: seasons["summer"] = summer_months
                        if rainy_months[0]: seasons["rainy"] = rainy_months
                        if spring_months[0]: seasons["spring"] = spring_months
                        if fall_months[0]: seasons["fall"] = fall_months
                        
                        location_info = {
                            "common_soil_types": soil_types,
                            "climate": climate,
                            "rainfall": rainfall,
                            "humidity": humidity if humidity else None,
                            "seasons": seasons
                        }
                        
                        self.location_manager.add_location(location_name, location_info)
                
                elif choice == "6":
                    print("\n--- Government Schemes and Subsidies ---")
                    print("1. View all schemes")
                    print("2. Search schemes by category")
                    print("3. Get schemes for specific crop")
                    print("4. Check scheme eligibility")
                    
                    scheme_choice = input("Enter your choice (1-4): ")
                    
                    if scheme_choice == "1":
                        schemes = self.scheme_manager.get_all_schemes()
                        print("\nAvailable Schemes:")
                        for scheme in schemes:
                            print(f"\n{scheme['name']} - {scheme['full_name']}")
                            print(f"Description: {scheme['description']}")
                            if 'benefits' in scheme:
                                print("Benefits:")
                                for benefit in scheme['benefits']:
                                    print(f"- {benefit}")
                    
                    elif scheme_choice == "2":
                        print("\nAvailable categories:")
                        print("- irrigation")
                        print("- insurance")
                        print("- credit")
                        print("- income_support")
                        print("- organic_farming")
                        print("- marketing")
                        print("- food_security")
                        
                        category = input("\nEnter category: ")
                        schemes = self.scheme_manager.get_schemes_by_category(category)
                        
                        if schemes:
                            print(f"\nSchemes for category '{category}':")
                            for scheme in schemes:
                                print(f"\n{scheme['name']} - {scheme['full_name']}")
                                print(f"Description: {scheme['description']}")
                        else:
                            print("No schemes found for this category.")
                    
                    elif scheme_choice == "3":
                        crop_name = input("Enter crop name: ")
                        state = input("Enter state: ")
                        land_area = float(input("Enter land area in hectares (optional, press Enter to skip): ") or 0)
                        
                        scheme_info = self.get_schemes_for_crop(crop_name, state, land_area)
                        
                        print("\nRelevant Schemes:")
                        for scheme in scheme_info['schemes']:
                            print(f"\n{scheme['name']} - {scheme['full_name']}")
                            print(f"Description: {scheme['description']}")
                            if 'benefits' in scheme:
                                print("Benefits:")
                                for benefit in scheme['benefits']:
                                    print(f"- {benefit}")
                        
                        print("\nAvailable Subsidies:")
                        for category, subsidy in scheme_info['subsidies'].items():
                            if subsidy:
                                print(f"{category.title()}: {subsidy}")
                    
                    elif scheme_choice == "4":
                        print("\nEnter farmer details to check eligibility:")
                        farmer_details = {
                            "land_ownership": input("Do you own land? (yes/no): ").lower() == "yes",
                            "has_bank_account": input("Do you have a bank account? (yes/no): ").lower() == "yes",
                            "state": input("Enter state: ")
                        }
                        
                        eligible_schemes = self.scheme_manager.get_eligible_schemes(farmer_details)
                        
                        if eligible_schemes:
                            print("\nYou are eligible for these schemes:")
                            for scheme in eligible_schemes:
                                print(f"\n{scheme['name']} - {scheme['full_name']}")
                                print(f"Description: {scheme['description']}")
                                if 'benefits' in scheme:
                                    print("Benefits:")
                                    for benefit in scheme['benefits']:
                                        print(f"- {benefit}")
                        else:
                            print("\nNo eligible schemes found based on provided details.")
                    
                    else:
                        print("Invalid choice for schemes menu.")
                
                elif choice == "7":
                    print("\nThank you for using Agri Wiz! Happy farming! 🌾")
                    break
                
                else:
                    print("Invalid choice. Please try again.")

def main():
    """Main entry point for Agri Wiz"""
    import sys
    
    # Check if GUI mode is requested
    if len(sys.argv) > 1 and sys.argv[1] == '--gui':
        # Import and start GUI
        from gui import AgriWizGUI
        app = AgriWizGUI()
        app.run()
        return

    # CLI mode
    agri_wiz = AgriWiz()
    
    print("\n" + "="*50)
    print("🌱 Welcome to Agri Wiz - Crop Recommendation System 🌱")
    print("="*50)
    print("\nTip: Run with --gui argument to use the graphical interface")
    
    agri_wiz.main_menu()

if __name__ == "__main__":
    main()