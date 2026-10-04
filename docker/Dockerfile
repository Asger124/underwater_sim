FROM osrf/ros:jazzy-desktop-full

# Avoid interactive prompts during apt installs
ENV DEBIAN_FRONTEND=noninteractive

# Install system utilities, X11/VNC stack, and Stonefish build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    wget \
    curl \
    python3-colcon-common-extensions \
    python3-rosdep \
    # Stonefish C++ core dependencies
    libglm-dev \
    libsdl2-dev \
    libfreetype6-dev \
    libglew-dev \
    libboost-system-dev \
    # Web VNC Desktop stack for cross-platform GUI access
    x11vnc \
    xvfb \
    fluxbox \
    novnc \
    websockify \
    && rm -rf /var/lib/apt/lists/*

# Set up working directory inside the container
WORKDIR /ros_ws

# Copy entrypoint script
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Auto-source ROS 2 in interactive bash shells
RUN echo "source /opt/ros/jazzy/setup.bash" >> /root/.bashrc && \
    echo "if [ -f /ros_ws/install/setup.bash ]; then source /ros_ws/install/setup.bash; fi" >> /root/.bashrc

ENTRYPOINT ["/entrypoint.sh"]
CMD ["bash"]