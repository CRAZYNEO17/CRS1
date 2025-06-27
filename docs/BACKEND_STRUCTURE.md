# Agri Wiz Backend - Application Structure

## Overview
The Agri Wiz backend is a Python-based agricultural recommendation system that provides crop recommendations, weather integration, government scheme information, and yield estimation capabilities. The application follows a modular architecture with clear separation of concerns.

## Directory Structure

```
backend/
├── agri_wiz.py                 # Main application orchestrator
├── app.py                      # Flask web server and REST API
├── setup.py                    # Environment setup and dependency installation
├── organize_data.py            # Data organization and migration script
├── requirements.txt            # Python dependencies
├── .env.development           # Development environment variables
├── .env                       # Production environment variables
├── docs/                      # Documentation directory
│   ├── README.md             # Documentation index
│   ├── BACKEND_STRUCTURE.md  # This file - application architecture
│   ├── API_DOCUMENTATION.md  # RESTful API reference
│   └── Code Citations.md     # Development references and credits
│
├── data/                      # Data storage directory
│   ├── raw/                   # Raw data files
│   │   ├── crop_data.csv      # Crop information database
│   │   ├── agricultural_schemes.json  # Government schemes data
│   │   └── location_data.json # Location and geographical data
│   └── processed/             # Processed and cached data
│       ├── weather_cache.json # Weather API response cache
│       └── models/            # Machine learning models
│           ├── rice_model.joblib
│           ├── wheat_model.joblib
│           └── *_scaler.joblib
│
├── utils/                     # Utility modules and helpers
│   ├── __init__.py           # Package initialization and exports
│   ├── location_data.py      # Location management and geographical data
│   ├── scheme_manager.py     # Government schemes and subsidies
│   ├── weather_api.py        # Weather API integration and GPS services
│   ├── weather_helpers.py    # Weather utility functions
│   └── yield_estimation.py   # ML-based crop yield estimation
│
├── routes/                    # Flask API route handlers
│   ├── __init__.py
│   ├── schemes.py            # Government schemes API endpoints
│   ├── state_crops.py        # State-specific crop recommendations
│   └── recommendation.py     # Main recommendation API endpoints
│
├── tests/                     # Test files and test data
│   ├── __init__.py
│   ├── test_agri_wiz.py
│   ├── test_weather_api.py
│   └── test_recommendations.py
│
├── __pycache__/              # Python bytecode cache
├── .venv/                    # Virtual environment (development)
├── venv/                     # Alternative virtual environment
└── .vscode/                  # VS Code configuration
```

## Core Components

### 1. Main Application Layer

#### `agri_wiz.py`
- **Purpose**: Central business logic orchestrator
- **Key Features**:
  - Crop recommendation engine
  - Location-based analysis
  - Integration with all utility modules
  - CLI interface for standalone operation
- **Main Classes**: `AgriWiz`
- **Dependencies**: All utility modules

#### `app.py`
- **Purpose**: Flask web server and REST API
- **Key Features**:
  - RESTful API endpoints
  - CORS configuration
  - Health check endpoints
  - Integration with route handlers
- **Port**: 5000 (configurable via environment)
- **Dependencies**: Flask, Flask-CORS, route blueprints

### 2. Utility Layer (`utils/`)

#### `location_data.py`
- **Purpose**: Geographical data management
- **Key Features**:
  - Location information lookup
  - Soil type and climate data
  - Regional agricultural parameters
- **Main Classes**: `LocationManager`

#### `scheme_manager.py`
- **Purpose**: Government schemes and subsidies
- **Key Features**:
  - Scheme recommendations by crop and location
  - Subsidy information lookup
  - Eligibility checking
- **Main Classes**: `SchemeManager`
- **Data Source**: `agricultural_schemes.json`

#### `weather_api.py`
- **Purpose**: Weather data integration
- **Key Features**:
  - Real-time weather data fetching
  - GPS location services (Windows Location API)
  - Weather-based recommendations
  - Caching mechanism
- **Main Classes**: `WeatherAPI`, `WeatherService`, `GPSConfig`
- **External APIs**: OpenWeatherMap, IP geolocation services

#### `weather_helpers.py`
- **Purpose**: Weather utility functions
- **Key Features**:
  - Humidity level categorization
  - Rainfall level assessment
  - Weather condition parsing
- **Functions**: `get_humidity_level()`, `get_rainfall_level()`

#### `yield_estimation.py`
- **Purpose**: ML-based crop yield prediction
- **Key Features**:
  - Random Forest regression models
  - Feature scaling and preprocessing
  - Model training and updating
  - Yield optimization suggestions
- **Main Classes**: `YieldEstimator`
- **Dependencies**: scikit-learn, numpy, joblib

### 3. API Layer (`routes/`)

#### `recommendation.py`
- **Purpose**: Core recommendation API endpoints
- **Endpoints**:
  - `GET /api/recommendations` - Location-based crop recommendations
  - `GET /api/recommendation/crop/<crop_name>` - Crop details
  - `GET /api/recommendation/calendar/<location>` - Crop calendar
  - `GET /api/recommendation/season` - Current season info

#### `schemes.py`
- **Purpose**: Government schemes API
- **Endpoints**:
  - `GET /api/schemes` - List all schemes
  - `GET /api/schemes/<scheme_name>` - Specific scheme details
  - `GET /api/schemes/state/<state>` - State-specific schemes

#### `state_crops.py`
- **Purpose**: State-specific crop information
- **Endpoints**:
  - `GET /api/state-crops/<state>` - Crops suitable for state
  - `GET /api/states` - List of supported states

### 4. Data Layer (`data/`)

#### Raw Data (`data/raw/`)
- **`crop_data.csv`**: Comprehensive crop database with growing parameters
- **`agricultural_schemes.json`**: Government schemes, subsidies, and policies
- **`location_data.json`**: Geographical and climatic data by location

#### Processed Data (`data/processed/`)
- **`weather_cache.json`**: Cached weather API responses
- **`models/`**: Trained ML models for yield estimation

### 5. Configuration and Setup

#### `setup.py`
- **Purpose**: Environment setup automation
- **Features**:
  - Virtual environment creation
  - Dependency installation
  - Platform-specific configurations

#### `organize_data.py`
- **Purpose**: Data migration and organization
- **Features**:
  - Move data files to appropriate directories
  - Create directory structure
  - Data validation

#### Environment Files
- **`.env.development`**: Development environment variables
- **`.env`**: Production environment variables
- **Variables**: Database URLs, API keys, debug flags

## Data Flow Architecture

```
User Request
    ↓
Flask App (app.py)
    ↓
Route Handler (routes/)
    ↓
AgriWiz Core (agri_wiz.py)
    ↓
Utility Modules (utils/)
    ↓
Data Sources (data/)
    ↓
External APIs (Weather, etc.)
    ↓
Response Processing
    ↓
JSON Response to User
```

## Key Features

### 1. Crop Recommendation System
- Multi-parameter analysis (soil, climate, season, humidity, etc.)
- Location-based recommendations
- Real-time weather integration
- Scoring algorithm with match percentages

### 2. Weather Integration
- Real-time weather data fetching
- GPS location detection (Windows Location API)
- IP-based location fallback
- Weather-based farming recommendations

### 3. Government Schemes
- Comprehensive scheme database
- State-specific recommendations
- Subsidy information
- Eligibility checking

### 4. Yield Estimation
- Machine learning-based predictions
- Environmental factor analysis
- Optimization suggestions
- Model training and updates

### 5. RESTful API
- Clean endpoint design
- JSON responses
- Error handling
- CORS support for frontend integration

## Technology Stack

### Backend Framework
- **Flask**: Web framework
- **Flask-CORS**: Cross-origin resource sharing

### Data Processing
- **pandas**: Data manipulation
- **numpy**: Numerical computing
- **scikit-learn**: Machine learning

### External Integrations
- **requests**: HTTP client for API calls
- **OpenWeatherMap API**: Weather data
- **Windows Location API**: GPS services

### Development Tools
- **python-dotenv**: Environment variable management
- **logging**: Application logging
- **csv/json**: Data serialization

## API Endpoints Summary

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/health` | GET | Health check |
| `/api/crops` | GET/POST | Crop management |
| `/api/recommendations` | GET | Location-based recommendations |
| `/api/recommendation/crop/<name>` | GET | Crop details |
| `/api/recommendation/calendar/<location>` | GET | Crop calendar |
| `/api/schemes` | GET | Government schemes |
| `/api/schemes/state/<state>` | GET | State-specific schemes |
| `/api/state-crops/<state>` | GET | State crop recommendations |
| `/api/weather/<location>` | GET | Weather data |
| `/api/yield/estimate` | POST | Yield estimation |

## Environment Setup

### Development
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows
.\venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run setup script
python setup.py

# Start development server
python app.py
```

### Production
```bash
# Set environment variables
export FLASK_ENV=production
export OPENWEATHERMAP_API_KEY=your_api_key

# Run with production WSGI server
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## Security Considerations

1. **API Keys**: Stored in environment variables
2. **CORS**: Configured for specific frontend origins
3. **Input Validation**: Parameter validation in API endpoints
4. **Error Handling**: Graceful error responses without exposing internals

## Performance Optimizations

1. **Caching**: Weather data caching to reduce API calls
2. **Model Loading**: ML models loaded once at startup
3. **Data Processing**: Efficient pandas operations for large datasets
4. **API Response**: Optimized JSON serialization

## Future Enhancements

1. **Database Integration**: Replace CSV/JSON with PostgreSQL/MongoDB
2. **Authentication**: User management and API authentication
3. **Real-time Updates**: WebSocket integration for live data
4. **Microservices**: Split into smaller, specialized services
5. **Containerization**: Docker deployment support
6. **API Documentation**: OpenAPI/Swagger integration
7. **Monitoring**: Application performance monitoring
8. **Testing**: Comprehensive test coverage

## Dependencies

### Core Dependencies
```
Flask>=2.0.0
Flask-CORS>=3.0.0
pandas>=1.3.0
numpy>=1.21.0
scikit-learn>=1.0.0
requests>=2.25.0
python-dotenv>=0.19.0
joblib>=1.1.0
```

### Development Dependencies
```
pytest>=6.0.0
pytest-cov>=2.12.0
black>=21.0.0
flake8>=3.9.0
```

## Contact and Support

For questions or contributions, please refer to the main project documentation or contact the development team.

---
*Last updated: December 2024*
*Version: 1.0.0*
