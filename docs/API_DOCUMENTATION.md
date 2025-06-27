# Agri Wiz API Documentation

Base URL: `http://localhost:5000`

## Health Check

### GET /api/health
Check if the API service is running.

**Response:**
```json
{
    "status": "healthy",
    "version": "1.0.0"
}
```

## Crops

### GET /api/crops
Get a list of all available crops and their characteristics.

**Response:**
```json
[
    {
        "crop_name": "string",
        "soil_types": "string",
        "climates": "string",
        "seasons": "string",
        "water_needs": "string",
        "humidity_preference": "string",
        "soil_fertility": "string"
    }
]
```

### POST /api/crops
Add a new crop to the database.

**Request Body:**
```json
{
    "crop_name": "string",
    "soil_types": "string",         // comma-separated list
    "climates": "string",          // comma-separated list
    "seasons": "string",           // comma-separated list
    "water_needs": "string",       // low, medium, or high
    "humidity_preference": "string", // low, medium, or high
    "soil_fertility": "string"     // low, medium, or high
}
```

**Response:**
```json
{
    "message": "Crop added successfully",
    "crop": {
        // Added crop data
    }
}
```

## Recommendations

### GET /api/recommendations
Get crop recommendations based on environmental parameters.

**Query Parameters:**
- soil_type (required): Type of soil (e.g., "clay", "loamy", "sandy")
- climate (required): Climate type (e.g., "tropical", "subtropical", "temperate")
- season (required): Growing season (e.g., "summer", "winter", "rainy")
- rainfall (optional): Rainfall level ("low", "medium", "high")
- humidity (optional): Humidity level ("low", "medium", "high")
- soil_fertility (optional): Soil fertility level ("low", "medium", "high")

**Response:**
```json
{
    "recommendations": [
        "crop_name1",
        "crop_name2"
    ],
    "scored_recommendations": [
        {
            "crop": "crop_name1",
            "match_percentage": 95.5
        }
    ]
}
```

### GET /api/recommendations/location/{location}
Get crop recommendations based on location name.

**Path Parameters:**
- location: Name of the location (e.g., "Punjab", "Kerala")

**Query Parameters:**
- humidity (optional): Override location's default humidity level
- soil_fertility (optional): Override location's default soil fertility level

**Response:**
```json
{
    "recommendations": [
        "crop_name1",
        "crop_name2"
    ],
    "location_details": {
        "soil_type": "string",
        "climate": "string",
        "season": "string",
        "rainfall": "string",
        "humidity": "string",
        "soil_fertility": "string"
    }
}
```

## Weather

### GET /api/weather/{location}
Get current weather data for a location.

**Path Parameters:**
- location: Name of the location

**Response:**
```json
{
    "temperature": number,      // in Celsius
    "humidity": number,        // percentage
    "rainfall": number,        // in mm
    "description": "string",
    "timestamp": number
}
```

## Yield Estimation

### POST /api/yield/estimate
Estimate crop yield based on growing conditions.

**Request Body:**
```json
{
    "crop_name": "string",
    "temperature": number,           // in Celsius
    "rainfall": number,             // in mm
    "humidity": number,            // percentage
    "soil_ph": number,            // pH value
    "soil_fertility": "string",   // low, medium, or high
    "water_availability": "string", // low, medium, or high
    "season": "string"            // summer, winter, rainy, spring
}
```

**Response:**
```json
{
    "estimated_yield": number,
    "confidence_interval": [
        number,  // lower bound
        number   // upper bound
    ],
    "unit": "quintals per hectare"
}
```

## Government Schemes

### GET /api/schemes
Get government schemes and subsidies for agriculture.

**Query Parameters:**
- crop (optional): Crop name for specific schemes
- state (optional): State name for regional schemes
- land_area (optional): Land area in hectares
- category (optional): Scheme category

**Response with category:**
```json
{
    "schemes": [
        {
            "name": "string",
            "full_name": "string",
            "description": "string",
            "benefits": [
                "string"
            ]
        }
    ]
}
```

**Response with crop and state:**
```json
{
    "schemes": [
        {
            "name": "string",
            "description": "string",
            "benefits": [
                "string"
            ]
        }
    ],
    "subsidies": {
        "machinery": "string",
        "irrigation": "string"
    }
}
```

## Error Responses

All endpoints may return error responses in the following format:

```json
{
    "error": "Error message describing what went wrong"
}
```

Common HTTP Status Codes:
- 200: Success
- 400: Bad Request (missing or invalid parameters)
- 404: Not Found (resource not found)
- 500: Internal Server Error

## Rate Limiting

The API currently does not implement rate limiting, but it's recommended to:
- Limit requests to weather API endpoints to once per minute per location
- Cache weather data responses for 1 hour
- Limit yield estimation requests to 100 per day per client

## Authentication

The API currently runs without authentication. For production use, implement:
1. API key authentication
2. Rate limiting per API key
3. HTTPS encryption