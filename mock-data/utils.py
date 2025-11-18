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

def generate_temperature(sim_time):
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

def generate_humidity(sim_time):
    """Generate humidity (inversely related to temperature)"""
    temp = generate_temperature(sim_time)
    
    # When temp is high, humidity is low (and vice versa)
    # Map temp (15-28) to humidity (80-40)
    humidity = 80 - (temp - 15) * (40 / 13)
    
    noise = random.uniform(-2, 2)
    humidity = humidity + noise
    
    # Clamp to realistic range
    humidity = max(30, min(90, humidity))
    
    return round(humidity, 1)



def generate_light_level(sim_time):
    """Light level based on time of day"""
    hour = sim_time.get_simulated_hour_float()
    
    # Dark at night, bright during day
    sunrise = 6.0
    sunset = 20.0
    
    if hour < sunrise or hour > sunset:
        # Night time
        return 0
    elif sunrise <= hour < sunrise + 2:
        # Sunrise transition (0 to max over 2 hours)
        progress = (hour - sunrise) / 2.0
        return int(config.LIGHT_MAX * progress)
    elif sunset - 2 < hour <= sunset:
        # Sunset transition (max to 0 over 2 hours)
        progress = (sunset - hour) / 2.0
        return int(config.LIGHT_MAX * progress)
    else:
        # Full daylight with slight variation
        base_light = config.LIGHT_MAX
        variation = random.uniform(-0.1, 0.1)
        return int(base_light * (1 + variation))