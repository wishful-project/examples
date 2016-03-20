__author__ = "Piotr Gawlowicz"
__copyright__ = "Copyright (c) 2015, Technische Universitat Berlin"
__version__ = "0.1.0"
__email__ = "gawlowicz@tkn.tu-berlin.de"


#Definition of Local Control Program
def my_local_control_program_rule(controller):
    #do all needed imports here!!!
    import datetime
    from wishful_framework import TimeEvent, PktEvent, MovAvgFilter, PeakDetector, Match, Action, Permanance, PktMatch, FieldSelector


    def pkt_based_rule_matched(ruleId, data):
        print(("{} Pkt Rule with id: {} was matched; Data: {}".format(datetime.datetime.now(), ruleId, data)))
        controller.send_upstream({"PKT_DST":data})

    @controller.set_default_callback()
    def default_callback(cmd, data):
        print(("{} DEFAULT CALLBACK : Cmd: {}, Returns: {}".format(datetime.datetime.now(), cmd, data)))

    #control loop
    ruleDesc = None
    print(("\nLocal Control Program - Name: {}, Id: {} - STARTED".format(controller.name, controller.id)))
    while not controller.is_stopped():
        msg = controller.recv(timeout=1)
        if msg == "install_pkt_rule":
            print(("{} Get dest of all packets".format(datetime.datetime.now())))
            ruleDesc = controller.rule.add(event=PktEvent(iface="wlan0"),
                                           selector=FieldSelector("IP.dst"),
                                           permanence=Permanance.PERSISTENT,
                                           ctrl_callback=pkt_based_rule_matched)

            print(("{} New rule with ID: {} was added".format(datetime.datetime.now(), ruleDesc.id)))


        elif msg == "remove_rule":
            retVal = ruleDesc.remove()
            print(("{} Rule with ID: {} was {}".format(datetime.datetime.now(), ruleDesc.id, retVal)))
            controller.send_upstream("RULE WAS REMOVED")

        else:
            print(("{} Waiting for message".format(datetime.datetime.now())))

    print(("Local Control Program - Name: {}, Id: {} - STOPPED".format(controller.name, controller.id)))