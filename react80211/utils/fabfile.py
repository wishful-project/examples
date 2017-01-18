#! /usr/bin/env python2
'''Utilities for performing REACT80211 experimets.
Requires Python 2.X for Fabric.
Author: Fabrizio Giuliano
'''

import os
import os.path
import datetime
import re


import fabric.api as fab
import fabric.utils
hosts_driver=[];

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
	#hosts_driver= [i.split(',')[1].replace("\n", "") for i in hosts_info]
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
def getIP(ifname):
    fab.run("ifconfig {}".format(ifname))

@fab.task
@fab.parallel

# Ad-hoc node association
#echo "usage $0 <iface> <essid> <freq> <power> <rate> <ip> <mac> <reload[1|0]>"
def associate(driver,iface,essid,freq,txpower,rate,ip_addr,rts='off',mac_address="aa:bb:cc:dd:ee:ff",skip_reload=False):


    	with fab.settings(warn_only=True):
		if driver=="ath9k":
    			if skip_reload == False:
				fab.run('sudo rmmod ath9k ath9k_common ath9k_hw ath mac80211 cfg80211')
				fab.run('sudo modprobe ath9k')
			else:
				fab.run('iw {0} ibss leave'.format(iface))
			fab.run('sudo iwconfig {0} mode ad-hoc; sudo ifconfig {0} {5} up;sudo iwconfig {0} txpower {3}; sudo iwconfig {0} rate {4}M fixed;sudo iw dev {0} ibss join {1} {2} fixed-freq {6}'.format(iface,essid,freq,txpower,rate,ip_addr,mac_address))
		        fab.run('sudo iwconfig {0} rts {1}'.format(iface,rts))
	
		if driver=="b43":
			
    			if skip_reload == False:
				fab.run('sudo rmmod b43')
				fab.run('sudo modprobe b43 qos=0')
			else:
				fab.run('iw {0} ibss leave'.format(iface))
			fab.run('sudo iwconfig {0} mode ad-hoc; sudo ifconfig {0} {5} up;sudo iwconfig {0} txpower {3}; sudo iwconfig {0} rate {4}M fixed;sudo iw dev {0} ibss join {1} {2} fixed-freq {6}'.format(iface,essid,freq,txpower,rate,ip_addr,mac_address))

@fab.task
@fab.parallel
def stop_wifi(driver):
    with fab.settings(warn_only=True):
	if driver == 'ath9k':
    		fab.run('sudo rmmod ath9k ath9k_common ath9k_hw ath mac80211 cfg80211')
	if driver == 'b43':
    		fab.run('sudo rmmod b43')
@fab.task
@fab.runs_once

#setup network, ad-hoc association
def network(txpower,host_file=''):
	print fab.env.hosts
	print hosts_driver
	for i in range(0,len(fab.env.hosts)):
		driver=hosts_driver[i];
		fab.execute(associate,driver,'wlan0','test',2437,txpower,6,'192.168.0.{0}'.format(i+1),'aa:bb:cc:dd:ee:ff',skip_reload=False,hosts=[fab.env.hosts[i]])


@fab.task
def connectivity_matrix_iperf():

        output = fab.run ("ifconfig  wlan0 | grep 'inet addr:' | cut -d: -f2 | awk '{ print $1}' ");
        i=int(output.split('.',3)[3])
	MAX_RATE=6e6;
        with fab.settings(warn_only=True):
		# RUN IPERF SERVER
		fab.execute(stop_iperf,hosts=[fab.env.host])
		fab.execute(iperf_server_conn_matrix,hosts=[fab.env.host]);

		for j in range(0,len(fab.env.hosts)):
			if fab.env.host != fab.env.hosts[j]:
				if i != int(j+1):
					#RUN IPERF CLIENT
					dst_ip='192.168.0.{0}'.format(i);
					fab.execute(stop_iperf,hosts=[fab.env.hosts[j]])
					fab.execute(iperf_client_conn_matrix,dst_ip,0.1,hosts=[fab.env.hosts[j]])
					iperf_output=fab.execute(get_iperf_server_conn_matrix_info,hosts=[fab.env.host])
		fab.execute(stop_iperf,hosts=[fab.env.host])
		iperf_output=iperf_output[iperf_output.keys()[0]]
		for line in iperf_output.splitlines():
			if re.search( dst_ip, line):
				iperf_stat=line.split(',',line.count(',')-1)
				j=int(iperf_stat[3].split('.',3)[3])
				if i != j:
					print "i={0} j={1}".format(i,j);
					conn_matrix[int(i)-1][int(j)-1]=float(iperf_stat[8])/MAX_RATE;
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

@fab.task
def get_iperf_server_conn_matrix_info():
    with fab.settings(warn_only=True):
	output=fab.run('cat /tmp/iperf.out')
	return output

@fab.task
def iperf_client_conn_matrix(server, duration,src_rate=100e6):
    fab.run('nohup iperf -i 1 -c {0} -u -t {1} -b {2} &> /dev/null &'.format(server, duration,src_rate),pty=False)

def start_iperf_server(trialnum,tx_id,rx_id, iperf_port):
    print 'mkdir -p ~/REACT80211/data/';
    fab.run('mkdir -p ~/REACT80211/data');
    fab.run('nohup iperf -i 1 -s -u -p {4} -y C > ~/REACT80211/data/{0}-{1}-{2}-{3}.csv  < /dev/null &'.format(datetime.date.today(),tx_id.lower(),rx_id.lower(),trialnum,iperf_port), pty=False)

@fab.task
@fab.parallel
def stop_iperf():
    with fab.settings(warn_only=True):
        fab.run('killall -9 iperf')


@fab.task
def run_iperf_client(server, duration,iperf_port):
    fab.run('nohup iperf -c {0} -u -t {1} -b 6000000 -p {2} >  /dev/null &'.format(server, duration,iperf_port),pty=False)

@fab.task
@fab.runs_once
def run_trial(trialnum):
    fab.execute(stop_iperf)

    fab.local('sleep 3')
    hn=[];
    for h in fab.env.hosts: 
	h=h.split('.',1)[0]
	hn.append(h)
    fab.execute(start_iperf_server,trialnum, hn[0],hn[1], 50012, hosts=[fab.env.hosts[1]])
    fab.execute(start_iperf_server,trialnum, hn[2],hn[1], 50032, hosts=[fab.env.hosts[1]])
    fab.execute(start_iperf_server,trialnum, hn[1],hn[0], 50021, hosts=[fab.env.hosts[0]])
   
    fab.local('sleep 3')
    fab.execute(run_iperf_client, '192.168.0.2', 60, 50012, hosts=[fab.env.hosts[0]])
    fab.execute(run_iperf_client, '192.168.0.2', 60, 50032, hosts=[fab.env.hosts[2]])
    fab.execute(run_iperf_client, '192.168.0.1', 60, 50021, hosts=[fab.env.hosts[1]])
    fab.local('sleep 60')
    fab.execute(stop_iperf)


@fab.task

@fab.task
def sync_date():
    controller_time=fab.local('echo $(date +%T)',capture=True)
    #fab.local('echo {0}'.format(controller_time))
    fab.run('date +%T -s {0}'.format(controller_time))

#@fab.task
#def get_node_list(node_file):
#	outlist=fab.local('node_list=$(val=$(cat {0}); echo $val | sed "s/ /,/g"); echo $node_list'.format(node_file))
#	print outlist
	
