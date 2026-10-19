# underwater_sim

BlueROV2 underwater simulation using ROS 2 Jazzy, Stonefish, and ArduSub SITL.

## Requirements

- Ubuntu 24.04
- ROS 2 Jazzy
- ArduPilot checked out at `~/ardupilot`
- `colcon`
- A graphical desktop for Stonefish

## First-time setup

From the repository root:

```bash
git submodule update --init --recursive
source /opt/ros/jazzy/setup.bash
cd ros_ws
colcon build --symlink-install
source install/setup.bash
```

If the build reports a missing `uint64_t` declaration in Stonefish, add this
line to `ros_ws/src/stonefish/Library/include/sensors/Sample.h`:

```cpp
#include <cstdint>
```

Then run the build again.

## Start the simulation

Use three terminals. Keep terminals 1 and 2 running.

### T1: Start ArduSub

```bash
cd ~/ardupilot
Tools/autotest/sim_vehicle.py \
  -v ArduSub \
  --model JSON \
  --no-mavproxy \
  --out=127.0.0.1:14550 \
  -P GPS1_TYPE=0 \
  -P EK3_SRC1_POSXY=6 \
  -P EK3_SRC1_VELXY=6 \
  -P EK3_SRC1_POSZ=1 \
  -P EK3_SRC1_YAW=1 \
  -P EK3_GPS_CHECK=0
```

Wait until ArduSub is running on `127.0.0.1:5760`.

### T2: Start Stonefish

```bash
cd ~/RP/underwater_sim
source /opt/ros/jazzy/setup.bash
source ros_ws/install/setup.bash
ros2 launch stonefish_bluerov2 bluerov2_sim.py
```

Wait until the Stonefish window is open and the bridge reports
`Callbacks received`.

### T3: Run the rectangle controller

```bash
cd ~/RP/underwater_sim
source /opt/ros/jazzy/setup.bash
source ros_ws/install/setup.bash
export PYTHONPATH="$HOME/ardupilot/modules/mavlink:$PYTHONPATH"
ros2 run stonefish_bluerov2 rectangle_mission.py
```

The controller:

- connects to ArduSub on TCP port `5760`;
- uses the Stonefish odometry topic `/bluerov2/odometry`;
- enters GUIDED mode and arms the vehicle;
- dives 1 metre and follows a 3 m by 2 m rectangle;
- disarms after returning to the start.

To change the rectangle:

```bash
ros2 run stonefish_bluerov2 rectangle_mission.py \
  --length 4 \
  --width 2 \
  --depth 1
```

All dimensions are in metres.

## Useful checks

Check that Stonefish is publishing odometry:

```bash
source /opt/ros/jazzy/setup.bash
source ~/RP/underwater_sim/ros_ws/install/setup.bash
ros2 topic echo /bluerov2/odometry
```

Check the thruster commands:

```bash
ros2 topic echo /bluerov2/setpoint/pwm
```

If the controller cannot connect, make sure T1 is still running and that
`SERIAL0 on TCP port 5760` appears in the ArduSub output.

If the vehicle does not enter GUIDED or arm, check the ArduSub terminal for
the pre-arm or mode error. Start T2 before T3 so odometry is available.

Press `Ctrl+C` in T3 to stop the controller. Then close T2 and T1.
