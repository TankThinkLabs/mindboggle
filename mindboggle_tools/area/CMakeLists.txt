# This is the root ITK CMakeLists file.
CMAKE_MINIMUM_REQUIRED(VERSION 2.8)
IF(COMMAND CMAKE_POLICY)
  CMAKE_POLICY(SET CMP0003 NEW)
ENDIF(COMMAND CMAKE_POLICY)


# This project is designed to be built outside the Insight source tree.
PROJECT(point_area)

# Find VTK.
FIND_PACKAGE(VTK REQUIRED)
INCLUDE(${VTK_USE_FILE})

ADD_EXECUTABLE(
PointAreaMain PointAreaMain.cpp
)
INSTALL(TARGETS PointAreaMain
    RUNTIME DESTINATION /bin)

TARGET_LINK_LIBRARIES(
PointAreaMain
MeshAnalyser
PointAreaComputer
vtkCommon
vtkRendering
vtkHybrid
)
