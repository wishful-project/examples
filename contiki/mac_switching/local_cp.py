__author__ = "Peter Ruckebusch"
__copyright__ = "Copyright (c) 2016, Ghent University, iMinds"
__version__ = "0.1.0"

# Definition of Local Control Program that is in place for measuring with some extensions it can also be made to configure devices.


def my_local_control_program(control_engine):
    # do all needed imports here!!!
    import time
    import datetime
    import gevent

    @control_engine.set_default_callback()
    def default_callback(cmd, data):
        print(("{} DEFAULT CALLBACK : Cmd: {}, Returns: {}".format(datetime.datetime.now(), cmd, data)))
        control_engine.send_upstream({"cmd": cmd, "result": data})

    def event_handler(event_name, event_value):
        control_engine.send_upstream({"event_name": event_name, "event_value": event_value})
        print(("{} Forwarding event {} with value: {}".format(datetime.datetime.now(), event_name, event_handler)))
        pass

    radio_platforms = control_engine.blocking(True).radio.iface("lowpan0").get_radio_platforms()
    for platform in radio_platforms:
        control_engine.blocking(False).net.iface(platform).subscribe_events_net(["RIME_appPerPacket_rxstats"],event_handler,0)
    print(("\nLocal Control Program - Name: {}, Id: {} - STARTED".format(control_engine.name, control_engine.id)))

    # control loop
    while not control_engine.is_stopped():
        gevent.sleep(10)
        print(("Local Control Program - Name: {}, Id: {} - RUNNING".format(control_engine.name, control_engine.id)))

    print(("Local Control Program - Name: {}, Id: {} - STOPPED".format(control_engine.name, control_engine.id)))
