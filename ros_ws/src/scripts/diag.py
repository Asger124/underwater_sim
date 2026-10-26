#!/usr/bin/env python3
"""
Diagnostic: arm in MANUAL, 3s neutral then 5s forward, and print what ArduSub
reports (arm state, status text, motor outputs).
Run with ArduSub + Stonefish already running.
"""
import time
from pymavlink import mavutil

CONN = "tcp:127.0.0.1:5772"

m = mavutil.mavlink_connection(CONN)
print("Waiting for heartbeat...")
m.wait_heartbeat()
print(f"Connected: system {m.target_system}, component {m.target_component}")

# A direct connection to ardusub (no MAVProxy) does not stream data by default,
# so ask for it explicitly.
m.mav.request_data_stream_send(
    m.target_system, m.target_component,
    mavutil.mavlink.MAV_DATA_STREAM_ALL, 10, 1)

m.set_mode(m.mode_mapping()["MANUAL"])
time.sleep(1)
m.arducopter_arm()

t0 = time.time()
armed = False
last_print = 0
while time.time() - t0 < 8:
    elapsed = time.time() - t0
    x = 0 if elapsed < 3 else 600
    m.mav.manual_control_send(m.target_system, x, 0, 500, 0, 0)

    while True:
        msg = m.recv_match(blocking=False)
        if msg is None:
            break
        t = msg.get_type()
        if t == "STATUSTEXT":
            print("STATUS:", msg.text)
        elif t == "HEARTBEAT" and msg.get_srcSystem() == m.target_system:
            armed = bool(msg.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED)
        elif t == "SERVO_OUTPUT_RAW" and time.time() - last_print > 0.5:
            last_print = time.time()
            servos = [getattr(msg, f"servo{i}_raw") for i in range(1, 9)]
            print(f"t={elapsed:4.1f}s x={x:3d} armed={armed} servos={servos}")
    time.sleep(0.1)

m.mav.manual_control_send(m.target_system, 0, 0, 500, 0, 0)
m.arducopter_disarm()
print("Done")
