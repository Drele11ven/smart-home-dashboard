from core.models import House
from core.controller import AutoController
from core.energy import EnergyMonitor

house = House()
controller = AutoController()
energy = EnergyMonitor()

room = house.rooms["Living Room"]

room.temp_sensor.set(30)
room.light_sensor.set(10)
room.presence_sensor.set(True)

outdoor_temp = 35
outdoor_light = 20

# Simulate 10 minutes
for _ in range(10):
    controller.control_room(room, outdoor_temp, outdoor_light)
    energy.update(room, minutes=1)

print("Total Energy (Wh):", round(energy.total_energy_wh, 2))
print("Details:", energy.device_log)
