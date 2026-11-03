# underwater_sim
 
BlueROV2 underwater simulation using ROS 2 Jazzy, Stonefish, and ArduSub SITL.
 
## Requirements
 
- Ubuntu 24.04
- ROS 2 Jazzy
- ArduPilot checked out at `~/ardupilot`
- `colcon`
- Stonefish installed
## Install Ros2 
Refer to the documentation for instlling ros2 jazzy
https://docs.ros.org/en/jazzy/Installation/Ubuntu-Install-Debs.html
 
## Install colcon: 
https://docs.ros.org/en/jazzy/Tutorials/Beginner-Client-Libraries/Colcon-Tutorial.html#install-colcon
 
## Installing and setting up stonefish. 
In this repository stonefish a fork of stonefish version 1.3 is referred to as a submodule. Navigate to the submodule and follow the readme. OBS. ignore the part that asks you to checkout to version 1.3, as the fork already is an instance of version 1.3  
 
## Stonefish ros2 Submodule 
This repository refers to a another fork of repository stonefish_ros2. This fork is set up to track version 1.3 - it needs to match the stonefish version. If all above steps wnet smoothly, you should now be able to move on to ardupilot setup
 
## Ardupilot 
Refer to this page for setting up Ardupolit SITL: https://ardupilot.org/dev/docs/building-setup-linux.html#building-setup-linux.
 
```bash
git clone --recurse-submodules https://github.com/ArduPilot/ardupilot
cd ardupilot
 
Tools/environment_install/install-prereqs-ubuntu.sh -y
. ~/.profile
```
 
Ardupilot should be ready to use at this point.
 
Run following commands to test that ArduSub is running porperly. For the first time the system will build the firmware for ArduPilot SITL to use.
 
```bash
cd ardupilot 
sim_vehicle.py -v ArduSub --map 
```
 
This will put the simulated vehicle in middle of nowhere going in to the ground. JUST AMAZING!!!
 
cd into this location in ardupilot directory `/home/bvibhav/Ardupilot/Tools/autotest/` and edit `locations.txt`. Add this line at the very bottom.
 
```text
PHILL=56.026930,-3.385670,0,0
```
 
Now run the commands again
 
```bash
cd ardupilot 
sim_vehicle.py -v ArduSub --map -L PHILL
```
 
 
## Running Ardupilot SITL with your own simulator
Run this command to start SITL with JSON simulator instead. This will let us connect to our own simulator on the local machine (this can be changed later for different IP).
 
```bash
sim_vehicle.py -v ArduSub --model JSON  --map -L PHILL -m --streamrate=-1
```
 
This will complain about link 1 down as SITL is not getting anything from simulator side.
 
## Run the project
 
From the repository root:
 
```bash
git submodule update --init --recursive (ved ikke med det her - legacy?)
source /opt/ros/jazzy/setup.bash
cd ros_ws
colcon build --symlink-install --event-handlers console_direct+ \
  --packages-select Stonefish
colcon build --symlink-install --event-handlers console_direct+ \
  --packages-select stonefish_ros2 stonefish_bluerov2 my_sim_package
source install/setup.bash
```
 
I THINK THIS IS DEPRECATED TRY IT WITHOUT TO SEE IF WE CAN DELETE IT 
 
If the build reports a missing `uint64_t` declaration in Stonefish, add this
line to `ros_ws/src/stonefish/Library/include/sensors/Sample.h`:
 
```cpp
#include <cstdint>
```
 
Then run the build again.
 
## HOW TO RUN 2 blue2rov in same simulation with different different missions: 
 
### Ardupilot SITL: 
First open 2 terminals (Ubuntu). 
Preferably do this while having the venv-ardupilot environment activated, 
to ensure that the correct packages are installed and used. `(venv-ardupilot)` should be seen in front of your Ubuntu username, 
if you followed installation guide above. 
 
In the first terminal navigate to the ardupilot root. From here write: 
 
```bash
Tools/autotest/sim_vehicle.py -v ArduSub --model JSON --sim-address=127.0.0.1 -I0
```
 
Do the same in the second terminal but now write: 
 
```bash
Tools/autotest/sim_vehicle.py -v ArduSub --model JSON --sim-address=127.0.0.1 -I1
```
 
 
### Stonefish: 
 
Now open a third terminal to launch stonefish: 
 
```bash
source /opt/ros/jazzy/setup.bash
 
cd ros_ws
colcon build --symlink-install --event-handlers console_direct+ \
  --packages-select Stonefish
source install/setup.bash
colcon build --symlink-install --event-handlers console_direct+ \
  --packages-select stonefish_ros2 stonefish_bluerov2 my_sim_package
source install/setup.bash
 
ros2 launch stonefish_bluerov2 bluerov2_sim.py
```
 
## giving commands through scripts: 
 
You need terminal ardusub instance. 
 
Currently you can use `working_square.py`, and `square.py` to send commands to the ardusub instances. 
 
Each script is configured to a specific ardusub instance port. 
 
To run the scripts write:
 
```bash
python3 working_square.py
python3 square.py
```
 
See the robots move around. 
 