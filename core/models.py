from core.sensors import TemperatureSensor, LightSensor, PresenceSensor
from core.actuators import Lamp, AirConditioner, Curtain


class Room:
    def __init__(self, name):
        self.name = name

        # Sensors
        self.temp_sensor = TemperatureSensor()
        self.light_sensor = LightSensor()
        self.presence_sensor = PresenceSensor()

        # Actuators
        self.lamp = Lamp()
        self.ac = AirConditioner()
        self.curtain = Curtain()

    @property
    def temperature(self):
        return self.temp_sensor.read()

    @property
    def light(self):
        return self.light_sensor.read()

    @property
    def presence(self):
        return self.presence_sensor.read()


class House:
    def __init__(self):
        self.rooms = {
            "Living Room": Room("Living Room"),
            "Bedroom": Room("Bedroom"),
            "Kitchen": Room("Kitchen"),
        }
