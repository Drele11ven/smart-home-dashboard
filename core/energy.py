class EnergyMonitor:
    def __init__(self):
        self.total_energy_wh = 0.0
        self.device_log = {
            "lamp": 0.0,
            "ac": 0.0,
        }
        self.history = []  # snapshot history

    def update(self, room, minutes=1):
        hours = minutes / 60.0

        if room.lamp.on:
            e = room.lamp.POWER_WATT * hours
            self.device_log["lamp"] += e
            self.total_energy_wh += e

        if room.ac.on:
            e = room.ac.POWER_WATT * hours
            self.device_log["ac"] += e
            self.total_energy_wh += e

    def snapshot(self):
        self.history.append({
            "lamp": self.device_log["lamp"],
            "ac": self.device_log["ac"],
            "total": self.total_energy_wh
        })

    def reset(self):
        self.total_energy_wh = 0.0
        self.device_log = {"lamp": 0.0, "ac": 0.0}
        self.history = []
