# WiSHFUL GNURadio example tutorial

For any information or issue, please contact Maicon Kist at kistm@tcd.ie

## Goal of this experiment

The goal of this experiment is to create an example tutorial for the WiSHFUL framework and the UPI functions usage that
run on GNURadio platform.
Specifically, this experiment uses the WiSHFUL framework and the UPI functions to set-up a GNURadio Tx/Rx pair and change parameters. All the UPI functions used in this example tutorial are fully documented at link https://wishful-project.github.io/wishful_upis/ and this example tutorial can be found at the link https://github.com/wishful-project/examples

We want to demonstrate how the WISHFUL UPI can be exploited to:
*i*) Setup two GNURadio waveforms, an OFDM Tx and a OFDM Rx;
*ii*) Show the use of UPI_R to monitor nodes parameters;
*iii*) Show the use of UPI_R functions to tune the nodes parameters.

# Getting Started

## 1. Reserving the VM's

Reserve ***three WiSHFUL nodes*** by using the reservation system at : https://www.iris-testbed.connectcentre.ie/reservation

These VMs are used as follows:
(*i*) one VM to run the the controller program, or WiSHFUL controller;
(*ii*) one VM to run the Tx;
(*iii*) one VM to run the RX.

### The WiSHFUL controller node

The controller is implemented in ```wishful_simple_controller.py```

The controller program permits to: (*i*) discovery of agent nodes, (*ii*) installation of GNURadio waveforms on the agents, (*iii*) monitor values from the GNURadio waveform, and (*iv*) configure parameters on the GNURadio waveform.

In addition, the WiSHFUL controller executes the logic
for controlling the experiment, where we distinguish three phases: (*i*) we wait for all agent nodes to connect in the WiSHFUL controller, (*ii*) setup the corresponding waveforms in each agent, and (*iii*) monitor/configure parameters on the GNURadio waveforms.

### The WiSHFUL agents

The two agents that we will use in this example dont implement any specific functionality. Their sole purpose in this experiment is to connect to the WiSHFUL controller and wait for instructions (passed through UPI calls).

The agents are implemented in:
- ```agent_tx.py``` for the transmitter;
- ```agent_rx.py``` for the receiver

In order to better understand all the phases of the this example tutorial and the single UPI function usage, we add
inline comment to both controller and agent programs.

## 2. Access WiSHFUL CONTROLLER
1. Open a shell in your computer.
2. Connect to controller PC (you can find the command in the reservation webpage):
    ```
    ssh -A -X -i your-private-key user@controller-vm-ip -oPort=22 -oProxyCommand='ssh -i path-to-your-private-key -oPort=22 user@134.226.55.214 -W %h:%p'
   ```
3. Move in the experiment directory
    ```
    cd /opt/examples/Get_Started_Examples/Simple-GNURadio-Example
    ```
4. Open ```wishful_simple_controller.py``` and change the following variables, replacing their values accordingly:
    ```
    controller_PC_IP_address = "controller-vm-ip" 
    controller_PC_interface = "ethinterface"
    ```
5. Start controller
    ```
    chmod +x wishful_simple_controller
    ./wishful_simple_controller (#run with -v for debugging)
    ```

## 3. Access the TX agent
1. Open a shell in your computer (you should have two shells now)
2. Connect to agent TX PC
    ```
    ssh -A -X -i your-private-key user@tx-vm-ip -oPort=22 -oProxyCommand='ssh -i path-to-your-private-key -oPort=22 user@134.226.55.214 -W %h:%p'
   ```
3. Move in the experiment directory
    ```
    cd examples/Get_Started_Examples/Simple-GNURadio-Example
    ```
4. Open ```agent_tx.py``` and change the following variables.
    ```
    agent_PC_interface = "ethernet_interface"
    ```
5. Start the TX agent
    ```
    chmod +x agent_tx
    ./agent_tx (#run with -v for debugging)
    ```
    
## 4. Access the RX agent
1. Open a shell in your computer (you should have three shells now)
2. connect to controller PC 
    ```
    ssh -A -X -i your-private-key user@rx-vm-ip -oPort=22 -oProxyCommand='ssh -i path-to-your-private-key -oPort=22 user@134.226.55.214 -W %h:%p'
   ```
3. move in the experiment directory
    ```
    cd examples/Get_Started_Examples/Simple-GNURadio-Example
    ```
4. Open ```agent_rx.py``` and change the following variables.
    ```
    agent_PC_interface = "ethernet_interface"
    ```
5. start the RX agent
    ```
    chmod +x agent_rx
    ./agent_rx (#run with -v for debugging)
    ```

## Acknowledgement
The research leading to these results has received funding from the European Horizon 2020 Programme under grant agreement n645274 (WiSHFUL project).

