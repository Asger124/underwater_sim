#!/usr/bin/env python3
"""
Diagnostic: arm in MANUAL, 3s neutral then 5s forward, and print what ArduSub
reports (arm state, status text, motor outputs).
Run with ArduSub + Stonefish already running.
"""
import time
from pymavlink import mavutil

FORWARD_INPUT = 600
TURN_INPUT = 300

INITIAL_WAIT = 3.0
FORWARD_TIME = 5.0
TURN_TIME = 3.0       # Initial trial; calibrate to reach 90 degrees
PAUSE_TIME = 3.0
FINAL_WAIT = 2.0

SEND_INTERVAL = 0.1

CONN = "tcp:127.0.0.1:5772"

m = mavutil.mavlink_connection(CONN)
print("Waiting for heartbeat...")
m.wait_heartbeat()
print(f"Connected: system {m.target_system}, component {m.target_component}")

def send_control(x=0, y=0, z=500, r=0):
    """Send one manual control command."""
    m.mav.manual_control_send(
        m.target_system, x, y, z, r, 0
    )

def run_phase(name, duration, x=0, y=0, z=500, r=0):
    """Repeat a control command for a specified duration."""
    print(f"{name}: {duration:.1f} seconds")

    start = time.monotonic()

    while time.monotonic() - start < duration:
        send_control(x, y, z, r)
        time.sleep(SEND_INTERVAL)
         # Briefly command neutral after every phase.
    send_control(0, 0, 500, 0)


# A direct connection to ardusub (no MAVProxy) does not stream data by default,
# so ask for it explicitly.
m.mav.request_data_stream_send(
    m.target_system, m.target_component,
    mavutil.mavlink.MAV_DATA_STREAM_ALL, 10, 1)

try:
    # Select MANUAL mode and arm.
    m.set_mode(m.mode_mapping()["MANUAL"])
    time.sleep(1)

    m.arducopter_arm()
    time.sleep(1)

    # Phase 1: initial neutral period
    run_phase("Initial neutral", INITIAL_WAIT)

    # Phase 2: first straight segment
    run_phase(
        "Forward segment 1",
        FORWARD_TIME,
        x=FORWARD_INPUT
    )

    # Phase 3: allow motion to settle
    run_phase("Pause before turn", PAUSE_TIME)

    # Phase 4: rotate in place
    run_phase(
        "Turn",
        TURN_TIME,
        r=TURN_INPUT
    )

    # Phase 5: allow rotation to settle
    run_phase("Pause after turn", PAUSE_TIME)

    # Phase 6: second straight segment
    run_phase(
        "Forward segment 2",
        FORWARD_TIME,
        x=FORWARD_INPUT) 

    # Phase 7: allow motion to settle2
    run_phase("Pause before turn2", PAUSE_TIME)

    # Phase 8: rotate in place again
    run_phase(
            "Turn",
            TURN_TIME,
            r=TURN_INPUT
        )

    # Phase 9: allow rotation to settle
    run_phase("Pause after turn2", PAUSE_TIME)

    # Phase 10: third straight segment
    run_phase(
        "Forward segment 3",
        FORWARD_TIME,
        x=FORWARD_INPUT)

    # Phase 11: allow motion to settle3
    run_phase("Pause before turn3", PAUSE_TIME)

    # Phase 12: rotate in place again
    run_phase(
            "Turn",
            TURN_TIME,
            r=TURN_INPUT
        )   
    # Phase 13: allow rotation to settle
    run_phase("Pause after turn3", PAUSE_TIME)

    # Phase 14: finish 
    run_phase("final forward segment", FORWARD_TIME, x=FORWARD_INPUT)   

    # Phase 15: finish
    run_phase("Final neutral", FINAL_WAIT)

finally:
    # Always attempt to stop movement before disarming.
    send_control(0, 0, 500, 0)
    time.sleep(0.5)
    m.arducopter_disarm()
    print("Experiment finished.")

# m.set_mode(m.mode_mapping()["MANUAL"])
# time.sleep(1)
# m.arducopter_arm()

# t0 = time.time()
# armed = False
# last_print = 0
# while time.time() - t0 < 8:
#     elapsed = time.time() - t0
#     x = 0 if elapsed < 3 else 600
#     m.mav.manual_control_send(m.target_system, x, 0, 500, 0, 0)

#     while True:
#         msg = m.recv_match(blocking=False)
#         if msg is None:
#             break
#         t = msg.get_type()
#         if t == "STATUSTEXT":
#             print("STATUS:", msg.text)
#         elif t == "HEARTBEAT" and msg.get_srcSystem() == m.target_system:
#             armed = bool(msg.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED)
#         elif t == "SERVO_OUTPUT_RAW" and time.time() - last_print > 0.5:
#             last_print = time.time()
#             servos = [getattr(msg, f"servo{i}_raw") for i in range(1, 9)]
#             print(f"t={elapsed:4.1f}s x={x:3d} armed={armed} servos={servos}")
#     time.sleep(0.1)

# m.mav.manual_control_send(m.target_system, 0, 0, 500, 0, 0)
# m.arducopter_disarm()
# print("Done")
