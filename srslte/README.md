WiSHFUL GNURadio example tutorial

For any information or issue, please contact Justin at justin.tallon@softwareradiosystems.com

## GOAL OF EXPERIEMNT ##

The goal of this experiement is to become familiar with the Wishful-srsLTE interface by setting up a simple tx-rx link and extracting some parameters



## 1. Reserving the VM's

1. Reserve ***two WiSHFUL nodes*** by using the reservation system at: https://www.iris-testbed.connectcentre.ie/reservation



## 2. Access the TX agent
1. Open a shell in your computer
2. Connect to agent TX PC
    ```
    ssh -A -X -i your-private-key user@tx-vm-ip -oPort=22 -oProxyCommand='ssh -i path-to-your-private-key -oPort=22 user@134.226.55.214 -W %h:%p'
   ```
3. Move in the experiment directory
    ```
    cd /opt/wishful/examples/srslte
    ```
4. Open ```agent_tx.py``` and change the "ethernet_interface" by the Ethernet inferface connected in the Iris testbed internal network (NOTE: much likely the interface is **ens3**):
    ```
    agent_PC_interface = "ethernet_interface"
    ```
5. Start the TX agent
    ```
    chmod +x agent_tx
    ./agent_tx (#run with -v for debugging)
    ```
    
## 3. Access the RX agent
1. Open a shell in your computer (you should have three shells now)
2. Connect to controller PC 
    ```
    ssh -A -X -i your-private-key user@rx-vm-ip -oPort=22 -oProxyCommand='ssh -i path-to-your-private-key -oPort=22 user@134.226.55.214 -W %h:%p'
   ```
3. Move in the experiment directory:
    ```
    cd /opt/wishful/examples/srslte
    ```
4. Open ```agent_rx.py``` and  change the "ethernet_interface" by the Ethernet inferface connected in the Iris testbed internal network (NOTE: much likely the interface is **ens3**):
    ```
    agent_PC_interface = "ethernet_interface"
    ```
5. Start the RX agent:
    ```
    chmod +x agent_rx
    ./agent_rx (#run with -v for debugging)


## 4. Access WiSHFUL CONTROLLER
1. On one of the existing nodes, it doesnt matter which one:


2. Move in the experiment directory
    ```
    cd /opt/wishful/examples/srslte
    ```
3. Open ```wishful_simple_controller.py``` and change "controller-vm-ip" and "ethinterface" by the IP address and the Ethernet interface of the Iris testbed network (NOTE: much likely the IP starts with **192.168.*.* ** and the interface is **ens3**): 
    ```
    controller_PC_IP_address = "controller-vm-ip" 
    controller_PC_interface = "ethinterface"
    ```
4. Start controller
    ```
    chmod +x wishful_simple_controller
    ./wishful_simple_controller_txrx (#run with -v for debugging)
    ```




at this point the Controller and two agents should be up and running.

In this experiement, we set the desired parameters in both the UE and the ENB before beginning to transmit and then receive our own signal. We then ensure our parameters are correct by querying them and make runtime reconfigurations if necessary. After this we take some measurements at the UE, make some reconfigurations at the ENB based on these measurmments before closing our agents and ending the experiement.


The controller drives the actions taken in the experiment. All possible actions can be carried out by the following UPI calls:


controller.node(nodes[0]).radio.activate_radio_program(<name_of_agent>)

is used to start an agent radio

controller.node(nodes[0]).radio.deactivate_radio_program(<name_of_agent>)


is used to stop a radio


parameters are set as follows:

controller.node(nodes[0]).radio.set_parameters({'<param_name>':<param_value>})

possible <param_names> in the case that the node is a UE: 

Frequency [‘LTE_UE_DL_FREQ’]: 				The frequency of reception
Gain [‘LTE_UE_RX_GAIN’]: 					The gain of the rf frontend.
No of antennas ['LTE_UE_NO_OF_ANTENNAS']: 		Number of antennas to receive with.
Equalizer mode['LTE_UE_EQUALIZER_MODE']: 		The algorithm used for equalization
Max turbo decoder its ['LTE_UE_MAX_TURBO_ITS']: 	Sets the maximum number of iterations allowed in the turbodecoder.
SSS algorithm ['LTE_UE_SSS_ALGORITHM']: 		The algorithm to use in the SSS detection.
Noise estimation algorithm: ['LTE_UE_NOISE_EST_ALG']: 	The algorithm used for noise estimation.
SNR EPA coeff ['LTE_UE_SNR_EMA_COEFF']: 		The coefficient for the SNR exponential moving average coefficient.
CFO tolerance ['LTE_UE_CFO_TOL']: 			The allowable Carrier Frequency offset.
RNTI ['LTE_UE_RX_RNTI']:   Radio Network Temporary Identifier

The ranges of acceptable values are as follows:

'LTE_UE_DL_FREQ': depends on the RF frontend for the TCD testbed its XXX
'LTE_UE_RX_GAIN': depends on the RF frontend usually 0-30
'LTE_UE_NO_OF_ANTENNAS': 1 or 2
'LTE_UE_EQUALIZER_MODE': Zero forcing or mmse denoted by 'zf' and 'mmse' respectively
'LTE_UE_MAX_TURBO_ITS': 0-4
'LTE_UE_SSS_ALGORITHM': 0,1 or 2 denoting the full, partial or diff algorithm respectively
'LTE_UE_NOISE_EST_ALG': 0,1 or 2 denoting PSS estimation, Reference Signal estimation or Empty Carrier estimation respectively
'LTE_UE_SNR_EMA_COEFF': 0-1 
'LTE_UE_CFO_TOL':0-50
'LTE_UE_RX_RNTI': 0-0xFFFF:  RNTIs are used to differentiate/identify a connected mode UE in the cell

possible <param_names> in the case that the node is a ENB:

Frequency [‘LTE_ENB_DL_FREQ’]:The frequency of the transmission.
Rf amp [‘LTE_ENB_RF_AMP’]: The soft amplitude of the transmitted signal.
Gain [‘LTE_ENB_TX_GAIN’]: The gain of the frontend.
Number of frames [‘LTE_ENB_NO_OF_FRAMES’]: The number of frames to transmit.
Which prbs [‘LTE_ENB_WHICH_PRBS’]: mask of which prbs to use.
bandwidth [‘LTE_ENB_DL_BW’]: Bandwidth of the transmission (bw).
MCS [‘LTE_ENB_MCS’]: The modulation and coding scheme.
PDSCH data [‘LTE_ENB_PDSCH_DATA’]: Whether or not to put data over the pdsch channel.
network port [‘LTE_ENB_NET_PORT’]: The TCP port to listen for data to transmit
RNTI ['LTE_ENB_RNTI']:   Radio Network Temporary Identifier

The range of acceptable values are as follows:

'LTE_ENB_DL_FREQ': depends on the RF frontend for the TCD testbed its XXX
'LTE_ENB_RF_AMP': 0-1
'LTE_ENB_TX_GAIN': depends on the RF frontend usually 0-30
'LTE_ENB_NO_OF_FRAMES': 1-anything (-1 for indefinite)
'LTE_ENB_WHICH_PRBS': 0xFFFF is all on 0x0000 is all off, hexidecimal mask to represent on/off prbs (must be contiguous)
'LTE_ENB_DL_BW': 2MHz,5MHz,10MHz,20MHz
'LTE_ENB_MCS': 0 - 25
'LTE_ENB_PDSCH_DATA': True/False
'LTE_ENB_NET_PORT': any free port
'LTE_ENB_RNTI':   0 -> 0xFFFF

so if I wanted to set my frequency to 2410000000Hz the command would be the following:

controller.node(nodes[0]).radio.set_parameters({'LTE_ENB_DL_FREQ':2410000000})

it is also possible to query any of these parameters by using the following command:

freq = controller.node(nodes[0]).radio.get_parameters(['LTE_ENB_DL_FREQ'])



The other main functionality is the ability to get measurements which is carried out as follows:

meas = controller.node(nodes[0]).radio.get_measurements({<measurement_name>})

This can be used with any of the following flags:

Carrier Freq offset(kHz)[‘CFO’]:The CFO corrected by the receiver
Signal to Noise Ratio(dB)[‘SNR’]:The SNR measured at the receiver
Reference Signal Received Power()[‘RSRP’]:
Reference Signal Received Quality()[‘RSRQ’]:
Noise()[‘NOSIE’]:The noise strength
Channel State Information(I/Q)[‘CSI’]:A representation of the channel in I/Q 
Number of Frames(*)[‘N_FRAMES’]:The number of frames received by the UE
PDSCH miss(%)[‘PDSCH_MISS’]:The percentage of the PDSCH that the UE has failed to decode
PDCCH miss(%)[‘PDCCH_MISS’]:The percentage of the PDCCH that the UE has failed to decode
modulation order(*)[‘MOD’]:The modulation order being transmitted
transport block size(*)[‘TBS’]:The size of the transport blocks used in the turbodecoder
Received Signal Strength Indicator () ['RSSI']:
Channel Quality Indicator () ['CQI'] :
The ID of the cell being decoded () ['ENB_ID']:


and in the transmitter:

Number of frames transmitted () ['NUM_TX']





