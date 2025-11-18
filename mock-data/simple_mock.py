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

print("Starting data generation...")
print("Press Ctrl+C to stop\n")
print(f"{'Real Time':<12} {'Sim Time':<12} {'Temp':<8} {'Humidity':<10} {'Light':<10}")
print("-" * 60)

try:
    reading_count = 0
    start_real_time = time.time()
    while True:
        # Get simulated time
        simulated_dt = sim_time.get_simulated_time()
        sim_hour = simulated_dt.strftime("%H:%M:%S")

        # Generate sensor values based on simulated time
        
        temp = utils.generate_temperature(sim_time)
        humidity = utils.generate_humidity(sim_time)
        light = utils.generate_light_level(sim_time)

        # Publish to MQTT
        client.publish("sensors/temperature", str(temp))
        client.publish("sensors/humidity", str(humidity))
        client.publish("sensors/light", str(light))

        #Display
        real_now = datetime.now().strftime("%H:%M:%S")
        print(f"{real_now:<12} {sim_hour:<12} {temp:<8}°C {humidity:<10}% {light:<10} lux")
        
        reading_count += 1
        
        # Check if we've completed 24 simulated hours
        elapsed_sim_seconds = (simulated_dt - sim_time.sim_start_time).total_seconds()
        if elapsed_sim_seconds >= 86400:  # 24 hours in seconds
            print("\n✅ Completed 24-hour simulation!")
            break
        
        # Wait for next reading
        time.sleep(config.MOCK_DATA_INTERVAL)
        
except KeyboardInterrupt:
    print("\n\nStopping mock generator...")
    client.loop_stop()
    client.disconnect()
    print("✅ Disconnected cleanly")

finally:
    elapsed_real = time.time() - start_real_time
    print(f"\nGenerated {reading_count} readings over {elapsed_real:.1f} seconds")
    print(f"Simulated time span: {elapsed_sim_seconds/3600:.1f} hours")

    client.loop_stop()
    client.disconnect()
    print("✅ Disconnected cleanly")