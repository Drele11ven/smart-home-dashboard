class Lamp:
    POWER_WATT = 10  # energy consumption

    def __init__(self):
        self.on = False
        self.brightness = 0  # 0–100 %

    def turn_on(self, brightness=70):
        self.on = True
        self.brightness = brightness

    def turn_off(self):
        self.on = False
        self.brightness = 0


class AirConditioner:
    POWER_WATT = 1500

    def __init__(self):
        self.on = False
        self.target_temp = 24
        self.mode = "NORMAL"  # NORMAL / ECO

    def turn_on(self, target_temp=24):
        self.on = True
        self.target_temp = target_temp
        self.mode = "NORMAL"

    def set_eco(self):
        self.on = True
        self.mode = "ECO"
        self.target_temp = 26

    def turn_off(self):
        self.on = False


class Curtain:
    def __init__(self):
        self.position = "CLOSED"  # OPEN / CLOSED / HALF

    def open(self):
        self.position = "OPEN"

    def close(self):
        self.position = "CLOSED"

    def half(self):
        self.position = "HALF"
