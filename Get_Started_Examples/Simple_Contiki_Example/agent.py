"""
contiki_control_agent.py: Implementation of WiSHFUL control agent for Contiki

Usage:
   agent.py [options] [-q | -v]

Options:
   --logfile name      Name of the logfile
   --config configFile Config file path

Example:
   python agent.py -v --config ./control_agent_config.yaml

Other options:
   -h, --help          show this help message and exit
   -q, --quiet         print less text
   -v, --verbose       print more text
   --version           show version and exit
"""

import logging
import yaml
import wishful_agent

__author__ = "Peter Ruckebusch"
__copyright__ = "Copyright (c) 2016, Ghent University, iMinds"
__version__ = "0.1.0"

# Get a logger.
log = logging.getLogger('contiki_control_agent.main')

# Create a WiSHFUL agent
control_agent = wishful_agent.Agent()

# Main function
def main(args):
    log.debug(args)
    # Get the agent configuration
    config_file_path = args['--config']
    config = None
    with open(config_file_path, 'r') as f:
        config = yaml.load(f)
    # Load the modules specified in the agent configuration
    control_agent.load_config(config)
    # Start the WiSHFUL agent
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

    logging.basicConfig(filename=logfile, level=log_level,
        format='%(asctime)s - %(name)s.%(funcName)s() - %(levelname)s - %(message)s')

    try:
        main(args)
    except KeyboardInterrupt:
        log.debug("Agent exits")
    finally:
        log.debug("Exit")
        control_agent.stop()
