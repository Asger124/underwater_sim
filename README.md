# underwater_sim

An underwater robotics simulation workspace using **ROS 2 Jazzy** and the
**Stonefish** simulator. This branch includes the Stonefish and Stonefish ROS 2
`v1.3` submodules and the BlueROV2 simulation package.

## Native BlueROV2 test

### Prerequisites

- Ubuntu 24.04
- ROS 2 Jazzy
- `colcon`
- Stonefish build dependencies: `build-essential`, `cmake`, `libglm-dev`,
  `libsdl2-dev`, `libfreetype6-dev`, `libglew-dev`, and `libboost-system-dev`

### Clone

```bash
git clone --branch addBlueRov2FromVm --recurse-submodules \
  https://github.com/Asger124/underwater_sim.git
cd underwater_sim
```

If the repository was cloned without submodules:

```bash
git submodule update --init --recursive
```

### Build

Use a fresh terminal, or make sure another ROS workspace is not sourced.
Older Stonefish libraries can cause ABI and symbol lookup errors.

```bash
source /opt/ros/jazzy/setup.bash
unset AMENT_PREFIX_PATH COLCON_PREFIX_PATH CMAKE_PREFIX_PATH LD_LIBRARY_PATH
source /opt/ros/jazzy/setup.bash

cd ros_ws
colcon build --symlink-install --event-handlers console_direct+ \
  --packages-select Stonefish
source install/setup.bash
colcon build --symlink-install --event-handlers console_direct+ \
  --packages-select stonefish_ros2 stonefish_bluerov2 my_sim_package
source install/setup.bash
```

Verify that the packages come from this workspace:

```bash
ros2 pkg prefix stonefish_ros2
ros2 pkg prefix stonefish_bluerov2
```

### Launch

Start the graphical BlueROV2 tank simulation:

```bash
ros2 launch stonefish_bluerov2 bluerov2_sim.py
```

The Stonefish window should open in the Ubuntu desktop. ArduPilot SITL is not
required just to check that the graphical scene starts. SITL is required for
vehicle-control integration.

## Known Stonefish v1.3 source fix

The upstream Stonefish `v1.3` tag does not include `<cstdint>` in
`Library/include/sensors/Sample.h`, although that header uses `uint64_t`.
Consequently, a clean native build can fail there. The local working copy used
to test this branch contains this one-line fix:

```cpp
#include <cstdint>
```

This file belongs to the external `stonefish` Git submodule and cannot be
included in a commit to this parent repository. Until the fix is published in
a shared Stonefish fork or upstream, apply it after cloning:

```bash
sed -i '/#define __Stonefish_Sample__/a #include <cstdint>' \
  ros_ws/src/stonefish/Library/include/sensors/Sample.h
```

Do not commit the modified file inside the submodule unless you have a shared
Stonefish fork and have pushed that submodule commit. The generated
`ros_ws/build/`, `ros_ws/install/`, `ros_ws/log/`, and
`ros_ws/stonefish-v1.3-install/` directories are local build artifacts and are
intentionally not committed.

## Docker/noVNC alternative

The repository also provides a Docker-based desktop:

```bash
docker compose up -d --build
```

Open <http://localhost:8080/vnc.html>, then build inside the container:

```bash
docker exec -it stonefish_jazzy_sim bash
/ros_ws/build.sh
source install/setup.bash
ros2 launch my_sim_package bringup.launch.py
```

Stop the container when finished:

```bash
docker compose down
```
