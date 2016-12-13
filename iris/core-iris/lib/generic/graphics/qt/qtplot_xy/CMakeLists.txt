
########################################################################
# Build the library from source files
########################################################################
SET(sources
  QtPlot_xy.cpp
)

IF (IRIS_HAVE_REALPLOT)
    ADD_LIBRARY(qtplot_xy ${sources})
    TARGET_LINK_LIBRARIES(qtplot_xy realplot)
    INCLUDE_DIRECTORIES(${CMAKE_CURRENT_BINARY_DIR})
    IRIS_SET_PIC(qtplot_xy)
    SET(IRIS_HAVE_QTPLOT_XY ON CACHE INTERNAL "Has QtPlot_xy been built?")
ELSE (IRIS_HAVE_REALPLOT)
    SET(IRIS_HAVE_QTPLOT_XY OFF CACHE INTERNAL "Has QtPlot_xy been built?")
    #IRIS_APPEND_NOINSTALL_LIST(radarmaccomponent)
ENDIF (IRIS_HAVE_REALPLOT)
