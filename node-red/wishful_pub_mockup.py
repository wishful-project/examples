import zmq
import random
import sys
import time
import pickle
import json
import random
import time
from random import randint

current_milli_time = lambda: int(round(time.time() * 1000))

class RadarDetectionEvent:
    def __init__(self):
        self.name = 'RadarDetectionEvent'
        self.ts = current_milli_time()

    def serialize(self):
        as_dict = {'ts': self.ts}
        serialized_dict = json.dumps(as_dict)
        return [self.name, serialized_dict]

class PacketLossEvent:
    def __init__(self, rssi):
        self.name = 'PacketLossEvent'
        self.ts = current_milli_time()
        self.rssi = rssi

    def serialize(self):
        as_dict = {'ts': self.ts, 'rssi': self.rssi}
        serialized_dict = json.dumps(as_dict)
        return [self.name, serialized_dict]


port = "5556"
if len(sys.argv) > 1:
    port =  sys.argv[1]
    int(port)

context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind("tcp://*:%s" % port)

#topics = ['RadarDetectionEvent', 'PacketLossEvent']
topics = ['PacketLossEvent']

while True:

    next_topic = random.choice(topics)
    print('%s' % (next_topic))

    if next_topic == 'RadarDetectionEvent':
        ev = RadarDetectionEvent()
    elif next_topic == 'PacketLossEvent':
        ev = PacketLossEvent(random.randint(0,63))

    mp_msg = ev.serialize()    

    print(mp_msg)

    socket.send_multipart(mp_msg)

    time.sleep(1)
