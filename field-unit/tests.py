import adafruit_dht
from gpiozero import MotionSensor, LightSensor,RGBLED,LED
from colorzero import Color
import time
from sensors import dht22_sensor, pir_sensor
import board

pir = MotionSensor(17)
led = RGBLED(27, 22, 23)
dht22 = dht22_sensor(board.D4)

def idle():
    led.blink(on_time=1, off_time=5, fade_in_time=1, fade_out_time=1, on_color=(0, 1, 0), off_color=(0, 0, 0), n=None, background=True)
    print("Idle state")

def motion():
    led.blink(on_time=0.3, off_time=0.3, fade_in_time=0.1, fade_out_time=0.1, on_color=(1, 0, 0), off_color=(0, 0, 0), n=None, background=True)
    print("Motion detected!")

def read_sensors(pir_state):
    led.color = Color('blue')
    print("Reading sensors...")
    time.sleep(0.5)
    temperature,humidity = dht22.read_sensor()

    if temperature is not None:
        print(f"Temp: {temperature:.1f}ºC  |  Humidity: {humidity:.1f}%")
    else:
        print("Failed to retrieve data from humidity sensor")
    
    if pir_state.motion_detected:
        motion()
    else:
        idle()
        
pir.when_motion = motion
pir.when_no_motion = idle

try: 
    while True:
        print("The script is running...")
        read_sensors(pir)
        time.sleep(30)
        

except KeyboardInterrupt:
    led.off()
    print("Program interrupted by user")