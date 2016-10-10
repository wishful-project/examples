__author__ = "Peter Ruckebusch"
__copyright__ = "Copyright (c) 2016, Ghent University, iMinds"
__version__ = "0.1.0"

# Definition of Local Control Program that is in place for measuring with some extensions it can also be made to configure devices.


def measurement_collector(control_engine):
    # do all needed imports here!!!
    import time
    import datetime
    import gevent

    @control_engine.set_default_callback()
    def default_callback(cmd, data):
        #print(("{} DEFAULT CALLBACK : Cmd: {}, Returns: {}".format(datetime.datetime.now(), cmd, data)))
        #~ control_engine.send_upstream({"cmd": cmd, "result": data})
        pass

    def collector_thread(interfaces, upi_type, measurement_key_list, collect_period, report_period, num_iterations, report_callback):
        if collect_period < report_period:
            report_period = collect_period


    def report_callback(report_name, event_value):
        control_engine.send_upstream({"report_name": event_name, "event_value": event_value})
        pass

    print(("local measurement collector - Name: {}, Id: {} - STARTED".format(control_engine.name, control_engine.id)))

    # control loop

    while not control_engine.is_stopped():
        msg = control_engine.recv(block=False)
        if msg is not None and type(msg) is dict and msg['command'] == 'GET_MEASUREMENTS_PERIODIC':
            radio_platforms = []

            else:
                print("local event listener unknown command {}".format(msg['command']))
        else:
            print("local event listener unknown msg type {}".format(msg))

        gevent.sleep(5)

    print(("local event listener - Name: {}, Id: {} - STOPPED".format(control_engine.name, control_engine.id)))
