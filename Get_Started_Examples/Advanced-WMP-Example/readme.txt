METAMAC howto

### WORKING ON EMULAB
reserve all the ALIX nodes and two SERVER (SERVER3 + SERVER15 + USRP5)
swap in the experiment alix-wishful (https://www.wilab2.ilabt.iminds.be/showexp.php3?pid=cognitiveradio&eid=alix-wishful)

#connect to controller PC [from ops.wilab2.ilabt.iminds.be (ssh  dgarlisi@ops.wilab2.ilabt.iminds.be)]
    SHELL A - CONTROLLER PC :
        ssh YOUR_USER@alixserver.alix-wishful.cognitiveradio.wilab2.ilabt.iminds.be
            run command to set speed alixnode network
            sudo ethtool -s eth4 speed 100 duplex full

#move files on wilab
rsync -avz --delete  --exclude=.git --exclude '*.o' --exclude '*.h' --exclude '*.c' --exclude '*.pyc' --exclude .repo/ ./wishful-github-manifest-3/  -e ssh dgarlisi@ops.wilab2.ilabt.iminds.be:~/wishful-github-manifest-3/

    deploy framework on alixnodes
        cd examples/wmp/wmp_metamac/wmp_helper
        sh deploy_upis.sh alixnode9,alixnode10,alixnode12,alixnode13,alixnode8
    sync nodes time:
        sh sync_date.sh alixnode9,alixnode10,alixnode12,alixnode13,alixnode8


connect to nodes [from ops.wilab2.ilabt.iminds.be (ssh  dgarlisi@ops.wilab2.ilabt.iminds.be)]
SHELL B  - ALIXNODE :
    ssh YOUR_USER@alixserver.alix-wishful.cognitiveradio.wilab2.ilabt.iminds.be
        ssh root@alixnode9


#start agent on alixnode
    python3 metamac_agent --config agent_config.yaml
    python3 metamac_agent --config agent_config_ap.yaml

#start controller on server
    172.16.0.8,alixnode8,AP,wmp,0
    172.16.0.9,alixnode9,STA,wmp,0
    172.16.0.10,alixnode10,STA,wmp,0
    172.16.0.12,alixnode12,STA,wmp,0
    172.16.0.13,alixnode13,STA,wmp,0

    python3 metamac_testbed_controller --config controller_config_wilab.yaml
    sudo apt-get install python3-matplotlib
    python3 metamac_experiment_controller --config controller_config_wilab.yaml (sudo apt-get install python3-matplotlib)

#forward command for experiment visualizer
    ssh -L 8401:server3:8401 dgarlisi@ops.wilab2.ilabt.iminds.be -v
    ssh -L 8400:server3:8400 dgarlisi@ops.wilab2.ilabt.iminds.be -v

###USRP acquiring
    #server
        sudo apt-get install apache2
        sudo cp -r /users/dgarlisi/USRP_DEMO/web-site /var/www/html/
        sudo cp -r /users/dgarlisi/USRP_DEMO/web-site/crewdemo /var/www/html/
        sudo /users/dgarlisi/USRP_DEMO/pyTrackers/pyUsrpTracker/run_usrp.sh 6
    #local pc
        ssh -L 8410:server13:80 dgarlisi@ops.wilab2.ilabt.iminds.be -v
        http://127.0.0.1:8410/crewdemo/plots/usrp.png

###TO CONNECT THE ALIXNODE TO INTERNET
    #on alixnode
        sudo ip route add default via 172.16.0.100 dev eth0
        add nameserver 8.8.8.8 on resolv.conf
    #on alix server
        sudo /sbin/iptables -P FORWARD ACCEPT
        sudo /sbin/iptables --table nat -A POSTROUTING -o eth0 -j MASQUERADE



### WORKING ON PALERMO TESTBED
#connect to controller PC
    ssh lab.tti.unipa.it

#move files on ttilab
    rsync -avz --delete  ./wishful-github-manifest-3  -e ssh domenico@lab.tti.unipa.it:/home/domenico/work/
    cd work/wishful-github-manifest-3/examples/wmp/wmp_metamac/

        cd wmp_helper/
    #deploy framework on alixnodes
        sh deploy_upis.sh alix02,alix04,alix05,alix10,alix14
    #sync nodes time:
        sh sync_date.sh alix02,alix04,alix05,alix10,alix14
        cd ..

#start agent
python3 metamac_agent --config agent_config.yaml
python3 metamac_agent --config agent_config_ap.yaml

#start controller
python3 metamac_testbed_controller --config controller_config_nova.yaml
    #test network
    ping 192.168.3.102
python3 metamac_experiment_controller --config controller_config_nova.yaml

#forward command
ssh -L 8301:127.0.0.1:8301 domenico@lab.tti.unipa.it -v
ssh -L 8300:127.0.0.1:8300 domenico@lab.tti.unipa.it -v

#start USRP
    ssh lab.tti.unipa.it
    ssh clapton.local
    sudo /home/domenico/work/CREW_FINAL_DEMO/pyTrackers/pyUsrpTracker/run_usrp.sh 6
    ssh -L 8310:10.8.9.3:80 domenico@lab.tti.unipa.it
    http://127.0.0.1:8310/crewdemo/plots/usrp.png
    python metamac_visualizer.py