"""
Local control program to be executed on remote nodes.
"""

__author__ = "Domenico Garlisi"
__copyright__ = "Copyright (c) 2016, Technische Universität Berlin"
__version__ = "0.1.0"



# Definition of Local Control Program
def my_local_control_program(controller):
    # do all needed imports here!!!
    import time
    import datetime
    import sys
    sys.path.append('../../../')
    sys.path.append("../../../agent_modules/wifi_ath")
    sys.path.append("../../../agent_modules/wifi_wmp")
    sys.path.append("../../../agent_modules/wifi")
    sys.path.append('../../../upis')
    sys.path.append('../../../framework')
    sys.path.append('../../../agent')
    from agent_modules.wifi_wmp.wmp_structure import UPI_R


    @controller.set_default_callback()
    def default_callback(cmd, data):
        print(("DEFAULT CALLBACK : Cmd: {}, Returns: {}".format(cmd, data)))

    # control loop
    print("Local ctrl program started: {}".format(controller.name))
    while not controller.is_stopped():
        msg = controller.recv(timeout=1)
        if msg:
            ch = msg["new_channel"]
            print("Schedule get monitor to {} in 5s:".format(ch))
            UPI_myargs = {'interface' : 'wlan0', 'measurements' : [UPI_R.REGISTER_1, UPI_R.REGISTER_2, UPI_R.NUM_TX_DATA_FRAME, UPI_R.NUM_RX_ACK, UPI_R.NUM_RX_ACK_RAMATCH, UPI_R.BUSY_TYME , UPI_R.TSF, UPI_R.NUM_RX_MATCH] }
            result = controller.delay(5).radio.get_measurement(UPI_myargs)
            controller.send_upstream({"myResult": result})

    print("Local ctrl program stopped: {}".format(controller.name))

# # Definition of Local Control Program for metamac
# def metamac_local_control_program(controller):
# 	# do all needed imports here!!!
# 	import time
# 	import datetime
# 	import sys
# 	import ctypes, os
# 	import csv
# 	sys.path.append('../../../')
# 	sys.path.append("../../../agent_modules/wifi_ath")
# 	sys.path.append("../../../agent_modules/wifi_wmp")
# 	sys.path.append("../../../agent_modules/wifi")
# 	sys.path.append('../../../upis')
# 	sys.path.append('../../../framework')
# 	sys.path.append('../../../agent')
# 	from agent_modules.wifi_wmp.wmp_structure import UPI_R
# 	from agent_modules.wifi_wmp.adaptation_module.libb43 import *
#
# 	usleep = lambda x: time.sleep(x/1000000.0)
#
# 	#Flags
# 	FLAG_USE_BUSY = 0
# 	read_interval = 0.011
#
# 	PACKET_TO_TRANSMIT	=	0x00F0
# 	MY_TRANSMISSION		=	0x00F2
# 	SUCCES_TRANSMISSION	=	0x00F4
# 	OTHER_TRANSMISSION	=	0x00F6
# 	BAD_RECEPTION		=	0x00FA
# 	BUSY_SLOT           =	0x00FC
#
# 	NEAR_SLOT	=	43
# 	COUNT_SLOT	=	43
# 	SINC_SLOT_2	=	40
# 	SINC_SLOT_1	=	41
# 	SINC_SLOT_0	=	42
#
# 	@controller.set_default_callback()
# 	def default_callback(cmd, data):
# 		print(("DEFAULT CALLBACK : Cmd: {}, Returns: {}".format(cmd, data)))
#
# 	class metamac_slot(ctypes.Structure):
# 		_fields_ = [
# 			('slot_num', ctypes.c_ulong),
# 			('slot_num', ctypes.c_ulong),
# 			('read_num', ctypes.c_ulong),
# 			('host_time', ctypes.c_uint64),
# 			('host_time', ctypes.c_uint64),
# 			('tsf_time', ctypes.c_uint64 ),
# 			('slot_index', ctypes.c_int),
# 			('slots_passed', ctypes.c_int),
#
# 			#Indicates if this slot was filled in because of a delay in	reading from the board.
# 			('filler', ctypes.c_char), #	uchar filler : 1;
# 			#Indicates that a packet was waiting to be transmitted in this slot.
# 			('packet_queued', ctypes.c_char), #uchar packet_queued : 1;
# 			#Indicates that a transmission was attempted in this slot.
# 			('transmitted', ctypes.c_char), #uchar transmitted : 1;
# 			#Indicates that a transmission was successful in this slot.
# 			('transmit_success', ctypes.c_char), #uchar transmit_success : 1;
# 			#Various measures for whether another node attempted to transmit.
# 			('transmit_other', ctypes.c_char), #uchar transmit_other : 1;
# 			('bad_reception', ctypes.c_char), #uchar bad_reception : 1;
# 			('busy_slot', ctypes.c_char), #uchar busy_slot : 1;
# 			#Indicates that either a transmission attempt was unsuccessful
# 			#in this slot or another node attempted a transmission.
# 			('channel_busy', ctypes.c_char) #uchar channel_busy : 1;
# 		]
#
# 	#void queue_multipush(struct metamac_queue *queue, struct metamac_slot *slots, size_t count)
# 	def queue_multipush(slots, count):
# 		# for (size_t i = 0; i < count; i++) {
# 		# 	if (queue->in == (queue->out + queue->capacity - 1) % queue->capacity) {
# 		# 		queue_resize(queue, queue->capacity * 2);
# 		# 	}
# 		#
# 		# 	queue->data[queue->in] = slots[i];
# 		# 	queue->in = (queue->in + 1) % queue->capacity;
# 		# }
# 		#
# 		# if (pthread_cond_broadcast(&queue->nonempty_cond) != 0) {
# 		# 	err(EXIT_FAILURE, "Error signaling condition variable");
# 		# }
#
# 		# queue->data[queue->in] = slots[i];
# 		# queue->in = (queue->in + 1) % queue->capacity;
#
# 		wtr = csv.writer(open ('out.csv', 'a'), delimiter=',', lineterminator='\n')
# 		for label in slots:
# 			wtr.writerows([label])
#
#
#
#
# 	# # control loop
#     # print("Local ctrl program started: {}".format(controller.name))
#     # while not controller.is_stopped():
#     #     msg = controller.recv(timeout=1)
#     #     if msg:
#     #         ch = msg["new_channel"]
#     #         print("Schedule get monitor to {} in 5s:".format(ch))
#     #         UPI_myargs = {'interface' : 'wlan0', 'measurements' : [UPI_R.REGISTER_1, UPI_R.REGISTER_2, UPI_R.NUM_TX_DATA_FRAME, UPI_R.NUM_RX_ACK, UPI_R.NUM_RX_ACK_RAMATCH, UPI_R.BUSY_TYME , UPI_R.TSF, UPI_R.NUM_RX_MATCH] }
#     #         result = controller.delay(5).radio.get_monitor(UPI_myargs)
#     #         controller.send_upstream({"myResult": result})
#
# 	b43_phy = None
# 	b43 = B43(b43_phy)
# 	slot_time = 0.0022
#
# 	slot_num = 0
# 	read_num = 0
# 	slot_index = 0 #(int)
# 	last_slot_index = 0 #(int)
# 	tsf = 0 #(uint64_t)
# 	last_tsf = 0 #(uint64_t)
# 	initial_tsf = 0 #(uint64_t)
#
# 	start_time = b43.monotonic_time() #(timespec)
# 	loop_end = 0 #(uint64_t)
#
# 	initial_tsf = b43.getTSFRegs()
# 	tsf = initial_tsf
# 	slot_index = b43.shmRead16(b43.B43_SHM_REGS, COUNT_SLOT) & 0x7
# 	slot_num = (slot_index + 1) % 8
#
# 	# metamac control loop
# 	while not controller.is_stopped() :
# 		msg = controller.recv(timeout=1)
#
# 		current_time =  b43.monotonic_time() #(timespec)
# 		loop_start = (current_time.tv_sec - start_time.tv_sec) * 1000000 + (current_time.tv_nsec - start_time.tv_nsec) / 1000 #(uint64_t )
# 		last_tsf = tsf
# 		tsf = b43.getTSFRegs()
# 		last_slot_index = slot_index
# 		slot_index = b43.shmRead16(b43.B43_SHM_REGS, COUNT_SLOT) & 0x7
#
# 		packet_queued = b43.shmRead16(b43.B43_SHM_SHARED, PACKET_TO_TRANSMIT) #(uint)
# 		transmitted = b43.shmRead16(b43.B43_SHM_SHARED, MY_TRANSMISSION) #(uint)
# 		transmit_success = b43.shmRead16(b43.B43_SHM_SHARED, SUCCES_TRANSMISSION) #(uint)
# 		transmit_other = b43.shmRead16(b43.B43_SHM_SHARED, OTHER_TRANSMISSION) #(uint)
# 		bad_reception = b43.shmRead16(b43.B43_SHM_SHARED, BAD_RECEPTION) #(uint)
# 		busy_slot = b43.shmRead16(b43.B43_SHM_SHARED, BUSY_SLOT) #(uint)
# 		end_slot_index = b43.shmRead16(b43.B43_SHM_REGS, COUNT_SLOT) & 0x7 #(int)
#
# 		channel_busy = 0 #(uint)
# 		if (FLAG_USE_BUSY) :
# 			channel_busy = (transmitted & ~transmit_success) |((transmit_other | bad_reception | busy_slot) & ~(transmitted & transmit_success))
# 		else:
# 			channel_busy = (transmitted & ~transmit_success) |((transmit_other | bad_reception) & ~(transmitted & transmit_success))
#
# 		slots_passed = slot_index - last_slot_index #(int)
# 		if slots_passed < 0:
# 			slots_passed = slots_passed + 8
# 		#int64_t actual = ((int64_t)tsf) - ((int64_t)last_tsf);
# 		actual = tsf - last_tsf
# 		if (actual < 0 or actual > 200000) :
# 			print("Received TSF difference of %lld between consecutive reads.\n", actual)
# 			# Unresolved bug with hardware/firmware/kernel driver causes occasional large jumps
# 			#in the TSF counter value. In this situation use time from the OS timer instead.
# 			#actual = ((int64_t)loop_start) - ((int64_t)loop_end)
# 			actual = loop_start - loop_end
#
# 		min_diff = abs(actual - slots_passed * slot_time) #(int64_t )
#
# 		#Suppose last_slot_index is 7 and slot_index is 5. Then, since the slot
# 		#is a value mod 8 we know the actual number of slots which have passed is
# 		#>= 6 and congruent to 6 mod 8. Using the TSF counter from the network card,
# 		#we find the most likely number of slots which have passed. */
# 		diff = abs(actual - (slots_passed + 8) * slot_time) #(int64_t )
# 		while (diff < min_diff) :
# 			slots_passed += 8
# 			min_diff = diff
# 			diff = abs(actual - (slots_passed + 8) * slot_time)
#
#
#
# 		#Because the reads are not atomic, the values for the slot
# 		#indicated by slot_index are effectively unstable and could change between
# 		#the reads for the different feedback variables. Thus, only the last 7 slots
# 		#can be considered valid. If more than 7 slots have passed, we have to inject
# 		#empty slots to maintain the synchronization. Note that the 7th most recent
# 		#slot is at an offset of -6 relative to the current slot, hence the -1. */
# 		slot_offset = slots_passed #(int)
# 		#int max_read_offset = (slot_index <= end_slot_index) ? slot_index - end_slot_index + 7 : slot_index - end_slot_index - 1;
# 		if (slot_index <= end_slot_index) :
# 			max_read_offset =  slot_index - end_slot_index + 7
# 		else:
# 			max_read_offset = slot_index - end_slot_index - 1
# 		while slot_offset > max_read_offset:
# 			slot_offset-= 1
# 			#Empty filler slot
# 			slot_num+=1
#
# 		slots=[8] #(struct metamac_slot)
# 		for i in len(slots):
# 			slots[i] = metamac_slot()
# 		ai = 0
#
# 		while slot_offset > 0 :
# 			slot_offset-=1
# 			si = slot_index - slot_offset #(int)
# 			if  si < 0 :
# 				si = si + 8
#
# 			slot_num+=1
# 			slots[ai].slot_num = slot_num
# 			slots[ai].read_num = read_num
# 			slots[ai].host_time = loop_start
# 			slots[ai].tsf_time = tsf
# 			slots[ai].slot_index = slot_index
# 			slots[ai].slots_passed = slots_passed
# 			slots[ai].filler = 0
# 			slots[ai].packet_queued = (packet_queued >> si) & 1
# 			slots[ai].transmitted = (transmitted >> si) & 1
# 			slots[ai].transmit_success = (transmit_success >> si) & 1
# 			slots[ai].transmit_other = (transmit_other >> si) & 1
# 			slots[ai].bad_reception = (bad_reception >> si) & 1
# 			slots[ai].busy_slot = (busy_slot >> si) & 1
# 			slots[ai].channel_busy = (channel_busy >> si) & 1
# 			ai+=1
#
# 		#queue_multipush(queue, slots, ai);
# 		queue_multipush(slots, ai)
#
# 		#clock_gettime(CLOCK_MONOTONIC_RAW, &current_time);
# 		current_time =  b43.monotonic_time() #(timespec)
# 		loop_end = (current_time.tv_sec - start_time.tv_sec) * 1000000 + (current_time.tv_nsec - start_time.tv_nsec) / 1000
# 		#delay = ((int64_t)loop_start) + read_interval - ((int64_t)loop_end) #(int64_t)
# 		delay = (loop_start + read_interval - loop_end) #(int64_t)
# 		if (delay > 0):
# 			usleep(delay)
#
# 		read_num += 1




