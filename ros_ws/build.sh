#!/usr/bin/env bash
set -e
cd /ros_ws
colcon build --symlink-install --packages-select Stonefish
source install/setup.bash
colcon build --symlink-install --packages-select stonefish_ros2 my_sim_package
echo "Done. Now run: source install/setup.bash"