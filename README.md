# underwater_sim

A containerized development environment for underwater robotics simulation
using **ROS 2 Jazzy** (Ubuntu 24.04) and the **Stonefish** simulator.
The simulator window is shown in your web browser through noVNC, so it works
the same on Windows (WSL2) and macOS.

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/), installed and **running**

## How to run

### 1. Clone the repository (with submodules)

```bash
git clone --recurse-submodules https://github.com/Asger124/underwater_sim.git
cd underwater_sim
```

If you cloned without `--recurse-submodules`, run:
```bash
git submodule update --init --recursive
```

### 2. Build and start the container

```bash
docker compose up -d --build
```
The first time takes several minutes.

### 3. Open the desktop in your browser

Go to <http://localhost:8080/vnc.html> and click **Connect**.
Simulator windows will appear here.

### 4. Build the workspace 

Open a shell inside the container:
```bash
docker exec -it stonefish_jazzy_sim bash
```
Your prompt should now look like `root@<id>:/ros_ws#`. Then run:
```bash
/ros_ws/build.sh
```
The Stonefish build takes a while.

When the script is finished run: 
```bash
source install/setup.bash
```


### 5. Launch the simulation

```bash
ros2 launch my_sim_package bringup.launch.py
```
Look at the simulation in the browser tab from step 3.

## Daily use

```bash
docker compose up -d                      # start the container
docker exec -it stonefish_jazzy_sim bash  # open a shell
source install/setup.bash                 # in every new shell
ros2 launch my_sim_package bringup.launch.py
exit                                      # exit the container
docker compose down                       # stop when finished
```