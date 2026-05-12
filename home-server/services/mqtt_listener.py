import paho.mqtt.client as mqtt
import json
import psycopg2
from datetime import datetime
import config # Importing your local config.py file

# This function runs as soon as the VM connects to the local Mosquitto broker
def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected to Broker. Result: {reason_code}")
    # Subscribe to the data topic (temp/hum) and the logs topic (events)
    client.subscribe("sensors/data")
    client.subscribe("sensors/logs")

# This function runs every time a new MQTT message arrives
def on_message(client, userdata, msg):
    try:
        # Convert the incoming bytes message into a Python Dictionary
        payload = json.loads(msg.payload.decode())
        
        # Open a fresh connection to the PostgreSQL database
        conn = psycopg2.connect(
            dbname=config.DB_NAME,
            user="joaommpalma", # Updated as requested
            password=config.DB_PASSWORD,
            host=config.DB_HOST
        )
        cur = conn.cursor()

        # Route the data based on which "topic" it arrived on
        if msg.topic == "sensors/data":
            # Insert temperature and humidity into weather_data table
            cur.execute(
                "INSERT INTO weather_data (temperature, humidity, pressure) VALUES (%s, %s, %s)",
                (payload['temp'], payload['hum'], payload['press'])
            )
            print(f"Stored Data: {payload['temp']}C, {payload['hum']}%, {payload['press']} hPa")
        
        elif msg.topic == "sensors/logs":
            # Insert system events into system_logs table
            cur.execute(
                "INSERT INTO system_logs (event_type, message) VALUES (%s, %s)",
                (payload['event'], payload['message'])
            )
            print(f"Logged Event: {payload['event']}")

        # Commit changes and close the connection
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error processing message: {e}")

# Initialize the MQTT Client (Version 2.x)
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.username_pw_set(config.MQTT_USERNAME, config.MQTT_PASSWORD)
client.on_connect = on_connect
client.on_message = on_message

print("Starting Listener...")
# Connect to the local broker on the VM
client.connect("localhost", 1883, 60)
# Start the loop that listens forever
client.loop_forever()