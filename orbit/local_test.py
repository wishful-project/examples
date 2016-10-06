import logging
import datetime
import time
import random
from random import randint
import wishful_upis as upis
from wishful_agent.core import wishful_module
from wishful_agent.timer import TimerEventSender

__author__ = "Anatolij Zubow"
__copyright__ = "Copyright (c) 2016, Technische Universität Berlin"
__version__ = "0.1.0"
__email__ = "{zubow}@tkn.tu-berlin.de"

'''
Local test of WiFi component.

sudo ../../../dev/bin/wishful-agent --config config_local.yaml
'''

@wishful_module.build_module
class WifiTestController(wishful_module.ControllerModule):
    def __init__(self):
        super(WifiTestController, self).__init__()
        self.log = logging.getLogger('WifiTestController')

    @wishful_module.on_start()
    def my_start_function(self):
        self.log.info("start wifi test")

        try:
            node = self.localNode
            self.log.info(node)
            device = node.get_device(0)
            self.log.info(device)

            wifaces = device.radio.get_interfaces()
            for wif in wifaces:
                self.log.info('WIFI::wif %s' % str(wif))
                winfo = device.radio.get_wifi_card_info(wif)
                self.log.info('WIFI::winfo: %s' % str(winfo))

                if winfo['driver'] == 'ath9k':
                    self.log.info('Running ATH9k driver')


        except Exception as e:
            self.log.error("{} Failed, err_msg: {}".format(datetime.datetime.now(), e))

        self.log.info('... done')

    @wishful_module.on_exit()
    def my_stop_function(self):
        self.log.info("stop wifi test")

