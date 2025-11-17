import paho.mqtt.client as mqtt
import time
import config
import random
import utils
import datetime

print("=== Mock Data Generator ===")
print(f"Connecting to MQTT broker at {config.MQTT_BROKER}:{config.MQTT_PORT}")


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
        
        temp = utils.generate_realistic_temperature()
        
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
