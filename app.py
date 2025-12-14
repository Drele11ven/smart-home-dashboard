
from core.models import House

house = House()
room = house.rooms["Living Room"]

room.temp_sensor.set(28)
room.presence_sensor.set(True)

room.lamp.turn_on()
room.ac.turn_on(23)

print(room.temperature)
print(room.lamp.on, room.ac.target_temp)
