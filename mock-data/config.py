# MQTT Settings (connects TO the server)
MQTT_BROKER = "localhost"  # Will be actual IP later (192.168.1.100)
MQTT_PORT = 1883
MQTT_USERNAME = "sensors"
MQTT_PASSWORD = "sensor123"

# Mock Data Settings
MOCK_DATA_INTERVAL = 5  # seconds between readings
MOCK_SPEED_MULTIPLIER = 288  # 1 = real time, 60 = 1 min = 1 hour, 144 = 10 min = 24 hours, 288 = 5 min = 24 hours

# Sensor simulation settings
TEMP_BASE = 21.5        # Average temperature (°C)
TEMP_AMPLITUDE = 6.5    # Temperature variation (+/-)
TEMP_PEAK_HOUR = 14     # Warmest at 2 PM

HUMIDITY_MIN = 40       # Minimum humidity (%)
HUMIDITY_MAX = 80       # Maximum humidity (%)

SOIL_INITIAL = 800      # Starting soil moisture
SOIL_DRAIN_RATE = 5     # How much it dries per reading
SOIL_MIN = 200          # Minimum (very dry)

LIGHT_MAX = 50000       # Maximum light (lux)
SUNRISE_HOUR = 6
SUNSET_HOUR = 20