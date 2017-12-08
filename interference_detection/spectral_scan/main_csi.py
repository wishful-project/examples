from spectral_acquire import spectral_recorder
import numpy as np
import time
from time import sleep
import math

from operator import itemgetter

import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

sr = spectral_recorder.SpectralRecorder(load=False)
time.sleep(1)
#sr.acquire("/tmp/data.tlv")
#out=sr.extract_samples("nodezotacc1.tlv","out.json")
# #print len(out)
# power_fim,ts_fim		= sr.analyze("experiments/flow_middle/flow-in-the-middle-FG-CA-D_l-1505384368.826742224_nodezotacg6.tlv")
# power_no_int,ts_no_int		= sr.analyze("experiments/no_interference/no_interference-CA-D_l-1505384897.699383675_nodezotacg6.tlv")
# power_hidden,ts_hidden  	= sr.analyze("experiments/hidden/hidden-AC-DC-C_l-1505384677.681075940_nodezotacd6.tlv")
# power_idle,ts_idle		= sr.analyze("experiments/no_interference/idle_D_l-1505398712.776407626_nodezotacg6.tlv")

measurements = []

measurements = sr.extract_samples(filename="experiments/flow_middle/flow-in-the-middle-FG-CA-D_l-1505384368.826742224_nodezotacg6.tlv",out_file="not-in-use.json")
# measurements = sr.extract_samples(filename="experiments/no_interference/no_interference-CA-D_l-1505384897.699383675_nodezotacg6.tlv",out_file="not-in-use.json")
# measurements = sr.extract_samples(filename="experiments/hidden/hidden-AC-DC-C_l-1505384677.681075940_nodezotacd6.tlv",out_file="not-in-use.json")
# measurements = sr.extract_samples(filename="experiments/no_interference/idle_D_l-1505398712.776407626_nodezotacg6.tlv",out_file="not-in-use.json")
#
# measurements[0]['fft_sub']

csi_data = map(itemgetter('fft_sub'), measurements)
rows = len(csi_data)
cols = len(csi_data[1])

# print ("measuremnets " %measurements(1)['tsf'])

chunk_size=200
# chunk_size=5000
step_size = 10

f = plt.figure()
f.set_size_inches(7.0, 9.0)
ax = f.gca()
f.show()


for b in range(0, int(math.floor(rows/chunk_size))):
	for step in range(0,chunk_size,chunk_size/step_size):
		# print("b = %d step = %d" %(b,step))
		start = chunk_size * b + step
		stop = chunk_size * b + chunk_size + step
		# print(start)
		# print(stop)

		ax.imshow(csi_data[start:stop], extent=[0, cols, stop, start])
		# plt.imshow(csi_data)
		# plt.show()
		f.canvas.draw()
		# sleep(0.5)
		raw_input('pause : press any key ...')
#
# fig = plt.figure(1)
# ax_t = fig.add_subplot(111)
# ax_t.plot(ts_fim,power_fim,'b.',label="FIM")
# ax_t.plot(ts_fim,power_fim,'r--')
# ax_t.set_ylim([-160,-20])
# ax_t.set_title('Timing');
# ax_t.set_ylabel('Power [dBm]')
# ax_t.set_xlabel('time [us]')
# ax_t.grid()
# ax_t.legend()
#
# fig = plt.figure(2)
# ax_t = fig.add_subplot(111)
# ax_t.plot(ts_no_int,power_no_int,'b.',label="no interf")
# ax_t.plot(ts_no_int,power_no_int,'r--')
# ax_t.set_ylim([-160,-20])
# ax_t.set_title('Timing');
# ax_t.set_ylabel('Power [dBm]')
# ax_t.set_xlabel('time [us]')
# ax_t.grid()
# ax_t.legend()
#
# fig = plt.figure(3)
# ax_t = fig.add_subplot(111)
# ax_t.plot(ts_hidden,power_hidden,'b.',label="hidden")
# ax_t.plot(ts_hidden,power_hidden,'r--')
# ax_t.set_ylim([-160,-20])
# ax_t.set_title('Timing');
# ax_t.set_ylabel('Power [dBm]')
# ax_t.set_xlabel('time [us]')
# ax_t.grid()
# ax_t.legend()
#
# fig = plt.figure(4)
# ax_t = fig.add_subplot(111)
# ax_t.plot(ts_idle,power_idle,'b.',label="idle")
# ax_t.plot(ts_idle,power_idle,'r--')
# ax_t.set_ylim([-160,-20])
# ax_t.set_title('Timing');
# ax_t.set_ylabel('Power [dBm]')
# ax_t.set_xlabel('time [us]')
# ax_t.grid()
# ax_t.legend()
# plt.tight_layout()
# #fig.savefig('scatter.png',dpi = 300)
# plt.show()
