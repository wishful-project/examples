"""
Local control program to be executed on remote nodes.
"""

__author__ = "Domenico Garlisi"
__copyright__ = "Copyright (c) 2016, CNIT"
__version__ = "0.2.0"


# Definition of Local Control Program
def my_local_control_program(controller):
    # do all needed imports here!!!
    import time
    import datetime
    import sys
    sys.path.append('../../../')
    sys.path.append("../../../agent_modules/wifi_ath")
    sys.path.append("../../../agent_modules/wifi_wmp")
    sys.path.append("../../../agent_modules/wifi")
    sys.path.append('../../../upis')
    sys.path.append('../../../framework')
    sys.path.append('../../../agent')
    from agent_modules.wifi_wmp.wmp_structure import UPI_R


    @controller.set_default_callback()
    def default_callback(cmd, data):
        print(("DEFAULT CALLBACK : Cmd: {}, Returns: {}".format(cmd, data)))

    # control loop
    print("Local ctrl program started: {}".format(controller.name))
    while not controller.is_stopped():
        msg = controller.recv(timeout=1)
        if msg:
            ch = msg["new_channel"]
            print("Schedule get monitor to {} in 5s:".format(ch))
            UPI_myargs = {'interface' : 'wlan0', 'measurements' : [UPI_R.REGISTER_1, UPI_R.REGISTER_2, UPI_R.NUM_TX_DATA_FRAME, UPI_R.NUM_RX_ACK, UPI_R.NUM_RX_ACK_RAMATCH, UPI_R.BUSY_TYME , UPI_R.TSF, UPI_R.NUM_RX_MATCH] }
            result = controller.delay(5).radio.get_measurement(UPI_myargs)
            controller.send_upstream({"myResult": result})

    print("Local ctrl program stopped: {}".format(controller.name))


# Definition of Local Control Program for wishful showcase3
def local_control_program(controller):
    # do all needed imports here!!!
    import time
    import datetime
    import sys
    sys.path.append('../../../')
    sys.path.append("../../../agent_modules/wifi_ath")
    sys.path.append("../../../agent_modules/wifi_wmp")
    sys.path.append("../../../agent_modules/wifi")
    sys.path.append('../../../upis')
    sys.path.append('../../../framework')
    sys.path.append('../../../agent')
    from agent_modules.wifi_wmp.wmp_structure import UPI_R


    @controller.set_default_callback()
    def default_callback(cmd, data):
        print(("DEFAULT CALLBACK : Cmd: {}, Returns: {}".format(cmd, data)))

    """
    Custom function used to implement local WiSHFUL controller
    """
    def customLocalCtrlFunction(controller, interface, tuning_enabler):

        import time
        import logging
        import math

        # references to Wishful framework
        #global upiHCImpl # interface used for communication with global controller and control runtime

        log = logging.getLogger()
        log.warning('*********** WISHFUL SC3 *************')
        log.warning('*********** starting local WiSHFUL controller **********************')

        # set start node CW
        # cw = 30
        # UPI_myargs = {'interface' : interface, UPI_RN.CSMA_CW : cw, UPI_RN.CSMA_CW_MIN : cw, UPI_RN.CSMA_CW_MAX : cw }
        # controller.radio.set_parameter(UPI_myargs)

        last_freezing_number = 0
        b = 0.3
        a = 0.1
        last_count_freezing = 0
        CWMIN = 15
        CWMAX = 1023
        T = 1
        ipt = 0
        cw_f = 64 #CWMIN
        cw = cw_f;
        cycle_update = 0
        data_tx=0
        data_tx_=0
        ack_rx = 0
        ack_rx_ = 0
        ack_rx_ramatch = 0
        ack_rx_ramatch_ = 0
        busytime = 0
        busytime_ = 0
        tsf_reg = 0
        tsf_reg_ = 0
        num_rx = 0
        num_rx_ = 0
        num_rx_success = 0
        num_rx_success_ = 0
        num_rx_match = 0
        num_rx_match_ = 0

        ip_address = controller.radio.get_iface_ip_addr(interface)
        #UPI_myargs = {'interface' : interface, UPI_R.CSMA_CW : CWMIN, UPI_R.CSMA_CW_MIN : CWMIN, UPI_R.CSMA_CW_MAX : CWMAX }
        #controller.radio.set_parameter(UPI_myargs)

        #upiHCImpl.startFunc()
        #while not upiHCImpl.stopIsSet():
        while not controller.is_stopped():
            msg = controller.recv(timeout=1)

            #find linux system time
            tsf=time.time()*1e6;

            #get node statistics
            UPI_myargs = {'interface' : interface, 'measurements' : [UPI_R.REGISTER_1, UPI_R.REGISTER_2, UPI_R.NUM_TX_DATA_FRAME, UPI_R.NUM_RX_ACK, UPI_R.NUM_RX_ACK_RAMATCH, UPI_R.BUSY_TYME , UPI_R.TSF, UPI_R.NUM_RX_MATCH] }
            node_measures = controller.radio.get_measurement(UPI_myargs)

            #IPT
            pos = 0
            ipt=node_measures[pos]
            K = 10
            GOOGLE = 2**K
            ipt = float(ipt) / GOOGLE

            #FREEZING
            pos += 1
            count_freezing=node_measures[pos]
            delta_freezing = count_freezing - last_count_freezing
            if delta_freezing < 0 :
                delta_freezing = 2 ** (16) -1 - last_count_freezing + count_freezing
            last_count_freezing = count_freezing
            delta_freezing=float(delta_freezing)

            #DATA_TX
            pos+=1
            data_tx = node_measures[pos]
            delta_data_tx=data_tx-data_tx_
            if delta_data_tx < 0 :
                 delta_data_tx= 2 ** (16) -1  - data_tx_ + data_tx
            data_tx_ = data_tx

            #ACK TOTAL
            pos += 1
            ack_rx = node_measures[pos]
            delta_ack_rx = ack_rx - ack_rx_
            if delta_ack_rx < 0 :
                 delta_ack_rx = 2 ** (16) -1  - ack_rx_ + ack_rx
            ack_rx_ = ack_rx
            delta_ack_rx=float(delta_ack_rx)

            #ACK WITH RAMATCH (TX_OK_MY_PACKET)
            pos += 1
            ack_rx_ramatch = node_measures[pos]
            delta_ack_rx_ramatch = ack_rx_ramatch - ack_rx_ramatch_
            if delta_ack_rx_ramatch < 0 :
                 delta_ack_rx_ramatch = 2 ** (16) -1  - ack_rx_ramatch_ + ack_rx_ramatch
            ack_rx_ramatch_ = ack_rx_ramatch
            delta_ack_rx_ramatch=float(delta_ack_rx_ramatch)

            #BUSYTIME
            pos += 1
            busytime = node_measures[pos]
            delta_busytime = busytime - busytime_
            if delta_busytime < 0 :
                 delta_busytime = 2 ** (16) -1  - busytime_ + busytime
            busytime_ = busytime
            delta_busytime=float(delta_busytime)

            #TSF
            pos += 1
            tsf_reg = node_measures[pos]
            delta_tsf_reg = tsf_reg - tsf_reg_
            if delta_tsf_reg < 0 :
                 delta_tsf_reg = 2 ** (64) - 1  - tsf_reg_ + tsf_reg
            tsf_reg_ = tsf_reg
            delta_tsf_reg=float(delta_tsf_reg)

            #NUM_RX_MATCH
            pos += 1
            num_rx_match = node_measures[pos]
            delta_num_rx_match = num_rx_match - num_rx_match_
            if delta_num_rx_match < 0 :
                 delta_num_rx_match = 2 ** (16) - 1  - num_rx_match_ + num_rx_match
            num_rx_match_ = num_rx_match
            delta_num_rx_match=float(delta_num_rx_match)

            """""""""""""""""""""""""""""""""""""""""""""
            execute MEDCA algorithm and find new CW value
            # ipt = ipt + a * (delta_freezing - ipt);
            # targetcw = -0.0131 * ipt ** 2 + 3.2180 * ipt + 13.9265;  # determine the target CW for this IPT
            """""""""""""""""""""""""""""""""""""""""""""

            #PHY
            bw=20;
            Tpre=16*20/bw;
            Tsig=4*20/bw;
            Tsym=4*20/bw;
            rate=6; #Mbps
            basic_rate=6; #Mbps

            #MAC
            tslot=9;
            SIFS=16;
            AIFS=3;
            DIFS=AIFS*tslot+SIFS;

            #PKT SIZE
            l_ack=14; #byte
            #data_size=200;
            data_size=1000;

            t_data= Tpre + Tsig + math.ceil(Tsym/2+(22+8*(data_size))/rate);
            t_ack=Tpre + Tsig+math.ceil(l_ack*8/basic_rate);
            EIFS= t_ack + SIFS + DIFS;

            #select algorithm to tune node CW
            alg="CW_OPT"

            if alg == "MEDCA" :
                targetcw = -0.0106 * ipt ** 2 + 2.9933 * ipt + 18.5519;  # determine the target CW for this IPT
                cw_f = cw_f + b * (targetcw - cw_f);
                cw = round(cw_f);
                cw = int(cw)
                cw = max(cw,CWMIN);
                cw = min(cw,CWMAX);

            # if alg == "FIXED":
            #     info_ctrl=upiHCImpl.getMsgFromController()
            #     if info_ctrl :
            #         n_tx_sta = info_ctrl['traffic_number']
            #         log.warning("num_tx_nodes=%d" % info_ctrl['traffic_number'] )
            #
            #     cw = 46

            if alg == "CW_OPT":

                msg = controller.recv(timeout=1)
                if msg:
                    n_tx_sta = msg["traffic_number"]
                    log.warning("num_tx_nodes=%d" % n_tx_sta )
                else:
                    n_tx_sta = 0

                Tc = t_data + EIFS; #Collision time
                cw_f = n_tx_sta * math.sqrt(2*Tc / tslot);
                cw = round(cw_f);
                cw = int(cw)
                cw = max(cw,CWMIN);
                cw = min(cw,CWMAX);

            #update CW
            if tuning_enabler == 1 and alg != "DCF" :
                log.warning(' >>>>>>>> CW setting : ENABLED');
                UPI_myargs = {'interface' : interface, UPI_R.CSMA_CW : cw, UPI_R.CSMA_CW_MIN : cw }
                controller.radio.set_parameter(UPI_myargs)
            else:
                log.warning(' >>>>>>>> CW setting : DISABLED');

            #send value to MASTER
            cycle_update += 1
            if not(cycle_update % 1):
                #communicate with global controller by passing control message
                #upiHCImpl.transmitCtrlMsgUpstream( { "measure" : [[delta_freezing, tsf_reg, delta_ack_rx_ramatch, cw, ipt, delta_data_tx, delta_ack_rx,  delta_busytime, delta_tsf_reg, delta_num_rx_match]], "ip_address" : (ip_address) } )
                #controller.send_upstream({"myResult": result})
                controller.send_upstream({ "measure" : [[delta_freezing, tsf_reg, delta_ack_rx_ramatch, cw, ipt, delta_data_tx, delta_ack_rx,  delta_busytime, delta_tsf_reg, delta_num_rx_match]], "ip_address" : (ip_address) })
            time.sleep(T)

        log.warning('Local WiSHFUL Controller END');
        return 'Local WiSHFUL Controller END'


    '''
    Remote execution main part
    '''
    while not controller.is_stopped():
        msg = controller.recv(timeout=1)
        if msg:
            interface = msg["interface"]
            tuning_enabler = msg["tuning_enabler"]
            #controller.send_upstream({"myResult": result})
        customLocalCtrlFunction(controller, interface, tuning_enabler)

    # """
    # Custom callback function used to receive result values from scheduled calls, i.e. if you schedule the execution of a
    # particular UPI_R/N function in the future this callback allows you to be informed about any function return values.
    # """
    # numCBs = {}
    # numCBs['res'] = 0
    # # use in while to lern if the local logic stopped e.g.
    # # while numCBs['res'] < 2:
    #
    # def resultCollector(json_message, funcId):
    #     log.warning('json: %s' % json_message)
    #     time_val = json_message['time']
    #     peer_node = json_message['peer']
    #     messagedata = json_message['msg']
    #     log.warning('Callback %d: Local controller receives data msg at %s from %s : %s' % (funcId, str(time_val), peer_node, messagedata))
    #     numCBs['res'] = numCBs['res'] + 1
    #
    #
    #
    # # stations_dump = [["192.168.3.103", "alix3", 0, 0, 0, 0, 0 ,0],
    # #                 ["192.168.3.104", "alix4", 0, 0, 0, 0, 0, 0],
    # #                 ["192.168.3.105", "alix5", 0, 0, 0, 0, 0, 0],
    # #                 ["192.168.3.106", "alix6", 0, 0, 0, 0, 0, 0],
    # #                 ["192.168.3.107", "alix7", 0, 0, 0, 0, 0, 0],
    # #                 ["192.168.3.110", "alix10", 0, 0, 0, 0, 0, 0],
    # #                 ["192.168.3.111", "alix11", 0, 0, 0, 0, 0, 0],
    # #                 ["192.168.3.112", "alix12", 0, 0, 0, 0, 0, 0],
    # #                 ["192.168.3.113", "alix13", 0, 0, 0, 0, 0, 0],
    # #                 ["192.168.3.114", "alix14", 0, 0, 0, 0, 0, 0]]
    #
    # # stations_dump = [["192.168.3.12", "alix12", 0, 0, 0, 0, 0 ,0, 0],
    # #             ["192.168.3.6", "alix6", 0, 0, 0, 0, 0, 0, 0],
    # #             ["192.168.3.7", "alix7", 0, 0, 0, 0, 0, 0, 0],
    # #             ["192.168.3.8", "alix8", 0, 0, 0, 0, 0, 0, 0],
    # #             ["192.168.3.10", "alix10", 0, 0, 0, 0, 0, 0, 0],
    # #             ["192.168.3.11", "alix11", 0, 0, 0, 0, 0, 0, 0],
    # #             ["192.168.3.13", "alix13", 0, 0, 0, 0, 0, 0, 0],
    # #             ["192.168.3.14", "alix14", 0, 0, 0, 0, 0, 0, 0]]
    #
    # """
    # Custom callback function used to receive control feedback results from local controllers.
    # """
    # def ctrlMsgCollector(json_message):
    #     global socket_visualizer
    #     global omlInst
    #
    #     time_val = json_message['time']
    #     peer_node = json_message['peer']
    #     msg_data = json_message['msg']
    #     remote_wlan_ipAddress = msg_data['ip_address']
    #     measurement_types = 'MEASURE'
    #     measurement = msg_data['measure']
    #
    #     #log.info('Global controller receives ctrl msg at %s from %s : %s' % (str(time_val), peer_node, str(msg_data) ))
    #     # add measurement on nodes element
    #     for node in mytestbed.wifinodes:
    #         if node.wlan_ipAddress == remote_wlan_ipAddress and measurement != False:
    #             node.last_bunch_measurement.append(measurement)
    #             #log.debug('Append measurements at node %s : %s' % (str(remote_wlan_ipAddress), str(measurement) ))
    #
    #
    #
    #     # measurement_types=['FREEZING_NUMBER', 'TSF', 'RX_ACK_RAMATCH', 'CW', 'IPT', 'TX_DATA', 'RX_ACK', 'BUSY_TIME', 'delta_TSF', 'NUM_RX_MATCH']
    #     # measure': [[0.0, 287963817, 0.0, 15, 1.79296875, 0, 0.0, 1786.0, 1017947.0, 0.0]]}
    #     #omlInst.addmp("IEEE802154_MACSTATS",
    #
    #     # "timestamp:int32
    #     # nodeID:int32
    #     # packetSize:int32
    #     # activeRadioprogram:string
    #
    #     # timeDiff:int32
    #
    #     # numTxRequest:int32
    #     # numTxRequestFail:int32
    #     # numTxAttempt:int32
    #     # numTxSuccess:int32
    #     # numTxFail:int32
    #     # numTxBusy:int32
    #     # numTxNoAck:int32
    #     # numTxCollision:int32
    #
    #     # numRx:int32
    #     # avgBackoffExponent:int32")
    #
    #     # omlLst = [int(time.time()),1,100,"TDMA"]
    #     # temp = [measurement_key_values["IEEE802154_MACSTATS"][0]]
    #     # for i in range(1,len(sensor_measurements_dct[1])):
    #     #   temp.append((measurement_key_values["IEEE802154_MACSTATS"])[i] - (sensor_measurements_dct[1])[i])
    #     # sensor_measurements_dct[1] = measurement_key_values["IEEE802154_MACSTATS"]
    #     # omlLst = omlLst + list(temp)
    #     # #~ log.info("%s",omlLst)
    #     # omlInst.inject("IEEE802154_MACSTATS", omlLst)
    #
    #     node_id = int(remote_wlan_ipAddress.split('.')[3])
    #     omlLst = [ int(time.time()), node_id, 1000, "RADIO_PROGRAM", 100000, measurement[0][5], measurement[0][5], measurement[0][5], measurement[0][5], 0, 0, 0, 0, measurement[0][9], measurement[0][3] ]
    #     # temp = [measurement_key_values["IEEE802154_MACSTATS"][0]]
    #     # for i in range(1,len(sensor_measurements_dct[1])):
    #     #   temp.append((measurement_key_values["IEEE802154_MACSTATS"])[i] - (sensor_measurements_dct[1])[i])
    #     # sensor_measurements_dct[1] = measurement_key_values["IEEE802154_MACSTATS"]
    #     # omlLst = omlLst + list(temp)
    #     # #~ log.info("%s",omlLst)
    #     omlInst.inject("IEEE802154_MACSTATS", omlLst)
    #
    #     # # add measurement on nodes element
    #     # #measurement_types=['FREEZING_NUMBER', 'TSF', 'RX_ACK_RAMATCH', 'CW', 'IPT', 'TX_DATA', 'RX_ACK', 'BUSY_TIME', 'delta_TSF', 'NUM_RX_MATCH']
    #     # for i in range(0,len(stations_dump)):
    #     #     if stations_dump[i][0] == remote_wlan_ipAddress and measurement != False:
    #     #         stations_dump[i][2] = measurement[0][0]
    #     #         stations_dump[i][3] = round(measurement[0][3], 1)
    #     #         stations_dump[i][4] = round(measurement[0][5], 1)
    #     #         stations_dump[i][5] = round(measurement[0][3], 1)
    #     #         stations_dump[i][6] = round(measurement[0][2], 1)
    #     #         stations_dump[i][7] = round((measurement[0][2] * 200 * 8 * 10 ), 1) #(I use frame of 200byte collected every 100ms)
    #
    #     # # add measurement on nodes element
    #     # #measurement_types=['FREEZING_NUMBER', 'TSF', 'RX_ACK_RAMATCH', 'CW', 'IPT', 'TX_DATA', 'RX_ACK', 'BUSY_TIME', 'delta_TSF', 'NUM_RX_MATCH']
    #     # for i in range(0,len(stations_dump)):
    #     #     if stations_dump[i][0] == remote_wlan_ipAddress and measurement != False:
    #     #         stations_dump[i][2] = measurement[0][0]				#'FREEZING_NUMBER'
    #     #         stations_dump[i][3] = round(measurement[0][3], 1)	#'CW'
    #     #         stations_dump[i][4] = round(measurement[0][5], 1)	#'TX_DATA'
    #     #         stations_dump[i][5] = round(measurement[0][2], 1)	#'TSF'
    #     #         stations_dump[i][6] = round((measurement[0][2] * 200 * 8 * 10 ), 1) #(I use frame of 200byte collected every 100ms)
    #     #         stations_dump[i][7] = round((measurement[0][9]), 1) #(I use frame of 200byte collected every 100ms)
    #
    #     # if remote_wlan_ipAddress == stations_dump[i][0] :
    #     #     # topic = random.randrange(9999,10005)
    #     #     # messagedata = random.randrange(1,215) - 80
    #     #     topic = 1001
    #     #     messagedata = 15
    #     #     print "%d %d" % (topic, messagedata)
    #     #     socket_visualizer.send("%d %d" % (topic, messagedata))
    #     json_message['traffic'] = get_traffic()
    #     socket_visualizer.send_json(json_message)

    #    # text_file.seek(0)
    #    # text_file.write('*********************************************************************************************************\n')
    #    # text_file.write('***************************      WiSHFUL SHOWCASE 3      ************************************************\n')
    #    # text_file.write('*********************************************************************************************************\n')
    #    # text_file.write('STATION\t\t\tFREEZING NUM\t\tCW\t\t\tTX DATA\t\t\tRX ACK\t\t\tTHR\n')
    #    #
    #    # for i in range(0,6):
    #    #     for j in range(1,7):
    #    #         text_file.write('%s\t\t\t' % (str(stations_dump[i][j])))
    #    #     text_file.write('\n')




    # """
    # Stop function used to send stop function to local controllers.
    # """
    # def stop_local_controller(mytestbed):
    #     CtrlFuncImpl = UPI_RN.stopFunc
    #     CtrlFuncargs =  {'interface' : 'wlan0'}
    #     now = get_now_full_second()
    #     # exec immediately
    #     exec_time = now + timedelta(seconds=3)
    #     log.warning(' >>>> Stop local WiSHFUL controller on all nodes - stop at : %s', str(exec_time))
    #     #nodes = upi_hc.getNodes()
    #     nodes = mytestbed.nodes
    #     try:
    #         callback = partial(resultCollector, funcId=99)
    #         mytestbed.global_mgr.runAt(nodes, UPI_RN.stopFunc, CtrlFuncargs, unix_time_as_tuple(exec_time), callback)
    #     except Exception as e:
    #         log.fatal("An error occurred when stop the local WiSHFUL controller: %s" % e)


    # ''' START MAIN CONTROL PROGRAM '''
    # if disable:
    #     stop_local_controller(mytestbed)
    #     return
    #
    # # register callback function for collecting results
    # mytestbed.global_mgr.setCtrlCollector(ctrlMsgCollector)
    # # deploy a custom control program on each node
    # CtrlFuncImpl = customLocalCtrlFunction
    # # get current time
    # now = get_now_full_second()
    # # exec immediately
    # exec_time = now + timedelta(seconds=3)
    # log.warning('Sending local WiSHFUL controller on all nodes - start at : %s', str(exec_time))
    #
    # #nodes = upi_hc.getNodes()
    # for node in mytestbed.wifinodes:
    #     node.measurement_types.append('FREEZING_NUMBER')
    #     node.measurement_types.append('CW')
    # nodes = mytestbed.nodes
    #
    #
    # ''' IMPLEMENT PYTHON VISUALIZER '''
    # ''' implement message zmq for realtime visualizer '''
    # #global socket_visualizer
    # #port = "12345"
    # #context = zmq.Context()
    # #socket_visualizer = context.socket(zmq.PUB)
    # #socket_visualizer.bind("tcp://*:%s" % port)
    #
    # ''' implement OML database setup for realtime visualizer '''
    # #global omlInst
    # #omlInst = oml4py.OMLBase("LocalControlProgram", "WiSHFUL", socket.gethostname(),"tcp:am.wilab2.ilabt.iminds.be:3004")
    # #omlInst.addmp("IEEE802154_MACSTATS", "timestamp:int32 nodeID:int32 packetSize:int32 activeRadioprogram:string timeDiff:int32 numTxRequest:int32 numTxRequestFail:int32 numTxAttempt:int32 numTxSuccess:int32 numTxFail:int32 numTxBusy:int32 numTxNoAck:int32 numTxCollision:int32 numRx:int32 avgBackoffExponent:int32")
    # #omlInst.start()
    #
    # try:
    #     # this is a non-blocking call
    #     callback = partial(resultCollector, funcId=99)
    #     #isOntheflyReconfig = True
    # 	CtrlFuncargs =  {'interface' : 'wlan0','medca_enabler' : 2}
    #     mytestbed.global_mgr.runAt(nodes[0], CtrlFuncImpl, CtrlFuncargs, unix_time_as_tuple(exec_time), callback )
    #     # CtrlFuncargs =  {'interface' : 'wlan0','medca_enabler' : 1}
    #     # mytestbed.global_mgr.runAt(nodes[1:2], CtrlFuncImpl, CtrlFuncargs, unix_time_as_tuple(exec_time), callback )
    #     CtrlFuncargs =  {'interface' : 'wlan0','medca_enabler' : 1}
    #     mytestbed.global_mgr.runAt(nodes[1:len(nodes)], CtrlFuncImpl, CtrlFuncargs, unix_time_as_tuple(exec_time), callback )
    # except Exception as e:
    #     log.fatal("An error occurred in local controller WiSHFUL sending and running : %s" % e)
    #
    # log.warning("Local logic STARTED")
    # return
