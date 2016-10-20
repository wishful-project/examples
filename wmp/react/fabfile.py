#! /usr/bin/env python2
'''Utilities for performing REACT80211 experimets.
Requires Python 2.X for Fabric.
Author: Fabrizio Giuliano
'''

import os
import os.path
import datetime
import re
import sys
#import scapy.all as scapy



from StringIO import StringIO
from fabric.api import get


import fabric
import fabric.api as fab
from fabric.api import hide, run, get
import fabric.utils
hosts_driver=[];
neigh_list=[]
#verbosity
#fabric.state.output['running'] = False
#fab.output_prefix = False

@fab.task
def set_hosts(host_file):
	#fab.env.hosts = open(host_file, 'r').readlines()
	hosts_info_file = open(host_file, 'r').readlines()
	hosts_info=[];
	hosts_driver=[];
	for i in hosts_info_file:
		if not i.startswith("#"):
			hosts_info.append(i);
	fab.env.hosts = [i.split(',')[0] for i in hosts_info] 
	hosts_driver= [i.split(',')[1].replace("\n", "") for i in hosts_info]
	return hosts_driver

#---------------------
#SET NODES    
hosts_driver=set_hosts('node_info.txt')

#CONNECTIVITY MATRIX
w=len(fab.env.hosts)
h=len(fab.env.hosts)

conn_matrix = [[0 for x in range(w)] for y in range(h)] 
for ii in range(0,len(fab.env.hosts)):
	conn_matrix[ii][ii]=1;
#---------------------
@fab.task
@fab.parallel
def reboot():
    fab.reboot()

@fab.task
@fab.parallel
def associate_mesh(driver,iface,mesh_id,freq,txpower,rate,ip_addr,rts='off'):
	mesh_iface='mesh0';
    	with fab.settings(warn_only=True):
		if driver=="ath9k":
			
			cmd_str='rmmod ath9k ath9k_common ath9k_hw ath mac80211 cfg80211;'
			cmd_str=cmd_str+' modprobe ath9k;'
			cmd_str=cmd_str+'iw dev {0} interface add {1} type mp; '.format(iface,mesh_iface)
			cmd_str=cmd_str+'iw dev {0} set freq {1}; '.format(mesh_iface,freq)
			cmd_str=cmd_str+'ifconfig {0} up; '.format(mesh_iface)
			cmd_str=cmd_str+'ifconfig {0} {1}; '.format(mesh_iface,ip_addr)
			cmd_str=cmd_str+'iw dev {0} mesh join {1}; '.format(mesh_iface,mesh_id)
			cmd_str=cmd_str+'iwconfig {0} txpower {1}; '.format(mesh_iface,txpower)
			cmd_str=cmd_str+'iwconfig {0} rate {1}M fixed; '.format(mesh_iface,rate)
		        cmd_str=cmd_str+'sudo iwconfig {0} rts {1}; '.format(iface,rts)
			fab.sudo(cmd_str)
			#iface_mon='mon0';
			#fab.sudo('iw dev {0} interface add {1} type monitor'.format(iface,iface_mon));
			#fab.sudo('ifconfig {0} up'.format(iface_mon));
		else:
			print "DRIVER {0} NOT SUPPORTED".format(driver)

@fab.task
@fab.parallel

# Ad-hoc node association
#echo "usage $0 <iface> <essid> <freq> <power> <rate> <ip> <mac> <reload[1|0]>"
def associate(driver,iface,essid,freq,txpower,rate,ip_addr,mac_address="aa:bb:cc:dd:ee:ff",skip_reload=False,rts='off'):


    	with fab.settings(warn_only=True):
		if driver=="ath9k":
    			if skip_reload == False:
				fab.run('sudo rmmod ath9k ath9k_common ath9k_hw ath mac80211 cfg80211')
				fab.run('sudo modprobe ath9k')
			else:
				fab.run('iw {0} ibss leave'.format(iface))
			fab.run('sudo iwconfig {0} mode ad-hoc; sudo ifconfig {0} {5} up;sudo iwconfig {0} txpower {3}; sudo iwconfig {0} rate {4}M fixed;sudo iw dev {0} ibss join {1} {2} fixed-freq {6}'.format(iface,essid,freq,txpower,rate,ip_addr,mac_address))
			iface_mon='mon0';
			fab.sudo('iw dev {0} interface add {1} type monitor'.format(iface,iface_mon));
			fab.sudo('ifconfig {0} up'.format(iface_mon));
		        fab.run('sudo iwconfig {0} rts {1}'.format(iface,rts))
	
		elif driver=="b43":
			
    			if skip_reload == False:
				fab.run('sudo rmmod b43')
				fab.run('sudo modprobe b43 qos=0')
			else:
				fab.run('iw {0} ibss leave'.format(iface))
			fab.run('sudo iwconfig {0} mode ad-hoc; sudo ifconfig {0} {5} up;sudo iwconfig {0} txpower {3}; sudo iwconfig {0} rate {4}M fixed;sudo iw dev {0} ibss join {1} {2} fixed-freq {6}'.format(iface,essid,freq,txpower,rate,ip_addr,mac_address))
		else: 
			"driver {} not supported".format(driver)
			return
@fab.task
@fab.parallel
def stop_wifi(driver='ath9k'):
    with fab.settings(warn_only=True):
	if driver == 'ath9k':
    		fab.run('sudo rmmod ath9k ath9k_common ath9k_hw ath mac80211 cfg80211')
	if driver == 'b43':
    		fab.run('sudo rmmod b43')
@fab.task
@fab.parallel
def set_txpower(txpower):
	fab.run('sudo iwconfig wlan0 txpower {0}'.format(txpower))

@fab.task
@fab.parallel
def load_REACT_kernel_module(enable_react='NO',driver='ath9k'):
	if driver == 'ath9k':
		if enable_react=='YES':
			netdir="net-atlas"
			ath_dir="ath"
		else:
			if enable_react=='NO':
				netdir="net-origin"
				ath_dir="ath-orig"
		with fab.settings(warn_only=True):
			driverdir="drivers/net/wireless/{0}/ath9k/".format(ath_dir)
			driverdir2="drivers/net/wireless/{0}/".format(ath_dir)
			fab.run( 'sudo cp ~/atlas/kernel-3.8.0-atlas/{0}/wireless/cfg80211.ko /lib/modules/3.8.0-37-generic/kernel/net/wireless/'.format(netdir))
			fab.run( 'sudo cp ~/atlas/kernel-3.8.0-atlas/{0}/mac80211/mac80211.ko /lib/modules/3.8.0-37-generic/kernel/net/mac80211/'.format(netdir))
			fab.run( 'sudo cp ~/atlas/kernel-3.8.0-atlas/{0}/*.ko /lib/modules/3.8.0-37-generic/kernel/drivers/net/wireless/ath/ath9k/'.format(driverdir))
			fab.run( 'sudo cp ~/atlas/kernel-3.8.0-atlas/{0}/ath.ko /lib/modules/3.8.0-37-generic/kernel/drivers/net/wireless/ath/'.format(driverdir2))
			#add python modules
			#fab.sudo('apt-get install python-scapy')
	fab.local('sleep 1');


@fab.task
@fab.parallel
def kill_ping():
        with fab.settings(warn_only=True):
		fab.run('sudo pkill -f ping');	
		fab.sudo('pkill -f send_react_ctrl_msgr.py')
@fab.task
@fab.parallel
def kill_react_ctrl_msgr():
        with fab.settings(warn_only=True):
		fab.sudo('pkill -f send_react_ctrl_msgr.py')

@fab.task
@fab.parallel
def run_ping(dst_ip,i_time):
	ping_msg="nohup ping {0} -i {1} -Q 150  -s 0 > /dev/null 2>/dev/null &".format(dst_ip,i_time)
	fab.run(ping_msg,pty=False);

@fab.task
def run_ping_REACT():
	i=fab.env.hosts.index(fab.env.host)
	ping_msg="";
	for j in range(0,len(fab.env.hosts)):
		dst_ip='192.168.0.{0}'.format(j+1);
		if i != j:
			print "i={0}; j={1}".format(i,j);
			fab.execute(run_ping,dst_ip,0.5,hosts=[fab.env.host])

@fab.task
def run_ping_REACT_mesh(neigh_list,i_time=0.5):
	ping_msg='';
	for dst_ip in neigh_list:
		print dst_ip
		fab.execute(run_ping,dst_ip,0.5,hosts=[fab.env.host])


@fab.task
#setup network, ad-hoc association
#def network(txpower,enable_react='',is_mesh=0,host_file=''):
def network(txpower,freq=2412,host_file=''):
	
	#search my host
	i_ip=fab.env.hosts.index(fab.env.host)
	#if enable_react=='YES':
	#		print "setup REACT nodes"
	#else:
	#	if enable_react=='NO':
	#		print "setup legacy IEEE 802.11 nodes"
	#	else:
	#		print "WRONG OPTION enable_react={0}, must be YES or NO".format(enable_react)
			return
	print fab.env.hosts
	print hosts_driver
	driver=hosts_driver[i_ip];
	#if is_mesh=='1':
	#	fab.execute(associate_mesh,driver,'wlan0','test',freq,txpower,6,'192.168.0.{0}'.format(i_ip+1),rts='250',hosts=[fab.env.hosts[i_ip]])
	#	return
	fab.execute(associate,driver,'wlan0','test',freq,txpower,6,'192.168.0.{0}'.format(i_ip+1),'aa:bb:cc:dd:ee:ff',skip_reload=False,rts='250',hosts=[fab.env.hosts[i_ip]])
	#fab.execute(run_ping_REACT,hosts=[fab.env.hosts[i_ip]])

def send_react_ctrl_msg(dst_ip,i_time):
	ctrl_msg="nohup python ~/REACT80211/send_react_ctrl_msgr.py -d {0} -i {1}  > /dev/null 2>/dev/null &".format(dst_ip,i_time)
	fab.sudo(ctrl_msg,pty=False);
@fab.task
def react_control_plane(neigh_list,i_time=0.5):
	for dst_ip in neigh_list:
		print dst_ip
		fab.execute(send_react_ctrl_msg,dst_ip,0.5,hosts=[fab.env.host])
	
@fab.task
def setup_react(is_mesh=0):
	fab.execute(kill_ping,hosts=[fab.env.host])
	fab.execute(kill_react_ctrl_msgr,hosts=[fab.env.host])
	if is_mesh=='1':
		neigh_list=neighbor_discovery()
	else:
		neigh_list=[];
		i=fab.env.hosts.index(fab.env.host)
		for j in range(0,len(fab.env.hosts)):
			fab.execute(run_ping_REACT,hosts=[fab.env.hosts[j]])
			#if i != j:
			#	neigh_list.append('192.168.0.{0}'.format(j+1));

	#fab.execute(react_control_plane,neigh_list,hosts=[fab.env.host])


@fab.task
@fab.runs_once
def stop_all():
	fab.execute(kill_ping)
	fab.execute(stop_iperf)
	fab.execute(stop_dmesg)
	fab.execute(stop_ieee_stats)
	fab.execute(stop_wifi)
	
@fab.task
@fab.runs_once
def connectivity_matrix_iperf():

        my_ip = fab.run ("ifconfig  wlan0 | grep 'inet addr:' | cut -d: -f2 | awk '{ print $1}' ");
        i=int(my_ip.split('.',3)[3])-1

        with fab.settings(warn_only=True):

		for i in range(0,len(fab.env.hosts)):
			with hide('output'):			
				fab.execute(iperf_server_conn_matrix,hosts=[fab.env.hosts[i]]);
			for j in range(0,len(fab.env.hosts)):
				tic()
				if i != j:
					#RUN IPERF CLIENT
					#fab.execute(stop_iperf,hosts=[fab.env.hosts[j]])
					dst_ip='192.168.0.{0}'.format(i+1);
					fab.execute(iperf_client_conn_matrix,dst_ip,0.1,hosts=[fab.env.hosts[j]])
					#fab.local ('sleep 0.2');
				toc()
			fab.execute(stop_iperf,hosts=[fab.env.hosts[i]])
			fab.execute(get_conn_matr,hosts=[fab.env.hosts[i]]);
			mmm_file = open("conn_matr.txt", "w")
			mmm_file.write('{0}'.format(conn_matrix))
			mmm_file.close()
@fab.task
def get_conn_matr():
	MAX_RATE=6e6;
	iperf_output=get_iperf_server_conn_matrix_info()
	iii=0;
	for line in iperf_output.splitlines():
		if (iii < len(fab.env.hosts)-1):
			if re.search( '192.168.0.', line):
				print line
				iperf_stat=line.split(',',line.count(',')-1)
				i=int(iperf_stat[1].split('.',3)[3])-1 #dst
				j=int(iperf_stat[3].split('.',3)[3])-1 #src
				print 'i={0} j={1}'.format(i,j)
				conn_matrix[int(i)][int(j)]=float(iperf_stat[8])/MAX_RATE;
			iii=iii+1
	print conn_matrix

@fab.task
def connectivity_matrix():

	output = fab.run ("ifconfig  wlan0 | grep 'inet addr:' | cut -d: -f2 | awk '{ print $1}' ");
        i=output.split('.',3)[3]

	for j in range(0,len(fab.env.hosts)):
	    if int(i) != int(j+1):
    		with fab.settings(warn_only=True):
			ping_output = fab.run('sudo ping -w1 -s1 -c100 -f 192.168.0.{0}'.format(j+1), pty=False)
			for line in ping_output.splitlines():
				#10 packets transmitted, 10 received, 0% packet loss, time 15ms
				if 'transmitted' in line:
					tx_packets=line.split(' ')[0]
					rx_packets=line.split(' ')[3]
					#loss=line.split(' ')[5]
					#rtt=line.split(' ')[9]
					conn_matrix[int(i)-1][int(j)]=float(rx_packets)/float(tx_packets);
		
	    else:
		conn_matrix[int(i)-1][int(j)]=-1;
	print conn_matrix

@fab.task
def iperf_server_conn_matrix():
    fab.run('nohup iperf -s -u -y C &> /tmp/iperf.out &',pty=False)
#    fab.run('nohup iperf -s -u -y C &',pty=False)

@fab.task
def get_iperf_server_conn_matrix_info():
	fd = StringIO()
	get('/tmp/iperf.out', fd)
	content=fd.getvalue()
#	content=fab.run('cat /tmp/iperf.out');
	return content

@fab.task
def iperf_client_conn_matrix(server, duration,src_rate=100e6):
    fab.run('nohup iperf -c {0} -u -t {1} -b {2} -y C'.format(server, duration,src_rate),pty=False)

def start_iperf_server(trialnum,tx_id,rx_id, iperf_port):
    data_path='~/REACT80211/wishful/data'
    fab.run('mkdir -p {}'.format(data_path));
    fab.run('nohup iperf -i 1 -s -u -p {4} -y C > {5}/{0}-iperf-{1}-{2}-{3}.csv  < /dev/null &'.format(datetime.date.today(),tx_id.lower(),rx_id.lower(),trialnum,iperf_port,data_path), pty=False)

@fab.task
@fab.parallel
def dmesg_logger(trialnum):
	h=fab.env.host;
	h=h.split('.',1)[0]
	h=h.lower();
	out_file='~/REACT80211/data/{0}-dmesg-{1}-{2}.csv'.format(datetime.date.today(),h,trialnum)
	fab.run('sudo bash -c "tail -f /var/log/kern.log | grep atlaslog_cw > {0} &" '.format(out_file),pty=False)

@fab.task
@fab.parallel
def stop_dmesg():
    with fab.settings(warn_only=True):
	fab.sudo('pkill -HUP -f kern.log')

@fab.task
def ieee_stats_logger(trialnum):
	h=fab.env.host;
	h=h.split('.',1)[0]
	h=h.lower();
	out_file='~/REACT80211/data/{0}-ieee_stats-{1}-{2}.csv'.format(datetime.date.today(),h,trialnum)
	fab.run('sudo bash -c "~/REACT80211/ieee_stats.sh > {0} &" '.format(out_file),pty=False)

@fab.task
@fab.parallel
def stop_ieee_stats():
    with fab.settings(warn_only=True):
    	#for i_kill in range(0,4): 
	#	fab.run('sudo bash -c "kill -9 $(ps aux | grep ieee_stats | awk \'{print $2}\')"');
	fab.sudo('pkill -HUP -f ieee_stats')

@fab.task
@fab.parallel
def stop_iperf():
    with fab.settings(warn_only=True):
        fab.run('killall -9 iperf')
def stop_iperf_server():
    with fab.settings(warn_only=True):
        fab.run('killall -9 iperf')
	fab.run('rm /tmp/iperf*.out');

@fab.task
def run_iperf_client(server, duration,iperf_port,src_rate=6000,enable_react='NO'):
	enable_react=enable_react.upper();
	if enable_react=='YES':
		fab.run('sudo bash -c "echo {0} > /sys/kernel/debug/ieee80211/phy0/source_rate" '.format(src_rate))
	"""
	else:
		if enable_react=='NO':
			with fab.settings(warn_only=True):
				#DISABLE REACT
				fab.run('sudo bash -c "echo 0 > /sys/kernel/debug/ieee80211/phy0/source_rate" ')
				#RE-ENABLE EXPONENTIAL BACKOFF
				fab.run('sudo bash -c "echo -1 > /sys/kernel/debug/ieee80211/phy0/cw" ')
	"""
	fab.run('nohup iperf -c {0} -u -t {1} -b {3}K -p {2} >  /dev/null &'.format(server, duration,iperf_port,src_rate),pty=False)


@fab.task
@fab.runs_once
def run_trial(trialnum,enable_react=''):
    if enable_react=='YES':
		trialnum='{0}-{1}'.format(trialnum,'REACT');
    else:
	if enable_react=='NO':
		trialnum='{0}-{1}'.format(trialnum,'RTS');
	else:
		print "WRONG OPTION enable_react={0}, must be YES or NO".format(enable_react)
		return
    print "running {0}".format(trialnum)

    fab.execute(stop_iperf)
    fab.local('sleep 3')
    hn=[];
    for h in fab.env.hosts: 
	h=h.split('.',1)[0]
	hn.append(h)
    print hn
    fab.execute(start_iperf_server,trialnum, hn[0],hn[1], 50012, hosts=[fab.env.hosts[1]])
    fab.execute(start_iperf_server,trialnum, hn[1],hn[2], 50023, hosts=[fab.env.hosts[2]])
    fab.execute(start_iperf_server,trialnum, hn[2],hn[3], 50034, hosts=[fab.env.hosts[3]])
    fab.execute(start_iperf_server,trialnum, hn[3],hn[0], 50041, hosts=[fab.env.hosts[0]])
   
    fab.local('sleep 3')
    duration=60
    src_rate=6000; # in Kbps
    fab.execute(run_iperf_client, '192.168.0.2', duration, 50012, src_rate,enable_react,hosts=[fab.env.hosts[0]])
    fab.execute(run_iperf_client, '192.168.0.3', duration, 50023, src_rate,enable_react,hosts=[fab.env.hosts[1]])
    fab.execute(run_iperf_client, '192.168.0.4', duration, 50034, src_rate,enable_react,hosts=[fab.env.hosts[2]])
    fab.execute(run_iperf_client, '192.168.0.1', duration, 50041, src_rate,enable_react,hosts=[fab.env.hosts[3]])
    fab.local('sleep {0}'.format(duration))
    fab.execute(stop_iperf)

@fab.task
def sync_date():
    controller_time=fab.local('echo $(date +%T)',capture=True)
    #fab.local('echo {0}'.format(controller_time))
    fab.run('date +%T -s {0}'.format(controller_time))

def tic():
    #Homemade version of matlab tic and toc functions
    import time
    global startTime_for_tictoc
    startTime_for_tictoc = time.time()

def toc():
    import time
    if 'startTime_for_tictoc' in globals():
        print "Elapsed time is " + str(time.time() - startTime_for_tictoc) + " seconds."
    else:
        print "Toc: start time not set"


@fab.task
def neighbor_discovery():

	#run a ping to all nodes
        my_ip = fab.run ("ifconfig  mesh0 | grep 'inet addr:' | cut -d: -f2 | awk '{ print $1}' ");
	my_mac = fab.run("ifconfig mesh0 | grep HWaddr | awk '{print $5}'")
        i=int(my_ip.split('.',3)[3])-1
	ping_msg="";
	for j in range(0,len(fab.env.hosts)):
		dst_ip='192.168.0.{0}'.format(j+1);
		if i != j:
			ping_msg=ping_msg+"nohup ping {0} -w1 -c 10 -Q 150  -s 0 > /dev/null 2>/dev/null & ".format(dst_ip)
	fab.run(ping_msg,pty=False);
		
	#get arp table
	arp=fab.run('arp',pty=False)
	stri = StringIO(arp)
	arp_list=[]
	mpath_list=[]
	neigh_list=[]
	for nl in stri:
		if (nl.find("mesh0")!=-1):
			nl=nl.replace("\t", " ")
			nl=nl.replace("\n", " ")
			nl=nl.replace(" ", ",")
			nl=nl.split(",")
			nl = filter(None, nl)
			arp_list.append(nl)
		


	#get mpath mesh 
	mpath=fab.run('sudo iw dev mesh0 mpath dump | grep mesh0',pty=False)
	stri = StringIO(mpath)
	for nl in stri:
		if (nl.find("mesh0")!=-1):
			nl=nl.replace("\t", " ")
			nl=nl.replace("\n", " ")
			nl=nl.replace(" ", ",")
			nl=nl.split(",")
			nl = filter(None, nl)
			mpath_list.append(nl)
	
	for i in range(0,len(arp_list)):
		for j in range(0,len(mpath_list)):
			if arp_list[i][2] == mpath_list[j][0]:

				if mpath_list[j][0] == mpath_list[j][1]:
					print "{0} is neighbor".format(arp_list[i][0]) 
					neigh_list.append(arp_list[i][0])
				else:
					print "{0} is NOT neighbor".format(arp_list[i][0]) 
	return neigh_list


