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
alix04,b43,10.8.8.104,2412,20,192.168.0.4,00:14:a5:e9:0c:74,B,AP,wlan0
alix05,b43,10.8.8.105,2412,20,192.168.0.5,00:14:a4:62:c8:21,C,STA,wlan0

#move files on ttilab
rsync -avz --delete --exclude=examples --exclude=.git --exclude '*.o' --exclude '*.h' --exclude '*.c' --exclude '*.pyc' --exclude .idea/ --exclude .repo/ ../../../  -e ssh clapton:~/wishful-github-manifest-7/
ssh clapton "mkdir -p wishful-github-manifest-7/examples"
rsync -avz --delete  --exclude=.git --exclude '*.o' --exclude '*.h' --exclude '*.c' --exclude '*.pyc' --exclude '*/*' ../../interference_detection/  -e ssh clapton:~/wishful-github-manifest-7/examples/interference_detection/
rsync -avz --delete  --exclude=.git --exclude '*.o' --exclude '*.h' --exclude '*.c' --exclude '*.pyc' ../../interference_detection/helper/  -e ssh clapton:~/wishful-github-manifest-7/examples/interference_detection/helper
rsync -avz --delete  --exclude=.git --exclude '*.o' --exclude '*.h' --exclude '*.c' --exclude '*.pyc' ../../interference_detection/station-conf/  -e ssh clapton:~/wishful-github-manifest-7/examples/interference_detection/station-conf

rsync -avz --delete --exclude=examples --exclude=.git --exclude '*.o' --exclude '*.h' --exclude '*.c' --exclude '*.pyc' --exclude .idea/ --exclude .repo/ ../../../  -e ssh lab.tti.unipa.it:~/wishful-github-manifest-7/
ssh lab.tti.unipa.it "mkdir -p wishful-github-manifest-7/examples"
rsync -avz --delete  --exclude=.git --exclude '*.o' --exclude '*.h' --exclude '*.c' --exclude '*.pyc' --exclude '*/*' ../../interference_detection/  -e ssh lab.tti.unipa.it:~/wishful-github-manifest-7/examples/interference_detection/
rsync -avz --delete  --exclude=.git --exclude '*.o' --exclude '*.h' --exclude '*.c' --exclude '*.pyc' ../../interference_detection/helper/  -e ssh lab.tti.unipa.it:~/wishful-github-manifest-7/examples/interference_detection/helper
rsync -avz --delete  --exclude=.git --exclude '*.o' --exclude '*.h' --exclude '*.c' --exclude '*.pyc' ../../interference_detection/station-conf/  -e ssh lab.tti.unipa.it:~/wishful-github-manifest-7/examples/interference_detection/station-conf


#connect to controller
    ssh lab.tti.unipa.it

#move on experiment directory
    cd wishful-github-manifest-7/examples/interference_detection/

#sync clock nodes
  cd helper
  sh sync_date.sh domenico clapton.local
  sh sync_date.sh root alix04,alix05

#deploy directory on nodes
  sh deploy_upis.sh domenico clapton.local
  sh deploy_upis.sh root alix04,alix05
  cd ..

#connect to nodes
    ssh clapton.local
        cd wishful-github-manifest/examples/interference_detection/
    ssh root@alix04
        cd wishful-github-manifest/examples/interference_detection/
    ssh root@alix05
        cd wishful-github-manifest/examples/interference_detection/

Tunnel over Nova by putty:
~~~~
tunnel for multipresa
tunnel for controller

#ssh -L 8501:10.8.8.10:8501 domenico@lab.tti.unipa.it -v
#ssh -L 8500:10.8.8.10:8500 domenico@lab.tti.unipa.it -v
#ssh -L 8001:10.8.8.22:80 domenico@lab.tti.unipa.it -v
#ssh -L 8002:10.8.8.4:80 domenico@lab.tti.unipa.it -v
#ssh -L 8502:10.8.8.5:8502 domenico@lab.tti.unipa.it -v

http://localhost:8001/login.html (ttilab)
http://localhost:8002/crewdemo/plots/usrp.png (http://10.8.9.3/crewdemo/plots/usrp.png)
~~~~

~~~~
#start USRP
~~~~
ON USRP : http://10.8.8.22/login.html (ttilab)
ssh lab.tti.unipa.it
    ssh doors.local
        cd Desktop/python-usrp-tracker-v2/pyUsrpTracker/
            sudo sh run_usrp.sh 6

ON ZIGBEE : http://10.8.8.22/login.html (ttilab)

~~~~
#start agent
~~~~
ssh clapton
sudo python3 agent --config agent_cfg_sta_clapton.yaml
ssh root@alix04
python3 agent --config agent_cfg_sta.yaml
ssh root@alix05
python3 agent --config agent_cfg_sta.yaml
~~~~

#controller (clapton --> CONTROLLER)
~~~~
sudo python3 controller --config controller_cfg_clapton.yaml --nodes node_info_ttilab_3full.txt
~~~~

#controller (nova --> CONTROLLER)
~~~~
sudo python3 controller --config controller_cfg_nova.yaml --nodes node_info_ttilab_3full.txt
~~~~


#starting reading tool
~~~~
cd wishful-github-manifest-7/examples/interference_detection/station-conf/reading-tool/
sudo ./b43-fwdump2
~~~~

#start spectral scan
#sh run_spectral_scan.sh
ssh domenico@extensa.local "rm -r /tmp/spectral_scan/; mkdir /tmp/spectral_scan"
scp pub_server.py domenico@extensa.local:/tmp/spectral_scan/
scp -r spectral_acquire domenico@extensa.local:/tmp/spectral_scan/
ssh -t domenico@extensa.local "sudo python /tmp/spectral_scan/pub_server.py"



#START graphical interface
cd visualizer
python graphic_interface.py

