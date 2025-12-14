class EnergyMonitor:
    def __init__(self):
        self.total_energy_wh = 0.0
        self.device_log = {
            "lamp": 0.0,
            "ac": 0.0,
        }

    def update(self, room, minutes=1):
        """
        Accumulate energy usage based on device state
        """
        hours = minutes / 60.0

        # Lamp energy
        if room.lamp.on:
            lamp_energy = room.lamp.POWER_WATT * hours
            self.device_log["lamp"] += lamp_energy
            self.total_energy_wh += lamp_energy

        # AC energy
        if room.ac.on:
            ac_energy = room.ac.POWER_WATT * hours
            self.device_log["ac"] += ac_energy
            self.total_energy_wh += ac_energy

    def reset(self):
        self.total_energy_wh = 0.0
        for k in self.device_log:
            self.device_log[k] = 0.0
