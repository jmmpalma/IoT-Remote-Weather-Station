import time
import json
import board
import busio
from adafruit_bme280 import basic as adafruit_bme280
import adafruit_bh1750
import paho.mqtt.client as mqtt
from gpiozero import MotionSensor, RGBLED, CPUTemperature
import config

# ######################  Configuration Constants  ######################
MAX_TRIGGERS = 3          # Max triggers allowed...
TRIGGER_WINDOW = 60       # ...within this many seconds
COOLDOWN_DURATION = 900   # 15 minutes in seconds

# ######################  State Variables  ######################
trigger_history = []      # List to store timestamps of recent triggers
cooldown_until = 0  
cpu = CPUTemperature()

######################## Get System Diagnostics ###########################
cpu_temp = round(cpu.temperature, 1) # Get Pi's internal heat

# ######################  Hardware Initialization  ######################
# LED pins: Red=13, Green=19, Blue=26
led = RGBLED(red=13, green=19, blue=26)
# PIR on GPIO 17
pir = MotionSensor(17)

########################  Helper Functions  ######################
# Function to keep the LED pulsing green in the background
def start_heartbeat():
    # Green (0, 1, 0) | On for 0.2s, Off for 19.8s
    led.blink(on_time=0.2, off_time=19.8, on_color=(0, 1, 0), off_color=(0, 0, 0), background=True)

# Helper function to send status messages to the Cloud VM
def send_log(event, message):
    try:
        payload = json.dumps({"event": event, "message": message})
        client.publish("sensors/logs", payload)
    except:
        print("Failed to send log")

# Triggered automatically when the PIR sees motion
def on_motion():
    global cooldown_until, trigger_history
    now = time.time()

    # 1. Check if we are in a 15-minute timeout
    if now < cooldown_until:
        return # Ignore the trigger silently

    # 2. Clean up history: Remove timestamps older than 60 seconds
    trigger_history = [t for t in trigger_history if now - t < TRIGGER_WINDOW]

    # 3. Check if we just hit the limit
    if len(trigger_history) >= MAX_TRIGGERS:
        cooldown_until = now + COOLDOWN_DURATION
        print(f"Rate limit reached. Cooling down until {time.ctime(cooldown_until)}")
        send_log("RATE_LIMIT", f"3 triggers in 60s. Locking PIR for 15 mins.")
        led.blink(on_time=0.2, off_time=19.8, on_color=(1, 0.5, 0), off_color=(0, 0, 0), background=True)# Orange blink light to show warning/cooldown
        return

    # 4. If we are under the limit, process the trigger
    trigger_history.append(now)
    print(f"Motion Detected! ({len(trigger_history)}/{MAX_TRIGGERS})")
    led.color = (1, 0, 0) # Solid Red
    send_log("PIR_TRIGGER", "Motion detected. System active.")

# Triggered automatically when motion stops
def on_no_motion():
    # Only return to green heartbeat if we aren't in a cooldown
    if time.time() > cooldown_until:
        start_heartbeat()

# Assign the functions to the PIR sensor events
pir.when_motion = on_motion
pir.when_no_motion = on_no_motion

# ######################  MQTT Setup  ######################
# Runs when the Pi successfully connects to the Cloud MQTT Broker
def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Pi Connected to Cloud. Code: {reason_code}")
    send_log("SYSTEM_START", "Weather station script initialized")

# Initialize MQTT Client
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.username_pw_set(config.MQTT_USERNAME, config.MQTT_PASSWORD)
client.on_connect = on_connect


###################### I2C Bus Setup #####################
# Both BME280 and BH1750 share these pins
i2c_bus = board.I2C()

# Initialize BME280 with safety check
bme_sensor = None
try:
    bme_sensor = adafruit_bme280.Adafruit_BME280_I2C(i2c_bus, address=0x76)
    print("BME280: Connected")
except Exception as e:
    print(f"BME280 Not connected: Error {e}")
    send_log("SENSOR_MISSING", f"BME280 could not be initialized: ({e})")

# Initialize BH1750 with safety check
light_sensor = None
try:
    light_sensor = adafruit_bh1750.BH1750(i2c_bus)
    print("BH1750: Connected")
except Exception as e:
    print("BH1750: Not connected")
    send_log("SENSOR_MISSING", f"BH1750 could not be initialized: ({e})")

######################  Main Logic ######################
try:
    print(f"Connecting to VM at {config.MQTT_BROKER}...")
    client.connect(config.MQTT_BROKER, 1883, 60)
    client.loop_start()
    time.sleep(2) # Starts a background thread for MQTT communication
    start_heartbeat()   # Starts the Green pulse

    while True:
        # --- 1. Get CPU Temp (Moved inside loop to keep it fresh) ---
        cpu_temp = round(cpu.temperature, 1)

        # --- 2. Read BME280 ---
        temp, hum, press = 0.0, 0.0, 0.0
        if bme_sensor:
            success = False
            for attempt in range(3): # Try up to 3 times
                try:
                    temp = round(bme_sensor.temperature, 1)
                    hum = round(bme_sensor.humidity, 1)
                    press = round(bme_sensor.pressure, 1)
                    success = True
                    break # If read works, exit the retry loop
                except Exception as e:
                    print(f"BME280 read failed (Attempt {attempt+1}/3): {str(e)}")
                    time.sleep(0.5) # Short delay before retrying
            if not success:
                send_log("SENSOR_ERROR", "BME280 read failed after 3 attempts.")
        else:
            send_log("SENSOR_MISSING", "BME280 not found on I2C bus.")

        # --- 3. Read BH1750 (Light) ---
        lux = 0.0
        if light_sensor:
            try:
                lux = round(light_sensor.lux, 1)
            except Exception as e:
                send_log("SENSOR_ERROR", f"BH1750 read failed: {str(e)}")
        # else:
            # send_log("SENSOR_MISSING", "BME280 not found on I2C bus.") - Uncomment when sensor is working

        # 4. Send DATA payload
        data_payload = {
            "temp": temp
            ,"hum": hum
            ,"press": press
            ,"lux": lux
        }
        client.publish("sensors/data", json.dumps(data_payload))
        
        # # 5. Send HEARTBEAT log
        # We include Ambient Temp, Humidity, and CPU Temp in the message
        log_msg = f"Health Status | CPU: {cpu_temp}C | Ambient: {temp}C | Hum: {hum}%"
        send_log("HEARTBEAT", log_msg)
        print(f"Heartbeat Sent: {log_msg}")
    
        time.sleep(900) # 15 Minute Cycle

except KeyboardInterrupt:
    print("Stopping...")
    led.off()
    client.loop_stop()