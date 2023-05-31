SET(HIVE_ROOT_PATH "${CMAKE_CURRENT_SOURCE_DIR}/../hive")
SET(WAX_CPP_PATH "${CMAKE_CURRENT_SOURCE_DIR}/../wax/wax.cpp")

LIST(APPEND CMAKE_MODULE_PATH
  "${CMAKE_CURRENT_SOURCE_DIR}/cmake"
  "${HIVE_ROOT_PATH}/cmake"
  "${HIVE_ROOT_PATH}/libraries/fc/CMakeModules"
  "${HIVE_ROOT_PATH}/libraries/fc/GitVersionGen"
)

project(wax)
cmake_minimum_required(VERSION 3.22.1)

find_package(PythonExtensions REQUIRED)

SET(CMAKE_POSITION_INDEPENDENT_CODE ON)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

set(CMAKE_EXPORT_COMPILE_COMMANDS "ON")
set(CMAKE_VERBOSE_MAKEFILE "ON")

include(hive_targets)

add_subdirectory("${HIVE_ROOT_PATH}/libraries/protocol" ${CMAKE_CURRENT_BINARY_DIR}/protocol)
add_subdirectory("${HIVE_ROOT_PATH}/libraries/fc" ${CMAKE_CURRENT_BINARY_DIR}/fc)
add_subdirectory("${HIVE_ROOT_PATH}/libraries/schema" ${CMAKE_CURRENT_BINARY_DIR}/schema)

add_python_library(${PROJECT_NAME} MODULE SOURCES ${WAX_CPP_PATH} cpython_interface.cpp LINK_LIBRARIES hive_protocol)

python_extension_module(${PROJECT_NAME})

file(COPY ${CMAKE_CURRENT_SOURCE_DIR}/cpython_interface.hpp DESTINATION ${CMAKE_CURRENT_BINARY_DIR})

INSTALL(TARGETS
  ${PROJECT_NAME}

  RUNTIME DESTINATION bin
  LIBRARY DESTINATION lib
  ARCHIVE DESTINATION lib
)
