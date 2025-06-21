# Agri Wiz - Agriculture Advisory REST API

Agri Wiz is a REST API service that provides agricultural recommendations, weather data, crop yield estimates, and information about government schemes for farmers.

## Features

- Crop recommendations based on soil and climate conditions
- Location-based crop recommendations
- Real-time weather data
- Crop yield estimation using machine learning models
- Government agricultural scheme information

## Installation

1. Clone the repository
2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```
3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the API Server

```bash
python app.py
```

The server will start on http://localhost:5000

## API Documentation

### Health Check
```
GET /api/health
```

### Crops
```
GET /api/crops
```
Get all available crops

```
POST /api/crops
```
Add a new crop
```json
{
    "crop_name": "string",
    "soil_types": "string",
    "climates": "string",
    "seasons": "string",
    "water_needs": "string",
    "humidity_preference": "string",
    "soil_fertility": "string"
}
```

### Recommendations
```
GET /api/recommendations?soil_type=<type>&climate=<climate>&season=<season>&rainfall=<level>&humidity=<level>&soil_fertility=<level>
```
Get crop recommendations based on parameters

```
GET /api/recommendations/location/<location>?humidity=<level>&soil_fertility=<level>
```
Get crop recommendations based on location

### Weather
```
GET /api/weather/<location>
```
Get weather data for a location

### Yield Estimation
```
POST /api/yield/estimate
```
Estimate crop yield
```json
{
    "crop_name": "string",
    "temperature": number,
    "rainfall": number,
    "humidity": number,
    "soil_ph": number,
    "soil_fertility": "string",
    "water_availability": "string",
    "season": "string"
}
```

### Government Schemes
```
GET /api/schemes?crop=<crop>&state=<state>&land_area=<area>
```
Get schemes by crop and location

```
GET /api/schemes?category=<category>
```
Get schemes by category

## Data Storage

- Raw data is stored in `data/raw/`
- Processed data and ML models are stored in `data/processed/`

## Environment Variables

- `PORT`: Server port (default: 5000)
- `OPENWEATHERMAP_API_KEY`: API key for weather data (optional)