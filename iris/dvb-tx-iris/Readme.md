# Interaction with the WiSHFUL framework
The DVB-T modulator has been conceived as a WiSHFUL Extension, it is possible
to control its operation by means of the WiSHFUL tools: thanks to the Patron TCD,
there is special controller module, named _forgecontroller_, that can be instantiated
in the xml file with the following lines

```xml
<controller class="forgecontroller">  
</controller>
```

and that can be used to control some operational parameters of the Iris DVB-T transmitter,
such as the frequency, the amplifier gain, and the output power.
The WiSHFUL controller can be directly used to modify one or more of the three
parameters in a single call to the WiSHFUL framework, together with a local WiSHFUL agent.
In order to start the controller, a specialized Python environment needs to be set-up.
With reference to the WiSHFUL code root folder, the controller and its environment
are started with the following commands

<code>. ./up_controller.sh</code>  
<code>cd examples/iris/dvb-tx-iris</code>  
<code>./start_controller.sh</code>

In another terminal one can start the slave/agent, with the following commands

<code>. ./up_slaves.sh</code>  
<code>cd examples/iris/dvb-tx-iris</code>  
<code>./start_agent.sh</code>

Finally, the Iris radio configuration XML file (with the specialized
Iris/WiSHFUL controller) can be loaded and run inside of Iris with the command

<code>./start_iris</code>

The output of Iris now will contain also the pings emitted by the Iris
controller in charge of talking with the WiSHFUL framework

<pre>
...  
Events Received: 0  
Events Received: 0  
Events Received: 0  
Events Received: 0  
Events Received: 0  
[INFO]    dvbt1scrambler1: Current TS bitrate: 22.4013 Mbps  
Events Received: 0  
Events Received: 0  
...  
</pre>

The controller will fire up when it receives an event from the
WiSHFUL controller (via the WiSHFUL agent). In the controller window,
we can enter the new transmission parameters

<pre>
************************ Wishful Controller  ************************  
*                                                                   *  
************************  Iris Integration   ************************  
Change the frequency: (y/n): y  
Write the frequency: 666000000  
Change the gain: (y/n): y  
Write the gain: 5  
Change the outpower: (y/n): y  
Write the outpower: 50  
New node appeared:  
ID: a58546ee-0d81-45d7-a414-566256572475  
IP: 127.0.0.1  
Name: agent_123  
Info: agent_info  
Modules: {0: 'LocalControlModule', 1: 'IrisModule', 2: 'PyreDiscoveryAgentModule'}  
Module_Functions: {0: ['stop_local_control_program', 'send_msg_to_local_control_program',
'start_local_control_program'], 1: ['set_outpower', 'set_frequency', 'set_rate', 'set_gain']}  
Module_Generators: {}  
Interfaces: {0: 'iris'}  
Iface_Modules: {0: [1]}  
Modules_without_iface: [0, 2]  
Sending parameters. . .  
Waiting return. . .  
2016-11-04 14:31:25.139233 DEFAULT CALLBACK : Group: all, NodeName: agent_123,
Cmd: set_frequency, Returns: ok  
2016-11-04 14:31:25.140457 DEFAULT CALLBACK : Group: all, NodeName: agent_123,
Cmd: set_gain, Returns: ok  
2016-11-04 14:31:25.141196 DEFAULT CALLBACK : Group: all, NodeName: agent_123,
Cmd: set_outpower, Returns: ok  
...  
</pre>

After a while, the WiSHFUL controller has received a positive
confirmation of the change of the transmission parameters. In the same time,
in the Iris output window, the events are received, executed, and confirmed back

<pre>
...  
Events Received: 0  
Received cmd: set:phyengine14.usrptx1.frequency=666000000  
handle_read: Sending ok:  
Received cmd: set:phyengine14.usrptx1.gain=5  
handle_read: Sending ok:  
Received cmd: set:phyengine11.dvbt1ofdmmod1.outpower=50  
handle_read: Sending ok:  
Received Event: (set, phyengine14.usrptx1.frequency=666000000)  
Received Event: (set, phyengine14.usrptx1.gain=5)  
Received Event: (set, phyengine11.dvbt1ofdmmod1.outpower=50)  
Events Received: 3  
[INFO]    usrptx1: Setting TX Frequency: 666MHz...  
[INFO]    usrptx1: LOG TX Frequency: 666MHz  
[INFO]    phyengine14: Reconfigured parameter frequency : 666000000  
[INFO]    usrptx1: Gain range: (0, 31.5, 0.5)  
[INFO]    usrptx1: Setting TX Gain: 5 dB...  
[INFO]    usrptx1: Actual TX Gain: 5 dB...  
[INFO]    phyengine14: Reconfigured parameter gain : 5  
[INFO]    phyengine11: Reconfigured parameter outpower : 50  
Events Received: 3  
Events Received: 3  
[INFO]    dvbt1scrambler1: Current TS bitrate: 22.3485 Mbps  
Events Received: 3  
...  
</pre>
