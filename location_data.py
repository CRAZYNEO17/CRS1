#!/usr/bin/env python
# Location Data Module for Agri Wiz
# Handles location-specific climate and soil information

import json
import os
from datetime import datetime

class LocationManager:
    def __init__(self):
        self.location_data = {}
        self.load_location_data()
    
    def load_location_data(self):
        """Load location data from JSON file."""
        try:
            if os.path.exists("location_data.json"):
                with open("location_data.json", "r") as file:
                    self.location_data = json.load(file)
                print(f"Loaded {len(self.location_data)} locations from database.")
            else:
                print("Location database not found. Creating sample data.")
                self.create_sample_data()
        except Exception as e:
            print(f"Error loading location data: {e}")
            self.create_sample_data()
    
    def create_sample_data(self):
        """Create sample location data if no data file exists."""
        self.location_data = {
            "punjab": {
                "common_soil_types": ["loamy", "sandy loam", "clay"],
                "climate": "subtropical",
                "rainfall": "medium",
                "humidity": "medium",
                "soil_fertility": "high",
                "seasons": {
                    "winter": ["december", "january", "february"],
                    "spring": ["march", "april"],
                    "summer": ["may", "june", "july"],
                    "rainy": ["july", "august", "september"],
                    "fall": ["october", "november"]
                }
            },
            "kerala": {
                "common_soil_types": ["laterite", "forest", "sandy"],
                "climate": "tropical",
                "rainfall": "high",
                "humidity": "high",
                "soil_fertility": "high",
                "seasons": {
                    "winter": ["december", "january"],
                    "summer": ["march", "april", "may"],
                    "rainy": ["june", "july", "august", "september", "october", "november"],
                    "spring": ["february", "march"]
                }
            },
            "california": {
                "common_soil_types": ["sandy", "clay", "loamy"],
                "climate": "mediterranean",
                "rainfall": "low",
                "humidity": "low",
                "soil_fertility": "medium",
                "seasons": {
                    "winter": ["december", "january", "february"],
                    "spring": ["march", "april", "may"],
                    "summer": ["june", "july", "august"],
                    "fall": ["september", "october", "november"]
                }
            }
        }
        self.save_location_data()
        print("Location data saved successfully.")
    
    def save_location_data(self):
        """Save location data to JSON file."""
        try:
            with open("location_data.json", "w") as file:
                json.dump(self.location_data, file, indent=4)
        except Exception as e:
            print(f"Error saving location data: {e}")
    
    def get_location_info(self, location_name):
        """Get information for a specific location."""
        # Handle coordinate-based location strings
        if ',' in location_name:
            try:
                parts = location_name.split(',')
                if len(parts) == 2:
                    # This is likely a lat,lon format
                    # Return default values for unknown locations
                    return {
                        "common_soil_types": ["loamy"],  # Default soil type
                        "climate": "subtropical",  # Moderate default
                        "rainfall": "medium",
                        "humidity": "medium",
                        "seasons": {
                            "winter": ["december", "january", "february"],
                            "spring": ["march", "april", "may"],
                            "summer": ["june", "july", "august"],
                            "rainy": ["july", "august", "september"],
                            "fall": ["october", "november"]
                        }
                    }
            except:
                pass
        
        # Try exact match first
        if location_name in self.location_data:
            return self.location_data[location_name]
            
        # Try with lowercase and underscore replacement
        location_key = location_name.lower().replace(" ", "_")
        if location_key in self.location_data:
            return self.location_data[location_key]
            
        # Try to find nearest matching location (fuzzy match)
        for key in self.location_data.keys():
            if key.replace("_", " ") in location_name.lower() or location_name.lower() in key.replace("_", " "):
                return self.location_data[key]
        
        # If no match found, return closest regional default
        if "india" in location_name.lower():
            return self.location_data.get("northern_india", self.location_data.get("southern_india"))
        
        # Return general defaults if no match found
        return {
            "common_soil_types": ["loamy"],
            "climate": "subtropical",
            "rainfall": "medium",
            "humidity": "medium",
            "seasons": {
                "winter": ["december", "january", "february"],
                "spring": ["march", "april", "may"],
                "summer": ["june", "july", "august"],
                "rainy": ["july", "august", "september"],
                "fall": ["october", "november"]
            }
        }
    
    def add_location(self, location_name, location_info):
        """Add a new location to the database."""
        location_key = location_name.lower().replace(" ", "_")
        self.location_data[location_key] = location_info
        self.save_location_data()
        print(f"Added {location_name} to the database.")
    
    def get_current_season_for_location(self, location_name):
        """Get the current season for a location based on current month."""
        location_info = self.get_location_info(location_name)
        if not location_info or "seasons" not in location_info:
            return None
        
        current_month = datetime.now().strftime("%B").lower()
        for season, months in location_info["seasons"].items():
            if current_month in months:
                return season
        return None
    
    def get_all_locations(self):
        """Get list of all locations in the database."""
        return list(self.location_data.keys())
    
    def get_soil_recommendations(self, location_name):
        """Get soil type recommendations for a location."""
        location_info = self.get_location_info(location_name)
        if location_info and "common_soil_types" in location_info:
            return location_info["common_soil_types"]
        return []
    
    def get_climate(self, location_name):
        """Get climate for a location."""
        location_info = self.get_location_info(location_name)
        if location_info and "climate" in location_info:
            return location_info["climate"]
        return ""
    
    def get_humidity(self, location_name):
        """Get humidity level for a location."""
        location_info = self.get_location_info(location_name)
        if location_info and "humidity" in location_info:
            return location_info["humidity"]
        return None

    def get_soil_fertility(self, location_name):
        """Get soil fertility level for a location."""
        location_info = self.get_location_info(location_name)
        if location_info and "soil_fertility" in location_info:
            return location_info["soil_fertility"]
        return None