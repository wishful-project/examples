__author__ = "Piotr Gawlowicz"
__copyright__ = "Copyright (c) 2015, Technische Universitat Berlin"
__version__ = "0.1.0"
__email__ = "gawlowicz@tkn.tu-berlin.de"


#Definition of Local Control Program
def my_local_control_program(controller):
    #do all needed imports here!!!
    import time
    import datetime


    @controller.set_default_callback()
    def default_callback(cmd, data):
        print(("{} DEFAULT CALLBACK : Cmd: {}, Returns: {}".format(datetime.datetime.now(), cmd, data)))
        result = controller.radio.iface("wlan0").get_channel()
        print(("{} Channel is: {}".format(datetime.datetime.now(), result)))
        controller.send_upstream({"myChannel":result})        


    #control loop
    print(("\nLocal Control Program - Name: {}, Id: {} - STARTED".format(controller.name, controller.id)))
    while not controller.is_stopped():
        msg = controller.recv(timeout=1)
        if msg:
            newChannel = msg["new_channel"]
            print("Next iteration:")

            print(("{} Scheduling set channel call with arg: {} in 5 seconds:".format(datetime.datetime.now(), newChannel)))
            controller.delay(5).radio.iface("wlan0").set_channel(newChannel)
        else:
            print(("{} Waiting for message".format(datetime.datetime.now())))

    print(("Local Control Program - Name: {}, Id: {} - STOPPED".format(controller.name, controller.id)))