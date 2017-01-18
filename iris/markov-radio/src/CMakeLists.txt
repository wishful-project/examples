########################################################################
# The dyspanradio binary
########################################################################

file(GLOB sources
    main.cpp
    ofdmtransceiver.cpp
    multichannelrx.cpp
    EnergyDetector2.cpp
    EnergyDetector.cpp
    MarkovChain.cpp
    ChannelSelector.cpp
)

file(GLOB headers
    dyspanradio.h
    ofdmtransceiver.h
    multichannelrx.h
    EnergyDetector2.h
    EnergyDetector.h
    MarkovChain.h
    ChannelSelector.h
    channels.h
    Buffer.h
    buffer_factory.h
    packetLib.h
EndianConversion.h
RawFileUtility.h)

INCLUDE_DIRECTORIES(${CMAKE_SOURCE_DIR}/clientlib)
ADD_EXECUTABLE(dyspanradio ${sources} ${headers})
TARGET_LINK_LIBRARIES(dyspanradio clientlib ${FFTW3F_LIBRARIES} ${UHD_LIBRARIES} ${Boost_LIBRARIES} ${LIQUIDDSP_LIBRARIES})

########################################################################
# Define Target: markov_chain_test
########################################################################
set(SOURCE_FILES
    MarkovChain.cpp
    ChannelSelector.cpp
    markov_chain_test.cpp)

add_executable(markov_chain_test ${SOURCE_FILES})
target_link_libraries(markov_chain_test)