"""
wifi_agent.py: Implementation of WiSHFUL agent for Contiki

Usage:
   wifi_agent.py [options] [-q | -v]

Options:
   --logfile name      Name of the logfile
   --discovery-interface discoveryInterface Ethernet interface used for node discovery.
   --wifi-interfaces wifiInterface Wi-Fi interfaces connected to agent.

Example:
   ./wifi_agent -v --discovery-interface eno1 --wifi-interfaces wlan0;wlan1

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

log = logging.getLogger('wifi_agent.main')
control_agent = wishful_agent.Agent()

def main(args):

    discovery_interface = args['--discovery-interface']
    wifi_interfaces = args['--wifi-interfaces'].strip(";").split(";")

    control_agent.set_agent_info(name="WiFiAgent", info="WiFiAgent", iface=discovery_interface)

    control_agent.add_module(moduleName="discovery", pyModule="wishful_module_discovery_pyre", className="PyreDiscoveryAgentModule", kwargs={"iface":discovery_interface, "groupName":"wishful_param_sweep"})

    control_agent.add_module(moduleName="wifi", pyModule="wishful_module_wifi_ath", className="Ath9kModule", interfaces=wifi_interfaces)

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
