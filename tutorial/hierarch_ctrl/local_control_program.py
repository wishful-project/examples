"""
Local control program to be executed on remote nodes.
"""

__author__ = "Piotr Gawlowicz, Anatolij Zubow"
__copyright__ = "Copyright (c) 2016, Technische Universität Berlin"
__version__ = "0.1.0"


# Definition of Local Control Program
def my_local_control_program(controller):
    # do all needed imports here!!!
    import time
    import datetime

    @controller.set_default_callback()
    def default_callback(cmd, data):
        print(("DEFAULT CALLBACK : Cmd: {}, Returns: {}".format(cmd, data)))
        result = controller.radio.iface("wlan0").get_channel()
        print(("Channel is: {}".format(result)))
        controller.send_upstream({"myChannel": result})


    # control loop
    print("Local ctrl program started: {}".format(controller.name))
    while not controller.is_stopped():
        msg = controller.recv(timeout=1)
        if msg:
            ch = msg["new_channel"]

            print("Schedule set channel to {} in 5s:".format(ch))
            controller.delay(5).radio.iface("wlan0").set_channel(ch)

    print("Local ctrl program stopped: {}".format(controller.name))