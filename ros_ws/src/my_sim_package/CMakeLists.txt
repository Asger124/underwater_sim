cmake_minimum_required(VERSION 3.8)
project(my_sim_package)

find_package(ament_cmake REQUIRED)

install(DIRECTORY
  launch
  scenarios
  data
  DESTINATION share/${PROJECT_NAME}
)

ament_package()