import sys
import zmq

port = "5562"
if len(sys.argv) > 1:
    port =  sys.argv[1]
    int(port)
    
if len(sys.argv) > 2:
    port1 =  sys.argv[2]
    int(port1)

# Socket to talk to server
context = zmq.Context()
socket = context.socket(zmq.SUB)

socket.connect ("tcp://localhost:%s" % port)

if len(sys.argv) > 2:
    socket.connect ("tcp://localhost:%s" % port1)

#topicfilter = b""
topicfilter = b"PacketLossAverageEvent"
socket.setsockopt(zmq.SUBSCRIBE, topicfilter)

# Process 5 updates
while True:
    string = socket.recv()
    print(string)
