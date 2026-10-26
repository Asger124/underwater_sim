#!/usr/bin/env python3
"""
Simple patterns for ArduSub (SITL) driving the Stonefish BlueROV2 (Heavy, FRAME_CONFIG 2).
Usage (venv active):
    python3 rov_patterns.py rectangle
    python3 rov_patterns.py circle
    python3 rov_patterns.py rectangle MANUAL     # optional mode override

Key points:
 - requests the MAVLink data stream (needed on a direct TCP connection)
 - MANUAL_CONTROL is sent continuously, also while waiting for attitude data
 - turns are closed-loop on ATTITUDE yaw
"""
import sys
import time
import math
from pymavlink import mavutil

CONN = "tcp:127.0.0.1:5772"
RATE_HZ = 10
MODE = "ALT_HOLD"      # depth hold; use "MANUAL" if depth control misbehaves

FWD = 600              # forward thrust, -1000..1000 (600 is known to move the ROV)
YAW_MAX = 400          # max yaw command during turns
YAW_KP = 8             # proportional gain: command per degree of error

SIDE_LONG_S = 6        # seconds of forward motion for the long sides
SIDE_SHORT_S = 3       # seconds of forward motion for the short sides

state = {"yaw": None, "armed": None, "expect_armed": False, "last_send": None}


def connect():
    m = mavutil.mavlink_connection(CONN)
    print("Waiting for heartbeat...")
    m.wait_heartbeat()
    print(f"Connected: system {m.target_system}, component {m.target_component}")
    m.mav.request_data_stream_send(
        m.target_system, m.target_component,
        mavutil.mavlink.MAV_DATA_STREAM_ALL, 10, 1)
    return m


def pump(m):
    """Drain all pending messages without blocking; keep latest yaw and print status text."""
    while True:
        msg = m.recv_match(blocking=False)
        if msg is None:
            return
        t = msg.get_type()
        if t == "ATTITUDE":
            state["yaw"] = math.degrees(msg.yaw) % 360
        elif t == "HEARTBEAT" and msg.get_srcSystem() == m.target_system:
            state["armed"] = bool(msg.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED)
        elif t == "STATUSTEXT":
            print("STATUS:", msg.text)


def send(m, x=0, y=0, z=500, r=0):
    """x fwd, y right, z thrust (500 = neutral), r yaw."""
    m.mav.manual_control_send(m.target_system, x, y, z, r, 0)


def tick(m, **kw):
    pump(m)
    if state["expect_armed"] and state["armed"] is False:
        raise RuntimeError("Vehicle disarmed (failsafe?), aborting")
    now = time.time()
    if state["last_send"] is not None and now - state["last_send"] > 0.5:
        print(f"WARNING: control gap of {now - state['last_send']:.2f}s")
    state["last_send"] = now
    send(m, **kw)
    time.sleep(1.0 / RATE_HZ)


def hold(m, seconds, **kw):
    end = time.time() + seconds
    while time.time() < end:
        tick(m, **kw)


def wait_for_yaw(m, timeout=5):
    end = time.time() + timeout
    while state["yaw"] is None and time.time() < end:
        tick(m)
    return state["yaw"] is not None


def turn_by(m, degrees, tol=4.0, timeout=20):
    """Closed-loop turn; positive = clockwise (right)."""
    if not wait_for_yaw(m):
        print("WARNING: no ATTITUDE received, doing a blind timed turn")
        hold(m, abs(degrees) / 15.0, r=300 if degrees > 0 else -300)
        return
    target = (state["yaw"] + degrees) % 360
    t0 = time.time()
    while time.time() - t0 < timeout:
        pump(m)
        err = (target - state["yaw"] + 540) % 360 - 180   # signed, -180..180
        if abs(err) < tol:
            break
        cmd = int(max(-YAW_MAX, min(YAW_MAX, err * YAW_KP)))
        send(m, r=cmd)
        time.sleep(1.0 / RATE_HZ)
    else:
        print("WARNING: turn timed out")
    hold(m, 1.0)   # let it settle


def set_mode(m, name):
    m.set_mode(m.mode_mapping()[name])
    print(f"Mode -> {name}")
    hold(m, 1)


def arm(m):
    m.arducopter_arm()
    m.motors_armed_wait()
    state["armed"] = True
    state["expect_armed"] = True
    print("Armed")


def disarm(m):
    hold(m, 1)
    m.arducopter_disarm()
    m.motors_disarmed_wait()
    print("Disarmed")


def rectangle(m):
    for i, side in enumerate((SIDE_LONG_S, SIDE_SHORT_S, SIDE_LONG_S, SIDE_SHORT_S), 1):
        print(f"Side {i}: forward {side}s")
        hold(m, side, x=FWD)
        hold(m, 1.0)               # coast to a stop
        print("Turn 90 deg right")
        turn_by(m, 90)


def circle(m, duration=40):
    # forward + constant yaw rate = circle; radius grows with FWD / yaw rate
    print("Circling...")
    hold(m, duration, x=FWD, r=200)


if __name__ == "__main__":
    pattern = sys.argv[1] if len(sys.argv) > 1 else "rectangle"
    if len(sys.argv) > 2:
        MODE = sys.argv[2].upper()

    m = connect()
    set_mode(m, MODE)
    arm(m)
    try:
        wait_for_yaw(m)
        if pattern == "circle":
            circle(m)
        else:
            rectangle(m)
    except KeyboardInterrupt:
        print("Interrupted")
    except RuntimeError as e:
        print(e)
    finally:
        state["expect_armed"] = False
        send(m)                 # neutral
        disarm(m)
