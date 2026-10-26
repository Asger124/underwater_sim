#!/usr/bin/env python3
"""
Simple square: forward, turn 90 deg right, repeat 4 times.
Run (venv active):  python3 square.py
Tune SIDE_SECONDS / FWD to change the size of the square.
"""
import math
import time
from pymavlink import mavutil

CONN = "tcp:127.0.0.1:5772"
MODE = "MANUAL"
FWD = 600            # forward thrust (-1000..1000)
SIDE_SECONDS = 5     # how long to drive each side
COAST_SECONDS = 1    # pause before each turn
TURN_DEG = 90        # positive = right (clockwise)
HZ = 20              # control message rate

yaw = None           # latest heading in degrees


def pump(m):
    """Read all waiting messages without blocking, keep latest heading."""
    global yaw
    while (msg := m.recv_match(blocking=False)) is not None:
        t = msg.get_type()
        if t == "ATTITUDE":
            yaw = math.degrees(msg.yaw) % 360
        elif t == "STATUSTEXT":
            print("STATUS:", msg.text)


def step(m, x=0, r=0):
    """One control tick: read messages, send command, wait."""
    pump(m)
    m.mav.manual_control_send(m.target_system, x, 0, 500, r, 0)
    time.sleep(1.0 / HZ)


def drive(m, seconds, x=0, r=0):
    end = time.time() + seconds
    while time.time() < end:
        step(m, x, r)


def turn(m, degrees, timeout=15):
    while yaw is None:          # wait for first heading
        step(m)
    target = (yaw + degrees) % 360
    end = time.time() + timeout
    while time.time() < end:
        err = (target - yaw + 540) % 360 - 180
        if abs(err) < 4:
            break
        step(m, r=int(max(-400, min(400, err * 8))))
    drive(m, 1)                 # settle


m = mavutil.mavlink_connection(CONN)
print("Waiting for heartbeat...")
m.wait_heartbeat()
m.mav.request_data_stream_send(
    m.target_system, m.target_component, mavutil.mavlink.MAV_DATA_STREAM_ALL, 10, 1)

m.set_mode(m.mode_mapping()[MODE])
drive(m, 1)
m.arducopter_arm()
m.motors_armed_wait()
print("Armed")

try:
    for side in range(1, 5):
        print(f"Side {side}")
        drive(m, SIDE_SECONDS, x=FWD)
        drive(m, COAST_SECONDS)
        turn(m, TURN_DEG)
    print("Square done")
finally:
    m.mav.manual_control_send(m.target_system, 0, 0, 500, 0, 0)
    time.sleep(0.5)
    m.arducopter_disarm()
    print("Disarmed")
