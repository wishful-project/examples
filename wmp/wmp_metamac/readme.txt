METAMAC howto
ssh domenico@lab.tti.unipa.it
rsync -avz --delete  ./wishful-github-manifest-3  -e ssh domenico@lab.tti.unipa.it:/home/domenico/work/
cd wishful-github-manifest-3/examples/wmp/wmp_metamac/

cd wmp_helper/
sh deploy_upis.sh alix02,alix04,alix05,alix10,alix14
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
ssh -L 8401:127.0.0.1:8401 domenico@lab.tti.unipa.it -v
ssh -L 8400:127.0.0.1:8400 domenico@lab.tti.unipa.it -v

#start USRP
ssh domenico@lab.tti.unipa.it
ssh domenico@clapton.local
sudo /home/domenico/work/CREW_FINAL_DEMO/pyTrackers/pyUsrpTracker/run_usrp.sh 6
ssh -L 8484:10.8.9.3:80 domenico@lab.tti.unipa.it
http://127.0.0.1:8484/crewdemo/plots/usrp.png

python send_command_v4.py