# MQTT Settings
MQTT_BROKER = "100.94.32.51"
MQTT_PORT = 1883
MQTT_USERNAME = "sensors"
MQTT_PASSWORD = "Kristin.2026!"
MQTT_TOPICS = [
    "sensors/#",      # All sensor topics
    "camera/#",       # Camera topics
    "system/#"        # System status
]

# Database Settings
DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "iot_remote_station_db"
DB_USER = "joaommpalma"
DB_PASSWORD = "sensorpass123"

# Web Server Settings
WEB_HOST = "0.0.0.0"  # Listen on all interfaces
WEB_PORT = 5000
WEB_DEBUG = True      # Set to False in production

# File Storage
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_DIR = os.path.join(BASE_DIR, "data/images")
LOG_DIR = os.path.join(BASE_DIR, "logs")

# Data Retention
KEEP_READINGS_DAYS = 30
KEEP_IMAGES_DAYS = 7

# Mock Data Settings (for testing)
MOCK_DATA_INTERVAL = 5  # seconds between readings
MOCK_SPEED_MULTIPLIER = 1  # 1 = real time, 60 = 1 min = 1 hour
