#!/usr/bin/env python
# Agri Wiz 1 - Enhanced Crop Recommendation System with Integrated GUI
# Incorporating Windows Location API, Weather Services, and Crop Recommendations

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import asyncio
import threading
import logging
import datetime
import json
import requests
import time
import os
from typing import Dict, Optional

try:
    import winsdk.windows.devices.geolocation as geo
    HAS_WINDOWS_LOCATION = True
except ImportError:
    HAS_WINDOWS_LOCATION = False

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
fh = logging.FileHandler('location_debug.log')
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

class IntegratedGPSService:
    """Integrated Windows GPS Location Service"""
    def __init__(self, loop=None):
        self.geolocator = None
        self.loop = loop or asyncio.get_event_loop()
        
    async def _init_geolocator(self) -> bool:
        """Initialize Windows Geolocator if not already initialized"""
        if not self.geolocator:
            try:
                if not HAS_WINDOWS_LOCATION:
                    logger.error("Windows Location API not available")
                    return False
                    
                # Try to create Geolocator instance
                self.geolocator = geo.Geolocator()
                self.geolocator.desired_accuracy = geo.PositionAccuracy.DEFAULT
                logger.info("Successfully created Geolocator instance")
                return True
            except Exception as e:
                logger.error(f"Error initializing Windows Geolocator: {str(e)}")
                return False
        return True

    async def get_location(self) -> Optional[Dict]:
        """Get location using Windows Location API"""
        try:
            logger.debug("Starting location detection")
            if await self._init_geolocator():
                try:
                    # Request location access with timeout
                    logger.debug("Requesting location access")
                    try:
                        async with asyncio.timeout(5) if hasattr(asyncio, 'timeout') else asyncio.TimeoutError(5):
                            status = await self.geolocator.request_access_async()
                            logger.debug(f"Location access status: {status}")
                    except AttributeError:
                        # Fallback for older Python versions
                        status = await asyncio.wait_for(self.geolocator.request_access_async(), timeout=5)
                    
                    if status == geo.GeolocationAccessStatus.ALLOWED:
                        try:
                            # Get position with timeout
                            logger.debug("Getting position")
                            try:
                                async with asyncio.timeout(10) if hasattr(asyncio, 'timeout') else asyncio.TimeoutError(10):
                                    position = await self.geolocator.get_geoposition_async()
                            except AttributeError:
                                # Fallback for older Python versions
                                position = await asyncio.wait_for(self.geolocator.get_geoposition_async(), timeout=10)
                            
                            if position and position.coordinate:
                                logger.info("Successfully obtained position")
                                return {
                                    "latitude": position.coordinate.latitude,
                                    "longitude": position.coordinate.longitude,
                                    "accuracy": position.coordinate.accuracy if hasattr(position.coordinate, 'accuracy') else None,
                                    "altitude": position.coordinate.altitude if hasattr(position.coordinate, 'altitude') else None,
                                    "source": "windows_gps",
                                    "timestamp": time.time()
                                }
                            else:
                                logger.error("No coordinate data available")
                                return None
                        except asyncio.TimeoutError:
                            logger.error("Timeout while getting position")
                            return None
                        except Exception as e:
                            logger.error(f"Error getting position: {e}")
                            return None
                    else:
                        logger.error(f"Location access not allowed. Status: {status}")
                        return None
                except asyncio.TimeoutError:
                    logger.error("Timeout while requesting location access")
                    return None
                except Exception as e:
                    logger.error(f"Error accessing location: {e}")
                    return None
            return None
        except Exception as e:
            logger.error(f"Error in get_location: {e}")
            return None

    async def _get_ip_location(self) -> Dict:
        """Get location based on IP address as fallback"""
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
                logger.warning(f"Error with {url}: {e}")
                continue

        logger.error("All IP geolocation services failed")
        return None

    async def get_location_name(self, lat: float, lon: float) -> Dict:
        """Get location name from coordinates using OpenStreetMap Nominatim"""
        try:
            params = {
                'lat': lat,
                'lon': lon,
                'format': 'json'
            }
            
            headers = {
                'User-Agent': 'AgriWiz/1.0',
                'Accept-Language': 'en-US,en;q=0.5'
            }
            
            response = requests.get(
                "https://nominatim.openstreetmap.org/reverse",
                params=params,
                headers=headers,
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                address = data.get('address', {})
                
                loc_name = (
                    address.get('city') or
                    address.get('town') or
                    address.get('village') or
                    address.get('suburb') or
                    address.get('county') or
                    address.get('state') or
                    address.get('country')
                )
                
                return {
                    'city': loc_name,
                    'state': address.get('state', ''),
                    'country': address.get('country', ''),
                    'display_name': data.get('display_name', f"{lat:.4f}, {lon:.4f}")
                }
        except Exception as e:
            logger.error(f"Error getting location name: {e}")
        
        return {
            'city': f"{lat:.4f}, {lon:.4f}",
            'state': '',
            'country': '',
            'display_name': f"{lat:.4f}, {lon:.4f}"
        }

class WeatherService:
    """Integrated Weather Service"""
    def __init__(self):
        self.cache_file = "weather_cache.json"
        self.cache_duration = 3600  # Cache weather data for 1 hour
        self.weather_cache = self._load_cache()
        self.settings = Settings()
        self.api_key = self.settings.get("openweathermap_api_key", "")
        self.units = self.settings.get("weather_units", "metric")

    def _load_cache(self) -> Dict:
        """Load the weather cache from file"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, "r") as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading weather cache: {e}")
        return {}

    def _save_cache(self):
        """Save weather data to cache"""
        try:
            with open(self.cache_file, "w") as f:
                json.dump(self.weather_cache, f)
        except Exception as e:
            logger.error(f"Error saving weather cache: {e}")

    def _is_cache_valid(self, key: str) -> bool:
        """Check if cache for a location is still valid"""
        if key in self.weather_cache:
            timestamp = self.weather_cache[key].get("timestamp", 0)
            return (time.time() - timestamp) < self.cache_duration
        return False

    async def get_weather(self, lat: float, lon: float) -> Dict:
        """Get weather data for coordinates using OpenWeatherMap API"""
        cache_key = f"{lat:.4f},{lon:.4f}"
        
        if self._is_cache_valid(cache_key):
            return self.weather_cache[cache_key]

        try:
            if not self.api_key:
                # Return mock data if no API key is configured
                return self._get_mock_weather(lat, lon)

            # Real OpenWeatherMap API call
            url = f"https://api.openweathermap.org/data/2.5/weather"
            params = {
                "lat": lat,
                "lon": lon,
                "appid": self.api_key,
                "units": self.units
            }
            
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: requests.get(url, params=params, timeout=10)
            )
            
            if response.status_code == 200:
                data = response.json()
                weather_data = {
                    "temperature": data["main"]["temp"],
                    "humidity": data["main"]["humidity"],
                    "description": data["weather"][0]["description"],
                    "wind_speed": data["wind"]["speed"],
                    "pressure": data["main"]["pressure"],
                    "timestamp": time.time()
                }
                
                # Cache the result
                self.weather_cache[cache_key] = weather_data
                self._save_cache()
                
                return weather_data
            else:
                logger.error(f"Weather API error: {response.status_code}")
                return self._get_mock_weather(lat, lon)
            
        except Exception as e:
            logger.error(f"Error getting weather: {e}")
            return self._get_mock_weather(lat, lon)

    def _get_mock_weather(self, lat: float, lon: float) -> Dict:
        """Generate mock weather data when API is unavailable"""
        current_hour = datetime.datetime.now().hour
        temp_base = 20 + (current_hour - 12) * 0.5
        return {
            "temperature": round(temp_base + (hash(str(lat)) % 10) - 5, 1),
            "humidity": round(60 + (hash(str(lon)) % 30), 0),
            "description": "Weather API not configured - Using mock data",
            "timestamp": time.time()
        }

class Settings:
    """Manages application settings and persistence"""
    def __init__(self):
        self.settings_file = "agri_wiz_settings.json"
        self.settings = self._load_settings()
    
    def _load_settings(self) -> Dict:
        """Load settings from JSON file"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, "r") as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading settings: {e}")
        return {
            "last_location": None,
            "use_windows_location": True,
            "weather_update_interval": 3600,
            "last_window_size": "1200x800",
            "openweathermap_api_key": "",  # Add default empty API key
            "weather_units": "metric"  # Add default units
        }
    
    def save_settings(self):
        """Save current settings to file"""
        try:
            with open(self.settings_file, "w") as f:
                json.dump(self.settings, f)
        except Exception as e:
            logger.error(f"Error saving settings: {e}")
    
    def get(self, key: str, default=None):
        """Get a setting value"""
        return self.settings.get(key, default)
    
    def set(self, key: str, value):
        """Set a setting value and save"""
        self.settings[key] = value
        self.save_settings()

class AgriWizGUI:
    def __init__(self):
        self.settings = Settings()
        
        self.root = tk.Tk()
        self.root.title("Agri Wiz - Crop Recommendation System")
        
        # Restore last window size
        last_size = self.settings.get("last_window_size", "1200x800")
        self.root.geometry(last_size)
        
        # Initialize asyncio event loop for background tasks
        self.loop = asyncio.new_event_loop()
        self.async_thread = threading.Thread(target=self._run_event_loop, daemon=True)
        self.async_thread.start()
        
        # Initialize GPS Service with settings
        self.gps_service = IntegratedGPSService(loop=self.loop)
        
        # Initialize Weather Service
        self.weather_service = WeatherService()
        
        # Initialize Agri Wiz backend
        from agri_wiz import AgriWiz
        self.agri_wiz = AgriWiz()
        
        # Additional variables for recommendations
        self.soil_type_var = tk.StringVar()
        self.climate_var = tk.StringVar()
        self.season_var = tk.StringVar()
        self.rainfall_var = tk.StringVar()
        self.humidity_var = tk.StringVar()
        self.soil_fertility_var = tk.StringVar()
        self.soil_ph_var = tk.StringVar()
        self.temperature_var = tk.StringVar()
        
        # Create main notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill='both', padx=5, pady=5)
        
        # Initialize variables
        self.location_var = tk.StringVar()
        last_location = self.settings.get("last_location")
        if last_location:
            self.location_var.set(last_location)
            
        self.status_var = tk.StringVar()
        self.weather_data = {}
        
        # Create tabs
        self.create_location_tab()
        self.create_recommendation_tab()
        self.create_weather_tab()
        self.create_settings_tab()
        
        # Add status bar
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var)
        self.status_bar.pack(fill='x', padx=5, pady=2)
        
        # Setup styles
        self.setup_styles()
        
        # Bind window resize event
        self.root.bind('<Configure>', self._on_window_resize)

    def _run_event_loop(self):
        """Run the asyncio event loop in a separate thread"""
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def run_async(self, coro):
        """Run an async coroutine from the GUI thread"""
        if not self.loop or not self.loop.is_running():
            return None
            
        future = asyncio.run_coroutine_threadsafe(coro, self.loop)
        try:
            return future.result(timeout=10)
        except asyncio.TimeoutError:
            self.status_var.set("Operation timed out")
            return None
        except Exception as e:
            self.status_var.set(f"Operation failed: {str(e)}")
            return None

    def setup_styles(self):
        """Configure styles for the GUI"""
        style = ttk.Style()
        style.configure('Header.TLabel', font=('Helvetica', 16, 'bold'))
        style.configure('Info.TLabel', font=('Helvetica', 10))
        style.configure('Success.TLabel', foreground='green')
        style.configure('Error.TLabel', foreground='red')

    def create_location_tab(self):
        """Create the location detection tab"""
        location_frame = ttk.Frame(self.notebook)
        self.notebook.add(location_frame, text="Location")

        # Location detection section
        detect_frame = ttk.LabelFrame(location_frame, text="Location Detection", padding=10)
        detect_frame.pack(fill='x', padx=5, pady=5)

        ttk.Label(detect_frame, text="Current Location:").pack(side='left', padx=5)
        ttk.Entry(detect_frame, textvariable=self.location_var, width=40).pack(side='left', padx=5)
        ttk.Button(detect_frame, text="Detect Location", 
                  command=lambda: self.run_async(self.detect_location())
        ).pack(side='left', padx=5)

        # Location details display
        self.location_text = scrolledtext.ScrolledText(location_frame, height=10)
        self.location_text.pack(fill='both', expand=True, padx=5, pady=5)

    async def detect_location(self):
        """Detect current location using Windows Location API with IP fallback"""
        try:
            self.status_var.set("Detecting location...")
            self.root.update_idletasks()
            
            # Try Windows Location API first
            location = await self.gps_service.get_location()
            
            # If Windows Location fails, try IP-based location
            if not location:
                self.status_var.set("Windows Location unavailable, trying IP-based location...")
                self.root.update_idletasks()
                location = await self.gps_service._get_ip_location()
                
            if not location:
                raise Exception(
                    "Could not detect location.\n\n"
                    "Please ensure:\n"
                    "1. Location services are enabled in Windows Settings\n"
                    "2. This app has permission to access location\n"
                    "3. You have an active internet connection"
                )

            # Get location name
            location_info = await self.gps_service.get_location_name(
                location['latitude'],
                location['longitude']
            )

            # Update GUI
            loc_display = location_info['display_name']
            self.location_var.set(loc_display)
            
            # Update location details
            self.location_text.delete(1.0, tk.END)
            self.location_text.insert(tk.END, f"""Location Details:
-------------------
Display Name: {location_info['display_name']}
Coordinates: {location['latitude']:.6f}, {location['longitude']:.6f}
City: {location_info['city']}
State: {location_info['state']}
Country: {location_info['country']}
Accuracy: {location.get('accuracy', 'N/A')} meters
Source: {location['source']}
""")

            self.status_var.set(f"Location detected: {loc_display}")
            
            # Update weather after location detection
            await self.update_weather(location['latitude'], location['longitude'])
            
        except Exception as e:
            error_msg = str(e)
            self.status_var.set(f"Error detecting location: {error_msg}")
            messagebox.showerror("Location Detection Error", error_msg)

    async def update_weather(self, lat=None, lon=None):
        """Update weather information display"""
        try:
            if lat is None or lon is None:
                # Try to parse coordinates from location var
                loc = self.location_var.get()
                if ',' in loc:
                    try:
                        parts = loc.replace('(', '').replace(')', '').split(',')
                        lat = float(parts[0])
                        lon = float(parts[1])
                    except:
                        raise ValueError("Please detect location first")
                else:
                    raise ValueError("Please detect location first")

            self.status_var.set("Fetching weather data...")
            weather_data = await self.weather_service.get_weather(lat, lon)
            
            if weather_data:
                self.weather_text.delete(1.0, tk.END)
                self.weather_text.insert(tk.END, f"""Current Weather Conditions:
-------------------------
Temperature: {weather_data['temperature']}°C
Humidity: {weather_data['humidity']}%
Description: {weather_data['description']}
Last Updated: {datetime.datetime.fromtimestamp(weather_data['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}
""")
                self.status_var.set("Weather data updated successfully")
            else:
                raise Exception("Could not fetch weather data")
                
        except Exception as e:
            self.status_var.set(f"Error updating weather: {str(e)}")
            messagebox.showerror("Error", f"Could not update weather: {str(e)}")

    def create_recommendation_tab(self):
        """Create the crop recommendation tab"""
        rec_frame = ttk.Frame(self.notebook)
        self.notebook.add(rec_frame, text="Recommendations")

        # Location-based recommendations
        loc_frame = ttk.LabelFrame(rec_frame, text="Location-Based Recommendations", padding=10)
        loc_frame.pack(fill='x', padx=5, pady=5)

        # Location entry
        loc_entry_frame = ttk.Frame(loc_frame)
        loc_entry_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(loc_entry_frame, text="Location:").pack(side='left', padx=5)
        ttk.Entry(loc_entry_frame, textvariable=self.location_var, width=40).pack(side='left', padx=5)
        ttk.Button(loc_entry_frame, text="Detect Location", 
                  command=lambda: self.run_async(self.detect_location())
        ).pack(side='left', padx=5)
        ttk.Button(loc_entry_frame, text="Get Recommendations", 
                  command=self.get_location_recommendations
        ).pack(side='left', padx=5)

        # Manual input recommendations
        manual_frame = ttk.LabelFrame(rec_frame, text="Manual Input Recommendations", padding=10)
        manual_frame.pack(fill='x', padx=5, pady=5)

        # Create grid for input fields
        params = [
            ("Soil Type:", self.soil_type_var, ["clay", "loamy", "sandy", "black soil"]),
            ("Climate:", self.climate_var, ["tropical", "subtropical", "temperate"]),
            ("Season:", self.season_var, ["summer", "winter", "rainy", "spring", "fall"]),
            ("Rainfall:", self.rainfall_var, ["low", "medium", "high"]),
            ("Humidity:", self.humidity_var, ["low", "medium", "high"]),
            ("Soil Fertility:", self.soil_fertility_var, ["low", "medium", "high"])
        ]

        for i, (label, var, values) in enumerate(params):
            ttk.Label(manual_frame, text=label).grid(row=i, column=0, sticky='w', padx=5, pady=2)
            ttk.Combobox(manual_frame, textvariable=var, values=values).grid(row=i, column=1, sticky='ew', padx=5, pady=2)

        # Optional parameters
        opt_frame = ttk.LabelFrame(manual_frame, text="Optional Parameters", padding=10)
        opt_frame.grid(row=len(params), column=0, columnspan=2, sticky='ew', padx=5, pady=5)

        ttk.Label(opt_frame, text="Soil pH:").grid(row=0, column=0, sticky='w', padx=5, pady=2)
        ttk.Entry(opt_frame, textvariable=self.soil_ph_var).grid(row=0, column=1, sticky='ew', padx=5, pady=2)

        ttk.Label(opt_frame, text="Temperature (°C):").grid(row=1, column=0, sticky='w', padx=5, pady=2)
        ttk.Entry(opt_frame, textvariable=self.temperature_var).grid(row=1, column=1, sticky='ew', padx=5, pady=2)

        # Auto-fill current season button
        ttk.Button(manual_frame, text="Use Current Season",
                  command=self.set_current_season
        ).grid(row=len(params)+1, column=0, columnspan=2, pady=5)

        # Get recommendations button
        ttk.Button(manual_frame, text="Get Recommendations",
                  command=self.get_manual_recommendations
        ).grid(row=len(params)+2, column=0, columnspan=2, pady=5)

        # Results display
        results_frame = ttk.LabelFrame(rec_frame, text="Recommendations", padding=10)
        results_frame.pack(fill='both', expand=True, padx=5, pady=5)

        self.recommendations_text = scrolledtext.ScrolledText(results_frame)
        self.recommendations_text.pack(fill='both', expand=True)

    def set_current_season(self):
        """Set the current season based on location"""
        if self.location_var.get():
            season = self.agri_wiz.location_manager.get_current_season_for_location(self.location_var.get())
            if not season:
                season = self.agri_wiz.get_current_season()
            self.season_var.set(season)
        else:
            season = self.agri_wiz.get_current_season()
            self.season_var.set(season)
        self.status_var.set(f"Current season set to: {season}")

    def get_location_recommendations(self):
        """Get crop recommendations based on location"""
        try:
            if not self.location_var.get():
                raise ValueError("Please enter or detect a location first")

            # Get recommendations
            recommendations, details = self.agri_wiz.get_recommendations_by_location(
                self.location_var.get(),
                self.humidity_var.get() or None,
                self.soil_fertility_var.get() or None,
                self.soil_ph_var.get() or None,
                self.temperature_var.get() or None
            )

            if not recommendations:
                raise ValueError("No recommendations found for this location")

            # Display results
            self.recommendations_text.delete(1.0, tk.END)
            self.recommendations_text.insert(tk.END, "Location Details:\n")
            self.recommendations_text.insert(tk.END, "-" * 50 + "\n")
            for key, value in details.items():
                if value:  # Only show non-empty values
                    self.recommendations_text.insert(tk.END, f"{key.replace('_', ' ').title()}: {value}\n")

            self.recommendations_text.insert(tk.END, "\nRecommended Crops:\n")
            self.recommendations_text.insert(tk.END, "-" * 50 + "\n")
            for i, crop in enumerate(recommendations, 1):
                self.recommendations_text.insert(tk.END, f"{i}. {crop['crop_name']}\n")
                self.recommendations_text.insert(tk.END, f"   Water needs: {crop['water_needs']}\n")
                if 'humidity_preference' in crop:
                    self.recommendations_text.insert(tk.END, f"   Humidity preference: {crop['humidity_preference']}\n")
                if 'soil_fertility' in crop:
                    self.recommendations_text.insert(tk.END, f"   Soil fertility needs: {crop['soil_fertility']}\n")
                self.recommendations_text.insert(tk.END, "\n")

            self.status_var.set("Recommendations generated successfully")

        except Exception as e:
            self.status_var.set(f"Error getting recommendations: {str(e)}")
            messagebox.showerror("Error", str(e))

    def get_manual_recommendations(self):
        """Get crop recommendations based on manual input"""
        try:
            # Validate required fields
            required = {
                'soil_type': self.soil_type_var.get(),
                'climate': self.climate_var.get(),
                'season': self.season_var.get()
            }

            missing = [k for k, v in required.items() if not v]
            if missing:
                raise ValueError(f"Please fill in required fields: {', '.join(missing)}")

            # Get recommendations
            recommendations, scored_recommendations = self.agri_wiz.get_recommendations(
                self.soil_type_var.get(),
                self.climate_var.get(),
                self.season_var.get(),
                self.rainfall_var.get() or None,
                self.humidity_var.get() or None,
                self.soil_fertility_var.get() or None,
                self.soil_ph_var.get() or None,
                self.temperature_var.get() or None
            )

            if not recommendations:
                self.status_var.set("No exact matches found, showing alternatives")
                self.recommendations_text.delete(1.0, tk.END)
                self.recommendations_text.insert(tk.END, "No crops match your exact criteria. Consider these alternatives:\n\n")
                for scored in scored_recommendations[:5]:  # Show top 5 alternatives
                    crop = scored['crop']
                    self.recommendations_text.insert(tk.END, f"{crop['crop_name']} - {scored['match_percentage']:.0f}% match\n")
                    self.recommendations_text.insert(tk.END, f"   Water needs: {crop['water_needs']}\n")
                    if 'humidity_preference' in crop:
                        self.recommendations_text.insert(tk.END, f"   Humidity preference: {crop['humidity_preference']}\n")
                    if 'soil_fertility' in crop:
                        self.recommendations_text.insert(tk.END, f"   Soil fertility needs: {crop['soil_fertility']}\n")
                    self.recommendations_text.insert(tk.END, "\n")
                return

            # Display results
            self.recommendations_text.delete(1.0, tk.END)
            self.recommendations_text.insert(tk.END, "Input Parameters:\n")
            self.recommendations_text.insert(tk.END, "-" * 50 + "\n")
            self.recommendations_text.insert(tk.END, f"Soil Type: {self.soil_type_var.get()}\n")
            self.recommendations_text.insert(tk.END, f"Climate: {self.climate_var.get()}\n")
            self.recommendations_text.insert(tk.END, f"Season: {self.season_var.get()}\n")
            if self.rainfall_var.get():
                self.recommendations_text.insert(tk.END, f"Rainfall: {self.rainfall_var.get()}\n")
            if self.humidity_var.get():
                self.recommendations_text.insert(tk.END, f"Humidity: {self.humidity_var.get()}\n")
            if self.soil_fertility_var.get():
                self.recommendations_text.insert(tk.END, f"Soil Fertility: {self.soil_fertility_var.get()}\n")

            self.recommendations_text.insert(tk.END, "\nRecommended Crops:\n")
            self.recommendations_text.insert(tk.END, "-" * 50 + "\n")
            for i, crop in enumerate(recommendations, 1):
                match_info = next((s for s in scored_recommendations if s['crop'] == crop), None)
                match_percentage = match_info['match_percentage'] if match_info else 100

                self.recommendations_text.insert(tk.END, f"{i}. {crop['crop_name']} - {match_percentage:.0f}% match\n")
                self.recommendations_text.insert(tk.END, f"   Water needs: {crop['water_needs']}\n")
                if 'humidity_preference' in crop:
                    self.recommendations_text.insert(tk.END, f"   Humidity preference: {crop['humidity_preference']}\n")
                if 'soil_fertility' in crop:
                    self.recommendations_text.insert(tk.END, f"   Soil fertility needs: {crop['soil_fertility']}\n")
                self.recommendations_text.insert(tk.END, "\n")

            self.status_var.set("Recommendations generated successfully")

        except Exception as e:
            self.status_var.set(f"Error getting recommendations: {str(e)}")
            messagebox.showerror("Error", str(e))

    def create_weather_tab(self):
        """Create the weather monitoring tab"""
        weather_frame = ttk.Frame(self.notebook)
        self.notebook.add(weather_frame, text="Weather")

        # Weather info display
        info_frame = ttk.LabelFrame(weather_frame, text="Current Weather", padding=10)
        info_frame.pack(fill='x', padx=5, pady=5)

        # Location frame
        loc_frame = ttk.Frame(info_frame)
        loc_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(loc_frame, text="Location:").pack(side='left', padx=5)
        ttk.Entry(loc_frame, textvariable=self.location_var, width=40).pack(side='left', padx=5)
        ttk.Button(loc_frame, text="Detect Location", 
                  command=lambda: self.run_async(self.detect_location())
        ).pack(side='left', padx=5)
        ttk.Button(loc_frame, text="Update Weather", 
                  command=lambda: self.run_async(self.update_weather())
        ).pack(side='left', padx=5)

        # Weather display
        self.weather_text = scrolledtext.ScrolledText(weather_frame, height=10)
        self.weather_text.pack(fill='both', expand=True, padx=5, pady=5)

    def create_settings_tab(self):
        """Create the settings tab"""
        settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(settings_frame, text="Settings")

        # Weather API settings
        api_frame = ttk.LabelFrame(settings_frame, text="OpenWeatherMap API Settings", padding=10)
        api_frame.pack(fill='x', padx=5, pady=5)

        # API Key entry
        ttk.Label(api_frame, text="API Key:").pack(anchor='w', padx=5, pady=2)
        self.api_key = tk.StringVar(value=self.settings.get("openweathermap_api_key", ""))
        api_key_entry = ttk.Entry(api_frame, textvariable=self.api_key, width=40)
        api_key_entry.pack(fill='x', padx=5, pady=2)
        
        # Units selection
        ttk.Label(api_frame, text="Units:").pack(anchor='w', padx=5, pady=2)
        self.units = tk.StringVar(value=self.settings.get("weather_units", "metric"))
        units_frame = ttk.Frame(api_frame)
        units_frame.pack(fill='x', padx=5, pady=2)
        ttk.Radiobutton(units_frame, text="Metric (°C)", value="metric", variable=self.units).pack(side='left', padx=5)
        ttk.Radiobutton(units_frame, text="Imperial (°F)", value="imperial", variable=self.units).pack(side='left', padx=5)

        # Location settings
        loc_frame = ttk.LabelFrame(settings_frame, text="Location Settings", padding=10)
        loc_frame.pack(fill='x', padx=5, pady=5)

        # Windows Location toggle
        self.use_windows_location = tk.BooleanVar(value=self.settings.get("use_windows_location", True))
        ttk.Checkbutton(
            loc_frame, 
            text="Use Windows Location Services (if available)", 
            variable=self.use_windows_location,
            command=self._on_location_setting_changed
        ).pack(anchor='w', padx=5, pady=2)

        # Weather settings
        weather_frame = ttk.LabelFrame(settings_frame, text="Weather Update Settings", padding=10)
        weather_frame.pack(fill='x', padx=5, pady=5)

        # Update interval
        ttk.Label(weather_frame, text="Weather update interval:").pack(anchor='w', padx=5, pady=2)
        self.update_interval = tk.StringVar(value=str(self.settings.get("weather_update_interval", 3600)))
        interval_frame = ttk.Frame(weather_frame)
        interval_frame.pack(fill='x', padx=5, pady=2)
        ttk.Entry(interval_frame, textvariable=self.update_interval, width=10).pack(side='left', padx=5)
        ttk.Label(interval_frame, text="seconds").pack(side='left')
        
        # Save button
        ttk.Button(
            settings_frame, 
            text="Save Settings",
            command=self._save_settings
        ).pack(pady=10)

    def _on_location_setting_changed(self):
        """Handle location setting changes"""
        self.settings.set("use_windows_location", self.use_windows_location.get())

    def _save_settings(self):
        """Save all settings"""
        try:
            # Validate update interval
            try:
                interval = int(self.update_interval.get())
                if interval < 60:
                    raise ValueError("Update interval must be at least 60 seconds")
                self.settings.set("weather_update_interval", interval)
            except ValueError as e:
                messagebox.showerror("Invalid Input", str(e))
                return

            # Save current location if available
            if self.location_var.get():
                self.settings.set("last_location", self.location_var.get())

            # Save API key and units
            self.settings.set("openweathermap_api_key", self.api_key.get())
            self.settings.set("weather_units", self.units.get())

            self.settings.save_settings()
            self.status_var.set("Settings saved successfully")
            messagebox.showinfo("Success", "Settings saved successfully")
        except Exception as e:
            self.status_var.set("Error saving settings")
            messagebox.showerror("Error", f"Could not save settings: {str(e)}")

    def _on_window_resize(self, event):
        """Handle window resize event"""
        if event.widget == self.root:
            size = f"{self.root.winfo_width()}x{self.root.winfo_height()}"
            self.settings.set("last_window_size", size)

    def on_closing(self):
        """Clean up when the window is closed"""
        # Save current location if available
        if self.location_var.get():
            self.settings.set("last_location", self.location_var.get())
            
        if self.loop and self.loop.is_running():
            self.loop.call_soon_threadsafe(self.loop.stop)
        self.root.destroy()

    def run(self):
        """Start the GUI application"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        try:
            self.root.mainloop()
        finally:
            if self.loop and self.loop.is_running():
                self.loop.call_soon_threadsafe(self.loop.stop)
                self.async_thread.join(timeout=1)

def main():
    """Main entry point"""
    app = AgriWizGUI()
    app.run()

if __name__ == "__main__":
    main()