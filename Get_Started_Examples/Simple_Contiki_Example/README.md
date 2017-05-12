# WiSHFUL Contiki example tutorial

The goal of this example tutorial is to demonstrate how to use the WiSHFUL framework and the UPI functions with Contiki sensor nodes. Specifically, this experiment uses the WiSHFUL framework and the UPI functions to modify configuration parameters in, and obtain monitoring info from, a sensor node using a global control program.

All the UPI functions used in this example tutorial are fully documented at link https://wishful-project.github.io/wishful_upis/ and this example tutorial can be found at the link https://github.com/wishful-project/examples.

We want to demonstrate how the WISHFUL UPI can be exploited for:
1. Setting up a small scale IPv6 network by configuring a node as RPL border router.
2. Reading the current value of the configuration parameters.
3. Changing the value of configuration parameters.
4. Obtaining monitoring information.

## Prerequisites
* An active reservation in Wilab 1 (office) or Wilab 2 (clean room).
* Experiment is swapped in using jFed with a correct image (see "Appendix I.	Creating a sensor compatible Ubuntu image." in WiSHFUL user guide for sensors.doc)
* WiSHFUL and Contiki repositories are correctly configured (see "II.	Initial set-up of repositories and WiSHFUL environment." in WiSHFUL user guide for sensors.doc).
* All the required tools and dependencies are installed.

## Step-by-step tutorial
First we need to flash an appropriate Contiki firmware on the sensor derives. Then we need to start an agent on each Linux machine and a global control program. In most cases, the agent code is always the same. The global control program on the other hand implements the required control logic and differs between different experiments.

### Compile and flash a WiSHFUL binary
Make sure you assign a different node ID to each sensor and select the correct USB device.
```bash
# goto Contiki directory
cd /groups/wall2-ilabt-iminds-be/<your-project-name>/contiki-imec
#goto IPv6 example with default contiki radio/rdc/mac driver
cd examples/wishful-ipv6/nullrdc-csma/

# Program Zolertia Zoul remote rev A
make TARGET=zoul BOARD=remote NODEID=0x0002 udp-example
make TARGET=zoul BOARD=remote NODEID=0x0002 udp-example.upload

# Program Imec RM090
make TARGET=rm090 udp-example
tos-set-symbols --objcopy msp430-objcopy --objdump msp430-objdump --target ihex  udp-example.rm090 udp-example.ihex node_id=1
../../../tools/rm090/ibcn-f5x-tos-bsl -c /dev/ttyUSB0 -5 -R --invert-reset --swap-reset-test -r -e -I -p udp-example.ihex
```
### Localhost example
Start a WiSHFUL agent:
```
python agent.py --config config/agent_configs/agent_lpl_csma_ipv6.yaml
```
Start a global control program that retrieves all configuration parameters and measurements from the attached sensor devices.
```
python global_cp.py --config config/localhost/global_cp_config.yaml
```

## Acknowledgement
The research leading to these results has received funding from the European
Horizon 2020 Programme under grant agreement n645274 (WiSHFUL project).
