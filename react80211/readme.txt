REACT howto

https://www.wilab2.ilabt.iminds.be/showexp.php3?pid=cognitiveradio&eid=atlas

#NODES
CONTROLLER
nodezotach4.wilab2.ilabt.iminds.be,ath9k,10.11.16.7,5180,1,192.168.0.1,00:0e:8e:30:9e:ce,A

CHAIN
nodezotacb3.wilab2.ilabt.iminds.be,ath9k,10.11.16.22,5180,1,192.168.0.1,mac_address,A
nodezotacb4.wilab2.ilabt.iminds.be,ath9k,10.11.16.33,5180,1,192.168.0.2,mac_address,B
nodezotacd3.wilab2.ilabt.iminds.be,ath9k,10.11.16.24,5180,3,192.168.0.3,mac_address,C
nodezotaci3.wilab2.ilabt.iminds.be,ath9k,10.11.16.29,5180,3,192.168.0.4,mac_address,D
nodezotack3.wilab2.ilabt.iminds.be,ath9k,10.11.16.31,5180,1,192.168.0.5,mac_address,E
nodezotack4.wilab2.ilabt.iminds.be,ath9k,10.11.16.42,5180,1,192.168.0.6,mac_address,F

FULL CONNECTED
nodezotach1.wilab2.ilabt.iminds.be,ath9k,10.11.16.7,5180,1,192.168.0.1,00:0e:8e:30:9e:ce,A
nodezotach2.wilab2.ilabt.iminds.be,ath9k,10.11.16.17,5180,3,192.168.0.2,00:0e:8e:30:9e:dc,B
nodezotach3.wilab2.ilabt.iminds.be,ath9k,10.11.16.28,5180,3,192.168.0.3,00:0e:8e:30:9d:ee,C

#move files on wilab
rsync -avz --delete  --exclude=.git --exclude '*.o' --exclude '*.h' --exclude '*.c' --exclude '*.pyc' --exclude .repo/ ./wishful-github-manifest-3/  -e ssh dgarlisi@ops.wilab2.ilabt.iminds.be:~/wishful-github-manifest-3/

#connect to nodes
ssh dgarlisi@ops.wilab2.ilabt.iminds.be
ssh dgarlisi@zotach1.wilab2.ilabt.iminds.be
...
ssh dgarlisi@zotach4.wilab2.ilabt.iminds.be

#sync clock nodes
sh sync_date.sh dgarlisi 10.11.16.17,10.11.16.7,10.11.16.2
sh sync_date.sh dgarlisi zotacc6,zotacg6,zotack6

NB: on wilab, we do not need deploy
 sh deploy_upis.sh dgarlisi zotacc6,zotacg6,zotack6

#move on experiment directory
cd wishful-github-manifest-3/examples/react80211/

#setup nodes
cd zotac-conf/scapy/ && sudo sh install_scapy.sh && cd ../../
cd zotac-conf/athmodules/ && sudo sh install_module.sh && cd ../../

#start agent
sudo python3 react_agent --config agent_cfg_wilab.yaml

#controller (39 --> CONTROLLER)
sudo python3 react_controller --config controller_cfg_wilab2.yaml --nodes node_info_wilab2_full.txt
sudo python3 react_controller --config controller_cfg_wilab2_zotach4.yaml --nodes node_info_wilab2_3chain.txt

#visualizer connect (39 --> CONTROLLER)
ssh -L 8401:10.11.16.39:8401 dgarlisi@ops.wilab2.ilabt.iminds.be -v
ssh -L 8400:10.11.16.39:8400 dgarlisi@ops.wilab2.ilabt.iminds.be -v

ssh -L 8400:127.0.0.1:8400 dgarlisi@nuc1 -v
ssh -L 8401:127.0.0.1:8401 dgarlisi@nuc1 -v
sudo openvpn --config ~/Desktop/portable-testbed/portableTestbed.ovpn

#visualizer
python react_visualizer.py

#nodezotacc6,ath9k,10.11.16.53,5180,5,192.168.0.1,00:0e:8e:30:9c:af,A
#nodezotacg6,ath9k,10.11.16.56,5180,8,192.168.0.2,00:0e:8e:30:9d:3c,B
#nodezotack6,ath9k,10.11.16.60,5180,8,192.168.0.3,00:0e:8e:30:9c:eb,C
