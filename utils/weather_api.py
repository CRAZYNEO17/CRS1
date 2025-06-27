#!/usr/bin/env python
# Weather API Module for Agri Wiz
# Fetches real-time weather data for crop recommendations

import json
import os
import urllib.request
import urllib.parse
import datetime
import time
import requests
import socket
import logging
import asyncio
from datetime import datetime
from typing import Dict, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class GPSConfig:
    """GPS Configuration and Management"""
    def __init__(self):
        """Initialize GPS configuration."""
        self.location_cache = {}
        self.cache_duration = 300  # Cache GPS location for 5 minutes
        self._geolocator = None
        self.use_windows_location = True
        
    async def _init_windows_location(self):
        """Initialize Windows location service"""
        try:
            import winsdk.windows.devices.geolocation as geolocation
            if not self._geolocator:
                self._geolocator = geolocation.Geolocator()
            return True
        except ImportError:
            logging.warning("Windows SDK not available")
            return False
        except Exception as e:
            logging.error(f"Error initializing Windows location: {e}")
            return False

    async def _get_ip_location(self) -> Dict:
        """Get location based on IP address."""
        # Try multiple IP geolocation services for reliability
        services = [
            ('http://ip-api.com/json/', lambda r: {
                'latitude': r['lat'],
                'longitude': r['lon'],
                'city': r['city'],
                'region': r['regionName'],
                'country': r['country'],
                'accuracy': 5000.0,
                'source': 'ip'
            }),
            ('https://ipapi.co/json/', lambda r: {
                'latitude': r['latitude'],
                'longitude': r['longitude'],
                'city': r['city'],
                'region': r['region'],
                'country': r['country_name'],
                'accuracy': 5000.0,
                'source': 'ip'
            }),
            ('https://geolocation-db.com/json/', lambda r: {
                'latitude': r['latitude'],
                'longitude': r['longitude'],
                'city': r['city'],
                'region': r.get('state', ''),
                'country': r['country_name'],
                'accuracy': 5000.0,
                'source': 'ip'
            })
        ]

        for url, parser in services:
            try:
                response = await asyncio.get_event_loop().run_in_executor(
                    None, 
                    lambda: requests.get(url, timeout=5)
                )
                if response.status_code == 200:
                    data = response.json()
                    if url == 'http://ip-api.com/json/' and data.get('status') != 'success':
                        continue
                    
                    location = parser(data)
                    location['timestamp'] = time.time()
                    return location
            except Exception as e:
                logging.warning(f"Error with {url}: {e}")
                continue

        logging.error("All IP geolocation services failed")
        return None

    async def get_location(self) -> Optional[Dict]:
        """Get location using Windows Location Service or fallback methods."""
        try:
            # Check cache first
            current_time = time.time()
            for location in self.location_cache.values():
                if current_time - location['timestamp'] < self.cache_duration:
                    return location

            # Try Windows Location Service first
            if self.use_windows_location and await self._init_windows_location():
                try:
                    import winsdk.windows.devices.geolocation as geolocation
                    status = await self._geolocator.request_access_async()
                    
                    if status == geolocation.GeolocationAccessStatus.ALLOWED:
                        position = await self._geolocator.get_geoposition_async()
                        if position and position.coordinate:
                            location = {
                                'latitude': position.coordinate.latitude,
                                'longitude': position.coordinate.longitude,
                                'accuracy': position.coordinate.accuracy,
                                'source': 'windows_gps',
                                'timestamp': time.time()
                            }
                            self.location_cache['windows'] = location
                            return location
                except Exception as e:
                    logging.warning(f"Windows location failed: {e}")
            
            # Try IP-based location as fallback
            ip_location = await self._get_ip_location()
            if ip_location:
                self.location_cache['ip'] = ip_location
                return ip_location

            return None
        except Exception as e:
            logging.error(f"Error getting location: {e}")
            return None

class WeatherAPI:
    def __init__(self, api_key=None):
        """Initialize the WeatherAPI with an optional API key."""
        self.api_key = api_key or os.getenv("OPENWEATHERMAP_API_KEY", "demo_key")
        self.cache_file = "weather_cache.json"
        self.cache_duration = 3600  # Cache weather data for 1 hour
        self.weather_cache = self._load_cache()
        self.gps_config = GPSConfig()
        self.nominatim_url = "https://nominatim.openstreetmap.org/reverse"
        self.nominatim_headers = {
            'User-Agent': 'AgriWiz/1.0'
        }
    
    async def get_current_location(self, use_gps: bool = True) -> Dict:
        """
        Get current location using Windows Location Service or IP-based geolocation.
        
        Args:
            use_gps: If True, try GPS first, fall back to IP if GPS fails
        """
        if use_gps:
            try:
                location = await self.gps_config.get_location()
                if location and location.get('source') == 'windows_gps':
                    # Get location name using reverse geocoding
                    location_name = await self._get_location_name(
                        location['latitude'], 
                        location['longitude']
                    )
                    location.update(location_name)
                    return location
            except Exception as e:
                logging.error(f"Error getting GPS location: {e}")
        
        # Fall back to IP-based location
        logging.info("Using IP-based location detection")
        return self.gps_config._get_ip_location()

    async def _get_location_name(self, lat: float, lon: float) -> Dict:
        """Get location name from coordinates using OpenStreetMap Nominatim."""
        try:
            params = {
                'lat': lat,
                'lon': lon,
                'format': 'json'
            }
            
            # Add necessary headers to comply with usage policy
            headers = {
                'User-Agent': 'AgriWiz/1.0 (agricultural-assistant)',
                'Accept-Language': 'en-US,en;q=0.5'
            }
            
            # Add timeout to prevent hanging
            response = requests.get(
                self.nominatim_url, 
                params=params, 
                headers=headers,
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                address = data.get('address', {})
                
                # Try various address fields in priority order
                loc_name = (
                    address.get('city') or
                    address.get('town') or
                    address.get('village') or
                    address.get('suburb') or
                    address.get('county') or
                    address.get('state_district') or
                    address.get('state') or
                    address.get('country')
                )
                
                if loc_name:
                    return {
                        'city': loc_name,
                        'state': address.get('state', ''),
                        'country': address.get('country', ''),
                        'display_name': data.get('display_name', f"{lat:.4f}, {lon:.4f}")
                    }
                    
        except requests.Timeout:
            logging.error("Timeout while getting location name")
        except Exception as e:
            logging.error(f"Error getting location name: {e}")
        
        # Return coordinates if geocoding fails
        return {
            'city': f"{lat:.4f}, {lon:.4f}",
            'state': '',
            'country': '',
            'display_name': f"{lat:.4f}, {lon:.4f}"
        }

    def _load_cache(self) -> Dict:
        """Load the weather cache from file if it exists."""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, "r") as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logging.error(f"Error loading weather cache: {e}")
            return {}
    
    def _save_cache(self):
        """Save the weather cache to file."""
        try:
            with open(self.cache_file, "w") as f:
                json.dump(self.weather_cache, f)
        except Exception as e:
            logging.error(f"Error saving weather cache: {e}")
    
    def _is_cache_valid(self, location: str) -> bool:
        """Check if cache for a location is still valid."""
        if location in self.weather_cache:
            timestamp = self.weather_cache[location].get("timestamp", 0)
            return (time.time() - timestamp) < self.cache_duration
        return False
    
    def get_weather_data(self, location):
        """
        Get current weather data for a location.
        
        This is a simplified implementation using OpenWeatherMap API.
        In production, replace this with actual API calls using your API key.
        """
        # Check if we have valid cached data
        if self._is_cache_valid(location):
            print(f"Using cached weather data for {location}")
            return self.weather_cache[location]
            
        try:
            # In a real implementation, use the API key and make actual HTTP requests
            if self.api_key == "demo_key":
                # Return mock data for demo purposes
                weather_data = self._get_mock_weather_data(location)
            else:
                # Construct the API URL (OpenWeatherMap example)
                encoded_location = urllib.parse.quote(location)
                url = f"http://api.openweathermap.org/data/2.5/weather?q={encoded_location}&appid={self.api_key}&units=metric"
                
                # Make the API request
                with urllib.request.urlopen(url) as response:
                    data = response.read()
                    weather_data = self._parse_api_response(json.loads(data))
                    
            # Cache the result
            weather_data["timestamp"] = time.time()
            self.weather_cache[location] = weather_data
            self._save_cache()
            
            return weather_data
            
        except Exception as e:
            print(f"Error fetching weather data for {location}: {e}")
            # Return mock data as fallback
            return self._get_mock_weather_data(location)
    
    def _parse_api_response(self, api_data):
        """Parse the OpenWeatherMap API response into our format."""
        try:
            return {
                "temperature": api_data["main"]["temp"],
                "humidity": api_data["main"]["humidity"],
                "rainfall": api_data.get("rain", {}).get("1h", 0),
                "description": api_data["weather"][0]["description"],
                "timestamp": time.time()
            }
        except KeyError as e:
            print(f"Error parsing API response: {e}")
            return self._get_mock_weather_data("unknown")
    
    def _get_mock_weather_data(self, location):
        """Generate mock weather data for demo purposes."""
        # Extract country/region from location if possible
        location_lower = location.lower()
        
        # Check for known locations and return more accurate mock data
        if "india" in location_lower:
            if "north" in location_lower or "punjab" in location_lower:
                return {
                    "temperature": 32.5,
                    "humidity": 65,
                    "rainfall": 0.5,
                    "description": "Partly cloudy",
                    "timestamp": time.time()
                }
            elif "south" in location_lower or "kerala" in location_lower:
                return {
                    "temperature": 30.0,
                    "humidity": 85,
                    "rainfall": 2.5,
                    "description": "Light rain",
                    "timestamp": time.time()
                }
        elif "usa" in location_lower:
            if "midwest" in location_lower:
                return {
                    "temperature": 22.0,
                    "humidity": 55,
                    "rainfall": 0.0,
                    "description": "Clear sky",
                    "timestamp": time.time()
                }
            elif "california" in location_lower:
                return {
                    "temperature": 25.0,
                    "humidity": 40,
                    "rainfall": 0.0,
                    "description": "Sunny",
                    "timestamp": time.time()
                }
        
        # Generic mock data if location not recognized
        current_month = datetime.now().month
        
        # Adjust temperature and rainfall based on season in northern hemisphere
        if 3 <= current_month <= 5:  # Spring
            temp = 20.0 + (hash(location) % 10) - 5
            rainfall = 1.0 + (hash(location[::-1]) % 3)
            humidity = 60 + (hash(location) % 20)
            description = "Spring showers"
        elif 6 <= current_month <= 8:  # Summer
            temp = 28.0 + (hash(location) % 15) - 7
            rainfall = 0.5 + (hash(location[::-1]) % 2)
            humidity = 55 + (hash(location) % 25)
            description = "Warm and humid"
        elif 9 <= current_month <= 11:  # Fall
            temp = 15.0 + (hash(location) % 10) - 5
            rainfall = 0.7 + (hash(location[::-1]) % 2.5)
            humidity = 50 + (hash(location) % 20)
            description = "Cool and breezy"
        else:  # Winter
            temp = 5.0 + (hash(location) % 15) - 10
            rainfall = 0.3 + (hash(location[::-1]) % 1.5)
            humidity = 40 + (hash(location) % 30)
            description = "Cold with occasional precipitation"
        
        return {
            "temperature": round(temp, 1),
            "humidity": round(humidity, 0),
            "rainfall": round(rainfall, 1),
            "description": description,
            "timestamp": time.time()
        }
    
    def get_weather_based_recommendations(self, weather_data):
        """
        Get recommendations based on current weather conditions.
        
        Returns a dictionary with recommendations and alerts.
        """
        recommendations = {
            "watering_advice": "",
            "alerts": [],
            "farming_tips": []
        }
        
        # Watering advice
        if weather_data["rainfall"] > 1.5:
            recommendations["watering_advice"] = "Skip watering today due to recent rainfall."
        elif weather_data["humidity"] > 80:
            recommendations["watering_advice"] = "Light watering recommended due to high humidity."
        elif weather_data["temperature"] > 30:
            recommendations["watering_advice"] = "Increase watering frequency due to high temperatures."
        else:
            recommendations["watering_advice"] = "Regular watering schedule recommended."
        
        # Weather alerts
        if weather_data["temperature"] > 35:
            recommendations["alerts"].append("HEAT ALERT: Protect sensitive crops from extreme heat.")
        elif weather_data["temperature"] < 5:
            recommendations["alerts"].append("FROST ALERT: Take measures to protect crops from frost.")
        
        if weather_data["rainfall"] > 3.0:
            recommendations["alerts"].append("HEAVY RAIN ALERT: Check for potential flooding and ensure proper drainage.")
        
        # Farming tips based on weather
        if 20 <= weather_data["temperature"] <= 30:
            recommendations["farming_tips"].append("Optimal temperature for most crop growth and development.")
        
        if weather_data["humidity"] > 70:
            recommendations["farming_tips"].append("High humidity increases disease risk. Monitor crops for fungal infections.")
        elif weather_data["humidity"] < 40:
            recommendations["farming_tips"].append("Low humidity may cause excessive transpiration. Consider shade for sensitive crops.")
        
        if "rain" in weather_data["description"].lower():
            recommendations["farming_tips"].append("Current rainfall presents a good opportunity for transplanting seedlings.")
        
        return recommendations

    def get_weather_by_coordinates(self, lat: float, lon: float) -> Dict:
        """Get weather data for specific coordinates."""
        try:
            # Use the coordinates to fetch weather data
            location_key = f"{lat:.4f},{lon:.4f}"
            
            # Check cache first
            if self._is_cache_valid(location_key):
                return self.weather_cache[location_key]
            
            if self.api_key == "demo_key":
                # Return mock data for demo purposes
                mock_data = self._get_mock_weather_data(location_key)
                mock_data.update({
                    'latitude': lat,
                    'longitude': lon,
                    'location': f"{lat:.4f}, {lon:.4f}"
                })
                return mock_data
            else:
                # Construct the API URL (OpenWeatherMap example)
                url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={self.api_key}&units=metric"
                
                # Make the API request
                with urllib.request.urlopen(url) as response:
                    data = response.read()
                    weather_data = self._parse_api_response(json.loads(data))
                    weather_data.update({
                        'latitude': lat,
                        'longitude': lon,
                        'location': f"{lat:.4f}, {lon:.4f}"
                    })
                    return weather_data

        except Exception as e:
            logging.error(f"Error getting weather for coordinates: {e}")
            return {
                "temperature": 25,
                "humidity": 60,
                "rainfall": 0,
                "description": "Error fetching weather data",
                "latitude": lat,
                "longitude": lon,
                "location": f"{lat:.4f}, {lon:.4f}"
            }

class WeatherService:
    def __init__(self):
        self.api_key = os.getenv("OPENWEATHERMAP_API_KEY", "demo_key")
        self.cache_file = "data/processed/weather_cache.json"
        self.cache = self.load_cache()

    def load_cache(self):
        """Load weather cache from JSON file."""
        try:
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            if os.path.exists(self.cache_file):
                with open(self.cache_file, "r") as file:
                    return json.load(file)
        except Exception as e:
            print(f"Error loading weather cache: {e}")
        return {}

    def save_cache(self):
        """Save weather cache to JSON file."""
        try:
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            with open(self.cache_file, "w") as file:
                json.dump(self.cache, file)
        except Exception as e:
            print(f"Error saving weather cache: {e}")

    def get_weather_forecast(self, location: str) -> Optional[Dict]:
        """Get 5-day weather forecast for a location."""
        # Check cache first
        cache_key = f"{location}_{datetime.now().strftime('%Y-%m-%d')}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        try:
            # Get coordinates first
            geo_url = f"http://api.openweathermap.org/geo/1.0/direct"
            params = {
                "q": location,
                "limit": 1,
                "appid": self.api_key
            }
            response = requests.get(geo_url, params=params)
            location_data = response.json()
            
            if not location_data:
                return None
                
            lat = location_data[0]["lat"]
            lon = location_data[0]["lon"]
            
            # Get weather forecast
            forecast_url = "https://api.openweathermap.org/data/2.5/forecast"
            params = {
                "lat": lat,
                "lon": lon,
                "appid": self.api_key,
                "units": "metric"
            }
            
            response = requests.get(forecast_url, params=params)
            forecast = response.json()
            
            # Process and cache the data
            processed_data = {
                "daily_forecasts": [],
                "averages": {
                    "temperature": 0,
                    "humidity": 0,
                    "rainfall": 0
                }
            }
            
            temp_sum = humid_sum = rain_sum = 0
            readings = 0
            
            for item in forecast["list"]:
                date = datetime.fromtimestamp(item["dt"]).strftime('%Y-%m-%d')
                temp = item["main"]["temp"]
                humidity = item["main"]["humidity"]
                rain = item["rain"]["3h"] if "rain" in item else 0
                
                processed_data["daily_forecasts"].append({
                    "date": date,
                    "temperature": temp,
                    "humidity": humidity,
                    "rainfall": rain
                })
                
                temp_sum += temp
                humid_sum += humidity
                rain_sum += rain
                readings += 1
            
            # Calculate averages
            processed_data["averages"]["temperature"] = temp_sum / readings
            processed_data["averages"]["humidity"] = humid_sum / readings
            processed_data["averages"]["rainfall"] = rain_sum
            
            # Cache the results
            self.cache[cache_key] = processed_data
            self.save_cache()
            
            return processed_data
            
        except Exception as e:
            print(f"Error fetching weather data: {e}")
            return None

    def get_weather_suitability(self, crop: Dict, location: str) -> Dict:
        """Determine weather suitability for a specific crop."""
        forecast = self.get_weather_forecast(location)
        if not forecast:
            return {"suitable": False, "reason": "Weather data unavailable"}

        averages = forecast["averages"]
        
        # Extract crop requirements
        temp_range = crop.get("temperature_range", "").split("-")
        rainfall_range = crop.get("rainfall_range_mm", "").split("-")
        
        if len(temp_range) == 2:
            min_temp, max_temp = map(float, temp_range)
            if not (min_temp <= averages["temperature"] <= max_temp):
                return {
                    "suitable": False,
                    "reason": f"Temperature {averages['temperature']:.1f}°C outside optimal range ({min_temp}-{max_temp}°C)"
                }
        
        if len(rainfall_range) == 2:
            min_rain, max_rain = map(float, rainfall_range)
            monthly_rain_estimate = averages["rainfall"] * 30  # Rough monthly estimate
            if not (min_rain <= monthly_rain_estimate <= max_rain):
                return {
                    "suitable": False,
                    "reason": f"Expected monthly rainfall {monthly_rain_estimate:.0f}mm outside optimal range ({min_rain}-{max_rain}mm)"
                }
        
        humidity_pref = crop.get("humidity_preference", "").split(",")
        current_humidity = "high" if averages["humidity"] >= 70 else "medium" if averages["humidity"] >= 40 else "low"
        
        if humidity_pref and current_humidity not in [h.strip() for h in humidity_pref]:
            return {
                "suitable": False,
                "reason": f"Current humidity level ({current_humidity}) not suitable for crop"
            }
        
        return {
            "suitable": True,
            "forecast": forecast,
            "details": {
                "temperature": f"{averages['temperature']:.1f}°C",
                "humidity": f"{averages['humidity']:.0f}%",
                "estimated_monthly_rainfall": f"{averages['rainfall'] * 30:.0f}mm"
            }
        }

# Helper function to get humidity level from percentage
def get_humidity_level(humidity_percentage):
    if humidity_percentage <= 40:
        return "low"
    elif humidity_percentage <= 70:
        return "medium"
    else:
        return "high"

# Helper function to get rainfall level from mm
def get_rainfall_level(rainfall_mm):
    if rainfall_mm <= 0.5:
        return "low"
    elif rainfall_mm <= 2:
        return "medium"
    else:
        return "high"

# Test the full weather API integration
async def test_weather_api():
    """Test the weather API with GPS integration"""
    api = WeatherAPI()
    
    # First try to get location with GPS
    location = await api.get_current_location(use_gps=True)
    
    if location:
        print(f"\nLocation obtained from {location.get('source', 'unknown')}:")
        print(f"Coordinates: {location.get('latitude', 'N/A')}, {location.get('longitude', 'N/A')}")
        print(f"City: {location.get('city', 'N/A')}")
        print(f"State: {location.get('state', 'N/A')}")
        print(f"Country: {location.get('country', 'N/A')}")
        
        # Get weather for this location
        weather = api.get_weather_by_coordinates(
            location['latitude'],
            location['longitude']
        )
        
        print(f"\nCurrent Weather:")
        print(f"Temperature: {weather.get('temperature')}°C")
        print(f"Humidity: {weather.get('humidity')}% ({get_humidity_level(weather.get('humidity', 0))})")
        print(f"Rainfall: {weather.get('rainfall')}mm ({get_rainfall_level(weather.get('rainfall', 0))})")
        print(f"Description: {weather.get('description', 'N/A')}")
        
        # Get recommendations
        recommendations = api.get_weather_based_recommendations(weather)
        print(f"\nRecommendations:")
        print(f"Watering Advice: {recommendations['watering_advice']}")
        
        if recommendations['alerts']:
            print("\nAlerts:")
            for alert in recommendations['alerts']:
                print(f"- {alert}")
        
        if recommendations['farming_tips']:
            print("\nFarming Tips:")
            for tip in recommendations['farming_tips']:
                print(f"- {tip}")
    else:
        print("Could not detect location")

# Simple test if run directly
if __name__ == "__main__":
    api = WeatherAPI()
    data = api.get_weather_data("Punjab, India")
    print(f"Weather for Punjab, India:")
    print(f"Temperature: {data['temperature']}°C")
    print(f"Humidity: {data['humidity']}% ({get_humidity_level(data['humidity'])})")
    print(f"Rainfall: {data['rainfall']}mm ({get_rainfall_level(data['rainfall'])})")
    print(f"Description: {data['description']}")
    
    recommendations = api.get_weather_based_recommendations(data)
    print("\nRecommendations:")
    print(f"- {recommendations['watering_advice']}")
    
    if recommendations["alerts"]:
        print("\nAlerts:")
        for alert in recommendations["alerts"]:
            print(f"- {alert}")
    
    if recommendations["farming_tips"]:
        print("\nFarming Tips:")
        for tip in recommendations["farming_tips"]:
            print(f"- {tip}")
            
    # Run the GPS-integrated test
    print("\nTesting GPS integration...")
    asyncio.run(test_weather_api())