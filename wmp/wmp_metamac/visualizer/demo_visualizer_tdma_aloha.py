#!/usr/bin/python
import subprocess
import pygame
import time
import sys
import re
import sys
import zmq
import os
import csv
import numpy
import json
from socket import *    # import *, but we'll avoid name conflict
from sys import argv
from thread import start_new_thread

HELP_MSG	= sys.argv[0]+" --address <IP> [--interval <X.Y>] [--max-ping <X>] [--history <X>] [--window-height <X>] [--window-width <X>] [--fullscreen] [--ping-threshold <X>]"

IP_ADDR		= "192.168.5.222" # Default IP
CLOCK_DELTA	= 0.1 #0.02 # Minimal refresh rate
MAX_PING	= 150.0 # The visualization will automatically scale to display 0 ping on top and MAX_PING ping at the bottom

MAX_DRAW_LINE = 6
MAX_RX_ACK_LINE = MAX_DRAW_LINE
MAX_STA1_PROTOCOL = MAX_DRAW_LINE
MAX_STA2_PROTOCOL = MAX_DRAW_LINE
MAX_STA3_PROTOCOL = MAX_DRAW_LINE
MAX_STA4_PROTOCOL = MAX_DRAW_LINE
MAX_STD_TX_FRAME_CUMULATIVE = MAX_DRAW_LINE
MAX_IPT = MAX_DRAW_LINE

HISTORY_SIZE	= 1200.0 # Number of history values to display
COORD_MULT	= {"X": 1, "Y": 1} # Coord scaler, automatically determined based on window size, MAX_PING and HISTORY_SIZE
RESOLUTION	= (1560, 450) # Default window size
#RESOLUTION	= (1024, 800) # Default window size
#RESOLUTION	= (1920, 500) # Default window size
RX_ACK_LINE	= []
STA1_PROTOCOL = []
STA2_PROTOCOL = []
STA3_PROTOCOL = []
STA4_PROTOCOL = []
STD_TX_FRAME_CUMULATIVE = []
RX_MATCH_LINE	= []
HISTORY		= []
SWITCH 		= []
PLOSS 		= []

TEXT_COLOR	= (180, 180, 180) # Infotext color
RED_COLOR	= (255, 0, 0)
YELLOW_COLOR	= (255, 255, 0)
#BLUE_COLOR	= (0, 0, 255)
BLUE_COLOR	= (146, 146, 146)
WITHE_COLOR = (255, 255, 255)

PING_THRESHOLD	= 250 # Ping above this value will raise the INTERNET DYING warning
LAG_THRESHOLD	= [ # You can define custom ping thresholds that will display lines across the screen
			{"ping": 40,  "color": (0, 120, 0), "desc": "AP1"},
			{"ping": 35, "color": (0, 120, 0), "desc": "AP2"}
		]


stations_dump = [["10.8.8.101", "alix01", 2.0, 1.0, 1, 1, 1 ,1, 1],
                ["10.8.8.102", "alix02", 2.0, 1.0, 1, 1, 1 ,1, 1],
                ["10.8.8.103", "alix03", 2.0, 1.0, 1, 1, 1 ,1, 1],
                ["10.8.8.104", "alix04", 2.0, 1.0, 1, 1, 1 ,1, 1],
                ["10.8.8.105", "alix05", 2.0, 1.0, 1, 1, 1 ,1, 1],
                ["10.8.8.115", "alix15", 2.0, 1.0, 1, 1, 1 ,1, 1],
                ["10.8.8.106", "alix06", 2.0, 1.0, 1, 1, 1 ,1, 1],
                ["10.8.8.107", "alix07", 2.0, 1.0, 1, 1, 1 ,1, 1],
                ["10.8.8.108", "alix08", 2.0, 1.0, 1, 1, 1 ,1, 1],
                ["10.8.8.109", "alix09", 2.0, 1.0, 1, 1, 1 ,1, 1],
                ["10.8.8.110", "alix10", 2.0, 1.0, 1, 1, 1 ,1, 1],
                ["10.8.8.111", "alix11", 2.0, 1.0, 1, 1, 1 ,1, 1],
                ["10.8.8.112", "alix12", 2.0, 1.0, 1, 1, 1 ,1, 1],
                ["10.8.8.113", "alix13", 2.0, 1.0, 1, 1, 1 ,1, 1]]


#num_active_traffic = 0
#old_num_active_traffic = 0

def getNextArg():
	getNextArg.n = getNextArg.n + 1
	return sys.argv[getNextArg.n]
getNextArg.n = 0

def parseArgs():
	global HELP_MSG
	global IP_ADDR
	global ZMQ_PORT
	global MAX_PING
	global CLOCK_DELTA
	global HISTORY_SIZE
	global RESOLUTION
	global PING_THRESHOLD

	try:
		while (True):
			a = getNextArg()
			if   ((a == "--help") or (a == "-h")):
				print HELP_MSG
				exit()
			elif (a == "--address"):
				IP_ADDR = getNextArg()
			elif (a == "--port"):
				ZMQ_PORT = getNextArg()
			elif (a == "--max-ping"):
				MAX_PING = float(getNextArg())
			elif (a == "--interval"):
				CLOCK_DELTA = float(getNextArg())
			elif (a == "--history"):
				HISTORY_SIZE = float(getNextArg())
			elif (a == "--fullscreen"):
				RESOLUTION = (0, 0)
			elif (a == "--window-width"):
				RESOLUTION = (int(getNextArg()), RESOLUTION[1])
			elif (a == "--window-height"):
				RESOLUTION = (RESOLUTION[0], int(getNextArg()))
			elif (a == "--ping-threshold"):
				PING_THRESHOLD = float(getNextArg())
	except IndexError:
		pass

def normalizePoints(p):
	i = 0
	ret = []
	for point in p:
		ret.append((i*COORD_MULT["X"], point*COORD_MULT["Y"]))
		i = i+1
	return ret

def getPing(ip):
	try:
		r = subprocess.check_output("/usr/bin/timeout 0.05 /bin/ping -qc 1 -W 1 -s 240 "+ip, shell=True)
		rg = re.search("(\d+\.\d+)/\d+\.\d+/\d+\.\d+/\d+\.\d+", r)
		if (rg):
			return float(rg.group(1))
		else:
			print "Unexpected error:", sys.exc_info()[0]
			return 500.0
	except:
	#	print "Unexpected error:", sys.exc_info()[0]
	#	return 100.0
	#except subprocess.CalledProcessError, e:
		#print "Ping stdout output:\n", e.output
		return 50.0
		
def main():
	global IP_ADDR
	global CLOCK_DELTA
	global HISTORY_SIZE
	global HISTORY
	global RX_ACK_LINE
	global STA1_PROTOCOL
	global STA2_PROTOCOL
	global STA3_PROTOCOL
	global STA4_PROTOCOL
	global IPT_LINE
	global STD_TX_FRAME_CUMULATIVE
	global MAX_PING
	global RESOLUTION
	global COORD_MULT
	global HELP_MSG
	#global num_active_traffic
	#global old_num_active_traffic

	#if (len(sys.argv) < 2):
	#	print HELP_MSG
	#	exit()

	parseArgs()

	CLOCK = -10.0
	OFFSET = 10
	OFFSET_LINE = 3

	pygame.init()
	pygame.display.set_caption("WISHFUL SHOWCASE 3")
	if (RESOLUTION == (0, 0)):
		screen = pygame.display.set_mode(RESOLUTION, pygame.FULLSCREEN)
	else:
		screen = pygame.display.set_mode(RESOLUTION)

	font = pygame.font.SysFont("monospace", 17)
	font2 = pygame.font.SysFont("monospace", 18)
	font1 = pygame.font.SysFont("monospace", 18)

	screen.blit(font.render("LOADING", True, (255, 255, 255)), (10, 10))
	pygame.display.update()

	#cnit image
	myimage1 = pygame.image.load("CNIT.GIF")
	imagerect1 = myimage1.get_rect()
	imagerect1.x = imagerect1.x + screen.get_width()-400
	imagerect1.y = imagerect1.y + screen.get_height()-150
	#wintech image
	myimage2 = pygame.image.load("header-graph.png")
	imagerect2 = myimage2.get_rect()
	# imagerect2.x = imagerect2.x + 100
	# imagerect2.y = imagerect2.y + 100

	COORD_MULT["X"] = screen.get_width() / HISTORY_SIZE
	COORD_MULT["Y"] = screen.get_height() / MAX_PING


	std_cumulative_tx_frame_interval_start = 0
	std_cumulative_tx_frame = 0

	#METAMAC VARIABLES
	NUM_PROTOCOL = 5

	#for x in range(HISTORY_SIZE):
	#	SWITCH.append()

	while True:

		for e in pygame.event.get():
			if (e.type == pygame.QUIT):
				pygame.quit()
				exit()
			if (e.type == pygame.KEYDOWN):
				if ((e.key == pygame.K_q) or (e.key == 113)):
					pygame.quit()
					exit()

		if (time.clock() > (CLOCK + CLOCK_DELTA)):
			CLOCK = time.clock()
			if (len(STA1_PROTOCOL) >= HISTORY_SIZE):
				#RX_ACK_LINE.pop(0)
				STA1_PROTOCOL.pop(0)
				STA2_PROTOCOL.pop(0)
				STA3_PROTOCOL.pop(0)
				STA4_PROTOCOL.pop(0)
				#RX_MATCH_LINE.pop(0)
				#IPT_LINE.pop(0)
				#HISTORY.pop(0)
				#SWITCH.pop(0)
				#PLOSS.pop(0)


			#n = getPing(IP_ADDR)
			# n = stations_dump[0][3]
			# if n == 50.0 and len(HISTORY) >= 1:
			# 	n = HISTORY[-1]
			# 	PLOSS.append(27.0)
			# 	#PLOSS.append(30.0)
			# else:
			# 	PLOSS.append(30.0)
            #

			# cumulative_tx_frame = 0
			# cumulative_freezing = 0
			# cumulative_ipt = 0
			# cumulative_rx_frame = 0

			# #print "RX FRAME"
			# AP_index=0
			# for row in stations_dump:
			# 	#for col in row:
			# 	if row[1] == "alix2":
			# 		break
			# 	AP_index += 1
			# cumulative_rx_frame = stations_dump[AP_index][7]
			# #print cumulative_rx_frame
            #
			# #print "TX FRAME"
			# for ii in range(1, len(stations_dump), 1):
			# 	#print "%s - %d" % (stations_dump[ii][1], stations_dump[ii][4])
			# 	cumulative_tx_frame += stations_dump[ii][4]
			# 	cumulative_freezing += stations_dump[ii][2]
			# 	cumulative_ipt += stations_dump[ii][8]
			# TX_FRAME_LINE_2.append( MAX_PING - 0.5 - (( cumulative_tx_frame/MAX_RX_MATCH_LINE)*MAX_PING ) )
            #
			# if num_active_traffic != 0:
			# 	cumulative_freezing = cumulative_freezing / num_active_traffic
			# 	#cumulative_ipt = cumulative_ipt / num_active_traffic
			# else:
			# 	cumulative_freezing = 0
			# 	#cumulative_ipt = 0

			# FREEZING.append( MAX_PING - 0.5 - (( cumulative_freezing / MAX_RX_MATCH_LINE) * MAX_PING ) )
			# IPT_LINE.append( MAX_PING - cumulative_ipt )
			# HISTORY.append( MAX_PING - stations_dump[2][3] ) #CW
			STA1_PROTOCOL.append( MAX_PING - 1 + OFFSET_LINE - (( stations_dump[2][2]/MAX_STA1_PROTOCOL)*MAX_PING ) )
			STA2_PROTOCOL.append( MAX_PING - 2 + OFFSET_LINE - (( stations_dump[3][2]/MAX_STA2_PROTOCOL)*MAX_PING ) )
			STA3_PROTOCOL.append( MAX_PING + 1 + OFFSET_LINE - (( stations_dump[4][2]/MAX_STA3_PROTOCOL)*MAX_PING ) )
			STA4_PROTOCOL.append( MAX_PING + 2 + OFFSET_LINE - (( stations_dump[5][2]/MAX_STA4_PROTOCOL)*MAX_PING ) )

			# if num_active_traffic != old_num_active_traffic :
			# 	std_cumulative_tx_frame = numpy.std(TX_FRAME_LINE_2[std_cumulative_tx_frame_interval_start:len(TX_FRAME_LINE_2)])
			# 	#print "New interval with len : " +  str(len(TX_FRAME_LINE_2) - std_cumulative_tx_frame_interval_start)
			# 	#print TX_FRAME_LINE_2[std_cumulative_tx_frame_interval_start:len(TX_FRAME_LINE_2)]
			# 	#print "STD = " + str(std_cumulative_tx_frame) + "\n"
			# 	old_num_active_traffic = num_active_traffic
			# 	std_cumulative_tx_frame_interval_start = len(TX_FRAME_LINE_2) + 5
			# STD_TX_FRAME_CUMULATIVE.append(MAX_PING - 0.5 - (( std_cumulative_tx_frame/MAX_RX_MATCH_LINE)*MAX_PING ))



			if (len(STA1_PROTOCOL) > 1):

				#set background color
				#screen.fill((78, 74, 76))
				screen.fill((63, 39, 96))

				screen.blit(font.render("MULT_X: "+str(COORD_MULT["X"])+", MULT_Y: "+str(COORD_MULT["Y"]), 1, TEXT_COLOR), (5, screen.get_height()-20))
				screen.blit(font.render("Clock: "+str(CLOCK), 1, TEXT_COLOR), (5, screen.get_height()-40))
				screen.blit(font.render("History size: "+str(HISTORY_SIZE), 1, TEXT_COLOR), (5, screen.get_height()-60))
				#num_active_traffic = stations_dump[0][8] + stations_dump[1][8] + stations_dump[2][8] + stations_dump[3][8] + stations_dump[4][8] + stations_dump[5][8] + stations_dump[6][8] + stations_dump[7][8]
				#screen.blit(font.render("Num active traffic: "+str(num_active_traffic), 1, TEXT_COLOR), (5, screen.get_height()-100))

				screen.blit(font.render("Active protocol station 4 : " + str(stations_dump[5][2]), 1, RED_COLOR), (800, screen.get_height()-20))
				screen.blit(font.render("Active protocol station 3 : " + str(stations_dump[4][2]) + "", 1, YELLOW_COLOR), (800, screen.get_height()-40))

				screen.blit(font.render("Active protocol station 2 : " + str(stations_dump[3][2]) + "", 1, WITHE_COLOR), (400, screen.get_height()-20))
				screen.blit(font.render("Active protocol station 1 : " + str(stations_dump[2][2]) + "", 1, BLUE_COLOR), (400, screen.get_height()-40))

				#screen.blit(font.render("Cumulative freezing : " + str(cumulative_freezing) + "/.5s", 1, (255, 255, 255)), (5, screen.get_height()-200))
				#screen.blit(font.render("Cumulative ipt : " + str(cumulative_ipt) + "/.5s", 1, (255, 255, 255)), (5, screen.get_height()-220))

				#PRINT IMAGES
				screen.blit(myimage1, imagerect1)
				screen.blit(myimage2, imagerect2)



				# new stuff
				#screen.blit(font2.render("Ping RTT", 1, TEXT_COLOR), (5, 10))
				#screen.blit(font1.render("" + str(MAX_PING - (MAX_PING/4) ) + " ", 1, (255, 0, 0) ), (5, screen.get_height()/4-10))

				screen.blit(font1.render("Protocol " + str(MAX_STA1_PROTOCOL  - (MAX_STA1_PROTOCOL/(NUM_PROTOCOL+1)) ) + " ALOHA ", 1, WITHE_COLOR), (screen.get_width() - 400, screen.get_height()/(NUM_PROTOCOL+1)-20+OFFSET))
				pygame.draw.line(screen, (100, 100, 100), (5, (screen.get_height()/(NUM_PROTOCOL+1))+OFFSET), (screen.get_width()-(NUM_PROTOCOL+1), (screen.get_height()/(NUM_PROTOCOL+1))+OFFSET))

				screen.blit(font1.render("Protocol " + str(MAX_STA1_PROTOCOL  - (MAX_STA1_PROTOCOL/(NUM_PROTOCOL+1)*2) ) + " TDMA SLOT 4 ", 1, WITHE_COLOR), (screen.get_width() - 400, screen.get_height()/(NUM_PROTOCOL+1)*2-20+OFFSET))
				pygame.draw.line(screen, (100, 100, 100), (5, (screen.get_height()/(NUM_PROTOCOL+1)*2)+OFFSET), (screen.get_width()-(NUM_PROTOCOL+1), (screen.get_height()/(NUM_PROTOCOL+1)*2)+OFFSET))

				#screen.blit(font1.render("" + str(MAX_PING/2) + " ", 1, (255, 0, 0)), (5, screen.get_height()/2-10))
				screen.blit(font1.render("Protocol " + str(MAX_STA1_PROTOCOL  - ((MAX_STA1_PROTOCOL/(NUM_PROTOCOL+1))*3) ) + " TDMA SLOT 3 ", 1, WITHE_COLOR), (screen.get_width() - 400, screen.get_height()/(NUM_PROTOCOL+1)*3-20+OFFSET))
				pygame.draw.line(screen, (100, 100, 100), (5, (screen.get_height()/(NUM_PROTOCOL+1)*3)+OFFSET), (screen.get_width()-(NUM_PROTOCOL+1), (screen.get_height()/(NUM_PROTOCOL+1)*3)+OFFSET))

				screen.blit(font1.render("Protocol " + str(MAX_STA1_PROTOCOL  - ((MAX_STA1_PROTOCOL/(NUM_PROTOCOL+1))*4) ) + " TDMA SLOT 2 ", 1, WITHE_COLOR), (screen.get_width() - 400, screen.get_height()/(NUM_PROTOCOL+1)*4-20+OFFSET))
				pygame.draw.line(screen, (100, 100, 100), (5, (screen.get_height()/(NUM_PROTOCOL+1)*4)+OFFSET), (screen.get_width()-(NUM_PROTOCOL+1), (screen.get_height()/(NUM_PROTOCOL+1)*4)+OFFSET))

				screen.blit(font1.render("Protocol " + str(MAX_STA1_PROTOCOL  - ((MAX_STA1_PROTOCOL/(NUM_PROTOCOL+1))*5) ) + " TDMA SLOT 1 ", 1, WITHE_COLOR), (screen.get_width() - 400, screen.get_height()/(NUM_PROTOCOL+1)*5-20+OFFSET))
				pygame.draw.line(screen, (100, 100, 100), (5, (screen.get_height()/(NUM_PROTOCOL+1)*5)+OFFSET), (screen.get_width()-(NUM_PROTOCOL+1), (screen.get_height()/(NUM_PROTOCOL+1)*5)+OFFSET))

				#screen.blit(font2.render("Packet loss", 1, TEXT_COLOR), (5, screen.get_height()-440))
				#screen.blit(font2.render("Serving AP", 1, TEXT_COLOR), (5, screen.get_height()-340))
				#screen.blit(font2.render("Telecommunication Networks Group (TKN)", 1, RED_COLOR), (screen.get_width()-800, screen.get_height()-90))
				#screen.blit(font2.render("Technische Universitaet Berlin", 1, RED_COLOR), (screen.get_width()-700, screen.get_height()-60))
				#screen.blit(font2.render("x", 1, RED_COLOR), (500, 500))

				#pygame.draw.lines(screen, (255, 0, 0), False, normalizePoints(HISTORY), 1)
				#pygame.draw.lines(screen, (255, 0, 0), False, normalizePoints(RX_ACK_LINE), 1)
				#pygame.draw.lines(screen, (0, 0, 255), False, normalizePoints(TX_FRAME_LINE), 1)
				pygame.draw.lines(screen, BLUE_COLOR, False, normalizePoints(STA1_PROTOCOL), 5)
				pygame.draw.lines(screen, WITHE_COLOR, False, normalizePoints(STA2_PROTOCOL), 5)
				pygame.draw.lines(screen, YELLOW_COLOR, False, normalizePoints(STA3_PROTOCOL), 5)
				pygame.draw.lines(screen, RED_COLOR, False, normalizePoints(STA4_PROTOCOL), 5)
				
				# for kk in range(len(HISTORY)):
				# 	if PLOSS[kk] is not 30.0:
				# 		xx = int(kk*COORD_MULT["X"])
				# 		yy = int(1*COORD_MULT["Y"])
				# 		#pygame.draw.circle(screen, (0, 255, 0), (xx,yy), 10, 2)
				# 		screen.blit(font.render("X", 1, YELLOW_COLOR), (xx,yy))
				
				pygame.display.update()

########################################################################




def ho_event(x):
	global ZMQ_PORT
	#global num_active_traffic

	local_network = 0
	if local_network :
		port2  = 4321
		sock = socket(AF_INET, SOCK_DGRAM)
		sock.bind(('',port2))
		while True:    # Run until cancelled
			message, client = sock.recvfrom(256) # <=256 byte datagram
			#print "Client connected:", client
			#sock.sendto(message, client)
			#print "Message:", message

			#{"active" : "0", "0":["0.254", "Aloha (p=0.75)"], "1":["0.175", "TDMA (slot 0)"], "2":["0.198", "TDMA (slot 1)"], "3":["0.198", "TDMA (slot 2)"], "4":["0.175", "TDMA (slot 3)"]}
			parsed_json = json.loads(message)

			#print(parsed_json['active'])
			remote_ipAddress = client[0]

			len_station_dump = len(stations_dump)
			#print 'len_station_dump %d' % len_station_dump

			# add measurement on nodes element
			for i in range(0,len_station_dump):
				#print 'stations_dump[i][0] (%s) == remote_wlan_ipAddress (%s)' % (str(stations_dump[i][0]), str(remote_wlan_ipAddress) )
				if stations_dump[i][0] == remote_ipAddress :
					stations_dump[i][2] = float(parsed_json['active'])+1	#active protocol
					stations_dump[i][3] = float(parsed_json['0'][0])	#protocol 1 weigth
					stations_dump[i][4] = parsed_json['0'][1]	#protocol 1 name
	else :
		context = zmq.Context()
		port1  = 8300
		# Socket to talk to server
		context = zmq.Context()
		socket_zmq = context.socket(zmq.SUB)
		socket_zmq.connect ("tcp://localhost:%s" % port1)
		socket_zmq.setsockopt(zmq.SUBSCRIBE, '')
		while True:
			parsed_json = socket_zmq.recv_json()
			#print('parsed_json : %s' % str(parsed_json))

			remote_ipAddress = parsed_json['node_ip_address'][0]
			len_station_dump = len(stations_dump)

			# add measurement on nodes element
			for i in range(0,len_station_dump):
				#print 'stations_dump[i][0] (%s) == remote_wlan_ipAddress (%s)' % (str(stations_dump[i][0]), str(remote_ipAddress) )
				if stations_dump[i][0] == remote_ipAddress :
					stations_dump[i][2] = float(parsed_json['active'])+1	#active protocol
					stations_dump[i][3] = float(parsed_json['0'][0])	#protocol 1 weigth
					stations_dump[i][4] = parsed_json['0'][1]	#protocol 1 name



start_new_thread(ho_event,(99,))
#ho_event(99)

# main loop
main()
#start_new_thread(main,(99,))
