#!/bin/bash
set -x

#if [ $# -lt 1 ]; then
#        echo "usage $0 <essid> <ip-addr>"
#        exit
#fi
if [ $# -lt 6 ]; then
echo "usage $0 <iface> <essid> <freq> <power> <rate> <ip> <mac>"
exit
fi

iface=$1
essid=$2;
freq=$3
txpower=$4
rate=$5
ip_addr=$6
mac_address=$7

ifconfig $iface down
iwconfig $iface mode ad-hoc
ifconfig $iface $ip_addr up
iwconfig $iface txpower $txpower
iwconfig $iface rate $rate fixed
#iw dev <devname> ibss join <SSID> <freq in MHz> [HT20|HT40+|HT40-|NOHT] [fixed-freq] [<fixed bssid>] [beacon-interval <TU>] [basic-rates <rate in Mbps,rate2,...>] [mcast-rate <rate in Mbps>] [key d:0:abcde]
iw dev $iface ibss join $essid $freq fixed-freq $mac_address

set +x

