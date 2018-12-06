"""
contiki_agent.py: Implementation of WiSHFUL agent for Contiki

Usage:
   contiki_agent.py [options] [-q | -v]

Options:
   --logfile name      Name of the logfile
   --discovery-interface discoveryInterface Ethernet interface used for node discovery.
   --lowpan-interfaces lowpanInterface 6LowPan interfaces connected to agent.

Example:
   ./contiki_agent --discovery-interface eno1 --lowpan-interfaces lowpan0;lowpan1

Other options:
   -h, --help          show this help message and exit
   -q, --quiet         print less text
   -v, --verbose       print more text
   --version           show version and exit
"""

import logging
import wishful_agent

__author__ = "Peter Ruckebusch"
__copyright__ = "Copyright (c) 2018, Ghent University, IDLAB, IMEC"
__version__ = "0.1.0"

log = logging.getLogger('contiki_agent.main')
control_agent = wishful_agent.Agent()

def main(args):

    discovery_interface = args['--discovery-interface']
    lowpan_interfaces = args['--lowpan-interfaces'].strip(";").split(";")
    print("interfaces {}".format(lowpan_interfaces))

    control_agent.set_agent_info(name="ContikiAgent", info="ContikiAgent", iface=discovery_interface)

    control_agent.add_module(moduleName="discovery", pyModule="wishful_module_discovery_pyre", className="PyreDiscoveryAgentModule", kwargs={"iface":discovery_interface, "groupName":"wishful_param_sweep"})

    control_agent.add_module(moduleName="gitar_engine", pyModule="wishful_module_gitar", className="GitarEngine", interfaces=lowpan_interfaces, kwargs={"GitarConfig" : './config/localhost/gitar.ini', "SupportedInterfaces": lowpan_interfaces})

    control_agent.add_module(moduleName="generic_connector", pyModule="wishful_module_generic", className="GenericConnector", interfaces=lowpan_interfaces, kwargs={"ControlAttributes": {"generic_connector": './config/protocol_connectors/generic_ctrl_attributes.csv'}, "ControlFunctions" : {"generic_connector": './config/protocol_connectors/generic_ctrl_functions.csv'}, "ProtocolConnectors": {"generic_connector": 0}, "SupportedInterfaces": lowpan_interfaces})

    control_agent.add_module(moduleName="ipv6_connector", pyModule="wishful_module_ipv6", className="IPv6Connector", interfaces=lowpan_interfaces, kwargs={"ControlAttributes": {"ipv6_connector": './config/protocol_connectors/ipv6_ctrl_attributes.csv', "rpl_connector": './config/protocol_connectors/rpl_ctrl_attributes.csv', "node_connector" : './config/protocol_connectors/node_ctrl_attributes.csv'}, "ControlFunctions" : {"ipv6_connector": './config/protocol_connectors/ipv6_ctrl_functions.csv', "rpl_connector": './config/protocol_connectors/rpl_ctrl_functions.csv', "node_connector" : './config/protocol_connectors/node_ctrl_functions.csv'}, "ProtocolConnectors": {'ipv6_connector': 1, 'rpl_connector': 2, "node_connector": 9}, "SupportedInterfaces": lowpan_interfaces})

    control_agent.add_module(moduleName="taisc_connector", pyModule="wishful_module_taisc", className="TAISCConnector", interfaces=lowpan_interfaces, kwargs={"RadioPrograms" : {"CSMA":0,"TDMA":2,"TSCH":1}, "ControlAttributes" : {'taisc_connector': './config/protocol_connectors/taisc_ctrl_attributes.csv'}, "ControlFunctions" : {'taisc_connector': './config/protocol_connectors/taisc_ctrl_functions.csv'}, "ProtocolConnectors": {'taisc_connector': 3}, "SupportedInterfaces": lowpan_interfaces})

    control_agent.run()


if __name__ == "__main__":
    try:
        from docopt import docopt
    except:
        print("""
        Please install docopt using:
            pip install docopt==0.6.1
        For more refer to:
        https://github.com/docopt/docopt
        """)
        raise

    args = docopt(__doc__, version=__version__)

    log_level = logging.INFO  # default
    if args['--verbose']:
        log_level = logging.DEBUG
    elif args['--quiet']:
        log_level = logging.ERROR

    logfile = None
    if args['--logfile']:
        logfile = args['--logfile']

    logging.basicConfig(filename=logfile, level=log_level, format='%(asctime)s - %(name)s.%(funcName)s() - %(levelname)s - %(message)s')

    try:
        main(args)
    except KeyboardInterrupt:
        log.debug("Agent exits")
    finally:
        log.debug("Exit")
        control_agent.stop()
