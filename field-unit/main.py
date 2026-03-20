import time
import json
import board
import adafruit_dht
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
# LED pins: Red=27, Green=22, Blue=23
led = RGBLED(red=27, green=22, blue=23)
# PIR on GPIO 17
pir = MotionSensor(17)
# DHT22 on GPIO 4 (Standard)
dht_device = adafruit_dht.DHT22(board.D4)

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

######################  Main Logic ######################
try:
    print(f"Connecting to VM at {config.MQTT_BROKER}...")
    client.connect(config.MQTT_BROKER, 1883, 60)
    client.loop_start() # Starts a background thread for MQTT communication
    start_heartbeat()   # Starts the Green pulse

    while True:
        # Capturing data from the DHT22
        # The DHT22 is unstable; we try 3 times before giving up
        temp, hum = None, None
        for _ in range(3):
            try:
                temp = dht_device.temperature
                hum = dht_device.humidity
                if temp is not None: break
            except RuntimeError:
                # DHT22 often throws a error; we just wait and retry
                time.sleep(2)
    
        # If we got a valid reading, send it to the Cloud
        if temp is not None:
            # Send DATA to weather_data table
            payload = json.dumps({"temp": temp, "hum": hum})
            client.publish("sensors/data", payload)
            
            # Send a rich log to the system_logs table
            # We include Ambient Temp, Humidity, and CPU Temp in the message
            log_msg = f"Health Status | CPU: {cpu_temp}C | Ambient: {temp}C | Hum: {hum}%"
            send_log("HEARTBEAT", log_msg)
            print(f"Heartbeat Sent: {log_msg}")
        else:
            # Even if DHT22 fails, we still send the CPU temp log so we know the Pi is alive
            log_msg = f"DHT22 Error | CPU Temp: {cpu_temp}C"
            send_log("SYSTEM_WARNING", log_msg)
            print(f"Warning Sent: {log_msg}")

        time.sleep(900) # 15 Minute Cycle

except KeyboardInterrupt:
    print("Stopping...")
    led.off()
    client.loop_stop()