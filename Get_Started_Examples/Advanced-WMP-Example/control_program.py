"""
Local control program to be executed on remote nodes.
"""

__author__ = "Domenico Garlisi"
__copyright__ = "Copyright (c) 2016, CNIT"
__version__ = "0.1.0"
__email__ = "domenico.garlisi@cnit.it"

import time
import datetime
import sys
from sys import stdout
from ctypes import *
import os
import csv
import signal
import threading
import math
import zmq
import netifaces as ni

libc = CDLL('libc.so.6')
usleep = lambda x: time.sleep(x/1000000.0)

sys.path.append('../../../')
sys.path.append("../../../agent_modules/wifi_ath")
sys.path.append("../../../agent_modules/wifi_wmp")
sys.path.append("../../../agent_modules/wifi")
sys.path.append('../../../upis')
sys.path.append('../../../framework')
sys.path.append('../../../agent')
# from agent_modules.wifi_wmp.wmp_structure import UPI_R
from agent_modules.wifi_wmp.adaptation_module.libb43 import *

# @controller.set_default_callback()
# def default_callback(cmd, data):
# 	print(("DEFAULT CALLBACK : Cmd: {}, Returns: {}".format(cmd, data)))

# manager = Manager()
# story_channel = manager.list()


story_file = None
reading_thread = None

def signal_handler(signal, frame):
	story_file.close()
	reading_thread.do_run = False
	reading_thread.join()
	time.sleep(2)
	sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)


# Definition of Local Control Program
#def my_local_control_program(controller):
def my_local_control_program():

	#Flags
	FLAG_USE_BUSY = 0
	FLAG_READONLY = 0
	FLAG_VERBOSE = 1
	read_interval = 7000 #12000 #(us)

	PACKET_TO_TRANSMIT	=0x00F0
	MY_TRANSMISSION		=0x00F2
	SUCCES_TRANSMISSION	=0x00F4
	OTHER_TRANSMISSION	=0x00F6
	BAD_RECEPTION		=0x00FA
	BUSY_SLOT           =0x00FC

	NEAR_SLOT	=	43
	COUNT_SLOT	=	43
	SINC_SLOT_2	=	40
	SINC_SLOT_1	=	41
	SINC_SLOT_0	=	42


	class tdma_param(ctypes.Structure):
		_fields_= [
			('frame_offset', ctypes.c_int),
			('frame_length', ctypes.c_int),
			('slot_assignment', ctypes.c_int)
		]

	class fsm_param(ctypes.Structure):
		_fields_= [
			#Parameter number.
			('num', ctypes.c_int),
			#Parameter value.
			('value', ctypes.c_int)
			#Linked list.
			#struct fsm_param *next;
		]

	class protocol(ctypes.Structure) :
		_fields_ = [
			#Unique identifier
			('id', ctypes.c_int),
			#Readable name, such as "TDMA (slot 1)"
			('name', c_char_p),
			#Path to the compiled (.txt) FSM implementation
			('fsm_path', ctypes.c_char_p),
			#Parameters for the FSM
			('fsm_params', fsm_param * 2),
			#Protocol emulator for determining decisions of protocol locally
			#protocol_emulator emulator;
			#Parameter for protocol emulator
			#void *parameter;
			('parameter', tdma_param)
		]

	# class metamac_slot(ctypes.Structure):
	# 	_fields_ = [
	# 		('slot_num', ctypes.c_ulong),
	# 		('read_num', ctypes.c_ulong),
	# 		('host_time', ctypes.c_uint64),
	# 		('host_time', ctypes.c_uint64),
	# 		('tsf_time', ctypes.c_uint64 ),
	# 		('slot_index', ctypes.c_int),
	# 		('slots_passed', ctypes.c_int),
    #
	# 		#Indicates if this slot was filled in because of a delay in	reading from the board.
	# 		('filler', ctypes.c_char), #	uchar filler : 1;
	# 		#Indicates that a packet was waiting to be transmitted in this slot.
	# 		('packet_queued', ctypes.c_char), #uchar packet_queued : 1;
	# 		#Indicates that a transmission was attempted in this slot.
	# 		('transmitted', ctypes.c_char), #uchar transmitted : 1;
	# 		#Indicates that a transmission was successful in this slot.
	# 		('transmit_success', ctypes.c_char), #uchar transmit_success : 1;
	# 		#Various measures for whether another node attempted to transmit.
	# 		('transmit_other', ctypes.c_char), #uchar transmit_other : 1;
	# 		('bad_reception', ctypes.c_char), #uchar bad_reception : 1;
	# 		('busy_slot', ctypes.c_char), #uchar busy_slot : 1;
	# 		#Indicates that either a transmission attempt was unsuccessful
	# 		#in this slot or another node attempted a transmission.
	# 		('channel_busy', ctypes.c_char) #uchar channel_busy : 1;
	# 	]

	class metamac_slot(ctypes.Structure):
		_fields_ = [
			('slot_num', ctypes.c_ulong),
			('read_num', ctypes.c_ulong),
			('host_time', ctypes.c_uint64),
			('host_time', ctypes.c_uint64),
			('tsf_time', ctypes.c_uint64 ),
			('slot_index', ctypes.c_int),
			('slots_passed', ctypes.c_int),

			#Indicates if this slot was filled in because of a delay in	reading from the board.
			('filler', ctypes.c_ubyte), #	uchar filler : 1;
			#Indicates that a packet was waiting to be transmitted in this slot.
			('packet_queued', ctypes.c_ubyte), #uchar packet_queued : 1;
			#Indicates that a transmission was attempted in this slot.
			('transmitted', ctypes.c_ubyte), #uchar transmitted : 1;
			#Indicates that a transmission was successful in this slot.
			('transmit_success', ctypes.c_ubyte), #uchar transmit_success : 1;
			#Various measures for whether another node attempted to transmit.
			('transmit_other', ctypes.c_ubyte), #uchar transmit_other : 1;
			('bad_reception', ctypes.c_ubyte), #uchar bad_reception : 1;
			('busy_slot', ctypes.c_ubyte), #uchar busy_slot : 1;
			#Indicates that either a transmission attempt was unsuccessful
			#in this slot or another node attempted a transmission.
			('channel_busy', ctypes.c_ubyte) #uchar channel_busy : 1;
		]

	class protocol_suite(ctypes.Structure) :
		_fields_ = [
			#Total number of protocols
			('num_protocols', ctypes.c_int),
			#Index of best protocol. Initially -1.
			('active_protocol', ctypes.c_int),
			#Index of protocols in slots. -1 Indicated invalid
			('slots', ctypes.c_int * 2),
			#Which slot is active. 0 indicates neither are active.
			('active_slot', ctypes.c_int),
			#Offset of slots numbering from read loop to slot numbering for TDMA.
			('slot_offset', ctypes.c_int),
			#Array of all protocols.
			('protocols', protocol * 4),
			#Array of weights corresponding to protocols.
			('weights', ctypes.c_double * 4),	#double *weights; !!!WARNING for *
			#Factor used in computing weights.
			('eta', ctypes.c_double),
			#Slot information for last to be emulated.
			('last_slot', metamac_slot),
			#Time of last protocol update.
			#('last_update', timespec), # struct  ;!!!WARNING for *
			#Indicates whether protocols should be cycled.
			('cycle', ctypes.c_int),
		]

	def set_parameter(b43, slot, num, value):

		param_addr = 0
		if num==10:
			param_addr = 0x16*2
		elif num==11:
			param_addr = 0x21*2
		elif num==12:
			param_addr = 0x1F*2
		elif num==13:
			param_addr = 0x20*2
		elif num==14:
			param_addr = 0x11*2
		elif num==15:
			param_addr = 0x12*2
		elif num==16:
			param_addr = 0x13*2
		elif num==17:
			param_addr = 0x14*2
		else:
			return

		if slot == 0 :
			param_addr += b43.PARAMETER_ADDR_BYTECODE_1
		else :
			param_addr += b43.PARAMETER_ADDR_BYTECODE_2

		b43.shmWrite16(b43.B43_SHM_SHARED, param_addr, value & 0xffff);



	def tdma_emulate(param, slot_num, offset):
		slot_num += offset
		tdma_params = param
		if ((slot_num - tdma_params.frame_offset) % tdma_params.frame_length) == tdma_params.slot_assignment :
			result = 1.0
		else :
			result = 0.0

		return result

	def configure_params(b43, slot, param):

		#while (param != N) {
		for i in range(2):
			set_parameter(b43, slot, param[i].num, param[i].value)



	def load_protocol(b43, suite, protocol):

		"""
		Update this function --> replace the shared memory write function with UPI for change parameter and load radio program
		 set_parameters(param_key_values_dict):
		 activate_radio_program(name)
		"""


		#struct options opt;
		active = suite.active_slot # Always 0 or 1 since metamac_init will already have run.
		inactive = 1 - active

		if (protocol == suite.slots[active]) :
			#This protocol is already running.
			pass
		else :
			#Protocol in active slot shares same FSM, but is not the same protocol
			#(already checked). Write the parameters for this protocol.
			configure_params(b43, active, suite.protocols[protocol].fsm_params)
			suite.slots[active] = protocol

		# elif (protocol == suite.slots[inactive]):
		# 	#Switch to other slot.
		# 	opt.active = (inactive == 0) ? "1" : "2"
		# 	writeAddressBytecode(df, &opt)
		# 	suite.active_slot = inactive
        #
		# elif (suite.slots[active] >= 0 ) : #and strcmp(suite->protocols[protocol].fsm_path, suite->protocols[suite->slots[active]].fsm_path) == 0) :
		# 	#Protocol in active slot shares same FSM, but is not the same protocol
		# 	#(already checked). Write the parameters for this protocol.
		# 	configure_params(b43, active, suite.protocols[protocol].fsm_params)
		# 	suite.slots[active] = protocol
        #
		# elif (suite.slots[inactive] >= 0): #and strcmp(suite->protocols[protocol].fsm_path, suite->protocols[suite->slots[inactive]].fsm_path) == 0) :
		# 	#Protocol in inactive slot shares same FSM, but is not the same protocol,
		# 	#so write the parameters for this protocol and activate it.
        #
		# 	# configure_params(df, inactive, suite->protocols[protocol].fsm_params);
		# 	# opt.active = (inactive == 0) ? "1" : "2";
		# 	# writeAddressBytecode(df, &opt);
        #
		# 	suite.slots[inactive] = protocol
		# 	suite.active_slot = inactive
        #
		# else:
		# 	#Load into inactive slot.
        #
		# 	# opt.load = (inactive == 0) ? "1" : "2";
		# 	# opt.name_file = suite->protocols[protocol].fsm_path;
		# 	# bytecodeSharedWrite(df, &opt);
		# 	# configure_params(df, inactive, suite->protocols[protocol].fsm_params);
		# 	# opt.active = opt.load;
		# 	# writeAddressBytecode(df, &opt);
        #
		# 	suite.slots[inactive] = protocol
		# 	suite.active_slot = inactive

		suite.active_protocol = protocol
		suite.last_update = monotonic_time()


	def metamac_evaluate(b43, suite):

		#Identify the best protocol.
		best = 0
		for i in range(suite.num_protocols):
			if (suite.weights[i] > suite.weights[best]) :
				best = i

		if (suite.cycle) :
			# struct timespec current_time;
			# clock_gettime(CLOCK_MONOTONIC_RAW, &current_time);
			# uint64_t timediff = (current_time.tv_sec - suite->last_update.tv_sec) * 1000000L +
			# 	(current_time.tv_nsec - suite->last_update.tv_nsec) / 1000L;
            #
			# if (timediff > 1000000L) {
			# 	load_protocol(df, suite, (suite->active_protocol + 1) % suite->num_protocols);
			# }
			pass
		elif (best != suite.active_protocol):
			load_protocol(b43, suite, best)

	#static void metamac_display(unsigned long loop, struct protocol_suite *suite)
	def metamac_display(loop, suite):
		# if (loop > 0):
		# 	#Reset cursor upwards by the number of protocols we will be printing.
		# 	print("\x1b[%dF", suite.num_protocols)

		for i in range(0, suite.num_protocols):
			active_string = ' '
			if suite.active_protocol == i:
				active_string = '*'

			#print("%c %5.3f %s\n" % (active_string, suite.weights[i], suite.protocols[i].name))
			if i == 0 :
				stdout.write("\r%c %5.3f %s -- " % (active_string, suite.weights[i], suite.protocols[i].name))
			else:
				stdout.write("%c %5.3f %s -- " % (active_string, suite.weights[i], suite.protocols[i].name))
			stdout.flush()

		global socket_visualizer
		#ip_address = controller.net.get_iface_ip_addr(interface)
		iface = 'wlan0'
		ip_address = [inetaddr['addr'] for inetaddr in ni.ifaddresses(iface)[ni.AF_INET]]
		stock_data = {
            'node_ip_address': ip_address,
            'active': suite.active_protocol
        }

		#send information to visualizer outside the laboratory
		#socket_visualizer.send(b'client message to server1')
		socket_visualizer.send_json(stock_data)
		message = socket_visualizer.recv()
		#print("Received reply [" + str(message) + "]")

	#void queue_multipush(struct metamac_queue *queue, struct metamac_slot *slots, size_t count)
	def queue_multipush(story_channel, story_file, story_channel_len, story_channel_len_diff):

		ai = story_channel_len - story_channel_len_diff
		while ai < story_channel_len :

			# print("%d - %d : %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d" %
			# ( ai, story_channel_len_diff, int(story_channel[ai].slot_num), int(story_channel[ai].read_num), int(story_channel[ai].host_time),
			# story_channel[ai].tsf_time, story_channel[ai].slot_index, story_channel[ai].slots_passed,
			# (story_channel[ai].filler), (story_channel[ai].packet_queued), (story_channel[ai].transmitted),
			# (story_channel[ai].transmit_success), (story_channel[ai].transmit_other),
			# (story_channel[ai].bad_reception), (story_channel[ai].busy_slot), (story_channel[ai].channel_busy) ))

			story_file.write("%d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d\n" %
			( int(story_channel[ai].slot_num), int(story_channel[ai].read_num), int(story_channel[ai].host_time),
			story_channel[ai].tsf_time, story_channel[ai].slot_index, story_channel[ai].slots_passed,
			(story_channel[ai].filler), (story_channel[ai].packet_queued), (story_channel[ai].transmitted),
			(story_channel[ai].transmit_success), (story_channel[ai].transmit_other),
			(story_channel[ai].bad_reception), (story_channel[ai].busy_slot), (story_channel[ai].channel_busy) ))

			ai += 1

		# if (logfile != NULL) {
		# 			fprintf(logfile, "%llu,%d,%llu,%llu,%llu,%d,%d,%01x,%01x,%01x,%01x,%01x,%01x,%01x,%01x,%s",
		# 				(unsigned long long) slots[i].slot_num,
		# 				suite->slot_offset,
		# 				(unsigned long long) slots[i].read_num,
		# 				(unsigned long long) slots[i].host_time,
		# 				(unsigned long long) slots[i].tsf_time,
		# 				slots[i].slot_index,
		# 				slots[i].slots_passed,
		# 				slots[i].filler,
		# 				slots[i].packet_queued,
		# 				slots[i].transmitted,
		# 				slots[i].transmit_success,
		# 				slots[i].transmit_other,
		# 				slots[i].bad_reception,
		# 				slots[i].busy_slot,
		# 				slots[i].channel_busy,
		# 				suite->protocols[suite->active_protocol].name);
        #
		# 			for (int i = 0; i < suite->num_protocols; i++) {
		# 				fprintf(logfile, ",%e", suite->weights[i]);
		# 			}
        #
		# 			fprintf(logfile, "\n");
		# 		}




	def acquire_slots_channel(story_channel):
		reading_thread = threading.currentThread()
		b43_phy = None
		b43 = B43(b43_phy)
		slot_time = 2200 #(us)

		slot_num = 0
		read_num = 0
		slot_index = 0 #(int)
		last_slot_index = 0 #(int)
		tsf = 0 #(uint64_t)
		last_tsf = 0 #(uint64_t)
		initial_tsf = 0 #(uint64_t)

		start_time = monotonic_time() #(timespec)
		loop_end = 0 #(uint64_t)

		initial_tsf = b43.getTSFRegs()
		tsf = initial_tsf
		slot_index = b43.shmRead16(b43.B43_SHM_REGS, COUNT_SLOT) & 0x7
		slot_num = (slot_index + 1) % 8

		# metamac control loop
		# while not controller.is_stopped() :
		# 	msg = controller.recv(timeout=1)
		while getattr(reading_thread, "do_run", True):

			current_time =  monotonic_time() #(timespec)
			loop_start = int((current_time.tv_sec - start_time.tv_sec) * 1000000 + (current_time.tv_nsec - start_time.tv_nsec) / 1000) #(uint64_t )
			last_tsf = tsf
			tsf = b43.getTSFRegs()
			last_slot_index = slot_index


			''' replaced the following part with UPI get_measurements_periodic
			START
			'''

			slot_index = b43.shmRead16(b43.B43_SHM_REGS, COUNT_SLOT) & 0x7

			packet_queued = b43.shmRead16(b43.B43_SHM_SHARED, PACKET_TO_TRANSMIT) #(uint)
			transmitted = b43.shmRead16(b43.B43_SHM_SHARED, MY_TRANSMISSION) #(uint)
			transmit_success = b43.shmRead16(b43.B43_SHM_SHARED, SUCCES_TRANSMISSION) #(uint)
			transmit_other = b43.shmRead16(b43.B43_SHM_SHARED, OTHER_TRANSMISSION) #(uint)
			bad_reception = b43.shmRead16(b43.B43_SHM_SHARED, BAD_RECEPTION) #(uint)
			busy_slot = b43.shmRead16(b43.B43_SHM_SHARED, BUSY_SLOT) #(uint)

			end_slot_index = b43.shmRead16(b43.B43_SHM_REGS, COUNT_SLOT) & 0x7 #(int)

			'''
			STOP
			'''
			channel_busy = 0 #(uint)
			if (FLAG_USE_BUSY) :
				channel_busy = (transmitted & ~transmit_success) |((transmit_other | bad_reception | busy_slot) & ~(transmitted & transmit_success))
			else:
				channel_busy = (transmitted & ~transmit_success) |((transmit_other | bad_reception) & ~(transmitted & transmit_success))

			slots_passed = slot_index - last_slot_index #(int)
			if slots_passed < 0:
				slots_passed = slots_passed + 8

			actual = tsf - last_tsf #int64_t actual = ((int64_t)tsf) - ((int64_t)last_tsf);

			#print(" read %d - last_tsf %d - tsf %d - diff %d: %x, %x, %x, %x, %x, %x, %x" % (read_num, last_tsf, tsf, actual, packet_queued, transmitted, transmit_success, transmit_other, bad_reception, busy_slot, end_slot_index))

			# if (actual < 0 or actual > 200000) :
			# 	print("Received TSF difference of %lld between consecutive reads.\n", actual)
			# 	# Unresolved bug with hardware/firmware/kernel driver causes occasional large jumps
			# 	#in the TSF counter value. In this situation use time from the OS timer instead.
			# 	#actual = ((int64_t)loop_start) - ((int64_t)loop_end)
			# 	actual = loop_start - loop_end
			# min_diff = abs(actual - slots_passed * slot_time) #(int64_t )
			# #Suppose last_slot_index is 7 and slot_index is 5. Then, since the slot
			# #is a value mod 8 we know the actual number of slots which have passed is
			# #>= 6 and congruent to 6 mod 8. Using the TSF counter from the network card,
			# #we find the most likely number of slots which have passed. */
			# diff = abs(actual - (slots_passed + 8) * slot_time) #(int64_t )
			# while (diff < min_diff) :
			# 	slots_passed += 8
			# 	min_diff = diff
			# 	diff = abs(actual - (slots_passed + 8) * slot_time)
			# #Because the reads are not atomic, the values for the slot
			# #indicated by slot_index are effectively unstable and could change between
			# #the reads for the different feedback variables. Thus, only the last 7 slots
			# #can be considered valid. If more than 7 slots have passed, we have to inject
			# #empty slots to maintain the synchronization. Note that the 7th most recent
			# #slot is at an offset of -6 relative to the current slot, hence the -1. */
			slot_offset = slots_passed #(int)
			# #int max_read_offset = (slot_index <= end_slot_index) ? slot_index - end_slot_index + 7 : slot_index - end_slot_index - 1;
			# if (slot_index <= end_slot_index) :
			# 	max_read_offset =  slot_index - end_slot_index + 7
			# else:
			# 	max_read_offset = slot_index - end_slot_index - 1
			#
			# while slot_offset > max_read_offset:
			# 	slot_offset-= 1
			# 	#Empty filler slot
			# 	slot_num+=1

			slots = [ metamac_slot() for i in range(8)] #(struct metamac_slot) |!!! warning for memory leak
			ai = 0
			while slot_offset > 0 :
				slot_offset-=1
				si = slot_index - slot_offset #(int)
				if  si < 0 :
					si = si + 8

				slot_num+=1
				slots[ai].slot_num = slot_num
				slots[ai].read_num = read_num
				slots[ai].host_time = loop_start
				slots[ai].tsf_time = tsf
				slots[ai].slot_index = slot_index
				slots[ai].slots_passed = slots_passed
				slots[ai].filler = 0
				slots[ai].packet_queued = (packet_queued >> si) & 1
				slots[ai].transmitted = (transmitted >> si) & 1
				slots[ai].transmit_success = (transmit_success >> si) & 1
				slots[ai].transmit_other = (transmit_other >> si) & 1
				slots[ai].bad_reception = (bad_reception >> si) & 1
				slots[ai].busy_slot = (busy_slot >> si) & 1
				slots[ai].channel_busy = (channel_busy >> si) & 1
				ai+=1

			for i in range(ai):
			# 	#save in dynamic array
			 	story_channel.append(slots[i])

			# for i in range(ai):
			# 	print("%d, %d, %d, " %   ( int(story_channel[i].slot_num), int(story_channel[i].read_num), int(story_channel[i].host_time) ))

			current_time =  monotonic_time() #(timespec)
			loop_end = int((current_time.tv_sec - start_time.tv_sec) * 1000000 + (current_time.tv_nsec - start_time.tv_nsec) / 1000)
			delay = (loop_start + read_interval - loop_end) #(int64_t) #delay = ((int64_t)loop_start) + read_interval - ((int64_t)loop_end) #(int64_t)
			#print("ai %d - loop_start %d - loop_end %d - diff %d - delay %d - story_channel_len %d" % (ai, loop_start, loop_end, loop_end-loop_start, delay, len(story_channel) ))
			# we cant make dalay minor of ~7ms
			if (delay > 0):
				#usleep(delay)
				libc.usleep(int(delay))

			# current_time_delay =  monotonic_time() #(timespec)
			# loop_end_delay = int((current_time_delay.tv_sec - current_time.tv_sec) * 1000000 + (current_time_delay.tv_nsec - current_time.tv_nsec) / 1000)
			# print(" delay %d" % (loop_end_delay))

			read_num+=1


	#Performs the computation for emulating the suite of protocols
	#for a single slot, and adjusting the weights.
	#void update_weights(struct protocol_suite* suite, struct metamac_slot current_slot)
	def update_weights(suite, current_slot, ai):
		#Accounting for the fact that the slots that TDMA variants transmit on are
		# not necessarily aligned to the slot indices provided by the board. For instance,
		# one would expect that TDMA-4 slot 1 would transmit on slot indexes 1 and 5, but
		# this is not necessarily true. Offset between transmissions will be 4, but not
		# necessarily aligned to the slot indexes.

		# print("%d - %d : %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d" %
		# 	( ai, story_channel_len_diff, int(story_channel[ai].slot_num), int(story_channel[ai].read_num), int(story_channel[ai].host_time),
		# 	story_channel[ai].tsf_time, story_channel[ai].slot_index, story_channel[ai].slots_passed,
		# 	(story_channel[ai].filler), (story_channel[ai].packet_queued), (story_channel[ai].transmitted),
		# 	(story_channel[ai].transmit_success), (story_channel[ai].transmit_other),
		# 	(story_channel[ai].bad_reception), (story_channel[ai].busy_slot), (story_channel[ai].channel_busy) ))


		#if (suite.protocols[suite.active_protocol].emulator == tdma_emulate && current_slot.transmitted):
		if (current_slot.transmitted):
			#Update slot_offset
			params = suite.protocols[suite.active_protocol].parameter
			neg_offset = (current_slot.slot_num - params.frame_offset - params.slot_assignment) % params.frame_length
			suite.slot_offset = (params.frame_length - neg_offset) % params.frame_length

			#If there is no packet queued for this slot, consider all protocols to be correct
			#and thus the weights will not change
		if (current_slot.packet_queued) :
			#z represents the correct decision for this slot - transmit if the channel
			#is idle (1.0) or defer if it is busy (0.0)

			z=0.0
			if (not current_slot.channel_busy):
				z = 1.0


			for p in range(suite.num_protocols) :
				# d is the decision of this component protocol - between 0 and 1
#				d = suite.protocols[p].emulator(suite->protocols[p].parameter,
#					current_slot.slot_num, suite->slot_offset, suite->last_slot);

				d = tdma_emulate(suite.protocols[p].parameter, current_slot.slot_num, suite.slot_offset)

#				stdout.write("[%d] d=%e, z=%e \n" % (p, d, z,))

				exponent = suite.eta * math.fabs(d - z)
				suite.weights[p] *= math.exp(-exponent)

				if suite.weights[p]<0.01:
					suite.weights[p]=0.01



			#Normalize the weights
			s = 0
			for p in range(suite.num_protocols):
				s += suite.weights[p]
			for p in range(suite.num_protocols):
				suite.weights[p] /= s


#			for p in range(suite.num_protocols):
#				stdout.write("%5.3f\n" % (suite.weights[p]))

		suite.last_slot = current_slot

	socket_visualizer = None

	def socket_visualizer():
		global socket_visualizer
		port = "8300"

		print('start socket visualizer')

		context = zmq.Context()
		socket_visualizer = context.socket(zmq.REQ)
		#socket_visualizer.connect("tcp://localhost:%s" % port)
		socket_visualizer.connect("tcp://10.8.8.6:%s" % port)


	''' Main program '''

	# # control loop
    # print("Local ctrl program started: {}".format(controller.name))
    # while not controller.is_stopped():
    #     msg = controller.recv(timeout=1)
    #     if msg:
    #         ch = msg["new_channel"]
    #         print("Schedule get monitor to {} in 5s:".format(ch))
    #         UPI_myargs = {'interface' : 'wlan0', 'measurements' : [UPI_R.REGISTER_1, UPI_R.REGISTER_2, UPI_R.NUM_TX_DATA_FRAME, UPI_R.NUM_RX_ACK, UPI_R.NUM_RX_ACK_RAMATCH, UPI_R.BUSY_TYME , UPI_R.TSF, UPI_R.NUM_RX_MATCH] }
    #         result = controller.delay(5).radio.get_monitor(UPI_myargs)
    #         controller.send_upstream({"myResult": result})

	if len(sys.argv) < 2:
		sys.exit('Usage: %s eta_value' % sys.argv[0])

	suite = protocol_suite()
	num_protocols = 4
	#eta = 0.5
	eta = float(sys.argv[1])
	print('eta = %f' % eta)

	socket_visualizer()

	protocols = [protocol() for i in range(num_protocols)]

	#setting protocol structure 0
	protocols[0].id = 1
	protocols[0].name =b'TDMA  (slot 0)'
	protocols[0].fsm_path = b'tdma-4.txt'
	#protocols[0].fsm_params = '/params'
	protocols[0].fsm_params[0].num = 12
	protocols[0].fsm_params[0].value = 4
	protocols[0].fsm_params[1].num = 11
	protocols[0].fsm_params[1].value = 0
	protocols[0].emulator = b'tdma'
	#protocols[0].parameter = 'params';
	protocols[0].parameter.frame_offset = 0
	protocols[0].parameter.frame_length = 4
	protocols[0].parameter.slot_assignment = 0

	protocols[1].id = 2
	protocols[1].name = b'TDMA  (slot 1)'
	protocols[1].fsm_path = b'tdma-4.txt'
	#protocols[0].fsm_params = '/params'
	protocols[1].fsm_params[0].num = 12
	protocols[1].fsm_params[0].value = 4
	protocols[1].fsm_params[1].num = 11
	protocols[1].fsm_params[1].value = 1
	protocols[1].emulator = b'tdma'
	#protocols[0].parameter = 'params';
	protocols[1].parameter.frame_offset = 0
	protocols[1].parameter.frame_length = 4
	protocols[1].parameter.slot_assignment = 1

	protocols[2].id = 3
	protocols[2].name = b'TDMA  (slot 3)'
	protocols[2].fsm_path = b'tdma-4.txt'
	#protocols[0].fsm_params = '/params'
	protocols[2].fsm_params[0].num = 12
	protocols[2].fsm_params[0].value = 4
	protocols[2].fsm_params[1].num = 11
	protocols[2].fsm_params[1].value = 2
	protocols[2].emulator = b'tdma'
	#protocols[0].parameter = 'params';
	protocols[2].parameter.frame_offset = 0
	protocols[2].parameter.frame_length = 4
	protocols[2].parameter.slot_assignment = 2

	protocols[3].id = 4
	protocols[3].name = b'TDMA  (slot 4)'
	protocols[3].fsm_path = b'tdma-4.txt'
	#protocols[0].fsm_params = '/params'
	protocols[3].fsm_params[0].num = 12
	protocols[3].fsm_params[0].value = 4
	protocols[3].fsm_params[1].num = 11
	protocols[3].fsm_params[1].value = 3
	protocols[3].emulator = b'tdma'
	#protocols[0].parameter = 'params';
	protocols[3].parameter.frame_offset = 0
	protocols[3].parameter.frame_length = 4
	protocols[3].parameter.slot_assignment = 3

	#protocols suite INIT VALUES
	suite.num_protocols = num_protocols

	#number of current active protocol from protocol structure
	suite.active_protocol = 1

	#number of protocol present in the specified slot
	suite.slots[0] = 1
	suite.slots[1] = 1

	#number of current active slot
	suite.active_slot = 1

	suite.slot_offset = 0

	suite.protocols[0] = protocols[0]
	suite.protocols[1] = protocols[1]
	suite.protocols[2] = protocols[2]
	suite.protocols[3] = protocols[3]
	for p in range(4) :
		suite.weights[p] = 1.0 / num_protocols

	suite.eta = eta
	suite.last_slot.slot_num = -1
	suite.last_slot.packet_queued = 0
	suite.last_slot.transmitted = 0
	suite.last_slot.channel_busy = 0
	suite.cycle = 0

	story_channel = [] # [ metamac_slot() ]
	global story_file
	global reading_thread
	# slots = [ metamac_slot() for i in range(8)]
	# story_channel.append(slots[0])
	# share_queue = Queue()

	reading_thread = threading.Thread(target=acquire_slots_channel, args=(story_channel,))
	reading_thread.start()
	# p = Process(target=acquire_slots_channel, args=(share_queue,))
	# p.start()
	#p.join()

	time.sleep(2)


	b43_phy = None
	b43 = B43(b43_phy)

	story_file = open("story.csv", "w")
	story_file.write("slot_num, read_num, host_time, tsf_time, slot_index, slots_passed, \
	 filler, packet_queued, transmitted, transmit_success, transmit_other, \
	 bad_reception, busy_slot, channel_busy \n")

	story_channel_len = 0
	# metamac control loop
	# while not controller.is_stopped() :
	# 	msg = controller.recv(timeout=1)

	#metamac_loop_break = 0
	last_update_time = monotonic_time()
	loop = 0

	while True: #(metamac_loop_break == 0)
		#print("Main thread")
		time.sleep(0.1)

		if( (len(story_channel) - story_channel_len) > 60):
			story_channel_len_old = len(story_channel)-60
		else:
			story_channel_len_old = story_channel_len

		story_channel_len = len(story_channel)
		story_channel_len_diff = story_channel_len - story_channel_len_old
		#print('\n\nstory_channel len %d - diff %d - last slot num %d' % (story_channel_len, story_channel_len_diff, story_channel[story_channel_len-1].slot_num))

		#store channel evolution on file
		if story_channel_len_diff > 0 :
		#
        # 	# struct metamac_slot slots[16];
        # 	# size_t count = queue_multipop(queue, slots, ARRAY_SIZE(slots));
        #
			queue_multipush(story_channel, story_file, story_channel_len, story_channel_len_diff)

			for i in range((story_channel_len - story_channel_len_diff), story_channel_len ):
				#print('\n\n i %d -story_channel len %d - diff %d - last slot num %d' % (i, story_channel_len, story_channel_len_diff, story_channel[story_channel_len-1].slot_num))
				update_weights(suite, story_channel[i], i)


		#Update running protocol
		#if (!(flags & FLAG_READONLY)) :
		if (not FLAG_READONLY):
			metamac_evaluate(b43, suite)

		if FLAG_VERBOSE :
			current_time =  monotonic_time() #(timespec)
			timediff = (current_time.tv_sec - last_update_time.tv_sec) * 1000000 + (current_time.tv_nsec - last_update_time.tv_nsec) / 1000
			# Update display every 1 second
			if (timediff > 1000000) :
				metamac_display(loop, suite)
				loop+=1
				last_update_time = current_time


if __name__ == "__main__":
	my_local_control_program()
