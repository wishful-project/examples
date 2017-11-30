#!/usr/bin/env python2
'''Utilities for performing Metamac experiments.
Requires Python 2.X for Fabric.
Author: Domenico Garlisi and Alice Lo Valvo
'''

'''

USRP su hendrix

$ ssh fabrizio@hendrix.local
$ cd /home/fabrizio/work/flex5gware/5gppp_rome/srsLTE/

per avviare tutto bisogna lanciare:
$ sh run_enb.sh

e poi anche far partire un iperf client:

$ iperf -c 127.0.0.1 -p 2000 -i 1 -t 100000

si dovrebbero vedere sul canale 6ms di traffico e 4ms di idle 


WMP setup

setu-up network
fab -f fab_wmp_lte.py -u root -H alix02,alix03 setup_testbed:alix02

create network
fab -f fab_wmp_lte.py -u root -H alix02,alix03 network:alix02

load correct radio program
fab -f fab_wmp_lte.py -u root -H alix03 load_active_radio_program

run traffic
fab -f fab_wmp_lte.py -u root -H alix02 start_iperf_server
fab -f fab_wmp_lte.py -u root -H alix03 start_iperf_client:alix02,60000,10M
fab -f fab_wmp_lte.py -u root -H alix03,alix02 stop_iperfd

usare il bytecode-manager per settare la maschera del TDMA wmp
ad ogni bit corrisponde uno slot da un millisecondo del frame da 10ms
1 = slot pieno (WIFI presente)
0 = slot vuoto (WIFI non presente)
bytecode-manager --set-tdma-mask 1100110011


'''

import os
import os.path
import datetime
import random

import fabric.api as fab
import fabric.utils
from StringIO import StringIO
import json
import time
import numpy

import socket
import subprocess
import sys

DEFAULT_MAC = 'tdma-4.txt'
demo_dir='~/work/demo-mobicom/rxagile'

def shift(l,n):
        return l[n:] + l[:n]
def get_last_psucc(psucc_list,L,est_slot):

	mask=""
	for x in psucc_list:
		if x > 0.5:
			maskval=1
		elif numpy.isinf(x):
			maskval=0
		else:
			maskval=0
		mask="{}{}".format(mask,maskval)

	mask_int = [ int(x) for x in list(mask)]
        mask_sum=0
        n_shift=0
        for x in list(mask_int):
                mask_sum+=x

        target_mask= [1]*mask_sum + [0]*(L-mask_sum)

        while n_shift < L:
                if mask_int != target_mask:
                        mask_int=shift(mask_int,-1)
                        psucc_list=shift(psucc_list,-1)
                        n_shift=n_shift+1;
                else:
                        break;
	psucc=psucc_list[mask_sum-1]
	return psucc;

def update_pattern(mask_int,L,est_slot):
        mask_sum=0
        n_shift=0
        for x in list(mask_int):
                mask_sum+=x

        target_mask= [1]*mask_sum + [0]*(L-mask_sum)
        print "target_mask={}".format(target_mask)
        print "mask_int={}".format(mask_int)

        while n_shift < L:
                if mask_int != target_mask:
                        mask_int=shift(mask_int,-1)
                        n_shift=n_shift+1;
                else:
                        break;

        if n_shift < L:
                if mask_sum < est_slot and est_slot < L:
                        print "---------"
                        print mask_int
                        print mask_sum
                        print est_slot
                        print "---------"

                        for i_mask in range(mask_sum,est_slot):
                                print i_mask
                                mask_int[i_mask]=1

                print n_shift
                mask_int=shift(mask_int,n_shift-(mask_sum-est_slot))
        print "mask_int={}".format(mask_int)
        return mask_int



@fab.task
@fab.runs_once
def check_all_hosts(interface):
    hosts = ['alix{0}'.format(i) for i in xrange(1, 21)]
    with fab.settings(skip_bad_hosts=True, abort_on_prompts=True):
        results = fab.execute(check_host, interface, hosts=hosts)
    print '== RESULTS =='
    for host, has_interface in results.iteritems():
        if has_interface == True:
            print '{0} has {1}'.format(host, interface)
    print '== END RESULTS =='

@fab.task
def check_host(interface):
    with fab.settings(warn_only=True):
        try:
            return fab.run('ip link show | grep {0}'.format(interface)).succeeded
        except SystemExit: # Hack to effect skip-on-prompt using abort-on-prompt setting provided by Fabric.
            return False

'''
BROADCOM MANAGMENT
'''

@fab.task
@fab.runs_once
def load_all_b43():
    hosts = ['alix{0}'.format(i) for i in xrange(1, 21)]
    with fab.settings(skip_bad_hosts=True, abort_on_prompts=True):
        fab.execute(load_b43, hosts=hosts)

@fab.task
def load_b43():
    try:
        fab.run('modprobe b43')
    except SystemExit: # Hack to effect skip-on-prompt using abort-on-prompt setting provided by Fabric.
        pass

'''
TESTBED MANAGMENT
'''
@fab.task
#@fab.parallel
@fab.runs_once
def setup_testbed(ap_node,fw_dir):
    fab.execute(copy_open_fw, hosts=[h for h in fab.env.hosts if h.split('@')[-1] == ap_node],fw_dir=fw_dir)
    #fab.execute(copy_open_fw, hosts=[h for h in fab.env.hosts if h.split('@')[-1] != ap_node])
    fab.execute(copy_wmp_fw, hosts=[h for h in fab.env.hosts if h.split('@')[-1] != ap_node],fw_dir=fw_dir)

@fab.task
@fab.runs_once
#@fab.parallel
def copy_open_fw(fw_dir):
    #fab.put(local_path='../../wmp-firmware/openfwwf-5.2/*.fw', remote_path='/lib/firmware/b43/' );
    #fab.put(local_path='WMP/openfwwf-5.2/*.fw', remote_path='/lib/firmware/b43/' );
    fab.put(local_path='{}/openfwwf-5.2-tsf-drift/*.fw'.format(fw_dir), remote_path='/lib/firmware/b43/' );
    fab.put(local_path='{}/bytecode-manager-v2.52.1/src/bytecode-manager'.format(fw_dir), remote_path='/bin/' );

@fab.task
@fab.runs_once
#@fab.parallel
def copy_wmp_fw(fw_dir):
    #fab.put(local_path='../../wmp-firmware/wmp3-2.47/*.fw', remote_path='/lib/firmware/b43/' );
    #fab.put(local_path='./openfwwf-5.2/*.fw', remote_path='/lib/firmware/b43/' );
    fab.put(local_path='{}/wmp3-2.47/*.fw'.format(fw_dir), remote_path='/lib/firmware/b43/' );
    #fab.put(local_path='./WMP//bytecode-manager-v2.52/src/bytecode-manager', remote_path='/bin/' );
    fab.put(local_path='{}/bytecode-manager-v2.52.1/src/bytecode-manager'.format(fw_dir), remote_path='/bin/' );
    fab.put(local_path='{}/sm/wmp-lte'.format(fw_dir), remote_path='/root/' );
    
'''
NETWORK MAMAGMENT
'''
WIFI_CHANNEL=11
@fab.task
@fab.runs_once
def network(ap_node, channel=WIFI_CHANNEL):
    fab.execute(start_ap, hosts=[h for h in fab.env.hosts if h.split('@')[-1] == ap_node],channel=channel)
    fab.execute(associate, hosts=[h for h in fab.env.hosts if h.split('@')[-1] != ap_node])

@fab.task
def start_ap(channel):
    #fab.run('ifconfig wlan0 192.168.0.$(hostname | grep -Eo [0-9]+) netmask 255.255.255.0 up')
    #load_mac(mac)
    with fab.settings(warn_only=True):
        fab.run('killall -9 hostapd')
    with fab.cd('work/association'):
        fab.run('if ! grep basic_rates=60 hostapd.conf; then echo "basic_rates=60" >> hostapd.conf; fi')
        #fab.run('if ! grep basic_rates=20 hostapd.conf; then echo "basic_rates=20" >> hostapd.conf; fi')
        fab.run('if ! grep "supported_rates=20 55 60 90 110 120 180 240 360 480 540" hostapd.conf; then echo "supported_rates=20 55 60 90 110 120 180 240 360 480 540" >> hostapd.conf; fi')
        
        fab.run("sed -i 's/macaddr_acl=1/macaddr_acl=0/' hostapd.conf")
        #fab.run("sed -i 's/channel=11/channel=6/' hostapd.conf")
#        fab.run("sed -i 's/channel=/c\channel=11/' hostapd.conf")
	fab.run("sed -i '/channel=/c\channel={}' hostapd.conf".format(channel))
        fab.run("sed -i 's/ssid=alix-ap/ssid=wmp-lte-ap/' hostapd.conf")
        fab.run("sed -i 's/wme_enabled=1/wme_enabled=0/' hostapd.conf")
    #   fab.run("sed -i 's/#hw_mode=b/hw_mode=b/' hostapd.conf")
    #   fab.run("sed -i 's/hw_mode=g/#hw_mode=g/' hostapd.conf")
        
    # Must not be prefixed with cd work/association or else the cd will interfere with nohup.
    fab.run('nohup work/association/up-hostapd.sh work/association/hostapd.conf 192.168.0.$(hostname | grep -Eo [0-9]+) >& hostapd.log < /dev/null &', pty=False)
    fab.run('sleep 2')
    fab.run('iwconfig wlan0 rate 6M fixed')
    fab.run('iwconfig wlan0 txpower 20dbm fixed')
    #load_mac(mac)

@fab.task
@fab.parallel
def associate():
    #fab.run('scp ~/toco/wmp-engine/*.fw /lib/firmware/b43/')
    #load_mac(mac)
    with fab.settings(warn_only=True):
	fab.run('killall -9 hostapd')
	fab.run('rmmod b43')
    fab.run('modprobe b43 qos=0')
    fab.run('ifconfig wlan0 192.168.0.$(hostname | grep -Eo [0-9]+) netmask 255.255.255.0')
    #fab.run('iwconfig wlan0 rate 24M fixed')
    fab.run('iwconfig wlan0 rate 6M fixed')
    fab.run('iwconfig wlan0 txpower 20dbm fixed')
    fab.run('iwconfig wlan0 essid wmp-lte-ap')
    
    fab.run('sleep 2')
    result = fab.run('iwconfig wlan0 | grep Access | awk \'{ print $4 }\';')
    attempts = 0
    while 'Not-Associated' in result and attempts < 10:
        fab.run('iwconfig wlan0 essid wmp-lte-ap')
        fab.run('sleep 1')
        result = fab.run('iwconfig wlan0 | grep Access | awk \'{ print $4 }\';')
        fab.run('sleep 2')
        attempts += 1
    if attempts >= 10:
        fabric.utils.abort('Could not associate node {0} with access point.'.format(fab.env.host_string))
	
'''
RADIO PROGRAM MANAGMENT
'''
@fab.task
@fab.parallel
def load_active_radio_program(mac='TDMA_LTE_3.txt'):
    '''Loads the given MAC protocol onto the WMP firmware. Paths are relative to the
    '''
    fab.run('bytecode-manager -l 2 -m ~/wmp-lte/{0}'.format(mac))
    fab.run('sleep 2')
    fab.run('bytecode-manager -a 2')


@fab.task
def setup(bw=20,channel=6):
	with fab.settings(
		#fab.hide('warnings', 'running', 'stdout', 'stderr'),
		fab.hide('stderr'),
		warn_only=True
	):
		
	#if True:
		channel=6
		bw=20
		fab.run('rm -rf /root/rxagile_cmd/bytecode-warp/')
		fab.put('{}/rxagile_cmd'.format(demo_dir))
		fab.run('dpkg -i /root/rxagile_cmd/*.deb')
		with fab.cd('/root/rxagile_cmd/bytecode-warp'):
			fab.run('make')
			fab.run('./bytecode-warp -e')
			#fab.run('./bytecode-warp -w warp1 -f {}'.format(channel))
			#fab.run('./bytecode-warp -w warp1 -b {}'.format(bw))
		with fab.cd('/root/rxagile_cmd/'):
			fab.run('gcc sendRawEth.c -o sendRawEth')
		fab.run("ifconfig eth1 192.168.2.$(hostname | grep -Eo [0-9]+)")
		#fab.run("ping 192.168.2.1 & sleep 2; killall ping")
		#fab.run("ping 192.168.2.11 & sleep 2; killall ping")
		#fab.run("ping 192.168.2.9 & sleep 2; killall ping")
		fab.run("ping -b 192.168.2.255 > /dev/null 2>&1 & sleep 0.1; killall ping > /dev/null 2>&1")

		#ARP
		fab.local("sh {}/rxagile_cmd/bytecode-warp/arp_set_cmd.sh ".format(demo_dir))
		
	
@fab.task
@fab.parallel
def setChannel(channel):
	with fab.settings(
		fab.hide('warnings', 'running', 'stdout', 'stderr'),
		#fab.hide('stderr'),
		warn_only=True
	):
		with fab.cd('/root/rxagile_cmd/bytecode-warp'):
			fab.run("kill -9 $(ps aux | grep bytecode-warp | grep bytecode-warp | awk '{ print $2 }')")
			fab.run('./bytecode-warp -w warp1 -f {}'.format(channel))

@fab.task
@fab.parallel
def setTxGain(gain):
	with fab.settings(
		#fab.hide('warnings', 'running', 'stdout', 'stderr'),
		fab.hide('stderr'),
		warn_only=True
	):
		with fab.cd('/root/rxagile_cmd/bytecode-warp'):
			fab.run("kill -9 $(ps aux | grep bytecode-warp | grep bytecode-warp | awk '{ print $2 }')")
			fab.run('./bytecode-warp -w warp1 -x {}'.format(gain))
@fab.task
@fab.parallel
def setCCA(cca):
	with fab.settings(
		#fab.hide('warnings', 'running', 'stdout', 'stderr'),
		fab.hide('stderr'),
		warn_only=True
	):
		with fab.cd('/root/rxagile_cmd/bytecode-warp'):
			fab.run("kill -9 $(ps aux | grep bytecode-warp | grep bytecode-warp | awk '{ print $2 }')")
			fab.run('./bytecode-warp -w warp1 -g {}'.format(cca))
@fab.task
@fab.parallel
def sendPing(ip_dest):
	with fab.settings(
		#fab.hide('warnings', 'running', 'stdout', 'stderr'),
		fab.hide('stderr'),
		warn_only=True
	):
		fab.run("ping -b {} -w 2".format(ip_dest))
@fab.task
@fab.parallel
def setBW(bw):
	with fab.settings(
		#fab.hide('warnings', 'running', 'stdout', 'stderr'),
		fab.hide('stderr'),
		warn_only=True
	):
		with fab.cd('/root/rxagile_cmd/bytecode-warp'):
			fab.run("kill -9 $(ps aux | grep bytecode-warp | grep bytecode-warp | awk '{ print $2 }')")
			fab.run('./bytecode-warp -w warp1 -b {}'.format(bw))


@fab.task
@fab.parallel
def get_bw_stats():
	UNIX_OUT='/tmp/preamble_stats'

	with fab.settings(
		fab.hide('warnings', 'running', 'stdout', 'stderr'),
		#fab.hide('stderr'),
		warn_only=True
	):
		with fab.cd('/root/rxagile_cmd/bytecode-warp'):
			ret = fab.run("sh get_bw_counter.sh") 

			if ret != "":
				if os.path.exists(UNIX_OUT):
					try:
						client = socket.socket( socket.AF_UNIX, socket.SOCK_DGRAM )
						client.connect(UNIX_OUT)
						out="0"
						client.send(str(ret))
						client.close()
					except Exception, e:
						print e


@fab.task
@fab.parallel
def setup_local(branch='metamac', get_src=True,firmware_branch=None, debug=False):

    '''Sets up the node by downloading the specified branch or commit and extracting necessary
    files, installing the WMP firmware, and building needed tools.
    '''

    if firmware_branch is None:
        firmware_branch = branch
    if get_src:
        with fab.cd('/tmp'):
            fab.run('rm -f *.deb')
            fab.run('wget http://security.ubuntu.com/ubuntu/pool/main/libx/libxml2/libxml2_2.9.1+dfsg1-3ubuntu4_i386.deb')
            fab.run('wget http://security.ubuntu.com/ubuntu/pool/main/libx/libxml2/libxml2-dev_2.9.1+dfsg1-3ubuntu4_i386.deb')
            fab.run('dpkg -i *.deb')
            fab.run('rm -f *.deb')

        fab.run('rm -rf metamac && mkdir metamac')
        with fab.cd('metamac'):
            wmp_dir='wireless-mac-processor-{0}/'.format(branch)
            fab.run('mkdir {0} && mkdir {0}/wmp-injection'.format(wmp_dir))
            fab.put(local_path='git/wireless-mac-processor/wmp-injection/*',remote_path='wireless-mac-processor-{0}/wmp-injection/'.format(branch));
		
        fab.run('mkdir {0}/mac-programs && mkdir {0}/mac-prorams/metaMAC-program/'.format(wmp_dir))
        fab.put(local_path='git/wireless-mac-processor/mac-programs/metaMAC-program/*',remote_path='wireless-mac-processor-{0}/mac-programs/metaMAC-program/'.format(branch) );


    fab.put(local_path='git/meta-MAC/wmp-firmware/wmp3-2.28/*.fw',remote_path='/lib/firmware/b43/')
    with fab.settings(warn_only=True):
        fab.run('rmmod b43')
    fab.run('sleep 1')
    fab.run('modprobe b43 qos=0')
    fab.run('sleep 1')

    with fab.cd('~/metamac/wireless-mac-processor-{0}/wmp-injection/bytecode-manager/'.format(branch)):
        if debug:
            fab.run("sed -i 's/CFLAGS=/CFLAGS=-g /' Makefile")
            fab.run("sed -i 's/-O[0-9]/ /' Makefile")
        fab.run('make bytecode-manager')
        fab.run('make metamac')
        fab.run('make tsfrecorder')
        fab.run('cp -f bytecode-manager ~/metamac/')
        fab.run('cp -f metamac ~/metamac/')
        fab.run('cp -f tsfrecorder ~/metamac/')

@fab.task
@fab.parallel
def reboot():
    fab.reboot()

def ap_ify(path):
    root, ext = os.path.splitext(path)
    return root + '.ap' + ext

def on_node(node):
    return fab.env.host_string.split('@')[-1] == node

@fab.task
def load_mac(mac, ap_node=None):
    '''Loads the given MAC protocol onto the WMP firmware. Paths are relative to the
    mac-programs/metaMAC-program directory
    '''

    if on_node(ap_node):
        mac = ap_ify(mac)
    fab.run('metamac/bytecode-manager -l 1 -m ~/metamac/wireless-mac-processor-*/mac-programs/metaMAC-program/{0}'.format(mac))
    fab.run('metamac/bytecode-manager -a 1')


'''
STATISTICS MANAGEMENT
'''
#@fab.task
#@fab.parallel
#def run_read_statistics():
    #WARNING - do not work
    #the script start, but the output files keep empty
    #fab.run('nohup python ~/toco/wmp_read_statistics/read_tx_statistics.py > wmp_statistics_log.out 2> wmp_statistics_log.err < /dev/null &', pty=False)
    

@fab.task
@fab.parallel
def stop_read_statistics(trialnum):

    #with fab.settings(warn_only=True):
    #    fab.run("kill $(ps aux | grep '[p]ython /root/toco/wmp_read_statistics/read_tx_statistics.py' | awk '{print $2}')")
    
    fab.local('mkdir -p data')
    localname = 'data/{0}-wmp_statistics_log-{1}-{2}.csv'.format(datetime.date.today(), fab.env.host_string.split('@')[-1], trialnum)
    with fab.settings(warn_only=True):
    #fab.run('cat iperf.out | grep "0,-" | grep -v nan > iperf2.out')
        fab.get(remote_path='wmp_statistics_log.csv', local_path=localname)
        #fab.get(remote_path='iperf2.out', local_path=localname_f)
	#fab.run('rm iperf2.out')


'''
IPERF TRAFFIC MANAGEMENT
'''
@fab.task
def start_iperf_server(gui_server,gui_port,iperf_port,type_id):

    stop_iperf_server(iperf_port)
    #cmd_iperf="nohup python /root/iperf_server.py -s {} -p {} -i {} -t {} > /dev/null 2>&1 &".format('10.8.19.1',10001,2001,'iperf_warp1')
    cmd_kill_server="kill -9 $(ps aux | grep iperf_server | grep " + iperf_port + " | awk {'print $2'})" 
    cmd_kill_iperf="kill -9 $(ps aux | grep iperf | grep " + iperf_port + " | awk '{print $2}') "
    cmd_iperf="nohup python /root/rxagile_cmd/iperf_server.py -s {} -p {} -i {} -t {} > /dev/null 2>&1 &".format(gui_server,gui_port,iperf_port,type_id)
    print cmd_iperf
    fab.run(cmd_iperf,pty=False)

@fab.task
def start_iperf_client(ip_dest, server_host, iperf_port,duration, bw):
#    fab.run('iperf -c 192.168.0.$(echo {0} | grep -Eo [0-9]+) -p 12345 -u -t {1} -b {2} -l500B'.format(server, duration, bw))
    #stop_iperf(iperf_port)
    #ip_dest=ip_dest+'{0:02d}'.format(int(server_host.replace('alix', '')))
    iperf_cmd='nohup iperf -c {} -p {} -u -t {} -b {} > /dev/null 2>&1 &'.format(ip_dest, iperf_port, duration, bw)
    print iperf_cmd
    fab.run(iperf_cmd,pty=False)

@fab.task
@fab.parallel
def start_raw_interf():
    raw_cmd="nohup /root/rxagile_cmd/sendRawEth > /dev/null 2>&1 &"
    print raw_cmd
    fab.run(raw_cmd,pty=False)

@fab.task
@fab.parallel
def stop_raw_interf():
    raw_cmd="killall -9 /root/rxagile_cmd/sendRawEth"
    print raw_cmd 
    fab.run(raw_cmd,pty=False)


@fab.task
def start_iperf_server_nolog(iperf_port):
    stop_iperf(iperf_port)
    cmd_iperf="nohup iperf -s -p {} -u > /dev/null 2>&1 &".format(iperf_port)
    print cmd_iperf
    fab.run(cmd_iperf,pty=False)


@fab.task
@fab.parallel
def stop_iperf_server(iperf_port):
    with fab.settings(warn_only=True):
	cmd_kill_server="kill -9 $(ps aux | grep iperf_server | grep " + iperf_port + " | awk {'print $2'})"
	cmd_kill_iperf="kill -9 $(ps aux | grep iperf | grep " + iperf_port + " | awk '{print $2}')"
        fab.run(cmd_kill_server)
	fab.run(cmd_kill_iperf)
@fab.task
@fab.parallel
def stop_iperf(iperf_port):
    with fab.settings(warn_only=True):
	cmd_kill_iperf="kill -9 $(ps aux | grep iperf | grep " + iperf_port + " | awk '{print $2}') > /dev/null 2>&1 "
	print cmd_kill_iperf
        fab.run(cmd_kill_iperf)



@fab.task
@fab.parallel
def stop_hostapd():
    with fab.settings(warn_only=True):
        fab.run('killall -9 hostapd')

@fab.task
@fab.parallel
def stop_wifi():
    with fab.settings(warn_only=True):
        fab.run('rmmod b43')

@fab.task
@fab.parallel
def run_iperf_dyn_client(server, duration,bw):
    sleep_dur=duration/len(bw)
    cmd=''
    dur=duration
    for i in range(len(bw)-1):
        cmd+='nohup iperf -c 192.168.0.$(echo {0} | grep -Eo [0-9]+) -u -t {1} -b {2} & sleep {3};'.format(server, dur,bw[i],sleep_dur)
        dur-=sleep_dur
    cmd+='iperf -c 192.168.0.$(echo {0} | grep -Eo [0-9]+) -u -t {1} -b {2}'.format(server,dur,bw[len(bw)-1])
    fab.run(cmd)


'''
TIME MANAGEMENT
'''
@fab.task
def sync_date():
    controller_time=fab.local('echo $(date +%T)',capture=True)
    #fab.local('echo {0}'.format(controller_time))
    fab.run('date +%T -s {0}'.format(controller_time))

@fab.task
@fab.runs_once
def stop_all():
    fab.execute(stop_wifi)
    fab.execute(kill_metamac)
    fab.execute(stop_iperf)
    fab.execute(stop_hostapd)



def ror(val, r_bits):
	r = lambda val, r_bits, max_bits: \
	    ((val & (2**max_bits-1)) >> r_bits%max_bits) | \
	    (val << (max_bits-(r_bits%max_bits)) & (2**max_bits-1))
	return r


@fab.task
def shm_reader():
	with fab.settings(
		fab.hide('warnings', 'running', 'stdout', 'stderr'),
		warn_only=True
	):
		command = 'bytecode-manager -x 2 | grep -e 0x00D -e 0x00E -e 0x00F'
		output = fab.run(command)
		output=output.replace(":", " ")
		output=output.replace("\t", "")
		output=output.replace("\n", "")
		output=output.replace("\r", "")
		output=output.split(" ")
		output=[x for x in output if 'x' not in x]
		pos=4
		tx_count=[]
		rx_ack_count=[]
		for i in range(0,10):
			val=output[i+4]
			hex_val="0x{}{}".format(val[2:4],val[0:2]);
			val=int(hex_val,16)
			tx_count.append(val)
			val=output[i+14]
			hex_val="0x{}{}".format(val[2:4],val[0:2]);
			val=int(hex_val,16)
			rx_ack_count.append(val)
		tx_count=[float(i) for i in tx_count]
		rx_ack_count=[float(i) for i in rx_ack_count]
		tx_count=numpy.array(tx_count)
		rx_ack_count=numpy.array(rx_ack_count)
		print tx_count
		print rx_ack_count

	return [tx_count,rx_ack_count]

@fab.task
def killControllerLTE():
	mask="1111111111"
	with fab.hide('output','running','warnings'), fab.settings(warn_only=True):
		fab.run('bytecode-manager --set-tdma-mask {}'.format(mask))

@fab.task
def getLTEstats():
	while True:
		with fab.hide('output','running','warnings'), fab.settings(warn_only=True):
			fab.get(remote_path="/tmp/lte_ue.json", local_path="/tmp/lte_ue.json")
		time.sleep(1)
"""
@fab.task
def syncAP():
	while True:
		try:
			fp=open('/tmp/lte_ue.json','r')
			lines = fp.readlines()
			if lines:
				first_line = lines[:1]
				last_line = lines[-1]

			print last_line
			stats = json.loads(last_line)
			bler = float(stats.get('PDSCH-BLER'))
			print bler
			val=0
			#if bler > 50 :
			#	val=2000
			#elif bler > 30 :
			#	val=1000
			if bler > 10:
				val=100
			elif bler > 5:
				val=50
			if bler > 5:
				print val
				fab.run('bytecode-manager --set-tsf {}'.format(val))
		except Exception: # Hack to effect skip-on-prompt using abort-on-prompt setting provided by Fabric.
			print "ops!"
		time.sleep(2)
		fp.close()
"""
@fab.task
def syncAP(psucc_thresh=0.75):
	psucc_=0;
	while True:
		try:
			fp=open('/tmp/controllerLTE.log','r')
			lines = fp.readlines()
			if lines:
				first_line = lines[:1]
				last_line = lines[-1]

#			print last_line
			stats = json.loads(last_line)
			psucc = float(stats.get('psucc'))
			mask_sum= float(stats.get('mask_sum'))
			psucc_list= stats.get('psucc_list')
			psucc=get_last_psucc(psucc_list,10,4)
			if numpy.isnan(psucc):
				psucc=float(0);
			from scipy.signal  import butter, lfilter, tf2ss 
			#alpha=0.5
			#psucc_=alpha*psucc+(1-alpha)*psucc_
			#psucc=psucc_

			val=0
#			if psucc < 0.65:
#				val=100
#			if psucc < 0.75:
#				val=200
#			if psucc < 0.85:
			if (mask_sum < 4) or (psucc < float(psucc_thresh)):
				val=10
#			elif psucc < 0.85:
#				val=50
			if val != 0:
				with fab.hide('output','running','warnings'), fab.settings(warn_only=True):
					fab.run('bytecode-manager --set-tsf {}'.format(val))
			print "mask_sum={} psucc={} drift={} psucc_thresh={}".format(mask_sum,psucc,val,psucc_thresh)
		except Exception: # Hack to effect skip-on-prompt using abort-on-prompt setting provided by Fabric.
			print "ops!"
		time.sleep(0.1)
		fp.close()
@fab.task
def controllerLTE(enable_controller=1):
	fh = StringIO();
	[tx_count_,rx_ack_count_]=shm_reader();
	count_round=0
	fp=open('/tmp/controllerLTE.log','w')

	if enable_controller=='2':
		with fab.hide('output','running','warnings'), fab.settings(warn_only=True):
			fab.run('bytecode-manager -a 1')
	else:
		print "ENABLE TDMA"
		with fab.hide('output','running','warnings'), fab.settings(warn_only=True):
			fab.run('bytecode-manager -a 2')
			fab.run('bytecode-manager --set-tdma-mask 1111111111')
	while True:
		count_round=count_round+1
		[tx_count,rx_ack_count]=shm_reader();
		dtx=numpy.mod(tx_count-tx_count_,0xFFFF)
		dack=numpy.mod(rx_ack_count-rx_ack_count_,0xFFFF)
		tx_count_=tx_count
		rx_ack_count_=rx_ack_count
		psucc=numpy.divide(dack,dtx)

		for i in range(0,len(psucc)):
			if numpy.isinf(psucc[i]):
				psucc[i]=0;
				continue
			if numpy.isnan(psucc[i]):
				psucc[i]=0;
				continue

		psucc_tot=numpy.divide(numpy.sum(dack),numpy.sum(dtx))
		print "rx_ack = {}".format(dack)
		print "tx     = {}".format(dtx)
		numpy.set_printoptions(precision=1)
		print "psucc  = {}".format(psucc)
		print "psucc_tot={}".format(psucc_tot)
		print "count_round={}".format(count_round)
		
		mask=""
		for x in psucc:
			if x > 0.5:
				maskval=1
			elif numpy.isinf(x):
				maskval=0
			else:
				maskval=0

			mask="{}{}".format(maskval,mask)
			mask_int = [ int(x) for x in list(mask)]
		mask_sum=0
		for x in list(mask_int):
			mask_sum+=x

		if mask=="0000000000":
			mask="1111111111"		
		EST_SLOT=4
		L=10
		print mask
		p_insert=numpy.random.rand();
		if mask_sum < EST_SLOT:
			p_insert=1;
			mask_int=update_pattern(mask_int,L,mask_sum+1)
#		else: 
#			p_insert=0
#		if p_insert > 0.01:
#			mask_int=update_pattern(mask_int,L,mask_sum+1)
		mask=""
		for x in mask_int:
			mask="{}{}".format(mask,x)
		#count_round=0
		print mask_int

		if enable_controller=='0':
			mask="1111111111"
		
		if enable_controller == '0' or enable_controller =='1':	
			with fab.hide('output','running','warnings'), fab.settings(warn_only=True):
				fab.run('bytecode-manager --set-tdma-mask {}'.format(mask))
		
		json_msg={ 'time':time.time(), 'psucc':psucc_tot, 'mask':mask,'enable_controller':enable_controller,'mask_sum':mask_sum, 'psucc_list':list(psucc)}
		print json_msg
		fp.write(json.dumps(json_msg))
		fp.write("\n")
		fp.flush()
		time.sleep(1)
	close(fp)


@fab.task
# Ad-hoc node association
#echo "usage $0 <iface> <essid> <freq> <power> <rate> <ip> <mac> <reload[1|0]>"
def adhoc(iface,essid,freq,txpower,rate,ip_addr,mac_address="aa:bb:cc:dd:ee:ff",driver="b43"):

	with fab.settings(warn_only=True):
		if driver=="ath5k":
			fab.run('rmmod ath5k') 
			fab.run('modprobe ath5k')
			fab.run('iwconfig {0} mode ad-hoc; ifconfig {0} {5} up;iwconfig {0} txpower {3}; iwconfig {0} rate {4}M fixed;iw dev {0} ibss join {1} {2} fixed-freq {6}'.format(iface,essid,freq,txpower,rate,ip_addr,mac_address))
	
		if driver=="b43":
			
			fab.run('rmmod b43')
			fab.run('modprobe b43 qos=0')
			#fab.run('iw {0} ibss leave'.format(iface))
			fab.run('iwconfig {0} mode ad-hoc; ifconfig {0} {5} up;iwconfig {0} txpower {3}; iwconfig {0} rate {4}M fixed;iw dev {0} ibss join {1} {2} fixed-freq {6}'.format(iface,essid,freq,txpower,rate,ip_addr,mac_address))
