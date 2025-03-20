from weather_api import WeatherAPI, get_humidity_level, get_rainfall_level
from gps_service import GPSService
import requests
import logging
import asyncio
from typing import Dict, Optional

class WebWeatherService(WeatherAPI):
    """Web-specific weather service that extends base WeatherAPI with additional features for web GUI"""
    
    def __init__(self, api_key=None):
        super().__init__(api_key)
        self.gps_service = GPSService()
        self.nominatim_url = "https://nominatim.openstreetmap.org/reverse"
        self.nominatim_headers = {
            'User-Agent': 'AgriWiz/1.0'  # Required by Nominatim ToS
        }
    
    async def get_current_location(self) -> Optional[Dict]:
        """Get current location using Windows GPS"""
        return await self.gps_service.get_location()
    
    def get_weather_by_coordinates(self, lat: float, lon: float) -> Dict:
        """Get weather data for coordinates."""
        try:
            # Use the coordinates to fetch weather data
            location_key = f"{lat:.4f},{lon:.4f}"
            
            # Check cache first
            if self._is_cache_valid(location_key):
                return self.weather_cache[location_key]
            
            # Make actual weather API call here
            weather_data = self._get_weather_data(lat, lon)
            
            # Cache the result
            weather_data["timestamp"] = time.time()
            self.weather_cache[location_key] = weather_data
            self._save_cache()
            
            return weather_data
            
        except Exception as e:
            logging.error(f"Error getting weather for coordinates: {e}")
            return {
                "temperature": 25,
                "humidity": 60,
                "rainfall": 0,
                "description": "Error fetching weather data"
            }

    async def get_weather_with_location(self, lat: float, lon: float) -> Dict:
        """Get both weather data and location information for coordinates."""
        try:
            # Get the weather data
            weather_data = self.get_weather_by_coordinates(lat, lon)
            
            # Get location information using Windows GPS
            location = await self.get_current_location()
            
            if location:
                # Use the high-accuracy GPS location
                location_info = await self._get_location_name(
                    location['latitude'],
                    location['longitude']
                )
                
                # Add GPS accuracy and altitude if available
                weather_data.update({
                    'accuracy': location['accuracy'],
                    'altitude': location['altitude'],
                    'speed': location['speed']
                })
            else:
                # Fallback to using provided coordinates with Nominatim
                location_info = await self._get_location_name(lat, lon)
            
            # Combine the data
            weather_data.update({
                'location': location_info['display_name'],
                'city': location_info['city'],
                'state': location_info['state'],
                'country': location_info['country']
            })
            
            return weather_data
            
        except Exception as e:
            logging.error(f"Error in get_weather_with_location: {e}")
            return {
                'error': str(e),
                'location': f"{lat:.4f}, {lon:.4f}",
                'temperature': 25,
                'humidity': 60,
                'rainfall': 0,
                'description': 'Error fetching weather data'
            }

    def format_weather_response(self, weather_data: Dict) -> Dict:
        """Format weather data for web API response."""
        return {
            'temperature': weather_data.get('temperature', 25),
            'humidity': weather_data.get('humidity', 60),
            'rainfall': weather_data.get('rainfall', 0),
            'location': weather_data.get('location', 'Unknown Location'),
            'city': weather_data.get('city'),
            'state': weather_data.get('state'),
            'country': weather_data.get('country'),
            'accuracy': weather_data.get('accuracy'),
            'altitude': weather_data.get('altitude'),
            'speed': weather_data.get('speed'),
            'description': weather_data.get('description', ''),
            'humidity_level': get_humidity_level(weather_data.get('humidity', 60)),
            'rainfall_level': get_rainfall_level(weather_data.get('rainfall', 0))
        }