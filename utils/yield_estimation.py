#!/usr/bin/env python
# Yield Estimation Module for Agri Wiz
# Estimates crop yields based on environment and growing conditions

import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import joblib
import os
from typing import Dict, Optional, List
import logging
import csv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class YieldEstimator:
    def __init__(self):
        """Initialize the YieldEstimator with model paths."""
        self.model_dir = "data/processed/models"
        self.load_models()

    def load_models(self):
        """Load ML models for yield estimation."""
        try:
            os.makedirs(self.model_dir, exist_ok=True)
            self.models = {}
            self.scalers = {}
            
            # Load available models
            for file in os.listdir(self.model_dir):
                if file.endswith("_model.joblib"):
                    crop_name = file.replace("_model.joblib", "")
                    model_path = os.path.join(self.model_dir, file)
                    scaler_path = os.path.join(self.model_dir, f"{crop_name}_scaler.joblib")
                    
                    if os.path.exists(scaler_path):
                        self.models[crop_name] = joblib.load(model_path)
                        self.scalers[crop_name] = joblib.load(scaler_path)
                        
        except Exception as e:
            print(f"Error loading yield estimation models: {e}")

    def _generate_sample_data(self) -> Dict:
        """Generate sample training data for initial models."""
        # This is a simplified data generator that uses real crop parameters
        # First read crop data to get proper ranges
        crop_params = {}
        try:
            with open("crop_data.csv", "r") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Set default ranges if not available
                    temp_range = ['20', '35']
                    rain_range = ['500', '1000']
                    base_yield = 30
                    
                    # Try to extract ranges from data
                    if row.get('temperature_range'):
                        try:
                            temp_range = row['temperature_range'].split('-')
                        except:
                            pass
                            
                    if row.get('rainfall_range_mm'):
                        try:
                            rain_range = row['rainfall_range_mm'].split('-')
                        except:
                            pass
                            
                    if row.get('yield_potential_qt_per_ha'):
                        try:
                            # Take first number if range is given
                            base_yield = float(row['yield_potential_qt_per_ha'].split('-')[0])
                        except:
                            base_yield = 30  # Default value
                    
                    crop_params[row['crop_name'].lower()] = {
                        'base_yield': base_yield,
                        'temp_range': (float(temp_range[0]), float(temp_range[-1])),
                        'rainfall_range': (float(rain_range[0]), float(rain_range[-1]))
                    }
                    
                logging.info(f"Loaded parameters for {len(crop_params)} crops")
                
        except Exception as e:
            logging.warning(f"Error reading crop parameters: {e}. Using default values.")
            # Fallback to default parameters if CSV read fails
            crop_params = {
                'rice': {'base_yield': 50, 'temp_range': (20, 35), 'rainfall_range': (1000, 2500)},
                'wheat': {'base_yield': 45, 'temp_range': (15, 25), 'rainfall_range': (650, 1000)},
                'corn': {'base_yield': 55, 'temp_range': (20, 30), 'rainfall_range': (500, 800)},
                'cotton': {'base_yield': 22, 'temp_range': (21, 30), 'rainfall_range': (500, 1000)},
                'sugarcane': {'base_yield': 700, 'temp_range': (20, 35), 'rainfall_range': (1500, 2500)}
            }

        # Rest of the function remains the same
        sample_data = {}
        
        for crop_name, params in crop_params.items():
            features = []
            yields = []
            
            # Generate 1000 sample points for each crop
            for _ in range(1000):
                # Generate random but realistic values
                temp = np.random.uniform(params['temp_range'][0], params['temp_range'][1])
                rainfall = np.random.uniform(params['rainfall_range'][0], params['rainfall_range'][1])
                humidity = np.random.uniform(40, 90)
                soil_ph = np.random.uniform(5.5, 7.5)
                soil_fertility = np.random.randint(1, 4)  # 1=low, 2=medium, 3=high
                water_availability = np.random.randint(1, 4)
                season = np.random.randint(1, 5)  # 1=spring, 2=summer, 3=fall, 4=winter
                
                features.append([temp, rainfall, humidity, soil_ph, soil_fertility, 
                               water_availability, season])
                
                # Calculate yield with some randomness and environmental factors
                base_yield = params['base_yield']
                
                # Temperature effect
                temp_optimal = (params['temp_range'][0] + params['temp_range'][1]) / 2
                temp_effect = 1 - abs(temp - temp_optimal) / temp_optimal * 0.5
                
                # Rainfall effect
                rainfall_optimal = (params['rainfall_range'][0] + params['rainfall_range'][1]) / 2
                rainfall_effect = 1 - abs(rainfall - rainfall_optimal) / rainfall_optimal * 0.5
                
                # Other factors
                soil_effect = soil_fertility / 3
                water_effect = water_availability / 3
                
                # Combined effect with some randomness
                yield_value = base_yield * temp_effect * rainfall_effect * soil_effect * water_effect
                yield_value *= np.random.uniform(0.9, 1.1)  # Add 10% random variation
                
                yields.append(yield_value)
            
            sample_data[crop_name] = {
                'features': features,
                'yields': yields
            }
        
        return sample_data

    def _preprocess_input(self, data: Dict, crop_name: str) -> Optional[np.ndarray]:
        """Preprocess input data for prediction."""
        try:
            # Convert input data to feature array
            features = []
            
            # Map season to number
            season_map = {'spring': 1, 'summer': 2, 'fall': 3, 'winter': 4}
            fertility_map = {'low': 1, 'medium': 2, 'high': 3}
            
            features.append(float(data.get('temperature', 25)))
            features.append(float(data.get('rainfall', 500)))
            features.append(float(data.get('humidity', 60)))
            features.append(float(data.get('soil_ph', 6.5)))
            features.append(fertility_map.get(data.get('soil_fertility', 'medium'), 2))
            features.append(fertility_map.get(data.get('water_availability', 'medium'), 2))
            features.append(season_map.get(data.get('season', 'summer'), 2))
            
            features = np.array(features).reshape(1, -1)
            
            # Scale features
            if crop_name in self.scalers:
                features = self.scalers[crop_name].transform(features)
                
            return features
            
        except Exception as e:
            print(f"Error preprocessing input: {e}")
            return None

    def predict_yield(self, crop_name: str, conditions: Dict) -> Dict:
        """
        Predict crop yield based on given conditions.
        
        Args:
            crop_name: Name of the crop
            conditions: Dictionary containing environmental conditions
        
        Returns:
            Dictionary with predicted yield and confidence interval
        """
        crop_name = crop_name.lower()
        
        if crop_name not in self.models:
            return {
                'error': 'Crop model not available',
                'estimated_yield': None,
                'confidence_interval': None
            }
            
        features = self._preprocess_input(conditions, crop_name)
        if features is None:
            return {
                'error': 'Error processing input data',
                'estimated_yield': None,
                'confidence_interval': None
            }
            
        try:
            # Get predictions from all trees in the forest
            predictions = [tree.predict(features)[0] 
                         for tree in self.models[crop_name].estimators_]
            
            # Calculate mean and confidence interval
            mean_yield = np.mean(predictions)
            confidence_interval = np.percentile(predictions, [5, 95])
            
            return {
                'estimated_yield': round(mean_yield, 2),
                'confidence_interval': [round(ci, 2) for ci in confidence_interval],
                'unit': 'quintals per hectare'
            }
            
        except Exception as e:
            return {
                'error': f'Error making prediction: {str(e)}',
                'estimated_yield': None,
                'confidence_interval': None
            }

    def update_model(self, crop_name: str, new_data: Dict[str, List]):
        """
        Update model with new training data.
        
        Args:
            crop_name: Name of the crop
            new_data: Dictionary containing 'features' and 'yields' lists
        """
        crop_name = crop_name.lower()
        
        try:
            X = np.array(new_data['features'])
            y = np.array(new_data['yields'])
            
            if crop_name in self.models:
                # Update existing model
                scaler = self.scalers[crop_name]
                X_scaled = scaler.transform(X)
                self.models[crop_name].fit(X_scaled, y)
            else:
                # Create new model
                scaler = StandardScaler()
                X_scaled = scaler.fit_transform(X)
                model = RandomForestRegressor(n_estimators=100, random_state=42)
                model.fit(X_scaled, y)
                
                self.models[crop_name] = model
                self.scalers[crop_name] = scaler
            
            # Save updated model and scaler
            model_file = os.path.join(self.model_dir, f"{crop_name}_model.joblib")
            scaler_file = os.path.join(self.model_dir, f"{crop_name}_scaler.joblib")
            
            joblib.dump(self.models[crop_name], model_file)
            joblib.dump(self.scalers[crop_name], scaler_file)
            
            return True
            
        except Exception as e:
            print(f"Error updating model: {e}")
            return False

    def get_yield_factors(self, crop_name: str) -> Dict:
        """Get the importance of different factors affecting yield."""
        crop_name = crop_name.lower()
        
        if crop_name not in self.models:
            return {'error': 'Crop model not available'}
            
        try:
            # Get feature importances from the model
            importances = self.models[crop_name].feature_importances_
            
            # Map importances to factors
            factors = {}
            for feature, importance in zip(self.feature_columns, importances):
                factors[feature] = round(importance * 100, 2)
            
            return {
                'factors': factors,
                'unit': 'percentage importance'
            }
            
        except Exception as e:
            return {'error': f'Error getting yield factors: {str(e)}'}

    def get_optimization_suggestions(self, crop_name: str, current_conditions: Dict) -> Dict:
        """Get suggestions for optimizing yield based on current conditions."""
        crop_name = crop_name.lower()
        
        if crop_name not in self.models:
            return {'error': 'Crop model not available'}
            
        try:
            # Get current predicted yield
            current_yield = self.predict_yield(crop_name, current_conditions)
            
            # Try variations in controllable parameters
            suggestions = []
            
            # Test different soil fertility levels
            for fertility in ['low', 'medium', 'high']:
                test_conditions = current_conditions.copy()
                test_conditions['soil_fertility'] = fertility
                test_yield = self.predict_yield(crop_name, test_conditions)
                
                if test_yield['estimated_yield'] > current_yield['estimated_yield']:
                    suggestions.append({
                        'factor': 'soil_fertility',
                        'suggestion': f"Increase soil fertility to {fertility}",
                        'potential_improvement': round(
                            test_yield['estimated_yield'] - current_yield['estimated_yield'], 2
                        )
                    })
            
            # Test different water availability levels
            for water in ['low', 'medium', 'high']:
                test_conditions = current_conditions.copy()
                test_conditions['water_availability'] = water
                test_yield = self.predict_yield(crop_name, test_conditions)
                
                if test_yield['estimated_yield'] > current_yield['estimated_yield']:
                    suggestions.append({
                        'factor': 'water_availability',
                        'suggestion': f"Adjust irrigation to achieve {water} water availability",
                        'potential_improvement': round(
                            test_yield['estimated_yield'] - current_yield['estimated_yield'], 2
                        )
                    })
            
            return {
                'current_yield': current_yield,
                'suggestions': sorted(suggestions, 
                                   key=lambda x: x['potential_improvement'],
                                   reverse=True)
            }
            
        except Exception as e:
            return {'error': f'Error generating optimization suggestions: {str(e)}'}

# Simple test if run directly
if __name__ == "__main__":
    estimator = YieldEstimator()
    
    # Test with rice in good conditions
    conditions = {
        "temperature": 30,
        "rainfall": 1500,
        "humidity": 70,
        "soil_ph": 6.5,
        "soil_fertility": "high",
        "water_availability": "high",
        "season": "summer"
    }
    
    yield_data = estimator.predict_yield("rice", conditions)
    print(f"Rice yield estimation:")
    print(f"Estimated yield: {yield_data['estimated_yield']} quintals per hectare")
    print(f"Confidence interval: {yield_data['confidence_interval'][0]} - {yield_data['confidence_interval'][1]} quintals per hectare")
    
    # Test updating model with new data
    new_data = {
        "features": [[30, 1500, 70, 6.5, 3, 3, 2]],
        "yields": [55]
    }
    estimator.update_model("rice", new_data)
    print("Model updated with new data.")
    
    # Test getting yield factors
    factors = estimator.get_yield_factors("rice")
    print(f"Yield factors: {factors}")
    
    # Test getting optimization suggestions
    suggestions = estimator.get_optimization_suggestions("rice", conditions)
    print(f"Optimization suggestions: {suggestions}")