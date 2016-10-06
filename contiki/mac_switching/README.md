
# TAISC mac switching example

In this example a global control program (`global_cp.py`) switches the MAC protocol on all nodes every X seconds.
The application RX events are captured by a local control program (`local_cp.py`).
This local CP is installed and started on all Linux host PCs using hierarchical control (HC) engine.
Also the locally observed events are forwared from the local CPs to the global CP using the HC engine.

## Example setup
On all Linux hosts, flash the RM-090 nodes. For each sensor modify the `SHORT_ADDR` and `SERIAL_DEV` arguments.
```
cd binaries/
./flash_nodes Wishful-application.rm090 <START_ADDR> <SERIAL_DEV)
```

## Example execution
