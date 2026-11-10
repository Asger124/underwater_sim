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

The apriltag_ros node depends on packages from AprilTag library, 
see:
```bash
ros_ws/src/apriltag_ros/.github/deps.repos
```

You can use the command 
```bash 
apt policy ros-jazzy-apriltag
```
to see which versions apt will install.
Most versions should work, but this command can confirm that apt installs versions close to the pinned versions: v3.4.5 and 2.0.2

To install write: 
```bash
sudo apt install ros-jazzy-apriltag ros-jazzy-apriltag-msgs
```
Then from the repository root, build and source the workspace:

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

## 2026-11-10: Fixed leader and follower controller test

The current simplified test does not run a leader mission. The leader remains
fixed at its configured position and offset in the Stonefish tank scenario.
Only the follower controller is started. This isolates AprilTag pose handling
and lets the follower react to the fixed leader pose.

Start the two ArduSub instances first:

### Terminal 1: leader ArduSub

```bash
cd ~/ardupilot
Tools/autotest/sim_vehicle.py \
  -v ArduSub \
  --model JSON \
  --sim-address=127.0.0.1 \
  -I0
```

### Terminal 2: follower ArduSub

```bash
cd ~/ardupilot
Tools/autotest/sim_vehicle.py \
  -v ArduSub \
  --model JSON \
  --sim-address=127.0.0.1 \
  -I1
```

### Terminal 3: Stonefish

```bash
cd ~/RP/underwater_sim
source /opt/ros/jazzy/setup.bash
source ros_ws/install/setup.bash
ros2 launch stonefish_bluerov2 bluerov2_sim.py
```

The launch file starts the ArduSim bridges for both vehicles. Wait until the
Stonefish window is open and both bridges report that they receive callbacks.

### Terminal 4: AprilTag detector

```bash
cd ~/RP/underwater_sim
source /opt/ros/jazzy/setup.bash
source ros_ws/install/setup.bash
ros2 run apriltag_ros apriltag_node --ros-args \
  -r image_rect:=/bluerov2_2/left/image_color \
  -r camera_info:=/bluerov2_2/left/camera_info \
  --params-file ros_ws/src/stonefish_bluerov2/config/tags.yaml
```

### Terminal 5: follower

```bash
cd ~/RP/underwater_sim
source /opt/ros/jazzy/setup.bash
source ros_ws/install/setup.bash
export PYTHONPATH="$HOME/ardupilot/modules/mavlink:$PYTHONPATH"
ros2 run stonefish_bluerov2 follower_pi_controller.py
```

The follower reads the AprilTag transform from
`bluerov2_2/camera_left` to `leader_tag_frame`. It uses camera-frame `x` for
lateral error, `y` for vertical error, and `z` for the forward-distance PI
controller. Its target is `x=0`, `y=0`, and `z=1.0` metre.

Verify the measured pose:

```bash
ros2 run tf2_ros tf2_echo bluerov2_2/camera_left leader_tag_frame
```

Because the leader is fixed, its pose and the AprilTag translation should stay
approximately constant. The follower should only move if the measured
translation differs from the target. Do not start
`leader_forward_mission.py` in this test.
