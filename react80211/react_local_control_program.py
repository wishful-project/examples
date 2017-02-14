"""
Local control program to be executed on remote nodes.
"""
__author__ = "Fabrizio Giuliano"
__copyright__ = "Copyright (c) 2016, CNIT"
__version__ = "0.1.0"

# Definition of Local Control Program
def react(controller):
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

	#enable debug print
	debug = False
	debug_statistics = True
	debug_cw_set = False
	debug_react_value = True

	starttime=time.time()

	neigh_list = {}
	pkt_stats= {}
	report_stats= {}

	MAX_OFFER_C=1
	CLAIM_CAPACITY=0.8
	mon_iface="mon0"

	MAX_THR=5140 #kbps
	#rate=0; #APP RATE

	"""
	REACT INIT
	"""
	def init(iface):
		global my_mac
		my_mac=str(netifaces.ifaddresses(iface)[netifaces.AF_LINK][0]['addr'])
		#init offer/claim structure
		init_pkt={}
		init_pkt['t']=0
		init_pkt['offer'] = MAX_OFFER_C
		init_pkt['claim'] = 0
		init_pkt['w'] = 0
		#init neighbors
		neigh_list[my_mac]=init_pkt

		setCW(iface,1,2,15,1023,0)
		setCW(iface,3,1,3,7,0)

		report_stats['thr'] = 0
		report_stats['cw'] = 0
		report_stats['psucc'] = 0
		report_stats['busytx2'] = 0
		report_stats['busy_time'] = 0

	"""
	get PHY name for current device
	"""
	def getPHY(iface="wlan0"):
		phy="phy" + iface[4]
		#phy = subprocess.Popen(["ls", "/sys/kernel/debug/ieee80211/"], stdout=subprocess.PIPE).communicate()[0]
		#phy_list={}

		# devs_info = subprocess.Popen(["iw","dev"], stdout=subprocess.PIPE).communicate()[0]
		# pp=str.split(str(devs_info),'\n')
		# iii=[x for x in pp if '\t\t' not in x]
		# key=''
		# for d in iii:
		# 	if '#' in d:
		# 		key=d;
		# 	if iface in d:
		# 		break
		#phy=key.replace("#","")

		return phy

	"""
	get iee80211 debugfs packet informations
	current format of iee80211_stats:
	{'failed_count': 0, 'dot11FCSErrorCount': 3, 'dot11RTSSuccessCount': 0, 'dot11TransmittedFrameCount': 1, 'dot11ACKFailureCount': 0, 'retry_count': 0, 'multiple_retry_count': 0, 'received_fragment_count': 30, 'frame_duplicate_count': 0, 'transmitted_fragment_count': 1, 'multicast_dot11TransmittedFrameCount': 1, 'multicast_received_frame_count': 20, 'dot11RTSFailureCount': 0}
	"""
	def get_ieee80211_stats(phy):
		out = subprocess.Popen(["bash","./ieee_stats.sh", phy], stdout=subprocess.PIPE).communicate()[0]
		ieee80211_stats_diff=json.loads(out.decode("utf-8") )
		return ieee80211_stats_diff

	"""
	Compute txtime theoretical value for given:
	% Input vars:
	%   v80211  : '11b', '11g', '11a' or '11p'
	%   bitrate : 1,2,5.5,11,6,9,12,18,24,36,48,54
	%   bw      : 20,10,5
	%   pkt_size: value in byte
	% NOTE: pkt_size means  MAC_H + LLC_H  + PAYLOAD + MAC_FCS
	"""
	def txtime_theor(v80211, bitrate, bw, pkt_size):
		Tpre=16*20/bw;
		Tsig=4*20/bw
		Tsym=4*20/bw;
		l_ack=14;
		l_rts=20;
		tx_time_theor=0
		if v80211 == '11b':
			CWmin=15;
			tslot=20;
			SIFS=10;
			AIFS=3;
			DIFS=AIFS*tslot+SIFS;
			t_ack=192+l_ack*28/bitrate+1;
			t_rts=192+l_rts*28/bitrate+1;
			tx_time_theor=192+(pkt_size+28)*8/bitrate+1;
			rate=bitrate;

		elif v80211 == '11g':
			rate=bitrate*bw/20;
			CWmin=15;
			tslot=9;
			SIFS=16;
			AIFS=3;
			DIFS=AIFS*tslot+SIFS;
			t_ack=Tpre + Tsig+math.ceil(l_ack*8/rate);
			t_rts=Tpre + Tsig+math.ceil(l_rts*8/rate);
			tx_time_theor= Tpre + Tsig + math.ceil(Tsym/2+(22+8*(pkt_size))/rate);

		elif v80211 == '11a':
			rate=bitrate*bw/20;
			CWmin=15;
			tslot=9;
			SIFS=16;
			AIFS=3;
			DIFS=AIFS*tslot+SIFS;
			t_ack=Tpre + Tsig+math.ceil(l_ack*8/bitrate);
			t_rts=Tpre + Tsig+math.ceil(l_rts*8/bitrate);
			tx_time_theor= Tpre + Tsig + math.ceil(Tsym/2+(22+8*(pkt_size))/rate);

		elif v80211 == '11p':
			rate=bitrate*bw/20;
			CWmin=15;
			tslot=13;
			SIFS=32;
			AIFS=2;
			DIFS=AIFS*tslot+SIFS;
			t_ack=Tpre + Tsig+math.ceil(l_ack*8/bitrate);
			t_rts=Tpre + Tsig+math.ceil(l_rts*8/bitrate);
			tx_time_theor= Tpre + Tsig + math.ceil(Tsym/2+(22+8*(pkt_size))/rate);

		return [tslot, tx_time_theor, t_rts, t_ack]

	"""
	Set CW
	"""
	def setCW(iface, qumId, aifs, cwmin, cwmax, burst):
		# # UPI
		# controller.radio.set_mac_access_parameters(iface=iface,queueId=qumId,queueParams=edcaParams)

		# echo "0 1 1 3 0" > /sys/kernel/debug/ieee80211/phy0/ath9k/txq_params
		# Proper sequence is : "qumId aifs cwmin cwmax burst"
		phy=getPHY(iface)
		edcaParams = edca.EdcaQueueParameters(aifs=aifs, cwmin=cwmin, cwmax=cwmax, txop=burst)
		if debug or debug_cw_set:
			print("set cw iface %s, qumId %s, aifs %s, cwmin %s, cwmax %s, burst %s" % (str(phy), str(qumId), str(aifs), str(cwmin), str(cwmax), str(burst)) )
		f_name='/sys/kernel/debug/ieee80211/{}/ath9k/txq_params'.format(phy)
		txq_params_msg='{} {} {} {} {}'.format(qumId,aifs,cwmin,cwmax,burst)
		f_cw = open(f_name, 'w')
		f_cw.write(txq_params_msg)	

	"""
	update CW decision based on ieee80211 stats values and virtual channel freezing estimation
	"""
	def update_cw(iface, time_interval, enable_react):
		cw_thread = threading.currentThread()

		CWMIN=15
		CWMAX=2047
		cw_=1023

		cw=cw_
		data_count_= 0
		rts_count_= 0
		ack_failure_count_ = 0

		busy_time = 0
		busy_time_ = 0

		SIFS=16 #usec
		tslot=9e-6 #usec

		#QUEUE CW SETTING
		qumId=1 #BE
		aifs=2
		burst=0

		pkt_size=1534
		phy=getPHY(iface)
		debug_cycle = 0
		cw_evaluate_cycle = 0
		number_of_setting_in_interval = 5
		cw_setting_interval = time_interval[0]/number_of_setting_in_interval

		average_enable = True

		while getattr(cw_thread, "do_run", True):
			#get stats

			#TODO: change/add/reuse UPI candidate: get_measurement
			# UPI_myargs = {'interface' : 'wlan0', 'measurements' : [UPI_R.dot11RTSSuccessCount,UPI_R.dot11RTSFailureCount] }
			# pkt_stats=controller.radio.get_measurements(UPI_myargs)

			#{"busy_time" : 1245283, "dot11ACKFailureCount" : 10182, "dot11FailedCount" : 87, "dot11FCSErrorCount" : 17627, "dot11FrameDuplicateCount" : 1398,
			# "dot11MulticastReceivedFrameCount" : 313176, "dot11MulticastTransmittedFrameCount" : 35308, "dot11MultipleRetryCount" : 9619,
			# "dot11ReceivedFragmentCount" : 565822, "dot11RetryCount" : 17584, "dot11RTSFailureCount" : 331102, "dot11RTSSuccessCount" : 261543,
			# "dot11TransmittedFragmentCount" : 297722, "dot11TransmittedFrameCount" : 297722, "rx_expand_skb_head_defrag" : 0,
			# "rx_handlers_drop" : 98606, "rx_handlers_drop_defrag" : 0, "rx_handlers_drop_nullfunc" : 0, "rx_handlers_drop_short" : 0,
			# "rx_handlers_fragments" : 0, "rx_handlers_queued" : 461432, "tx_expand_skb_head" : 0, "tx_expand_skb_head_cloned" : 40986, "tx_handlers_drop" : 0,
			# "tx_handlers_drop_not_assoc" : 0, "tx_handlers_drop_unauth_port" : 0, "tx_handlers_drop_wep" : 0, "tx_handlers_queued" : 0, "tx_status_drop" : 0 }
			# dot11TransmittedFragmentCount	297722
			# dot11ACKFailureCount 			 10182
			# dot11RTSSuccessCount			261543
			# dot11RTSFailureCount			331102

			if cw_evaluate_cycle > (number_of_setting_in_interval-2):
				pkt_stats=get_ieee80211_stats(phy)
				if pkt_stats:
					# consider only RTS statistics
					# data_count = pkt_stats['dot11RTSSuccessCount'] - data_count_
					# rts_count = pkt_stats['dot11RTSSuccessCount'] + pkt_stats['dot11RTSFailureCount'] - rts_count_
					# data_count_=pkt_stats['dot11RTSSuccessCount']
					# rts_count_=pkt_stats['dot11RTSSuccessCount'] + pkt_stats['dot11RTSFailureCount']

					#consider scenario with e without RTS/CTS
					data_count = pkt_stats['dot11TransmittedFragmentCount'] - data_count_
					rts_count = pkt_stats['dot11RTSSuccessCount'] + pkt_stats['dot11RTSFailureCount'] - rts_count_
					ack_failure_count = pkt_stats['dot11ACKFailureCount'] - ack_failure_count_
					data_count_=pkt_stats['dot11TransmittedFragmentCount']
					rts_count_=pkt_stats['dot11RTSSuccessCount'] + pkt_stats['dot11RTSFailureCount']
					ack_failure_count_ = pkt_stats['dot11ACKFailureCount']

					busy_time = (pkt_stats['busy_time'] - busy_time_)/10
					busy_time_ = pkt_stats['busy_time']

					tx_goal=0
					I=0
					dd = time_interval[0]
					gross_rate = float(CLAIM_CAPACITY)*float(neigh_list[my_mac]['claim'])

					[tslot, tx_time_theor, t_rts, t_ack]= txtime_theor('11a', 6, 20, pkt_size)

					busytx2 =  0.002198*float(data_count) + 0.000081*float(rts_count) #how much time the station spent in tx state during the last observation internval
					#busytx2 =  0.002071*float(data_count) + 0.000046*float(rts_count) #how much time the station spent in tx state during the last observation internval

					if rts_count > 0:
						freeze2 = float(dd) - float(busytx2) - cw_/float(2)*float(tslot)*rts_count #how long the backoff has been frozen;
						avg_tx = float(busytx2)/float(rts_count) #average transmission time in a transmittion cycle
						psucc = float(data_count)/float(rts_count)
					else:
						freeze2 = float(dd) - float(busytx2)
						avg_tx=0
						psucc= float(data_count)/float(data_count + ack_failure_count)

					if avg_tx > 0:
						tx_goal = float(dd * gross_rate)/float(avg_tx)
					else:
						tx_goal = 0

					freeze_predict = float(freeze2) / float(dd-busytx2) * float(dd - dd * float(gross_rate))
					if tx_goal > 0:
						cw = 2/float(0.000009) * (dd - tx_goal * avg_tx -freeze_predict) / float(tx_goal)

					if average_enable:
						#moving average
						cw_= 0.6 * cw_ + 0.4 * cw
					else:
						#not everage
						cw_ = cw

					if cw_ < CWMIN:
						cw_=CWMIN
						cw_array = [cw_] * number_of_setting_in_interval
					elif cw_ > CWMAX:
						cw_=CWMAX
						cw_array = [cw_] * number_of_setting_in_interval
					else:
						#cw_= pow(2, round(math.log(cw_)/math.log(2))) - 1
						cw_floor= pow(2, math.floor(math.log(cw_)/math.log(2))) - 1
						cw_ceil= pow(2, math.ceil(math.log(cw_)/math.log(2))) - 1
						if cw_floor == cw_ceil:
							cw_array = [cw_ceil] * number_of_setting_in_interval
						elif cw_ == cw_floor or cw_ == cw_ceil:
							cw_array = [cw_] * number_of_setting_in_interval
						else:
							interval = cw_ceil - cw_floor
							position_in_interval = cw_ - cw_floor
							position_percent = position_in_interval / interval
							cw_array = [cw_floor] * (number_of_setting_in_interval - round(position_percent * number_of_setting_in_interval))
							cw_array = cw_array + [cw_ceil] * round(position_percent * number_of_setting_in_interval)


					thr=(data_count)*1470*8 / float(dd*1e6)
					if debug or debug_statistics:
						if debug_cycle > 3:
							#print("t=%.4f,dd=%.4f data_count=%.4f rts_count=%.4f busytx2=%.4f(%.4f) gross_rate=%.4f,avg_tx=%.4f freeze2=%.4f freeze_predict=%.4f tx_goal=%.4f I=%.4f cw=%.4f cw_=%.4f psucc=%.4f thr=%.4f" % (time.time(), dd, data_count, rts_count, busytx2, busytx2/float(dd), gross_rate, avg_tx, freeze2, freeze_predict, tx_goal, I, cw, cw_, psucc, thr))
							print("data_count=%.4f rts_count=%.4f cw=%.4f cw_=%.4f psucc=%.4f thr=%.4f -- cw_array : %s" % (data_count, rts_count, cw, cw_, psucc, thr, str(cw_array) ))
							debug_cycle = 0
						else:
							debug_cycle +=1

				#store statistics for report
				report_stats['thr'] = thr
				report_stats['cw'] = cw_
				report_stats['psucc'] = psucc
				report_stats['busytx2'] = busytx2
				report_stats['busy_time'] = busy_time
				cw_evaluate_cycle = 0

			else:
				cw_evaluate_cycle += 1

			# ENFORCE CW
			if enable_react[0]:
				# cwmin=int(cw_)
				# cwmax=int(cw_)
				setCW(iface, qumId, aifs, cw_array[cw_evaluate_cycle], cw_array[cw_evaluate_cycle], burst)

			time.sleep(cw_setting_interval - ((time.time() - starttime) % cw_setting_interval))


	def update_offer():
		done = False
		A = MAX_OFFER_C
		global my_mac
		D = [key for key,val in neigh_list.items()]
		Dstar=[]
		while done == False:
			Ddiff=list(set(D)-set(Dstar))
			if set(D) == set(Dstar):
				done = True
				neigh_list[my_mac]['offer'] = A + max([val['claim'] for key,val in neigh_list.items()])
			else:
				done = True
				neigh_list[my_mac]['offer'] = A / float(len(Ddiff))
				for b in Ddiff:
					if neigh_list[b]['claim'] < neigh_list[my_mac]['offer']:
						Dstar.append(b)
						A -= neigh_list[b]['claim']
						done = False


	def update_claim():
		off_w=[val['offer'] for key,val in neigh_list.items()]
		off_w.append(neigh_list[my_mac]['w'])
		neigh_list[my_mac]['claim']=min(off_w)


	def sniffer_REACT(iface, i_time):
		call_timeout=i_time[0]/2
		call_count=2000
		receiver_thread = threading.currentThread()
		while getattr(receiver_thread, "do_run", True):
			# UPI
			pktlist = controller.net.sniff_layer2_traffic(iface=mon_iface, sniff_timeout=call_timeout)
			for pkt in pktlist:
				try:

					# print('received frame addr1 %s - addr2 %s - addr3 %s' % (str(pkt.addr1), str(pkt.addr2), str(pkt.addr3)))
					# payload=bytes(pkt[2])
					# print('received frame payload %s \n' % (str(payload)))
					# print('received frame pkt %s' % (str(pkt)))
					# print('\n\n')

					# if my_mac == '00:15:6d:85:90:2d':
					# 	if pkt.addr2 == '00:00:00:c0:00:c0' or pkt.addr2 == '00:00:00:bf:00:c1' or pkt.addr2 == '00:00:00:bb:00:b8' or pkt.addr2 == '00:00:00:bc:00:ba' or pkt.addr2 == '00:00:00:b0:00:b8' or pkt.addr2 == '00:00:00:ae:00:b7':
					# 		rx_mac = 'null'
					# 	elif pkt.addr2 == my_mac :
					# 		rx_mac = my_mac
					# 	else:
					# 		continue
					# elif my_mac == '00:15:6d:85:75:b3':
					# 	if pkt.addr2 == '00:be:00:b6:01:a0' or pkt.addr2 == '00:c7:00:b8:01:af' or pkt.addr2 == '00:c5:00:b8:01:ad' or pkt.addr2 == '00:be:00:b5:01:a1' or pkt.addr2 == '00:bf:00:b7:01:a2' or pkt.addr2 == '00:c7:00:b7:01:b0':
					# 		rx_mac = 'null'
					# 	elif pkt.addr2 == my_mac :
					# 		rx_mac = my_mac
					# 	else:
					# 		continue
					# else:
					# 	rx_mac = str(pkt.addr2)
					rx_mac = str(pkt.addr2)
					if rx_mac == my_mac:
						pass
					else:
						payload=bytes(pkt[2])
						#print('received frame payload %s \n' % (str(payload)))
						if 'claim' in str(payload):
							payload='{'+re.search(r'\{(.*)\}', str(payload) ).group(1)+'}'
							curr_pkt = json.loads(payload)
							rx_mac = curr_pkt['mac_address']
							neigh_list[str(rx_mac)] = curr_pkt
							curr_pkt['t'] = float(time.time())
							update_offer()
							update_claim()

				except (Exception) as err:
					if debug:
						print ( "exception - error in receive frame : ", err)
					pass

	def send_ctrl_msg(iface,json_data):
		a=scapy.all.RadioTap()/scapy.all.Dot11(addr1="ff:ff:ff:ff:ff:ff", addr2=my_mac, addr3="ff:ff:ff:ff:ff:ff")/json_data
		# UPI
		controller.net.inject_frame(iface=mon_iface, frame=a, is_layer_2_packet=True, tx_count=1, pkt_interval=0)

	def send_REACT_msg(iface, i_time, iperf_rate):
		#TX
		global my_mac
		cycle = 0
		sender_thread = threading.currentThread()
		while getattr(sender_thread, "do_run", True):
			rate = min((float)( MAX_OFFER_C ),( (iperf_rate[0]*MAX_OFFER_C)/float(MAX_THR)) )
			neigh_list[my_mac]['w']=rate
			if debug or debug_react_value:
				if cycle > 50:
					for key,val in neigh_list.items():
						print('%s : %s' %(str(key), str(val)))
					print('')
					cycle = 0
				else:
					cycle +=1
			try:
				pkt_to_send={}
				neigh_list[my_mac]['t']=float(time.time())
				pkt_to_send['t'] = neigh_list[my_mac]['t']
				pkt_to_send['claim'] = neigh_list[my_mac]['claim']
				pkt_to_send['offer'] = neigh_list[my_mac]['offer']
				pkt_to_send['mac_address'] = my_mac
				#pkt_to_send['w']=neigh_list[my_mac]['w']
				json_data = json.dumps(pkt_to_send)

				#check dead nodes
				timeout = 30 #sec
				for key,val in neigh_list.items():
					if float(time.time())-val['t'] > timeout:
						neigh_list.pop(key)
						update_offer()
						update_claim()
				
				# REACT variables updated, transmit!
				send_ctrl_msg(iface, json_data)

			except (Exception) as err:
				if debug:
					print ( "send_REACT_msg exception", err)
				pass
			tx_interval=i_time[0]/10
			time.sleep(tx_interval - ((time.time() - starttime) % tx_interval))


	log = logging.getLogger()
	log.info('*********** WISHFUL *************')
	log.info('*********** starting local WiSHFUL controller **********************')
	msg={}
	print("Local ctrl program started: {}".format(controller.name))
	while not controller.is_stopped():
		msg = controller.recv(timeout=1)
		if msg:
			print("START REACT main function")
			#INIT REACT INFO
			init(msg["iface"])
			try:

				#Thread transmitter
				i_time = []
				i_time.append(msg['i_time'])
				iperf_rate = []
				iperf_rate.append(msg['iperf_rate'])
				enable_react = []
				enable_react.append(msg['enable_react'])

				sender_thread = threading.Thread(target=send_REACT_msg, args=(msg['iface'], i_time, iperf_rate,))
				sender_thread.do_run = True
				sender_thread.start()

				#thread receiver
				receiver_thread = threading.Thread(target=sniffer_REACT, args=(msg['iface'], i_time, ))
				receiver_thread.do_run = True
				receiver_thread.start()

				#update CW
				cw_thread = threading.Thread(target=update_cw, args=(msg['iface'], i_time, enable_react, ))
				cw_thread.do_run = True
				cw_thread.start()

			except (Exception) as err:
				if debug:
					print ( "exception", err)
					print ("Error: unable to start thread")
				pass

			break

	#CONTROLLER MAIN LOOP
	while not controller.is_stopped():
		msg = controller.recv(timeout=1)
		if msg:
			log.info("Receive message %s" % str(msg))
			#i_time[0] = msg['i_time']
			iperf_rate[0] = msg['iperf_rate']
			enable_react[0] = msg['enable_react']

			if enable_react[0] == 0:
				setCW(msg['iface'],1,2,15,1023,0)

		#send statistics to controller
		if 'w' in neigh_list[my_mac]:
			if debug:
				print('send message to controller')
			#print( "measure w %s claim %s offer %s " % (str( neigh_list[my_mac]['w']), str(neigh_list[my_mac]['claim']), str(neigh_list[my_mac]['offer'])) )
			controller.send_upstream({ "measure" : [[neigh_list[my_mac]['t'], neigh_list[my_mac]['w'], neigh_list[my_mac]['claim'], neigh_list[my_mac]['offer'], report_stats['thr'], report_stats['cw'], report_stats['psucc'], report_stats['busytx2'], report_stats['busy_time'] ]], "mac_address" : (my_mac) })

	receiver_thread.do_run = False
	receiver_thread.join()
	sender_thread.do_run = False
	sender_thread.join()
	cw_thread.do_run = False
	cw_thread.join()
	time.sleep(2)
