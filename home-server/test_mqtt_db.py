
import paho.mqtt.client as mqtt
import psycopg2
from datetime import datetime
import time
import config

print("=== MQTT & Database Test ===\n")

# Test 1: Database Connection
print("1. Testing database connection...")
try:
    conn = psycopg2.connect(
        host=config.DB_HOST,
        port=config.DB_PORT,
        database=config.DB_NAME,
        user=config.DB_USER,
        password=config.DB_PASSWORD
    )
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    db_version = cursor.fetchone()
    print(f"   ✅ Database connected: {db_version[0][:50]}...")
    cursor.close()
    conn.close()
except Exception as e:
    print(f"   ❌ Database connection failed: {e}")
    exit(1)

# Test 2: MQTT Connection
print("\n2. Testing MQTT connection...")

mqtt_connected = False

def on_connect(client, userdata, flags, rc):
    global mqtt_connected
    if rc == 0:
        print("   ✅ MQTT connected successfully")
        mqtt_connected = True
        client.subscribe("test/#")
    else:
        print(f"   ❌ MQTT connection failed with code {rc}")

def on_message(client, userdata, msg):
    print(f"   📨 Received: {msg.topic} -> {msg.payload.decode()}")

client = mqtt.Client()
client.username_pw_set(config.MQTT_USERNAME, config.MQTT_PASSWORD)
client.on_connect = on_connect
client.on_message = on_message

try:
    client.connect(config.MQTT_BROKER, config.MQTT_PORT, 60)
    client.loop_start()
    
    # Wait for connection
    time.sleep(2)
    
    if mqtt_connected:
        # Test 3: Publish and receive message
        print("\n3. Testing MQTT publish/subscribe...")
        client.publish("test/hello", "Hello from Python!")
        time.sleep(1)
        
        # Test 4: Write to database
        print("\n4. Testing database write...")
        conn = psycopg2.connect(
            host=config.DB_HOST,
            port=config.DB_PORT,
            database=config.DB_NAME,
            user=config.DB_USER,
            password=config.DB_PASSWORD
        )
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO sensor_readings (sensor_name, value, unit) VALUES (%s, %s, %s)",
            ("test_sensor", 42.0, "test_unit")
        )
        conn.commit()
        print("   ✅ Database write successful")
        
        # Test 5: Read from database
        print("\n5. Testing database read...")
        cursor.execute(
            "SELECT * FROM sensor_readings ORDER BY timestamp DESC LIMIT 1"
        )
        row = cursor.fetchone()
        print(f"   ✅ Latest reading: ID={row[0]}, Time={row[1]}, Sensor={row[2]}, Value={row[3]}, Unit={row[4]}")
        
        cursor.close()
        conn.close()
        
        print("\n✅ All tests passed! System is ready.\n")
    else:
        print("\n❌ MQTT connection failed")
        exit(1)
    
    client.loop_stop()
    client.disconnect()
    
except Exception as e:
    print(f"   ❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
