__author__ = "Peter Ruckebusch"
__copyright__ = "Copyright (c) 2016, Ghent University, iMinds"
__version__ = "0.1.0"

# Definition of Local Control Program that is in place for generating wifi interference.


def wifi_interference_ap(control_engine):
    # do all needed imports here!!!
    import gevent
    import subprocess
    print(("local monitor cp  - Name: {}, Id: {} - Started".format(control_engine.name, control_engine.id)))
	subprocess.call(['sudo','bash','./contiki_helpers/startAP.sh'])
	gevent.sleep(5)
	subprocess.call(['/usr/bin/screen','-h','1000','-dmS','80211acIPerf','/usr/bin/iperf','-s','-i','1','-u'])
	gevent.sleep(60)
	subprocess.call(['sudo','killall','iperf'])
	subprocess.call(['sudo','killall','hostapd'])
	gevent.sleep(5)
    print(("local monitor cp  - Name: {}, Id: {} - STOPPED".format(control_engine.name, control_engine.id)))
