class TemperatureSensor:
    def __init__(self, value=22.0):
        self.value = value

    def read(self):
        return self.value

    def set(self, value):
        self.value = round(float(value), 1)


class LightSensor:
    def __init__(self, value=50):
        self.value = value  # 0–100

    def read(self):
        return self.value

    def set(self, value):
        self.value = int(value)


class PresenceSensor:
    def __init__(self, present=False):
        self.present = present

    def read(self):
        return self.present

    def set(self, present: bool):
        self.present = present
