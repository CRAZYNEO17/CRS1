# AgriWiz - Enhanced Crop Recommendation System

AgriWiz is a comprehensive agricultural advisory system that helps farmers make informed decisions about crop selection based on:
- Local soil conditions and climate
- Real-time weather data and forecasts
- Government schemes and subsidies
- Machine learning-based yield predictions

## Features

- **Smart Crop Recommendations**: Get personalized crop recommendations based on:
  - Soil type and fertility
  - Local climate and weather conditions
  - Season and rainfall patterns
  - Water availability and humidity requirements

- **Weather Integration**:
  - Real-time weather data and 5-day forecasts
  - Weather suitability analysis for different crops
  - Seasonal planning based on weather patterns

- **Yield Estimation**:
  - ML-based crop yield predictions
  - Confidence intervals for yield estimates
  - Optimization suggestions for better yields
  - Factor importance analysis

- **Government Scheme Integration**:
  - Up-to-date information on agricultural schemes
  - Eligibility checking for different schemes
  - Subsidy information for seeds, machinery, and irrigation
  - State-specific scheme recommendations

## Installation

1. Clone the repository
2. Run the setup script to create a virtual environment and install dependencies:
   ```bash
   python setup.py
   ```
3. Activate the virtual environment:
   - Windows: `.\\venv\\Scripts\\activate`
   - Unix/MacOS: `source venv/bin/activate`

## Usage

### Command Line Interface
Run the program in CLI mode:
```bash
python agri_wiz.py
```

### Graphical Interface
Run the program in GUI mode:
```bash
python agri_wiz.py --gui
```

## Available Commands

1. Get crop recommendations
   - Based on soil type, climate, and season
   - Optional parameters for more accurate recommendations

2. Get location-based recommendations
   - Uses pre-configured location data
   - Integrates real-time weather information

3. View weather forecasts
   - 5-day weather forecasts
   - Temperature, humidity, and rainfall data

4. Estimate crop yields
   - ML-based yield predictions
   - Optimization suggestions

5. Access government schemes
   - View all available schemes
   - Check eligibility
   - Get scheme recommendations by crop

## Data Sources

- Crop data from Indian Council of Agricultural Research (ICAR)
- Weather data from OpenWeather API
- Government schemes from various agricultural departments
- Soil data from National Bureau of Soil Survey and Land Use Planning

## Requirements

- Python 3.8 or higher
- Dependencies listed in requirements.txt
- Internet connection for weather data

## Contributing

1. Fork the repository
2. Create a new branch for your feature
3. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

For support or queries, please open an issue in the repository.