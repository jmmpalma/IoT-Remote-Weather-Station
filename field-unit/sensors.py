import time
import board
import busio
from adafruit_bme280 import basic as adafruit_bme280
import adafruit_bh1750
from gpiozero import CPUTemperature

class SensorManager:
    def __init__(self):
        self.i2c = board.I2C()
        self.cpu = CPUTemperature()
        self.bme = None
        self.bh1750 = None
        self.setup_sensors()

    def setup_sensors(self):
        # BME280 Initialization
        try:
            self.bme = adafruit_bme280.Adafruit_BME280_I2C(self.i2c, address=0x76)
            print("BME280: Initialized")
        except Exception as e:
            print(f"BME280: Failed to initialize sensor ({e})")

        # BH1750 Initialization
        try:
            self.bh1750 = adafruit_bh1750.BH1750(self.i2c)
            print("BH1750: Initialized")
        except Exception as e:
            print(f"BH1750: Failed to initialize sensor ({e})")

    def read_all(self):
        # Default empty values
        data = {"temp": 0.0, "hum": 0.0, "press": 0.0, "lux": 0.0, "cpu": 0.0}
        
        # 1. CPU Temp
        data["cpu"] = round(self.cpu.temperature, 1)

        # 2. BME280 with internal retry
        if self.bme:
            for _ in range(3):
                try:
                    data["temp"] = round(self.bme.temperature, 1)
                    data["hum"] = round(self.bme.humidity, 1)
                    data["press"] = round(self.bme.pressure, 1)
                    break
                except:
                    time.sleep(0.5)

        # 3. Light Sensor
        if self.bh1750:
            try:
                data["lux"] = round(self.bh1750.lux, 1)
            except:
                pass

        return data