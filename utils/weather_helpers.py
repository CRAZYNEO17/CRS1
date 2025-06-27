"""
Weather utility functions for classifying humidity and rainfall levels.
"""

def get_humidity_level(humidity_percentage):
    """
    Classify humidity level based on percentage.
    
    Args:
        humidity_percentage (float): Humidity percentage (0-100)
        
    Returns:
        str: 'low', 'medium', or 'high' based on humidity level
    """
    if humidity_percentage <= 40:
        return "low"
    elif humidity_percentage <= 70:
        return "medium"
    else:
        return "high"

def get_rainfall_level(rainfall_mm):
    """
    Classify rainfall level based on millimeters.
    
    Args:
        rainfall_mm (float): Rainfall amount in millimeters
        
    Returns:
        str: 'low', 'medium', or 'high' based on rainfall amount
    """
    if rainfall_mm <= 0.5:
        return "low"
    elif rainfall_mm <= 2:
        return "medium"
    else:
        return "high"
