__author__ = "Peter Ruckebusch"
__copyright__ = "Copyright (c) 2016, Ghent University, iMinds"
__version__ = "0.1.0"

# Definition of Local Control Program that is in place for generating wifi interference.


def wifi_interference_ap(control_engine):
    # do all needed imports here!!!
    import gevent
    import subprocess
    started = False
    print(("local ap  - Name: {}, Id: {} - Started".format(control_engine.name, control_engine.id)))
    while control_engine.is_stopped():
        msg = control_engine.recv(block=False)
        if msg is not None and type(msg) is dict:
            if msg['command'] == "start_wifi_interference":
                subprocess.call(['sudo','bash','./contiki_helpers/startAP.sh',msg['wifi_channel']])
                gevent.sleep(5)
                subprocess.call(['/usr/bin/screen','-h','1000','-dmS','80211acIPerf','/usr/bin/iperf','-s','-i','1','-u'])
                started = True
            elif msg['command'] == "stop_wifi_interference":
                subprocess.call(['sudo','killall','iperf'])
                subprocess.call(['sudo','killall','hostapd'])
                started = False
        gevent.sleep(1)
    if started:
        subprocess.call(['sudo','killall','iperf'])
        subprocess.call(['sudo','killall','hostapd'])
    print(("local ap - Name: {}, Id: {} - Started".format(control_engine.name, control_engine.id)))
