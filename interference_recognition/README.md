Wishful INTERFERENCE
============================

### INTERFERENCE how-to on w-ilab.t

### 0. Reserve and swap in the experiment
 EMULAB experiment link (atlas)
 https://www.wilab2.ilabt.iminds.be/showexp.php3?pid=cognitiveradio&eid=atlas
 
### 1. run the showcase 
 CONTROLLER
 nodezotach4,ath9k,10.11.16.39,5180,1,192.168.0.1,00:0e:8e:30:9e:ce,A
 
 EXPERIMET NODES
 nodezotacd6,ath9k,10.11.16.54,5180,3,192.168.0.1,00:0e:8e:30:9c:ba,A
 nodezotacg6,ath9k,10.11.16.56,5180,3,192.168.0.2,00:0e:8e:30:9d:3c,B
 nodezotacj6,ath9k,10.11.16.59,5180,3,192.168.0.3,00:0e:8e:30:9c:ea,C
 nodezotacb1,ath9k,10.11.16.1,5180,3,192.168.0.4,00:0e:8e:30:9c:b3,D
 nodezotack1,ath9k,10.11.16.10,5180,3,192.168.0.5,00:0e:8e:30:9e:ea,E
 nodezotaci3,ath9k,10.11.16.29,5180,3,192.168.0.6,00:0e:8e:30:91:7b,F

 #move files on wilab (we need copy one time, the wilab testbed filesystem replace all user directory on testbed nodes)
 
  rsync -avz --delete  --exclude=.git --exclude '*.o' --exclude '*.h' --exclude '*.c' --exclude '*.pyc' --exclude .repo/ ./wishful-github-manifest-4/  -e ssh user@ops.wilab2.ilabt.iminds.be:~/wishful-github-manifest-4/

 #connect to nodes
  ssh user@ops.wilab2.ilabt.iminds.be
  ssh user@zotacd6
  ...
  ssh user@zotach4

 #move on experiment directory
  cd wishful-github-manifest-4/examples/interference_recognition/

 #sync clock nodes
  sh sync_date.sh user zotacc6,zotacg6,zotack6,zotacb1,zotack1,zotaci3

 #start agent
sudo python3 agent --config agent_cfg_wilab.yaml

#controller (zotach4 (39) --> CONTROLLER)
sudo python3 controller --config controller_cfg_wilab2_zotach4.yaml --nodes node_info_wilab2_4hop.txt

if matplotlib module fails, please install it using
~~~~
sudo apt-get install python3-matplotlib
~~~~

### INTERFERENCE how-to on ttilab
 
### 1. run the showcase 
 CONTROLLER
 nova
 
 EXPERIMET NODES

~~~~
clapton.local,ath9k,10.8.9.3,5180,20,192.168.0.1,a8:54:b2:69:3b:e3,A,AP,wlan0
 nautilus.local,ath9k,10.8.8.1,5180,20,192.168.0.2,00:15:6d:85:75:b3,B,STA,wlan0
 extensa.local,ath9k,10.8.8.5,5180,20,192.168.0.3,00:15:6d:85:90:2d,C,STA,wlan0

 #move files on wilab
 
  rsync -avz --delete  --exclude=.git --exclude '*.o' --exclude '*.h' --exclude '*.c' --exclude '*.pyc' --exclude .repo/ ./wishful-github-manifest-4/  -e ssh lab.tti.unipa.it:~/wishful-github-manifest-4/

 #connect to nodes
 
  ssh clapton.local
  ssh nautilus.local
  ssh extensa.local

 #move on experiment directory
 
  cd wishful-github-manifest-4/examples/interference_recognition/

 #sync clock nodes

  cd helper
  sh sync_date.sh <user> clapton.local,nautilus.local,extensa.local

 #deploy directory on nodes
 
  sh deploy_upis.sh <user> clapton.local,nautilus.local,extensa.local
  cd .. 
~~~~
#start agent
~~~~
sudo python3 agent --config agent_cfg_ttilab.yaml
~~~~

#controller (nova --> CONTROLLER)
~~~~
sudo python3 controller --config controller_cfg_nova.yaml --nodes node_info_ttilab_3full.txt
~~~~

#visualizer connection (39 --> CONTROLLER)
~~~~
ssh -L 8401:10.11.16.39:8401 user@ops.wilab2.ilabt.iminds.be -v
ssh -L 8400:10.11.16.39:8400 user@ops.wilab2.ilabt.iminds.be -v
~~~~
#START graphical interface
cd visualizer
python graphic_interface.py



#if needed
#setup nodes
~~~~
cd station-conf/scapy/ && sudo sh install_scapy.sh && cd ../../
cd station-conf/compact/ && bash build.sh --load-module && cd ../../
~~~~
# how to read the busytime with iw.
iw dev wlan0 surveydump