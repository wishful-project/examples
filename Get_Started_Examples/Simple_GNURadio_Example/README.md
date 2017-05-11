WiSHFUL GNURadio example tutorial
============================

For any information or issue, please contact Maicon Kist at kistm@tcd.ie

The goal of this experiment is to create an example tutorial for the WiSHFUL framework and the UPI functions usage that
run on GNURadio platform. Specifically, this experiment uses the WiSHFUL framework and the UPI functions to set-up a GNURadio Tx/Rx pair and change parameters. All the UPI functions used in this example tutorial are fully
documented at link https://wishful-project.github.io/wishful_upis/ and this example tutorial can be found at the link
https://github.com/wishful-project/examples

We want to demonstrate how the WISHFUL UPI can be exploited to:
i) Setup two GNURadio waveforms, an OFDM Tx and a OFDM Rx;
ii) Show how to use the UPI to monitor the nodes parameters;
iii) Show how use the UPI functions to tune the nodes parameters;

In order to implement the experiment, we need 3 VM's in the Iris Tesbed. These VMs are used as follows: (i) one VM to run the the controller program, or WiSHFUL controller, (ii) one VM to run the Tx, and (iii) one VM to run the RX .
The controller program permits to: (i) discovery of agent nodes, (ii) installation of GNURadio waveforms on the agents, (iii) monitor values from the GNURadio waveform, and (iv) configure parameters on the GNURadio waveform.

In addition, the WiSHFUL controller executes the logic
for controlling the experiment, where we distinguish three phases: (i) we wait for all agent nodes to connect in the WiSHFUL controller, (ii) setup the corresponding waveforms in each agent, and (iii) monitor/configure parameters on the GNURadio waveforms.

The present example tutorial has been tested on the WiSHFUL platform nodes present in the Iris Testbet.

In order to better understand all the phases of the this example tutorial and the single UPI function usage, we add
inline comment to both controller and agent programs.


This example tutorial is composed of three main python programs and other 2 additional GNURadio grc files.
The python programs are (i) wishful_simple_controller that runs on experiment PC and performs experiment actions,
(ii) agent_tx which is the GNURadio agent that will be the transmitter and (iii) agent_rx for the receiver (in fact both agents have the same code, the only thing that changes is that they identify themselves with different names to the WiSHFUL controller).

### Experiment nodes selection and interface configuration
The wishful_simple_controller, agent_tx, and agent_rx contains a setting part, that must been
setted with the experiment nodes and PC information. For each node is needed reporting ip, name and interface.
An example of configuration is reported below.

"""
Setting of experiment nodes, ip address and name
"""
#wishful_simples_controller
controller_PC_ip_address = "172.16.0.100"
controller_PC_interface = "eth0"

# agent_tx
agent_PC_ip_address = "172.16.0.101"
agent_PC_interface = "eth0"

# agent_rx
agent_PC_ip_address = "172.16.0.201"
agent_PC_interface = "eth0"


"""
END setting of experiment nodes
"""

### 1. Reserve and run the experiment in Iris Testbed
Reserve three nodes by using the reservation system at : https://www.iris-testbed.connectcentre.ie/reservation.

### 2. Starting the experiment 

After gaining access to the nodes that you reserved, you can start the experiment. You can use any of the nodes as the controller, TX or RX, as long as yout do the proper IP configurations mentioned

    SHELL 1 - WiSHFUL CONTROLLER :
        - connect to controller PC (you can find the command in the reservation webpage):
				ssh -A -X -i your-private-key user@controller-vm-ip -oPort=22 -oProxyCommand='ssh -i path-to-your-private-key -oPort=22 user@134.226.55.214 -W %h:%p '

        - move in the experiment directory
                cd examples/Get_Started_Examples/Simple-GNURadio-Example

		  - configure the necessary variables in wishful_simple_controller file
					 open wishful_simple_controller with the texteditor of your choice
					 change the variable controller_PC_ip_address to match the IP of this VM

        - start controller
            chmod +x wishful_simple_controller
            ./wishful_simple_controller (#run with -v for debugging)


    SHELL 2  - TX :
        - connect to agent TX PC

        - move in the experiment directory
                cd examples/Get_Started_Examples/Simple-GNURadio-Example

		  - configure the necessary variables in agent_tx file
					 open agent_tx with the texteditor of your choice
					 change the variables agent_PC_ip_address and agent_PC_interface

        - start the TX agent
            chmod +x agent_tx
            ./agent_tx (#run with -v for debugging)

    SHELL 2  - RX :
        - connect to controller PC 

        - move in the experiment directory
                cd examples/Get_Started_Examples/Simple-GNURadio-Example

		  - configure the necessary variables in agent_rx file
					 open agent_tx with the texteditor of your choice
					 change the variables agent_PC_ip_address and agent_PC_interface

        - start the RX agent
            chmod +x agent_rx
            ./agent_rx (#run with -v for debugging)

## Acknowledgement
The research leading to these results has received funding from the European
Horizon 2020 Programme under grant agreement n645274 (WiSHFUL project).
