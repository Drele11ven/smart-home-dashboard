from data.preferences import COMFORT


class AutoController:
    def control_room(self, room, outdoor_temp, outdoor_light):
        """
        Automatically controls room actuators based on:
        - indoor conditions
        - outdoor conditions
        - presence
        - comfort preferences
        """

        # 1. No presence → energy saving
        if not room.presence:
            room.lamp.turn_off()
            room.ac.set_eco()
            room.curtain.close()
            return

        # 2. Lighting logic
        if room.light < COMFORT["light_min"]:
            if outdoor_light > 60:
                room.curtain.open()
                room.lamp.turn_off()
            else:
                room.curtain.close()
                room.lamp.turn_on(70)
        else:
            room.lamp.turn_off()

        # 3. Temperature logic
        if room.temperature > COMFORT["temp_max"]:
            if outdoor_temp < room.temperature:
                room.curtain.open()
                room.ac.turn_off()
            else:
                room.ac.turn_on(target_temp=23)

        elif room.temperature < COMFORT["temp_min"]:
            room.curtain.close()
            room.ac.turn_off()
