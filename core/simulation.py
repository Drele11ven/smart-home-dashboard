# core/simulation.py

import math
import pandas as pd
from core.models import House
from core.controller import AutoController
from core.energy import EnergyMonitor
from data.preferences import COMFORT


def outdoor_environment(hour):
    """
    Hour-based outdoor model (24h sinusoidal for temp and light)
    """
    minute = hour * 60
    temp = 20 + 10 * math.sin((minute - 360) * math.pi / 720)
    light = max(0, 100 * math.sin((minute - 360) * math.pi / 720))
    return round(temp, 1), int(light)


def comfort_score(room):
    """
    Calculate comfort based on temperature and light
    """
    if not room.presence:
        return 100  # empty room → full comfort

    # Temperature comfort
    if COMFORT["temp_min"] <= room.temperature <= COMFORT["temp_max"]:
        temp_score = 100
    else:
        dist = min(abs(room.temperature - COMFORT["temp_min"]),
                   abs(room.temperature - COMFORT["temp_max"]))
        temp_score = max(0, 100 - dist * 20)

    # Light comfort
    if room.light >= COMFORT["light_min"]:
        light_score = 100
    else:
        light_score = max(0, (room.light / COMFORT["light_min"]) * 100)

    return round(0.6 * temp_score + 0.4 * light_score, 1)


def simulate_hour(house, controller, outdoor_temp, outdoor_light, hour, manual_settings=None):
    """
    Simulate 1 hour for all rooms.
    If manual_settings=None → AUTO mode, else MANUAL mode
    """
    hourly_energy = 0
    comfort_list = []

    for room in house.rooms.values():

        # ---------- Presence simulation ----------
        # People absent during office hours (9-17)
        if 9 <= hour < 17:
            room.presence_sensor.set(False)
        else:
            room.presence_sensor.set(True)

        # ---------- Manual mode ----------
        if manual_settings:
            room.temp_sensor.set(manual_settings["temp"])
            room.light_sensor.set(manual_settings["light"])

            if manual_settings["ac"]:
                room.ac.turn_on(manual_settings["temp"])
            else:
                room.ac.turn_off()

            if manual_settings["lamp"]:
                room.lamp.turn_on()
            else:
                room.lamp.turn_off()

            if manual_settings["curtain"] == "OPEN":
                room.curtain.open()
            else:
                room.curtain.close()

            # Outdoor influence for manual curtains
            if room.curtain.position == "OPEN":
                room.light_sensor.set(min(100, room.light + int(outdoor_light * 0.3)))

        # ---------- AUTO mode ----------
        else:
            controller.control_room(room, outdoor_temp, outdoor_light)

        # ---------- Indoor physics ----------
        # Temperature dynamics
        if room.ac.on:
            target = room.ac.target_temp
            room.temp_sensor.set(room.temperature + (target - room.temperature) * 0.1)
        else:
            room.temp_sensor.set(room.temperature + (outdoor_temp - room.temperature) * 0.02)

        # Light dynamics
        light = room.light_sensor.read()
        if room.curtain.position == "OPEN":
            light += outdoor_light * 0.3
        if room.lamp.on:
            light += room.lamp.brightness * 0.5
        room.light_sensor.set(min(100, int(light)))

        # ---------- Hourly energy ----------
        lamp_energy = room.lamp.POWER_WATT * 1 if room.lamp.on else 0
        ac_energy = room.ac.POWER_WATT * 1 if room.ac.on else 0
        hourly_energy += lamp_energy + ac_energy

        # ---------- Comfort ----------
        comfort_list.append(comfort_score(room))

    avg_comfort = sum(comfort_list) / len(comfort_list)
    return hourly_energy, avg_comfort


def run_24h_simulation(manual_settings):
    """
    Runs 24h simulation for AUTO vs MANUAL
    """
    auto_house = House()
    manual_house = House()
    auto_controller = AutoController()

    auto_energy_hourly = []
    manual_energy_hourly = []
    auto_comfort_hourly = []
    manual_comfort_hourly = []

    for hour in range(24):
        # Outdoor environment
        outdoor_temp, outdoor_light = outdoor_environment(hour)

        # ---------- AUTO ----------
        energy_auto, comfort_auto = simulate_hour(
            auto_house, auto_controller,
            outdoor_temp, outdoor_light,
            hour, manual_settings=None
        )
        auto_energy_hourly.append(energy_auto)
        auto_comfort_hourly.append(comfort_auto)

        # ---------- MANUAL ----------
        energy_manual, comfort_manual = simulate_hour(
            manual_house, auto_controller,
            outdoor_temp, outdoor_light,
            hour, manual_settings=manual_settings
        )
        manual_energy_hourly.append(energy_manual)
        manual_comfort_hourly.append(comfort_manual)

    return pd.DataFrame({
        "Hour": list(range(24)),
        "AUTO Energy": auto_energy_hourly,
        "MANUAL Energy": manual_energy_hourly,
        "AUTO Comfort": auto_comfort_hourly,
        "MANUAL Comfort": manual_comfort_hourly,
    })
