#run example controller
#run with -v for debugging
./wishful_simple_controller --config ./controller_config.yaml 

#run example agent - scapy requires sudo !!!
#run with -v for debugging
sudo su
source ../../dev/bin/activate
./wishful_simple_agent --config ./agent_config.yaml