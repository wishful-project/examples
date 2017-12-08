#! /usr/bin/python2.7
import zmq
import sys
import time
from spectral_acquire import spectral_recorder
import numpy as np
import time
from time import sleep
import math
from operator import itemgetter
import os

port = "8502"
if len(sys.argv) > 1:
    port =  sys.argv[1]
    int(port)


context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind("tcp://*:%s" % port)

#ACQUIRE SPECTRAL SCAN 
filename="/tmp/demo.tlv"


while True:
	sr = spectral_recorder.SpectralRecorder(load=True, offline=False,freq=2437e6)
	sr.acquire(filename,T_acquire=0.4)
	time.sleep(1)
	print "samples acquired"
	msg_size=os.stat(filename).st_size
	print "file size={}".format(msg_size)
	target = open(filename, 'rb')
	spectral_raw = target.read(msg_size)
	target.close()

	socket.send(spectral_raw)
	time.sleep(2)
