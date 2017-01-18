"""
Local control program to be executed on remote nodes.
"""

__author__ = "Fabrizio Giuliano"
__copyright__ = "Copyright (c) 2016, CNIT"
__version__ = "0.1.0"

import signal
import datetime
import logging
import time
import sys




def signal_handler(signal, frame):
		story_file.close()
		reading_thread.do_run = False
		reading_thread.join()
		time.sleep(2)
		sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# Definition of Local Control Program
def react(controller):
	import sys
	sys.path.append('../../')
	sys.path.append("../../agent_modules/wifi_ath")
	sys.path.append("../../agent_modules/wifi_wmp")
	sys.path.append("../../agent_modules/wifi")
	sys.path.append("../../agent_modules/ras_antenna")
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

	import wishful_framework.upi_arg_classes.edca as edca

	neigh_list = {};
	ieee80211_stats={}
	ieee80211_stats_={}
	pkt_stats={}
	C=1
	CLAIM_CAPACITY=0.8 # TEST 3,4,bis,5wrong, CLAIM=0.8 TEST1,2 CLAIM_CAPACITY=1 TEST6 CLAIM_CAPACITY=1
	mon_iface="mon0"
	t_tx=float(time.time())
	debug=False
	react_count=0

	cw_=1023
	cw=cw_
	data_count_=0
	rts_count_=0
	starttime=time.time()


	MAX_THR=5140 #kbps
	rate=0; #APP RATE

	"""
	REACT INIT
	"""
	def init(iface):
		global my_mac;
		my_mac=str(netifaces.ifaddresses(iface)[netifaces.AF_LINK][0]['addr'])

		global cw
		global cw_
		global data_count_
		global rts_count_

		cw_=1023
		cw=cw_
		data_count_=0
		rts_count_=0

		print("my_mac={}".format(my_mac))
		setCW(iface,1,2,15,1023,0)
		setCW(iface,3,1,3,7,0)
		init_pkt={};
		init_pkt['t']=0
		init_pkt['offer'] = C
		init_pkt['claim'] = 0
		init_pkt['w'] = 0

		neigh_list[my_mac]=init_pkt


	"""
	get PHY name for current device
	"""
	def getPHY(iface="wlan0"):
		devs_info = subprocess.Popen(["iw","dev"], stdout=subprocess.PIPE).communicate()[0]
		pp=str.split(str(devs_info),'\n')
		iii=[x for x in pp if '\t\t' not in x]	
		#phy = subprocess.Popen(["ls", "/sys/kernel/debug/ieee80211/"], stdout=subprocess.PIPE).communicate()[0]
		phy_list={}
		val=[]
		key=''
		for d in iii:
			if '#' in d:
				key=d;
			if iface in d:
				break
				
		phy=key.replace("#","")
		phy="phy0"
		return phy

	"""
	get iee80211 debugfs packet informations
	current format of iee80211_stats:
	{'failed_count': 0, 'dot11FCSErrorCount': 3, 'dot11RTSSuccessCount': 0, 'dot11TransmittedFrameCount': 1, 'dot11ACKFailureCount': 0, 'retry_count': 0, 'multiple_retry_count': 0, 'received_fragment_count': 30, 'frame_duplicate_count': 0, 'transmitted_fragment_count': 1, 'multicast_dot11TransmittedFrameCount': 1, 'multicast_received_frame_count': 20, 'dot11RTSFailureCount': 0}
	"""
	def get_ieee80211_stats(iface,sleeptime):
		global pkt_stats
		phy=getPHY(iface);
		#while True:
		out = subprocess.Popen(["bash","ieee_stats.sh",phy,"{}".format(sleeptime)], stdout=subprocess.PIPE).communicate()[0]
		ieee80211_stats_diff=json.loads(out.decode("utf-8") )
			#pkt_stats=ieee80211_stats_diff
		return ieee80211_stats_diff
	#BUG: follow approach seems to be too slow and grab wrong values
		
		"""
		global pkt_stats
		phy=getPHY(iface);
		stats_path="/sys/kernel/debug/ieee80211/{}/statistics/*".format(phy)
		i=0
		stats_file_list=glob.glob(stats_path)
		f={}
		ieee80211_stats_diff={}
		for ff in stats_file_list:
			f[i] = open(ff, 'r')
			i+=1;
		while True:
			for i in range(0,len(f)):
				key=str.split(stats_file_list[i],"/")[-1]
				try:
					val=int(f[i].read())
				except Exception,err:
					val=0
				ieee80211_stats[key]=val
			
			if ieee80211_stats_ :
				for key in ieee80211_stats:
					ieee80211_stats_diff[key]=ieee80211_stats[key]-ieee80211_stats_[key]
					ieee80211_stats_[key]=ieee80211_stats[key]
			else:
				for key in ieee80211_stats:
					ieee80211_stats_[key]=ieee80211_stats[key];
			pkt_stats=ieee80211_stats_diff
		#return ieee80211_stats_diff
		
		"""

	"""
	Compute txtime theoretical value for given:
	% Input vars:
	%   v80211  : '11b', '11g', '11a' or '11p'
	%   bitrate : 1,2,5.5,11,6,9,12,18,24,36,48,54
	%   bw      : 20,10,5
	%   pkt_size: value in byte
	% NOTE: pkt_size means  MAC_H + LLC_H  + PAYLOAD + MAC_FCS
	"""
	def txtime_theor(v80211,bitrate,bw,pkt_size):
	    Tpre=16*20/bw;
	    Tsig=4*20/bw;
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
		
	def update_cw(iface,i_time,enable_react,sleep_time):

		while True:
			if 1:
				update_cw_decision(iface,enable_react,sleep_time);
			time.sleep(sleep_time - ((time.time() - starttime) % sleep_time))

	"""
	Set CW
	"""

	def setCW(iface,qumId,aifs,cwmin,cwmax,burst):

	#       echo "0 1 1 3 0" > /sys/kernel/debug/ieee80211/phy0/ath9k/txq_params
	#
	#       Proper sequence is : "qumId aifs cwmin cwmax burst"

		phy=getPHY(iface);	
		
		#TODO: add SETCW UPI
		edcaParams = edca.EdcaQueueParameters(aifs=aifs, cwmin=cwmin, cwmax=cwmax, txop=burst)
		print("----->:{}".format(edcaParams))
#		edcaParams = edca.EdcaQueueParameters(aifs=1, cwmin=1, cwmax=1, txop=1)
#		# UPI
#		controller.radio.set_mac_access_parameters(iface=iface,queueId=qumId,queueParams=edcaParams)

		f_name='/sys/kernel/debug/ieee80211/{}/ath9k/txq_params'.format(phy);
		txq_params_msg='{} {} {} {} {}'.format(qumId,aifs,cwmin,cwmax,burst)
		f_cw = open(f_name, 'w')
		f_cw.write(txq_params_msg)	

	"""
	update CW decision based on ieee80211 stats values and virtual channel freezing estimation
	"""
	def update_cw_decision(iface,enable_react,sleep_time):
		#get stats
		global my_mac
		global cw
		global cw_
		global data_count_
		global rts_count_
		CWMIN=15
		CWMAX=2047
		#TODO: change/add/reuse UPI candidate: get_measurement
		UPI_myargs = {'interface' : 'wlan0', 'measurements' : [UPI_R.dot11RTSSuccessCount,UPI_R.dot11RTSFailureCount] }
		pkt_stats=controller.radio.get_measurements(UPI_myargs)
		pkt_stats=get_ieee80211_stats(iface,sleep_time)
		pkt_size=1534

		if pkt_stats:
			if rts_count_ == 0 and data_count_ == 0:
				data_count = pkt_stats['dot11RTSSuccessCount'] - data_count_
				rts_count = pkt_stats['dot11RTSSuccessCount'] + pkt_stats['dot11RTSFailureCount'] - rts_count_
				data_count_=pkt_stats['dot11RTSSuccessCount']
				rts_count_=pkt_stats['dot11RTSSuccessCount'] + pkt_stats['dot11RTSFailureCount']
				return
			data_count = pkt_stats['dot11RTSSuccessCount'] - data_count_
			rts_count = pkt_stats['dot11RTSSuccessCount'] + pkt_stats['dot11RTSFailureCount'] - rts_count_
			data_count_=pkt_stats['dot11RTSSuccessCount']
			rts_count_=pkt_stats['dot11RTSSuccessCount'] + pkt_stats['dot11RTSFailureCount']
			tx_goal=0
			I=0
			dd = sleep_time;
			gross_rate = float(CLAIM_CAPACITY)*float(neigh_list[my_mac]['claim']);
			
			[tslot, tx_time_theor, t_rts, t_ack]= txtime_theor('11a',6,20,pkt_size)
	#                busytx2 =  0.002198*float(data_count) + 0.000081*float(rts_count); #how much time the station spent in tx state during the last observation internval
			busytx2 =  0.002071*float(data_count) + 0.000046*float(rts_count); #how much time the station spent in tx state during the last observation internval
			SIFS=16 #usec
			tslot=9e-6 #usec
			#freeze2 = dd - busytx2 - cw_/float(2)*tslot*rts_count - 2*SIFS*1e-6; #how long the backoff has been frozen;
			freeze2 = float(dd) - float(busytx2) - cw_/float(2)*float(tslot)*rts_count; #how long the backoff has been frozen;
			if rts_count > 0:
				avg_tx = float(busytx2)/float(rts_count); #average transmission time in a transmittion cycle
				psucc = float(data_count)/float(rts_count);
			else:
				avg_tx=0
				psucc=0

			if avg_tx > 0:
				tx_goal = float(dd*gross_rate)/float(avg_tx);
			else:
				tx_goal = 0

			freeze_predict = float(freeze2)/float(dd-busytx2)*float(dd-dd*float(gross_rate))  ;


			if tx_goal > 0:
				cw = 2/float(0.000009) * (dd-tx_goal*avg_tx-freeze_predict)/float(tx_goal);


			if cw < CWMIN: 
				cw_=CWMIN
			elif cw > CWMAX:
				cw_=CWMAX
			else:
				# TEST1
				#cw_=cw

	 
				# TEST2	CLAIM_CAPACITY = 1; TEST3 CLAIM_CAPACITY = 0.8		
				#cw_=cw 
				#cw_= pow(2, math.ceil(math.log(cw_)/math.log(2)))-1;
				
				#TEST 4 CLAIM_CAPACITY = 0.8 #GOOD
				cw_=cw 
				cw_= pow(2, round(math.log(cw_)/math.log(2)))-1;
				
				#TEST 5 CLAIM_CAPACITY = 1 #BAD!

				#cw_=cw 
				#cw_= pow(2, round(math.log(cw_)/math.log(2)))-1;
				#cw_ = (alpha * cw_ + (1-alpha) * cw );
			
			# ENFORCE CW
			qumId=1 #BE
			aifs=2
			cwmin=int(cw_);
			cwmax=int(cw_);
			burst=0
			if enable_react:
				setCW(iface,qumId,aifs,cwmin,cwmax,burst);
			thr=(data_count)*1470*8/float(dd*1e6); 
			if debug:	
				print("t=%.4f,dd=%.4f data_count=%.4f rts_count=%.4f busytx2=%.4f(%.4f) gross_rate=%.4f,avg_tx=%.4f freeze2=%.4f freeze_predict=%.4f tx_goal=%.4f I=%.4f cw=%.4f cw_=%.4f psucc=%.4f thr=%.4f" % (time.time(),dd,data_count,rts_count,busytx2,busytx2/float(dd),gross_rate,avg_tx,freeze2,freeze_predict,tx_goal,I,cw,cw_,psucc,thr))
			out_val="%.4f,%.4f,%.4f,%.4f,%.4f,%.4f,%.4f,%.4f,%.4f,%.4f,%.4f,%.4f,%.4f,%.4f,%.4f" % (time.time(),dd,data_count,rts_count,busytx2,gross_rate,avg_tx,freeze2,freeze_predict,tx_goal,I,cw,cw_,psucc,thr)
			
			my_ip=str(netifaces.ifaddresses(iface)[netifaces.AF_INET][0]['addr'])
			#my_ip.replace(".","_")	
			out_file="{}.csv".format(my_ip);
			with open(out_file, "a") as myfile:
				myfile.write(out_val+"\n")
			
	"""
	def updateAction(iface,i_time):
	  # uploadPacket function has access to the url & token parameters because they are 'closed' in the nested function
		def uploadPacket(pkt):
			global my_mac
			global t_tx
			global react_count
			try:
				rx_mac=str(pkt.addr2)
				if rx_mac == my_mac:
					pass
				else:
					payload=str(pkt[2])
					if 'claim' in str(payload):
						payload='{'+re.search(r'\{(.*)\}', str(payload) ).group(1)+'}'
						curr_pkt=json.loads(payload)
						neigh_list[str(rx_mac)]=curr_pkt;
						curr_pkt['t'] = float(time.time())
						update_offer();
						update_claim();
			except (Exception) as err:
				if debug:
					print ( "exception", err)           
					print ("Error: unable to start thread")
				pass
		return uploadPacket
	"""
	def update_offer():
		done = False;
		A = C;
		global my_mac
		D = [key for key,val in neigh_list.items()]
		Dstar=[];	
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

	def sniffer_REACT(iface,i_time):
		
		#scapy.all.sniff(iface=mon_iface, prn=updateAction(iface,i_time),store=0)

		call_timeout=i_time/2
		call_count=2000
		while True:
#			pktlist = scapy.all.sniff(iface=mon_iface, timeout=call_timeout, count=call_count,store=1)
			# UPI
			pktlist = controller.net.sniff_layer2_traffic(iface=mon_iface, sniff_timeout=call_timeout, ipdst=None, ipsrc=None)
			for pkt in pktlist:
				try:
					rx_mac=str(pkt.addr2)
					if rx_mac == my_mac:
						pass
					else:
						payload=bytes(pkt[2])
						if 'claim' in str(payload):
							payload='{'+re.search(r'\{(.*)\}', str(payload) ).group(1)+'}'
							curr_pkt=json.loads(payload)
							neigh_list[str(rx_mac)]=curr_pkt;
							curr_pkt['t'] = float(time.time())
							update_offer();
							update_claim();
				except (Exception) as err:
					if debug:
						print ( "exception", err)           
					pass

	def send_ctrl_msg(iface,json_data):
		a=scapy.all.RadioTap()/scapy.all.Dot11(addr1="ff:ff:ff:ff:ff:ff", addr2=my_mac, addr3="ff:ff:ff:ff:ff:ff")/json_data
#		scapy.all.sendp(a, iface=mon_iface,verbose=0)
		# UPI
		controller.net.inject_frame(iface=mon_iface,frame=a,is_layer_2_packet=True,tx_count=1, pkt_interval=0)

	def send_REACT_msg(iface,i_time,iperf_rate,enable_react):
		#TX
		global my_mac
		while True:
			rate = min((float)( C ),( (iperf_rate*C)/float(MAX_THR)) );
			neigh_list[my_mac]['w']=rate
			if debug:
				#keyprint=""
				#for key,val in neigh_list.items():
				#	keyprint="{},{}".format(keyprint,key)
				print(neigh_list)
				#print(keyprint)
			try:
				pkt_to_send={};

				neigh_list[my_mac]['t']=float(time.time())
				pkt_to_send['t']=neigh_list[my_mac]['t']
				pkt_to_send['claim']=neigh_list[my_mac]['claim']
				pkt_to_send['offer']=neigh_list[my_mac]['offer']
				#pkt_to_send['w']=neigh_list[my_mac]['w']
				json_data = json.dumps(pkt_to_send)
				
				
				#check dead nodes
				#timeout = i_time * 100
				timeout = 30 #sec
				
				for key,val in neigh_list.items():
					if float(time.time())-val['t'] > timeout:
						neigh_list.pop(key)
						update_offer()
						update_claim()
				
				# REACT variables updated, transmit!
				send_ctrl_msg(iface,json_data)

			except (Exception) as err:
				if debug:
					print ( "send_REACT_msg exception", err)           
				pass
			tx_interval=i_time/10
			time.sleep(tx_interval - ((time.time() - starttime) % tx_interval))

	def usage(in_opt,ext_in_opt):
		print("input error: here optionlist: \n{0} --> {1}\n".format(in_opt,str(ext_in_opt)))

	def main(iface="wlan0",i_time=1,iperf_rate=0,enable_react=False):
		print("values:")
		print("iface={}".format(iface))
		print("i_time={}".format(i_time))
		print("iperf_rate={}".format(iperf_rate))
		print("enable_react={}".format(enable_react))
		
		#INIT REACT INFO
		init(iface);
		try:

			#Thread transmitter
			_thread.start_new_thread( send_REACT_msg,(iface,i_time,iperf_rate,enable_react ) )

			#thread receiver
			_thread.start_new_thread( sniffer_REACT,(iface,i_time ) )

			#update CW
			_thread.start_new_thread(update_cw,(iface,i_time,enable_react,i_time))

		except (Exception) as err:
			if debug:
				print ( "exception", err)           
				print ("Error: unable to start thread")
			pass

		while 1:
		   pass


	msg={};
	while True:
		msg = controller.recv(timeout=1)
		if msg:
			break;
	print("START REACT main function")
	main(msg["iface"],msg["i_time"],msg["iperf_rate"],msg["enable_react"]);
	print("REACT main function started")
