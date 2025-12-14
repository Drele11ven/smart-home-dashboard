from data.preferences import COMFORT

class AutoController:
    def control_room(self, room, outdoor_temp, outdoor_light):

        # --- 1. No presence → ECO ---
        if not room.presence:
            room.lamp.turn_off()
            room.curtain.close()
            room.ac.turn_on(COMFORT["eco_temp"])
            return

        # --- 2. LIGHTING (prefer daylight, then lamp) ---
        if room.light < COMFORT["light_min"]:
            if outdoor_light > 50:
                room.curtain.open()
                room.lamp.turn_off()
            else:
                room.curtain.close()
                room.lamp.turn_on(50)
        else:
            room.lamp.turn_off()

        # --- 3. TEMPERATURE (energy-aware) ---
        if room.temperature > COMFORT["temp_max"]:
            if outdoor_temp < room.temperature:
                room.curtain.open()        # passive cooling
                room.ac.turn_off()
            else:
                room.curtain.close()
                room.ac.turn_on(COMFORT["temp_max"])

        elif room.temperature < COMFORT["temp_min"]:
            room.curtain.close()
            room.ac.turn_off()

        else:
            # Inside comfort band → avoid wasting energy
            room.ac.turn_off()
