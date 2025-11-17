import math
from datetime import datetime
import random

def generate_realistic_temperature():
    """Generate temperature based on time of day"""
    
    # Get current hour (0-23)
    current_hour = datetime.now().hour
    
    # Temperature parameters
    base_temp = 21.5      # Average temperature
    amplitude = 6.5       # How much it varies (+/- 6.5°C)
    peak_hour = 14        # Warmest at 2 PM
    
    # Calculate temperature using sine wave
    # Math: temp varies sinusoidally over 24 hours
    hour_angle = (current_hour - peak_hour) * (2 * math.pi / 24)
    temp = base_temp + amplitude * math.cos(hour_angle)
    
    # Add random noise (sensors aren't perfect)
    noise = random.uniform(-0.5, 0.5)
    temp = temp + noise
    
    return round(temp, 1)