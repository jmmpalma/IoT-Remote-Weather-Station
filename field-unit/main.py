import time
import board
from sensors import dht22_sensor, pir_sensor

# --- CONFIGURATION ---
dht22 = dht22_sensor(board.D4)
pir = pir_sensor(17)

# --- TIMING VARIABLES ---
last_temp_read_time = 0
TEMP_READ_INTERVAL = 10.0  # Read temp every 10 seconds

print("Weather Station Initialized. Press Ctrl+C to stop.")

#try-except block to allow graceful exit on Ctrl+C
try:
    while True:
        # Task A: Check for movement

        
        ### Read temperature sensors Sensor ###
        current_time = time.time()

        temperature,humidity = dht22.read_sensor()

        if temperature is not None:
            print(f"Timestamp: {current_time:.1f} | Temp: {temperature:.1f}ºC  |  Humidity: {humidity:.1f}%")
        else:
            print("Sensor read None (Wait for next cycle)")
        
        # Wait 10 seconds before next read (DHT22 needs 2s rest)
        time.sleep(10.0)
        
except KeyboardInterrupt:
    print("\nExiting...")
    dht22.exit()