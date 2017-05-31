"""
Local control program to be executed on remote nodes.
"""
__author__ = "Domenico Garlisi, Pierluigi Gallo"
__copyright__ = "Copyright (c) 2016, CNIT"
__version__ = "0.1.0"
__email__ = "domenico.garlisi@cnit.it; pierluigi.gallo@unipa.it"


# Definition of Local Control Program
def read_busy_time(controller):
    import sys
    sys.path.append('../../')
    sys.path.append("../../agent_modules/wifi_ath")
    sys.path.append("../../agent_modules/wifi_wmp")
    sys.path.append("../../agent_modules/wifi")
    sys.path.append("../../agent_modules/net_linux")
    sys.path.append('../../upis')
    sys.path.append('../../framework')
    sys.path.append('../../framework/wishful_framework/upi_arg_classes/')
    sys.path.append('../../agent')
    import math
    import scapy
    import binascii
    import getopt, sys
    import time
    import json
    import netifaces
    import re
    import signal

    import string, random
    import glob
    import subprocess
    import _thread
    import threading
    import logging
    import wishful_framework.upi_arg_classes.edca as edca
    import upis.wishful_upis.meta_radio as radio

    #enable debug print
    debug = False
    debug_statistics = True

    starttime=time.time()

    neigh_list = {}
    pkt_stats= {}
    report_stats= {}


    mon_iface="mon0"

    MAX_THR=5140 #kbps
    #rate=0; #APP RATE

    """
    interference recognition initialization
    """
    def init(iface):
        global my_mac
        my_mac=str(netifaces.ifaddresses(iface)[netifaces.AF_LINK][0]['addr'])
        #setCW(iface,1,2,15,1023,0)
        #setCW(iface,3,1,3,7,0)

        report_stats['thr'] = 0
        report_stats['tx_attempts'] = 0
        report_stats['busy_time'] = 0
        report_stats['reading_time'] = 0

        report_stats['tx_activity'] = 0
        report_stats['num_tx'] = 0
        report_stats['num_tx_success'] = 0

    """
    get PHY name for current device
    """
    def getPHY(iface="wlan0"):
        phy="phy" + iface[4]
        return phy

    """
    Set CW
    """
    # def setCW(iface, qumId, aifs, cwmin, cwmax, burst):
    # 	# # UPI
    # 	# controller.radio.set_mac_access_parameters(iface=iface,queueId=qumId,queueParams=edcaParams)
    #
    # 	# echo "0 1 1 3 0" > /sys/kernel/debug/ieee80211/phy0/ath9k/txq_params
    # 	# Proper sequence is : "qumId aifs cwmin cwmax burst"
    # 	phy=getPHY(iface)
    # 	edcaParams = edca.EdcaQueueParameters(aifs=aifs, cwmin=cwmin, cwmax=cwmax, txop=burst)
    # 	if debug or debug_cw_set:
    # 		print("set cw iface %s, qumId %s, aifs %s, cwmin %s, cwmax %s, burst %s" % (str(phy), str(qumId), str(aifs), str(cwmin), str(cwmax), str(burst)) )
    # 	f_name='/sys/kernel/debug/ieee80211/{}/ath9k/txq_params'.format(phy)
    # 	txq_params_msg='{} {} {} {} {}'.format(qumId,aifs,cwmin,cwmax,burst)
    # 	f_cw = open(f_name, 'w')
    # 	f_cw.write(txq_params_msg)


    def reading_function(iface, time_interval):
        reading_thread = threading.currentThread()
        print('start reading_function')

        # CWMIN = 2
        # CWMAX = 1023
        # cw_ = 32

        busy_time = 0
        busy_time_ = 0
        tx_activity = 0
        tx_activity_ = 0
        num_tx = 0
        num_tx_ = 0
        num_tx_success = 0
        num_tx_success_ = 0
        rx_activity = 0
        rx_activity_ = 0
        ext_busy_time = 0
        ext_busy_time_ = 0

        # QUEUE CW SETTING
        qumId = 1  # BE
        #qumId = 2  # VI
        aifs = 2
        burst = 0

        phy = getPHY(iface)
        reading_interval = time_interval[0] * 5
        #dd = time_interval[0]
        reading_time_ = 0

        reading_time = time.time()
        while (round(reading_time*10)%100) != 0:
            time.sleep(0.1)
            reading_time = time.time()
        local_starttime = reading_time

        while getattr(reading_thread, "do_run", True):
            #[pkt_stats, reading_time] = get_ieee80211_stats(phy)
            UPIargs = { 'parameters' : [radio.BUSY_TIME.key, radio.EXT_BUSY_TIME.key, radio.TX_ACTIVITY.key, radio.NUM_TX.key, radio.NUM_TX_SUCCESS.key, radio.RX_ACTIVITY.key] }
            pkt_stats = controller.radio.get_parameters(UPIargs)
            reading_time = time.time()
            if pkt_stats:
                if True:
                    print ("pkt_stats = %s" % (str(pkt_stats)))
                    dd = float(reading_time - reading_time_)

                    busy_time = pkt_stats[radio.BUSY_TIME.key] - busy_time_
                    ext_busy_time = pkt_stats[radio.EXT_BUSY_TIME.key] - ext_busy_time_
                    tx_activity = pkt_stats[radio.TX_ACTIVITY.key] - tx_activity_
                    rx_activity = pkt_stats[radio.RX_ACTIVITY.key] - rx_activity_

                    num_tx = pkt_stats[radio.NUM_TX.key] - num_tx_
                    # print ("num tx = %s" %(num_tx))
                    num_tx_success = pkt_stats[radio.NUM_TX_SUCCESS.key] - num_tx_success_

                    busy_time_ = pkt_stats[radio.BUSY_TIME.key]
                    ext_busy_time_ = pkt_stats[radio.EXT_BUSY_TIME.key]
                    tx_activity_ = pkt_stats[radio.TX_ACTIVITY.key]
                    rx_activity_ = pkt_stats[radio.RX_ACTIVITY.key]
                    num_tx_ = pkt_stats[radio.NUM_TX.key]
                    num_tx_success_ = pkt_stats[radio.NUM_TX_SUCCESS.key]


                if debug or debug_statistics:
                    # if debug_cycle > 3:
                    if True:
                        print(
                            "%.6f - busytime=%.4f ext_busy_time=%.4f tx_activity=%.4f rx_activity=%.4f num_tx=%.4f num_tx_success=%.4f\n" % (
                            reading_time, busy_time, ext_busy_time, tx_activity, rx_activity, num_tx, num_tx_success))
                        debug_cycle = 0
                    else:
                        debug_cycle += 1

                # store statistics for report
                report_stats['reading_time'] = reading_time

                report_stats['busy_time'] = busy_time
                report_stats['tx_activity'] = tx_activity
                report_stats['num_tx'] = num_tx
                report_stats['num_tx_success'] = num_tx_success

            time.sleep(reading_interval - ((time.time() - local_starttime) % reading_interval))


    log = logging.getLogger()
    log.info('*********** WISHFUL *************')
    log.info('*********** starting local WiSHFUL controller **********************')
    msg={}
    print("Local ctrl program started: {}".format(controller.name))
    distributed = False
    cycle_1 = 0
    while not controller.is_stopped():
        msg = controller.recv(timeout=1)
        if msg:
            print("START main function")
            #INIT
            init(msg["iface"])
            try:

                i_time = []
                i_time.append(msg['i_time'])

                #read function starting
                reading_thread = threading.Thread(target=reading_function, args=(msg['iface'], i_time))
                reading_thread.do_run = True
                print ("starting reading thread")
                reading_thread.start()

            except (Exception) as err:
                if debug:
                    print ( "exception", err)
                    print ("Error: unable to start thread")
                pass
            break

    #CONTROLLER MAIN LOOP
    while not controller.is_stopped():
        msg = controller.recv(timeout=5)
        if msg:
            #log.info("Receive message %s" % str(msg))
            i_time[0] = msg['i_time']
            #setCW(msg['iface'],1,2,15,1023,0)

        #send statistics to controller
        if 'reading_time' in report_stats:
            # controller.send_upstream({ "reading_time" : report_stats['reading_time'],
            # 						   "measurements":
            # 							   {"busy_time": report_stats['busy_time'],
            # 		"tx_activity": report_stats['tx_activity'],
            # 								"num_tx" : report_stats['num_tx'],
            # 								"num_tx_success" : report_stats['num_tx_success']
            # 								} ,
            # 								"mac_address" : (my_mac) })
            controller.send_upstream({"measure": [
                [report_stats['reading_time'], report_stats['busy_time'], report_stats['tx_activity'], report_stats['num_tx'], report_stats['num_tx_success']]], "mac_address": (my_mac)})



    reading_thread.do_run = False
    reading_thread.join()
    time.sleep(2)
