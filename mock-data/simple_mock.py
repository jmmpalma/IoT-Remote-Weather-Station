import paho.mqtt.client as mqtt
import time
import config
import random
import utils
from datetime import datetime

print("=" * 50)
print("Mock Data Generator with Time Acceleration")
print("=" * 50)
print(f"Simulating 24 hours in 10 minutes")
print(f"Speed multiplier: {config.MOCK_SPEED_MULTIPLIER}x")
print(f"Data interval: {config.MOCK_DATA_INTERVAL} seconds")
print(f"Expected data points: ~{int(600 / config.MOCK_DATA_INTERVAL)}")
print("=" * 50)

# Create simulated time tracker
sim_time = utils.SimulatedTime(
    speed_multiplier=config.MOCK_SPEED_MULTIPLIER,
    start_hour=0  # Start at midnight
)

client = mqtt.Client()
client.username_pw_set(config.MQTT_USERNAME, config.MQTT_PASSWORD)

# Connect
try:
    client.connect(config.MQTT_BROKER, config.MQTT_PORT, 60)
    client.loop_start()
    print("✅ Connected to MQTT broker")
except Exception as e:
    print(f"❌ Failed to connect: {e}")
    exit(1)

time.sleep(1)

print(f"\nGenerating mock data every {config.MOCK_DATA_INTERVAL} seconds...")
print("Press Ctrl+C to stop\n")

try:
    counter = 0
    while True:
        # Simple version - just send counter
        # TODO: You'll replace this with realistic sensor functions
        
        temp = utils.generate_realistic_temperature(sim_time)
        
        # Publish to MQTT
        client.publish("sensors/temperature", str(temp))
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Published temp: {temp}°C")
        
        counter += 1
        
        # Wait before next reading
        time.sleep(config.MOCK_DATA_INTERVAL)
        
except KeyboardInterrupt:
    print("\n\nStopping mock generator...")
    client.loop_stop()
    client.disconnect()
    print("✅ Disconnected cleanly")
