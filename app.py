import streamlit as st
import pandas as pd
import math

from streamlit_autorefresh import st_autorefresh
from core.models import House
from core.controller import AutoController
from core.energy import EnergyMonitor
from data.preferences import COMFORT
from core.simulation import run_24h_simulation

def comfort_score(room):
    if not room.presence:
        return 100

    # --- Temperature comfort ---
    if COMFORT["temp_min"] <= room.temperature <= COMFORT["temp_max"]:
        temp_score = 100
    else:
        dist = min(
            abs(room.temperature - COMFORT["temp_min"]),
            abs(room.temperature - COMFORT["temp_max"])
        )
        temp_score = max(0, 100 - dist * 20)

    # --- Light comfort ---
    if room.light >= COMFORT["light_min"]:
        light_score = 100
    else:
        light_score = max(0, (room.light / COMFORT["light_min"]) * 100)

    return round(0.6 * temp_score + 0.4 * light_score, 1)



# =========================
# Page Config
# =========================
st.set_page_config(
    page_title="Smart Home Dashboard",
    layout="wide"
)


# =========================
# Session State Init
# =========================
if "house" not in st.session_state:
    st.session_state.house = House()
    st.session_state.controller = AutoController()
    st.session_state.energy = EnergyMonitor()
    st.session_state.auto_mode = True

    st.session_state.sim_minute = 0
    st.session_state.sim_running = True

    st.session_state.energy_auto = 0.0
    st.session_state.energy_manual = 0.0


house = st.session_state.house
controller = st.session_state.controller
energy = st.session_state.energy


# =========================
# Simulation Models
# =========================
def outdoor_environment(sim_minute):
    """
    24h sinusoidal day/night model
    """
    temp = 20 + 10 * math.sin((sim_minute - 360) * math.pi / 720)
    light = max(0, 100 * math.sin((sim_minute - 360) * math.pi / 720))
    return round(temp, 1), int(light)


def update_room_physics(room, outdoor_temp, outdoor_light):
    """
    Indoor physics simulation
    """

    # Temperature behavior
    if room.ac.on:
        target = room.ac.target_temp
        room.temp_sensor.set(
            room.temperature + (target - room.temperature) * 0.1
        )
    else:
        room.temp_sensor.set(
            room.temperature + (outdoor_temp - room.temperature) * 0.02
        )

    # Light behavior
    light = room.light_sensor.read()

    if room.curtain.position == "OPEN":
        light += outdoor_light * 0.3

    if room.lamp.on:
        light += room.lamp.brightness * 0.5

    room.light_sensor.set(min(100, int(light)))


# =========================
# Sidebar
# =========================
st.sidebar.header("⏱ Simulation Control")

hour = st.session_state.sim_minute // 60
minute = st.session_state.sim_minute % 60

st.sidebar.write(f"Simulated Time: **{hour:02d}:{minute:02d}**")

st.session_state.sim_running = st.sidebar.toggle(
    "Run Simulation",
    value=st.session_state.sim_running
)

st.session_state.auto_mode = st.sidebar.toggle(
    "AUTO Mode",
    value=st.session_state.auto_mode
)

st.sidebar.markdown("---")
st.sidebar.metric(
    "Total Energy (Wh)",
    round(energy.total_energy_wh, 2)
)



# =========================
# Global Environment
# =========================
outdoor_temp, outdoor_light = outdoor_environment(st.session_state.sim_minute)

st.sidebar.markdown("---")
st.sidebar.subheader("🌍 Outdoor Environment")
st.sidebar.write(f"🌡 Temperature: **{outdoor_temp} °C**")
st.sidebar.write(f"☀ Light: **{outdoor_light} %**")

st.sidebar.markdown("## 😊 Overall Comfort")

scores = [
    comfort_score(room)
    for room in house.rooms.values()
    if room.presence
]

overall = round(sum(scores) / len(scores), 1) if scores else 100
st.sidebar.metric("House Comfort Score", f"{overall} / 100")



st.sidebar.markdown("---")
st.sidebar.header("Simulation Control")

run_simulation = st.sidebar.button("Run 24h AUTO vs MANUAL")

manual_temp = st.sidebar.slider("Manual Target Temp (°C)", 18, 30, 24)
manual_light = st.sidebar.slider("Manual Light Level (%)", 0, 100, 70)
manual_curtain = st.sidebar.selectbox("Curtain Position", ["OPEN", "CLOSED"])
manual_ac = st.sidebar.checkbox("AC ON", True)
manual_lamp = st.sidebar.checkbox("Lamp ON", True)
if run_simulation:
    settings = {
        "temp": manual_temp,
        "light": manual_light,
        "curtain": manual_curtain,
        "ac": manual_ac,
        "lamp": manual_lamp,
    }

    df = run_24h_simulation(settings)

    st.header("24-Hour AUTO vs MANUAL Comparison")

    st.subheader("Energy Consumption (Wh)")
    st.line_chart(df[["AUTO Energy", "MANUAL Energy"]])

    st.subheader("Comfort Score")
    st.line_chart(df[["AUTO Comfort", "MANUAL Comfort"]])

    auto_total = df["AUTO Energy"].sum()
    manual_total = df["MANUAL Energy"].sum()

    savings = manual_total - auto_total

    st.metric("AUTO Energy (Wh)", f"{auto_total:.1f}")
    st.metric("MANUAL Energy (Wh)", f"{manual_total:.1f}")
    st.metric("Energy Saved (Wh)", f"{savings:.1f}")
# =========================
# Main UI
# =========================
st.title("🏠 Smart Home Simulator")

st.markdown("## Rooms")

for room_name, room in house.rooms.items():
    with st.expander(room_name, expanded=True):

        col1, col2, col3 = st.columns(3)

        # ---------- Sensors ----------
        with col1:
            st.subheader("Sensors")

            st.write(f"Indoor Temp: **{room.temperature:.1f} °C**")
            st.write(f"Indoor Light: **{room.light} %**")

            # Presence simulation (day logic)
            current_hour = st.session_state.sim_minute // 60
            presence = 7 <= current_hour <= 23
            room.presence_sensor.set(presence)

            st.write("Presence:", "YES" if room.presence else "NO")

        # ---------- Actuators ----------
        with col2:
            st.subheader("Actuators")

            if not st.session_state.auto_mode:
                if st.button("Lamp ON", key=f"{room_name}_lamp_on"):
                    room.lamp.turn_on()

                if st.button("Lamp OFF", key=f"{room_name}_lamp_off"):
                    room.lamp.turn_off()

                room.ac.target_temp = st.slider(
                    "AC Target (°C)",
                    18, 30, room.ac.target_temp,
                    key=f"{room_name}_ac_target"
                )

                if st.button("AC ON", key=f"{room_name}_ac_on"):
                    room.ac.turn_on(room.ac.target_temp)

                if st.button("AC OFF", key=f"{room_name}_ac_off"):
                    room.ac.turn_off()

                if st.button("Curtain OPEN", key=f"{room_name}_curtain_open"):
                    room.curtain.open()

                if st.button("Curtain CLOSE", key=f"{room_name}_curtain_close"):
                    room.curtain.close()

        # ---------- Status ----------
        with col3:
            st.subheader("Status")

            st.write(f"💡 Lamp: **{'ON' if room.lamp.on else 'OFF'}**")
            st.write(f"❄ AC: **{'ON' if room.ac.on else 'OFF'}**")
            st.write(f"🎯 AC Target: **{room.ac.target_temp} °C**")
            st.write(f"🪟 Curtain: **{room.curtain.position}**")

        # ---------- Simulation Step ----------
        update_room_physics(room, outdoor_temp, outdoor_light)

        if st.session_state.auto_mode:
            controller.control_room(room, outdoor_temp, outdoor_light)

        energy.update(room, minutes=1)


# =========================
# Energy Accounting
# =========================
if st.session_state.auto_mode:
    st.session_state.energy_auto += energy.total_energy_wh
else:
    st.session_state.energy_manual += energy.total_energy_wh


# =========================
# Energy Charts
# =========================
st.markdown("---")
st.markdown("## 🔋 Energy Monitoring")

energy.snapshot()
df = pd.DataFrame(energy.history)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Total Energy Over Time")
    st.line_chart(df["total"])

with col2:
    st.subheader("Energy by Device")
    st.area_chart(df[["lamp", "ac"]])


# =========================
# House Overview
# =========================
st.markdown("---")
st.markdown("## 🗺 House Overview")

cols = st.columns(len(house.rooms))

for col, (name, room) in zip(cols, house.rooms.items()):
    with col:
        st.markdown(f"### {name}")
        st.metric("Temp (°C)", f"{room.temperature:.1f}")
        st.metric("Light (%)", room.light)
        st.metric("Presence", "YES" if room.presence else "NO")
        st.write("💡 Lamp:", "ON" if room.lamp.on else "OFF")
        st.write("❄ AC:", "ON" if room.ac.on else "OFF")
        st.write("🪟 Curtain:", room.curtain.position)
        score = comfort_score(room)
        st.metric("😊 Comfort Score", f"{score} / 100")
        st.markdown("---")


# =========================
# AUTO vs MANUAL Comparison
# =========================
st.markdown("---")
st.markdown("## ⚖ AUTO vs MANUAL Energy Usage")

compare_df = pd.DataFrame({
    "Mode": ["AUTO", "MANUAL"],
    "Energy (Wh)": [
        st.session_state.energy_auto,
        st.session_state.energy_manual
    ]
})

st.bar_chart(compare_df.set_index("Mode"))


# =========================
# Advance Time
# =========================
if st.session_state.sim_running:
    st_autorefresh(interval=300, key="sim_clock")  # 300 ms per minute
    st.session_state.sim_minute = (st.session_state.sim_minute + 1) % 1440
