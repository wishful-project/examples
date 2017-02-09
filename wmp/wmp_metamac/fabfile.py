#!/usr/bin/env python2
'''Utilities for performing Metamac experiments.
Requires Python 2.X for Fabric.
Author: Nathan Flick
Improved: Domenico Garlisi
'''

import os
import os.path
import datetime

import fabric.api as fab
import fabric.utils



''' 
tool usage:

SETUP
def setup_local(get_src=True, debug=False):
fab -u root -H alix02,alix03,alix04,alix05,alix15 setup_local:1,0

NETWORK
fab -u root -H alix02,alix03,alix04,alix05,alix15 network:alix02

METAMAC TDMA
fab -u root -H alix02,alix03,alix04,alix05,alix15 run_trial:tdma-1,tdma-4.xml,alix02,0.25,10.8.8.10
metamac/metamac -l metamac.log metamac/wireless-mac-processor/mac-programs/metaMAC-program/tdma-4.xml -g 10.8.8.6 -v -e 0.25
metamac/metamac metamac/wireless-mac-processor/mac-programs/metaMAC-program/tdma-4.xml -g 10.8.8.6 -v -e 0.25
fab -u root -H alix03,alix04,alix05,alix15 stop_metamac:tdma-1

METAMAC ALOHA
fab -u root -H alix02,alix03,alix04,alix05,alix15 run_trial:tdma-aloha,tdma-aloha_p04.xml,alix02,0.25,10.8.8.10
metamac/metamac -l metamac.log metamac/wireless-mac-processor/mac-programs/metaMAC-program/tdma-aloha_075.xml -g 10.8.8.6 -v -e 0.25
metamac/metamac metamac/wireless-mac-processor/mac-programs/metaMAC-program/tdma-aloha_075.xml -g 10.8.8.6 -v -e 0.25
fab -u root -H alix03,alix04,alix05,alix15 stop_metamac:tdma-aloha-1

METAMAC ALOHA GOOD WORK
fab -u root -H alix02,alix03,alix04,alix05,alix15 run_trial:tdma-aloha,tdma-4-wintech-09.xml,alix02,0.5,10.8.8.10
metamac/metamac -v -g 10.8.8.6  metamac/wireless-mac-processor/mac-programs/metaMAC-program/tdma-4-wintech-09.xml -e 0.5
metamac/metamac -v -g 10.8.8.10  metamac/wireless-mac-processor/mac-programs/metaMAC-program/tdma-4-wintech-09.xml -e 0.5
fab -u root -H alix03,alix04,alix05,alix15 stop_metamac:tdma-aloha

TRAFFIC
fab -u root -H alix02 start_iperf_server:0
fab -u root -H alix03,alix04,alix05,alix15 start_iperf_client:alix02,600,2M,1200
fab -u root -H alix02,alix03,alix04,alix05,alix15 stop_iperf

TRAFFIC
iperf -c 192.168.0.2 -i 1 -t 600 -p 8484 -b 1.5M -l 1200
iperf -s -u -p 8484 -i 1



GOOD WORK
metamac/metamac -v -g 10.8.8.6  metamac/wireless-mac-processor/mac-programs/metaMAC-program/tdma-4-wintech-09.xml -e 0.5

'''



DEFAULT_MAC = 'tdma-4.txt'

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

@fab.task
@fab.parallel
def setup(branch='metamac', get_src=False, firmware_branch=None, debug=False, gituser='fabriziogiuliano'):

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
		fab.run('wget --no-check-certificate github.com/{1}/wireless-mac-processor/archive/{0}.zip'.format(branch,gituser))
		fab.run('unzip {0}.zip "wireless-mac-processor-{0}/wmp-injection/bytecode-manager/*"'.format(branch))
		fab.run('unzip {0}.zip "wireless-mac-processor-{0}/mac-programs/metaMAC-program/*"'.format(branch))
	
		if firmware_branch != branch:
		    fab.run('rm {0}.zip'.format(branch))
		    fab.run('wget --no-check-certificate github.com/{1}/wireless-mac-processor/archive/{0}.zip'.format(firmware_branch,gituser))

		fab.run('unzip {0}.zip "wireless-mac-processor-{0}/wmp-engine/broadcom-metaMAC/*"'.format(firmware_branch))
		fab.run('rm {0}.zip'.format(firmware_branch))
      
    
    with fab.cd('metamac/wireless-mac-processor-{0}/wmp-engine/broadcom-metaMAC/'.format(firmware_branch)):
        fab.run('cp ucode5.fw b0g0bsinitvals5.fw b0g0initvals5.fw /lib/firmware/b43')
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
def setup_local(get_src=True, debug=False):

    '''Sets up the node by downloading the specified branch or commit and extracting necessary
    files, installing the WMP firmware, and building needed tools.
    '''
    
    if get_src:
	    #with fab.cd('/tmp'):
		#fab.run('rm -f *.deb')
		#fab.run('wget http://security.ubuntu.com/ubuntu/pool/main/libx/libxml2/libxml2_2.9.1+dfsg1-3ubuntu4_i386.deb')
		#fab.run('wget http://security.ubuntu.com/ubuntu/pool/main/libx/libxml2/libxml2-dev_2.9.1+dfsg1-3ubuntu4_i386.deb')
		#fab.run('dpkg -i *.deb')
		#fab.run('rm -f *.deb')

	    fab.run('rm -rf metamac && mkdir metamac')
	    with fab.cd('metamac'):
		wmp_dir='wireless-mac-processor';
	    	fab.run('mkdir {0} && mkdir {0}/wmp-injection &&  mkdir {0}/wmp-injection/bytecode-manager'.format(wmp_dir));
		fab.put(local_path='../../wireless-mac-processor/wmp-injection/bytecode-manager/*',remote_path='wireless-mac-processor/wmp-injection/bytecode-manager');
		
	    	fab.run('mkdir {0}/mac-programs && mkdir {0}/mac-programs/metaMAC-program'.format(wmp_dir));
		fab.put(local_path='../../wireless-mac-processor/mac-programs/metaMAC-program/*',remote_path='wireless-mac-processor/mac-programs/metaMAC-program/' );
       
    with fab.cd('~/metamac/wireless-mac-processor/wmp-injection/bytecode-manager/'):
        if debug:
            fab.run("sed -i 's/CFLAGS=/CFLAGS=-g /' Makefile")
            fab.run("sed -i 's/-O[0-9]/ /' Makefile")
        fab.run('make clean')
        fab.run('make bytecode-manager')
        fab.run('make metamac')
        #fab.run('make tsfrecorder')
        fab.run('cp -f bytecode-manager ~/metamac/')
        fab.run('cp -f metamac ~/metamac/')
        #fab.run('cp -f tsfrecorder ~/metamac/')

    #fab.put(local_path='git/meta-MAC/wmp-firmware/wmp3-2.28/*.fw',remote_path='/lib/firmware/b43/');
    fab.put(local_path='../../wireless-mac-processor/wmp-engine/broadcom-metaMAC/v2/*.fw',remote_path='/lib/firmware/b43/');
    
    with fab.settings(warn_only=True):
    	fab.run('rmmod b43')
    fab.run('sleep 0.5')
    fab.run('modprobe b43 qos=0')
    fab.run('sleep 0.5')
    fab.run('ifconfig wlan0 up')
    
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


#MANAGED NETWORK

@fab.task
def start_ap(mac):
    
    with fab.settings(warn_only=True):
    	fab.run('killall -9 hostapd')
    	fab.run('killall -9 metamac')
    fab.run('scp ~/work/openfwwf-5.2/*.fw /lib/firmware/b43/')
    
    with fab.cd('work/association'):
        fab.run('if ! grep basic_rates=60 hostapd.conf; then echo "basic_rates=60" >> hostapd.conf; fi')
        fab.run('if ! grep supported_rates=60 hostapd.conf; then echo "supported_rates=60" >> hostapd.conf; fi')
                
        #fab.run('if ! grep basic_rates=20 hostapd.conf; then echo "basic_rates=20" >> hostapd.conf; fi')
        #fab.run('if ! grep "supported_rates=20 55 60 90 110 120 180 240 360 480 540" hostapd.conf; then echo "supported_rates=20 55 60 90 110 120 180 240 360 480 540" >> hostapd.conf; fi')
        
        fab.run("sed -i 's/macaddr_acl=1/macaddr_acl=0/' hostapd.conf")
        fab.run("sed -i 's/channel=11/channel=6/' hostapd.conf")
        #fab.run("sed -i 's/channel=6/channel=11/' hostapd.conf")

        fab.run("sed -i 's/ssid=alix-ap/ssid=metamac-ap/' hostapd.conf")
        fab.run("sed -i 's/wme_enabled=1/wme_enabled=0/' hostapd.conf")
        
    # Must not be prefixed with cd work/association or else the cd will interfere with nohup.
    fab.run('nohup work/association/up-hostapd.sh work/association/hostapd.conf 192.168.0.$(hostname | grep -Eo [0-9]+) >& hostapd.log < /dev/null &', pty=False)
    fab.run('sleep 2')
    
@fab.task
@fab.parallel
def associate(mac=DEFAULT_MAC):

    #load_mac(mac)
    with fab.settings(warn_only=True):
    	fab.run('killall -9 hostapd')
	fab.run('rmmod b43')
    fab.run('modprobe b43 qos=0')
    fab.run('ifconfig wlan0 192.168.0.$(hostname | grep -Eo [0-9]+) netmask 255.255.255.0')
    fab.run('iwconfig wlan0 essid metamac-ap')
    fab.run('iwconfig wlan0 txpower 15dbm')
    result = fab.run('iwconfig wlan0 | grep Access | awk \'{ print $4 }\';')
    attempts = 0
    while 'Not-Associated' in result and attempts < 10:
        fab.run('iwconfig wlan0 essid metamac-ap')
        fab.run('sleep 1')
        result = fab.run('iwconfig wlan0 | grep Access | awk \'{ print $4 }\';')
        attempts += 1
    if attempts >= 10:
        fabric.utils.abort('Could not associate node {0} with access point.'.format(fab.env.host_string))
    fab.run('iwconfig wlan0 rate 6M fixed')
    #load_mac(mac)

@fab.task
@fab.runs_once
def network(ap_node, mac=DEFAULT_MAC):

    fab.execute(kill_metamac)
    fab.execute(start_ap, ap_ify(mac), hosts=[h for h in fab.env.hosts if h.split('@')[-1] == ap_node])
    fab.execute(associate, mac, hosts=[h for h in fab.env.hosts if h.split('@')[-1] != ap_node])


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



#MANAGED TRAFFIC

@fab.task
def start_iperf_server(logging='1'):
    with fab.settings(warn_only=True):
        fab.run('killall iperf')
    fab.local('sleep 1')
    if logging=='1':
      fab.run('nohup iperf -i 1 -s -u -y C > iperf.out 2> iperf.err < /dev/null &', pty=False)
    else:
      fab.run('nohup iperf -s -u > iperf.out 2> iperf.err < /dev/null &', pty=False)

@fab.task
@fab.parallel
def start_iperf_client(server, duration, bw, length):
    with fab.settings(warn_only=True):
        fab.run('killall iperf')
    fab.run('nohup iperf -c 192.168.0.$(echo {0} | grep -Eo [0-9]+) -u -t {1} -b {2} -l {3} > iperf.out 2> iperf.err < /dev/null &'.format(server, duration, bw, length), pty=False)

@fab.task
@fab.parallel
def start_iperf_dyn_client(server, duration,bw):
	sleep_dur=duration/len(bw)
	cmd='';
	dur=duration
	for i in range(len(bw)-1):
		cmd+='nohup iperf -c 192.168.0.$(echo {0} | grep -Eo [0-9]+) -u -t {1} -b {2} & sleep {3};'.format(server, dur,bw[i], sleep_dur)
		dur-=sleep_dur
	cmd+='iperf -c 192.168.0.$(echo {0} | grep -Eo [0-9]+) -u -t {1} -b {2}'.format(server,dur,bw[len(bw)-1])
	fab.run(cmd);

@fab.task
def stop_iperf_server(trialnum):
    with fab.settings(warn_only=True):
        fab.run('killall iperf')
    fab.local('mkdir -p data')
    localname = 'data/{0}-iperf-{1}-{2}.csv'.format(datetime.date.today(), fab.env.host_string.split('@')[-1], trialnum)
    localname_f = 'data/{0}-iperf_f-{1}-{2}.csv'.format(datetime.date.today(), fab.env.host_string.split('@')[-1], trialnum)
    with fab.settings(warn_only=True):
	fab.run('cat iperf.out | grep "0,-" | grep -v nan > iperf2.out')
        fab.get(remote_path='iperf.out', local_path=localname)
        fab.get(remote_path='iperf2.out', local_path=localname_f)
	fab.run('rm iperf2.out')

@fab.task
@fab.parallel
def stop_iperf():
    with fab.settings(warn_only=True):
        fab.run('killall -9 iperf')



#MANAGED METAMAC

@fab.task
@fab.parallel
def start_metamac(suite, ap_node=None, eta=0.0, remote_logging='10.8.8.6', cycle=False,):
    if on_node(ap_node):
        suite = ap_ify(suite)
    arguments = ''
    if cycle:
        arguments += '-c '
    if eta > 0.0:
        arguments += '-e {0} '.format(eta)
    if remote_logging:
	arguments += '-g {0} '.format(remote_logging)
    if not on_node(ap_node):
	with fab.settings(warn_only=True):
		fab.run('killall -9 metamac');
		#fab.run('~/metamac/bytecode-manager -l1 -m /root/metamac/wireless-mac-processor-aloha/mac-programs/metaMAC-program/dcf_v3-2.txt && ~/metamac/bytecode-manager -a 1')
#		fab.run('~/metamac/bytecode-manager -l1 -m /root/metamac/wireless-mac-processor-aloha/mac-programs/metaMAC-program/aloha-slot-probability-always.txt && ~/metamac/bytecode-manager -a 1')
#		fab.run('killall -9 metamac; nohup metamac/metamac {0} -l metamac.log metamac/wireless-mac-processor/mac-programs/metaMAC-program/{1} > metamac.out 2> metamac.err < /dev/null &'.format(arguments, suite), pty=False)
		fab.run('killall -9 metamac; nohup metamac/metamac {0} metamac/wireless-mac-processor/mac-programs/metaMAC-program/{1} > metamac.out 2> metamac.err < /dev/null &'.format(arguments, suite), pty=False)

@fab.task
@fab.parallel
def kill_metamac():
    with fab.settings(warn_only=True):
    	fab.run('killall -9 metamac')
@fab.task
@fab.parallel
def stop_metamac(trialnum):
    fab.run('sleep 2')
    with fab.settings(warn_only=True):
    	fab.run('killall -9 metamac')
    fab.local('sleep 2')
    localname = 'data/{0}-{1}-{2}.csv'.format(datetime.date.today(), fab.env.host_string.split('@')[-1], trialnum)
    fab.local('mkdir -p data')
    with fab.settings(warn_only=True):
        fab.get(remote_path='metamac.log', local_path=localname)

@fab.task
@fab.runs_once
def pkt_dump(trialnum,action='run'):
    	with fab.settings(warn_only=True):
		fab.local('sudo killall -9 tcpdump')
		fab.local('sudo rmmod ath9k')
	if action=='stop':
		print ":::::::: STOP"
		return True;
	if action=='run':
		fab.local('sudo modprobe ath9k')
		fab.local('sudo rfkill unblock all')
		fab.local('sudo ifconfig wlan0 down; sudo iwconfig wlan0 mode monitor; sudo ifconfig wlan0 up; sudo iwconfig wlan0 channel 6; sudo iwconfig wlan0 rate 6M fixed')
		localname = 'data/{0}-pkt_dump-{1}.csv'.format(datetime.date.today(), trialnum)
		fab.local('mkdir -p data')
		fab.local('sleep 5')
		#fab.local('sudo tcpdump -i wlan0 net 192.168.0.0/24 and dst port 5001 | awk \'{print $2","$14}\' | sed \'s/us//\' > '+localname+'&')
		fab.local('sudo tcpdump -i wlan0 | grep -v Ack | grep -v Beacon | grep \"IP 192.168.0\" | awk \'{print $1","$2","$14}\' | sed \'s/us//\' > '+localname+' &')

@fab.task
def stop_pkt_dump():
    	with fab.settings(warn_only=True):
		fab.local('sudo killall -9 tcpdump')
		fab.local('sudo rmmod ath9k')
	print "PKT_DUMP STOP!!"


@fab.task
@fab.runs_once
def run_trial(trialnum, suite, ap_node, eta, ip_gateway):
    #start iperf traffic server
    #fab.execute(start_iperf_server, hosts=[ap_node])
    
    fab.execute(kill_metamac)
    fab.execute(start_metamac, suite, ap_node, eta, ip_gateway)
    
    #fab.execute(pkt_dump,trialnum)
    
    #src_rate_step=[10e3,190e3,200e3,400e3,6e6]
    ##src_rate_step=[100e3]
    ##src_rate_step=[6e6]
    #exp_duration=30*len(src_rate_step);
    #fab.execute(run_iperf_dyn_client, ap_node, exp_duration,src_rate_step, hosts=[h for h in fab.env.hosts if h.split('@')[-1] != ap_node])
    #fab.local('sleep 120')
    
    #fab.execute(stop_metamac, trialnum)
    
    #fab.execute(stop_iperf_server, trialnum, hosts=[ap_node])
    #fab.execute(stop_iperf)
    
    #fab.execute(stop_pkt_dump)

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

@fab.task
def trial_errors():
    fab.run('cat metamac.err')

