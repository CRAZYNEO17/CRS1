import requests
import os
import pytz

from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


class LiveLocationManager:
    def __init__(self, openweather_api_key):
        """Initialize LiveLocationManager with OpenWeatherMap API key."""

        self.openweather_api_key = openweather_api_key or os.getenv(
            "OPENWEATHER_API_KEY"
        )


    def get_live_weather(self, lat, lon):
        """Fetch detailed live weather data from OpenWeatherMap API."""
        if not self.openweather_api_key:
            raise ValueError("OpenWeatherMap API key is missing.")

        print("openweather_api_key", self.openweather_api_key)
        print("lat", lat)
        print("lon", lon)

        try:
            # Current weather endpoint
            url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={self.openweather_api_key}&units=metric"
            response = requests.get(url)
            data = response.json()

            print("data", data)

            # Convert sunrise/sunset to local time (using Indian timezone)
            timezone = pytz.timezone("Asia/Kolkata")
            print("this is running 39")
            sunrise = (
                datetime.utcfromtimestamp(data["sys"]["sunrise"])
                .replace(tzinfo=pytz.utc)
                .astimezone(timezone)
                .strftime("%#I:%M %p")
            )
            print("this is running 46")
            sunset = (
                datetime.utcfromtimestamp(data["sys"]["sunset"])
                .replace(tzinfo=pytz.utc)
                .astimezone(timezone)
                .strftime("%#I:%M %p")
            )
            print("this is running 53") 
            

            print("return_data", {
                "temperature": data["main"]["temp"],
                "feels_like": data["main"]["feels_like"],
                "humidity": data["main"]["humidity"],
                "wind_speed": data["wind"]["speed"],
                "wind_direction": data["wind"]["deg"],
                "pressure": data["main"]["pressure"],
                "visibility_km": data.get("visibility", 10000) / 1000,  # default to 10 km
                "cloud_cover": data["clouds"]["all"],  # %
                "dew_point": None,  # Needs calculation or OneCall API
                "sunrise": sunrise,
                "sunset": sunset,
                "weather_description": data["weather"][0]["description"].capitalize(),
                "rainfall_mm": data.get("rain", {}).get("1h", 0),
            })
            return {
                "temperature": data["main"]["temp"],
                "feels_like": data["main"]["feels_like"],
                "humidity": data["main"]["humidity"],
                "wind_speed": data["wind"]["speed"],
                "wind_direction": data["wind"]["deg"],
                "pressure": data["main"]["pressure"],
                "visibility_km": data.get("visibility", 10000) / 1000,  # default to 10 km
                "cloud_cover": data["clouds"]["all"],  # %
                "dew_point": None,  # Needs calculation or OneCall API
                "sunrise": sunrise,
                "sunset": sunset,
                "weather_description": data["weather"][0]["description"].capitalize(),
                "rainfall_mm": data.get("rain", {}).get("1h", 0),
            }

        except Exception as e:
            print(f"Error fetching weather: {e}")
            return {}


    def get_live_soil_data(self, lat, lon):
        """Fetch live soil pH data using SoilGrids API v2."""
        try:
            url = (
                "https://rest.isric.org/soilgrids/v2.0/properties/query"
                f"?lon={lon}&lat={lat}"
                "&property=phh2o"
                "&depth=0-5cm"
                "&value=mean"
            )
            response = requests.get(url)
            print(f"[DEBUG] SoilGrids API URL: {url}")
            print(f"[DEBUG] SoilGrids API status code: {response.status_code}")
            data = response.json()
            print(f"[DEBUG] Full SoilGrids response: {data}")

            # Extract pH value for 0-5cm depth, mean
            phh2o = None
            try:
                phh2o = data["properties"]["phh2o"]["values"]["0-5cm"]["mean"]
            except Exception as e:
                print(f"[DEBUG] Error extracting pH: {e}")

            print(f"[DEBUG] Extracted soil pH: {phh2o}")
            return {"soil_ph": phh2o}
        except Exception as e:
            print(f"Error fetching soil data: {e}")
            return {}


if __name__ == "__main__":
    # Example coordinates: Pune, India
    lat = 18.5204
    lon = 73.8567

    # Pass your API key here or set OPENWEATHER_API_KEY as environment variable
    live_manager = LiveLocationManager(openweather_api_key="your_openweather_api_key")

    print("📡 Fetching Live Weather...")
    weather = live_manager.get_live_weather(lat, lon)
    print("Temperature:", weather.get("temperature"))
    print("Humidity:", weather.get("humidity"))
    print("Rainfall (last 1hr):", weather.get("rainfall"))
    print("Description:", weather.get("weather_description"))

    print("\n🧪 Fetching Live Soil Data...")
    soil = live_manager.get_live_soil_data(lat, lon)
    print("Soil pH:", soil.get("soil_ph"))
