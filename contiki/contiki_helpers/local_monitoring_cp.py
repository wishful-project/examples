__author__ = "Peter Ruckebusch"
__copyright__ = "Copyright (c) 2016, Ghent University, iMinds"
__version__ = "0.1.0"

# Definition of Local Control Program that is in place for monitoring.


def local_monitoring_program(control_engine):
    # do all needed imports here!!!
    import gevent

    @control_engine.set_default_callback()
    def default_callback(cmd, data):
        #print(("{} DEFAULT CALLBACK : Cmd: {}, Returns: {}".format(datetime.datetime.now(), cmd, data)))
        control_engine.send_upstream({"msg_type": "cmd_result", "cmd": cmd, "result": data})
        pass

    def event_handler(interface, event_name, event_value):
        control_engine.send_upstream({"msg_type": "event", "interface": interface, "event_name": event_name, "event_value": event_value})
        pass

    def report_callback(interface, report):
        control_engine.send_upstream({"msg_type": "report", "interface": interface, "report": report})
        pass

    print(("local monitor cp started - Name: {}, Id: {} - STARTED".format(control_engine.name, control_engine.id)))

    # control loop
    while not control_engine.is_stopped():
        msg = controller.recv(block=False)
        if msg is not None and type(msg) is dict and 'command' in msg:
            radio_platforms = []
            if 'interface' in msg:
                ifaces = msg['interface']
            else:
                ifaces = control_engine.blocking(True).radio.iface("lowpan0").get_radio_platforms()
            if msg['command'] == 'SUBSCRIBE_EVENT':
                for iface in ifaces:
                    if msg['upi_type'] == 'net':
                        control_engine.blocking(False).net.iface(iface).subscribe_events_net(msg['event_key_list'],event_handler,msg['event_duration'])
                    elif msg['upi_type'] == 'radio':
                        control_engine.blocking(False).radio.iface(iface).subscribe_events(msg['event_key_list'],event_handler,msg['event_duration'])
                    else:
                        print("async event listener unsupported upi_type {}".format(msg['upi_type']))
            elif msg['command'] == 'GET_MEASUREMENTS_PERIODIC':
                for iface in ifaces:
                    if msg['upi_type'] == 'net':
                        control_engine.blocking(False).iface(iface).net.get_measurements_periodic_net(msg['measurement_key_list'], msg['collect_period'], msg['report_period'], msg['num_iterations'], report_handler)
                    elif msg['upi_type'] == 'radio':
                        control_engine.blocking(False).iface(iface).radio.get_measurements_periodic(msg['measurement_key_list'], msg['collect_period'], msg['report_period'], msg['num_iterations'], report_handler)
                    else:
                        print("periodic measurement collector unsupported upi_type {}".format(msg['upi_type']))
            else:
                print("local monitoring unknown command {}".format(msg['command']))
        else:
            print("local monitoring unknown msg type {}".format(msg))

        gevent.sleep(5)

    print(("local monitor cp  - Name: {}, Id: {} - STOPPED".format(control_engine.name, control_engine.id)))
