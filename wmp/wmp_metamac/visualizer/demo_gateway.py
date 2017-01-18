__author__ = 'domenico'

import random
from socket import *    # import *, but we'll avoid name conflict
from sys import argv, exit
import demjson
import zmq
import time
import subprocess

import json
from thread import start_new_thread

"""

"""

#VISUALIZER
def visualizer_handler(x):
    #setup socket to send information outside the laboratory
    ''' implement message zmq for realtime visualizer '''
    #global socket_visualizer
    port = "8300"
    context = zmq.Context()
    socket_visualizer = context.socket(zmq.PUB)
    socket_visualizer.bind("tcp://*:%s" % port)
    print('start server on 8300 port ... sending protocol information to remote DEMO console')

    #
    # for ii in range(1,999):
    #     msg_data={ "measure" : [1, 2], "ip_address" : ('192.168.0.3') }
    #     msg_data['traffic'] = ii
    #     socket_visualizer.send_json(msg_data)
    #     print('send message %d' % ii)
    #     time.sleep(1)


    #RECEIVE information from nodes
    #setup socket to receive information from nodes inside the laboratory
    port2  = 4321
    ip_address = '10.8.8.10'
    sock = socket(AF_INET, SOCK_DGRAM)
    sock.bind((ip_address,port2))
    while True:    # Run until cancelled
        message, client = sock.recvfrom(256) # <=256 byte datagram
        parsed_json = json.loads(message)
        #{"active" : "0", "0":["0.254", "Aloha (p=0.75)"], "1":["0.175", "TDMA (slot 0)"], "2":["0.198", "TDMA (slot 1)"], "3":["0.198", "TDMA (slot 2)"], "4":["0.175", "TDMA (slot 3)"]}
        #print('1' + str(parsed_json))
        parsed_json['node_ip_address']=client
        #{'node_ip_address': ('10.8.8.104', 58100), u'1': [u'0.057', u'TDMA (slot 1)'], u'0': [u'0.210', u'TDMA (slot 0)'], u'3': [u'0.042', u'TDMA (slot 3)'], u'2': [u'0.057', u'TDMA (slot 2)'], u'4': [u'0.632', u'Aloha (p=0.9)'], u'active': u'4'}
        #print('2' + str(parsed_json) + '\n')

        #send information to visualizer outside the laboratory
        socket_visualizer.send_json(parsed_json)



def main():

    port = "8301"
    context = zmq.Context()
    socket_command = context.socket(zmq.REP)
    socket_command.bind("tcp://*:%s" % port)
    print('start server on 8301 port ... listening command from remote DEMO console')

    node_server_port = 8400
    sock = socket(AF_INET, SOCK_DGRAM)
    print('open socket on port 8400 ... to send command to DEMO nodes')

    while True:
        parsed_json = socket_command.recv_json()
        print('parsed_json : %s' % str(parsed_json))
        time.sleep (0.5)
        socket_command.send("ACK")

        # print(parsed_json['type'])
        # print(parsed_json['command'])
        # print(parsed_json['ip_address'])

        if parsed_json['type']=='protocol':
            print('manage protocol')
            json_command = demjson.encode([parsed_json])
            sock.sendto(json_command, (parsed_json['ip_address'], node_server_port))

        if parsed_json['type']=='traffic':
            print('manage traffic')
            command = parsed_json['command']
            nl_output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)


start_new_thread(visualizer_handler,(99,))
#ho_event(99)

# main loop
main()