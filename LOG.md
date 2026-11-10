# Development Log

## 2026-11-03: BlueROV2 AprilTag vision test

- Added an AprilTag 36h11, ID 0, to the siulated BlueROV2 in 'bluerov2.scn'.
note: all april tags aperently needs a white boarder around them.
- Configured the tag surface to use the complete texture with `uv_mode="1"`.

- added `apriltag_ros` to workspace and added a simple tags.yaml file for the detector.

- ran apriltag_ros detector with command
  line remappings to the second vehicle's left camera. 
- Made the simulated bluerovs stay in a fixed-position  to make sure the tag is in the bluerov_2 left camera visoin. This prevents the
  vehicles from drifting or spinning when no ArduPilot or mission is running alowing for the tag to be in vision at all times.

### Reproduce the fixed-position vision test

From the repository root, build and source the workspace:

```bash
cd ~/RP/underwater_sim
source /opt/ros/jazzy/setup.bash
cd ros_ws
colcon build --symlink-install --packages-select apriltag_ros stonefish_bluerov2
source install/setup.bash
```

Start Stonefish in a separate terminal. no nned to start ArduPilott:

```bash
cd ~/RP/underwater_sim
source /opt/ros/jazzy/setup.bash
source ros_ws/install/setup.bash
ros2 launch stonefish_bluerov2 bluerov2_sim.py
```

Start the AprilTag detector in another terminal:

```bash
cd ~/RP/underwater_sim
source /opt/ros/jazzy/setup.bash
source ros_ws/install/setup.bash
ros2 run apriltag_ros apriltag_node --ros-args \
  -r image_rect:=/bluerov2_2/left/image_color \
  -r camera_info:=/bluerov2_2/left/camera_info \
  --params-file ros_ws/src/stonefish_bluerov2/config/tags.yaml
```

Check that the detector is connected to the camera:

```bash
source /opt/ros/jazzy/setup.bash
source ~/RP/underwater_sim/ros_ws/install/setup.bash
ros2 node info /apriltag
```

The node should subscribe to:

```text
/bluerov2_2/left/image_color
/bluerov2_2/left/camera_info
```

View the camera feed:

```bash
source /opt/ros/jazzy/setup.bash
source ~/RP/underwater_sim/ros_ws/install/setup.bash
ros2 run rqt_image_view rqt_image_view
```

Select `/bluerov2_2/left/image_color` in `rqt_image_view`. The tag must be
fully visible for a sucessfull detection.

```bash
source /opt/ros/jazzy/setup.bash
source ~/RP/underwater_sim/ros_ws/install/setup.bash
ros2 topic echo /detections
```

Successful detections contain an entry with family `36h11` and ID `0`.

### Getting the 3D tag pose and distance

The AprilTag node estimates the tag pose with PnP and publishes it on `/tf`.
The pose is only valid when the camera is calibrated and the configured tag
size matches the physical tag. The current configuration uses a `0.25` m tag;
update `ros_ws/src/stonefish_bluerov2/config/tags.yaml` if the printed tag has
a different edge length.

Check the available TF frames:

```bash
ros2 topic echo /tf
```

The configured tag frame is `leader_tag_frame`. To inspect its pose directly,
replace `<camera_frame>` with the camera frame shown in the camera info header:

```bash
ros2 topic echo /bluerov2_2/left/camera_info --once
ros2 run tf2_ros tf2_echo <camera_frame> leader_tag_frame
```

The transform translation is in meters. For a camera optical frame, `x` is
left/right, `y` is up/down, and `z` is forward distance. The 3D distance to
the tag is:

```text
distance = sqrt(x*x + y*y + z*z)
```

For leader-follower control, use the relative position errors:

```text
forward_error = z - desired_distance
lateral_error = x
vertical_error = y
```

### Fixed versus dynamic vehicles

The tank scenario currently passes `fixed="true"` to both vehicle includes in
`ros_ws/src/stonefish_bluerov2/scenarios/bluerov2_tank.scn`. This is useful for
camera and AprilTag testing because the vehicles remain in their initial poses
without requiring ArduPilot control.

Fixed vehicles cannot follow a mission. To run a mission, change both
vehicle entries to:

```xml
<arg name="fixed" value="false"/>
```

Rebuild the package after changing the scenario:

```bash
cd ~/RP/underwater_sim/ros_ws
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install --packages-select stonefish_bluerov2
source install/setup.bash
```

Then start the two ArduSub SITL instances and the mission scripts according to
the current mission setup in the repository. Do not use the fixed vision-test
configuration for mission execution.
