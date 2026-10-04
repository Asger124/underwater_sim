#!/bin/bash
set -e

# Start virtual display (Xvfb) for headless 3D rendering
Xvfb :99 -screen 0 1280x800x24 &
export DISPLAY=:99

# Start lightweight window manager
fluxbox &

# Start VNC server attached to virtual display
x11vnc -display :99 -forever -shared -noxrecord -noxfixes -noxdamage -nopw -rfbport 5900 &

# Start noVNC web server on port 8080
websockify --web=/usr/share/novnc/ 8080 localhost:5900 &

# Source ROS 2 setup automatically
source /opt/ros/jazzy/setup.bash
if [ -f "/ros_ws/install/setup.bash" ]; then
    source /ros_ws/install/setup.bash
fi

exec "$@"