#!/bin/sh
BUILD_DIR=../build_release/src
cd $BUILD_DIR
# Creates a radio in N210, that transmits and senses simultaneously
# Some relevant parameters:
### reconfig_wait - The minimum time the SU stays in a channel
### second_av_size - is optimized for the Energy Detector
### channel_rate - defines the rate of transmission
./dyspanradio --freq=2.4125e9 --channel_bandwidth=5000000 --channel_rate 5000000 --num_channels=4 --txgain_uhd=18 --txgain_soft=-10 --challenge=true --debug=false --txsubdev="A:0" --mod qam16 --learning=true --reconfig_wait=10 --second_av_size=1.5
