
import adafruit_dht
from gpiozero import MotionSensor, LightSensor

class dht22_sensor:
    def __init__(self, pin):
        self.dht22 = adafruit_dht.DHT22(pin)

    def read_sensor(self):
        try:
            return self.dht22.temperature, self.dht22.humidity

        except RuntimeError as error:
            # DHT sensors are tricky. Common errors are checksum failures.
            # We just ignore the error and try again next loop.
            print(f"DHT Reading Error: {error.args[0]}")
            
            return None, None

        except Exception as error:
            self.dht22.exit()
            raise error
    def exit(self):
        self.dht22.exit()
        
class pir_sensor:
    def __init__(self, pin):
        self.pir_sensor = MotionSensor(pin)

    def motion_detected(self):
        return self.pir_sensor.motion_detected