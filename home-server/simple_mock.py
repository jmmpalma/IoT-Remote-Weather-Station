import paho.mqtt.client as mqtt
import time
import config

print("Starting simple mock generator...")

client = mqtt.Client()
client.username_pw_set(config.MQTT_USERNAME, config.MQTT_PASSWORD)

client.connect(config.MQTT_BROKER, config.MQTT_PORT, 60)
client.loop_start()

time.sleep(2)

for i in range(10):
    # TODO 6: Publish the number i to topic "test/counter"
    client.publish("test/counter", str(i))

    print(f"Published: {i}")

    time.sleep(2)

client.loop_stop()
client.disconnect()

print("Done!")