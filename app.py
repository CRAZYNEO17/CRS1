# REST API Server for Agri Wiz
from flask import Flask, request, jsonify # type: ignore
from flask_cors import CORS # type: ignore
from agri_wiz import AgriWiz
from utils.weather_api import WeatherAPI
from utils.location_data import LiveLocationManager as LocationManager
import logging
import os
from dotenv import load_dotenv

# Load environment variables from .env.development when running in development
if os.getenv('FLASK_ENV') == 'development' or not os.getenv('FLASK_ENV'):
    # Try to load .env.development first, fallback to .env
    env_file = '.env.development' if os.path.exists('.env.development') else '.env'
    if os.path.exists(env_file):
        load_dotenv(env_file)
        print(f"Loaded environment variables from {env_file}")
    else:
        print("No environment file found, using system environment variables")
else:
    # In production, load .env or use system environment variables
    if os.path.exists('.env'):
        load_dotenv('.env')
        print("Loaded environment variables from .env")

# adding routes
from routes import schemes
from routes.schemes import schemes_bp
from routes.state_crops import state_crops_bp
from routes.recommendation import recommendation_bp
from routes.health import health_bp
from routes.crops import crops_bp
from routes.weather import weather_bp
from routes.yield_routes import yield_routes_bp


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

app = Flask(__name__)

# Configure Flask app from environment variables
app.config['DEBUG'] = os.getenv('FLASK_DEBUG', 'False').lower() in ('true', '1', 'yes')
app.config['ENV'] = os.getenv('FLASK_ENV', 'production')

# Display configuration info
print(f"Flask Environment: {app.config['ENV']}")
print(f"Debug Mode: {app.config['DEBUG']}")

# Enable CORS for all routes
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000", "http://127.0.0.1:3000"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Register the schemes blueprint
app.register_blueprint(schemes_bp)
app.register_blueprint(state_crops_bp)
app.register_blueprint(recommendation_bp)
app.register_blueprint(health_bp)
app.register_blueprint(crops_bp)
app.register_blueprint(weather_bp)
app.register_blueprint(yield_routes_bp)

print("something")

agri_wiz = AgriWiz()
weather_api = WeatherAPI()

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
