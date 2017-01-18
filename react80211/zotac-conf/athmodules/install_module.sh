#!/bin/bash

rmmod ath9k 
rmmod ath9k_common 
rmmod ath9k_hw 
rmmod ath 
rmmod mac80211 
rmmod cfg80211
rmmod compat

insmod ./compat.ko
insmod ./cfg80211.ko
insmod ./mac80211.ko 
insmod ./ath.ko 
insmod ./ath9k_hw.ko 
insmod ./ath9k_common.ko 
insmod ./ath9k.ko 


