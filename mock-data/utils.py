import math
from datetime import datetime, timedelta
import random
import config
import time

# ============== Simulated Time Class ==============
class SimulatedTime:
    """Tracks simulated time that runs faster than real time"""
    
    def __init__(self, speed_multiplier, start_hour):
        """
        speed_multiplier: How many real seconds = 1 simulated second
        start_hour: What hour to start simulation at (0-23)
        """
        self.speed_multiplier = speed_multiplier
        self.real_start_time = time.time()
        
        # Start at specific hour of "today"
        now = datetime.now()
        self.sim_start_time = now.replace(hour=start_hour, minute=0, second=0, microsecond=0)
    
    def get_simulated_time(self):
        """Get current simulated time"""
        # How much real time has passed?
        real_elapsed = time.time() - self.real_start_time
        
        # How much simulated time has passed?
        sim_elapsed = real_elapsed * self.speed_multiplier
        
        # Calculate simulated datetime
        simulated_datetime = self.sim_start_time + timedelta(seconds=sim_elapsed)
        
        return simulated_datetime
    
    def get_simulated_hour(self):
        """Get current simulated hour (0-23)"""
        sim_time = self.get_simulated_time()
        return sim_time.hour
    
    def get_simulated_hour_float(self):
        """Get hour as float (e.g., 14.5 = 2:30 PM)"""
        sim_time = self.get_simulated_time()
        return sim_time.hour + sim_time.minute / 60.0 + sim_time.second / 3600.0

# ============== Sensor Generation Functions ==============

def generate_realistic_temperature(sim_time):
    """Generate temperature based on time of day"""
    
    # Get current hour (0-23)
    #current_hour = datetime.now().hour
    hour = sim_time.get_simulated_hour_float()

    # Temperature parameters
    base_temp = config.TEMP_BASE          # 21.5°C average
    amplitude = config.TEMP_AMPLITUDE     # ±6.5°C variation
    peak_hour = config.TEMP_PEAK_HOUR 
    
    # Calculate temperature using sine wave
    # Math: temp varies sinusoidally over 24 hours
    hour_angle = (hour - peak_hour) * (2 * math.pi / 24)
    temp = base_temp + amplitude * math.cos(hour_angle)
    
    # Add random noise (sensors aren't perfect)
    noise = random.uniform(-0.3, 0.3)
    temp = temp + noise
    
    return round(temp, 1)

def generate_realistic_humidity():
    """Humidity is inversely related to temperature"""
    # TODO: Think about the logic
    # - When hot (high temp), humidity is low
    # - When cool (low temp), humidity is high
    # - Range: 40-80%
    
    # Hint: You could use the temperature to calculate humidity
    # Or create another time-based pattern
    
    pass  # Replace with your code



def generate_light_level():
    """Light level based on time of day"""
    # TODO: Think about the logic
    # - 0 at night (20:00 - 06:00)
    # - Max at noon (12:00)
    # - Range: 0-50000 lux
    
    pass  # Replace with your code