#!/usr/bin/python

import sys
import subprocess
import time
import multiprocessing
from time import gmtime, strftime

from numpy import *
from datetime import datetime, date, timedelta

import numpy as np
import matplotlib

# Force matplotlib to not use any Xwindows backend.
matplotlib.use('Agg')
import matplotlib.pyplot as plt, os, fnmatch
from matplotlib.backends.backend_pdf import PdfPages

import json

with open('measure.json') as data_file:
	data = json.load(data_file)

measurement_types=['TIME', 'PROTOCOL', 'THR']
update_y = 0
x = array(data.get(list(sort(data.keys()))[0]));
dim = x.shape
yaxis = [0] * dim[0]
my_dpi=100
width=1024
height=768

#for node in data.keys():
for node in list(sort(data.keys())):

	nodeIp=node
	x = array(data.get(nodeIp))
	#print("%s" % str(x))

	dim = x.shape
	xaxis = []

	if len(dim) > 2:
		number_type_measurements = dim[2]
	else:
		number_type_measurements = 1



	for meas_type_id in range(number_type_measurements):

		if measurement_types[meas_type_id] == "TIME" :
			min_TSF=np.min(x[:,0,meas_type_id])
			for ii in range(dim[0]):
				xaxis.append(x[ii][0][meas_type_id])


		if measurement_types[meas_type_id] == "THR" :
			#yaxis = [0] * dim[0]
			#figure_id += 1
			if nodeIp=="192.168.3.110" or nodeIp=="192.168.3.104" or nodeIp=="192.168.3.105" or nodeIp=="192.168.3.114":
				print(" node : " + nodeIp + " ( plot --> " + measurement_types[meas_type_id] + " )")
				for ii in range(dim[0]):
					yaxis[ii] += x[ii][0][meas_type_id]


		if measurement_types[meas_type_id] == "PROTOCOL" :
			num_rx_match_yaxis = []
			#figure_id += 1

			if nodeIp=="192.168.3.110" or nodeIp=="192.168.3.104" or nodeIp=="192.168.3.105" or nodeIp=="192.168.3.114":

				print(" node : " + nodeIp + " ( plot --> " + measurement_types[meas_type_id] + " )")

				for ii in range(dim[0]):
					num_rx_match_yaxis.append(x[ii][0][meas_type_id])

				figure_id = 0
				fig=plt.figure(figure_id)
				ax = fig.add_subplot(211)
				#if nodeIp=="10.8.8.105" or nodeIp=="10.8.8.107" or nodeIp=="10.8.8.110":
				#if nodeIp!="10.8.8.102":
				#nodeIp_label=nodeIp.replace("10.8.8.1","sta")
				nodeIp_label = 'PROTOCOL'
				ax.plot((xaxis-min_TSF)/1e6, num_rx_match_yaxis, '--', label=nodeIp_label);

				ax.grid(True)
				ax.set_xlim([0, (np.max(xaxis)-np.min(xaxis))/1e6])
				ax.set_ylim([0, 1200])

				fig.set_size_inches(width/my_dpi,height/my_dpi)
				plt.tight_layout()
				legend = ax.legend()


		if measurement_types[meas_type_id] == "CW" :
			num_cw_yaxis = []
			#figure_id += 1

			if nodeIp=="10.8.8.102":
			#if nodeIp=="10.8.8.105" or nodeIp=="10.8.8.107" or nodeIp=="10.8.8.110" or nodeIp=="10.8.8.111" or nodeIp=="10.8.8.112" or nodeIp=="10.8.8.113" or nodeIp=="10.8.8.114":

				print " node : " + nodeIp + " ( plot --> " + measurement_types[meas_type_id] + " )"

				for ii in range(dim[0]):
					num_cw_yaxis.append(x[ii][0][meas_type_id])

				figure_id = 0
				fig=plt.figure(figure_id)
				ax = fig.add_subplot(212)
				#if nodeIp=="10.8.8.105" or nodeIp=="10.8.8.107" or nodeIp=="10.8.8.110":
				#if nodeIp!="10.8.8.102":
				#nodeIp_label=nodeIp.replace("10.8.8.1","sta")
				nodeIp_label = 'CW'
				ax.plot((xaxis-min_TSF)/1e6, num_cw_yaxis, color='k', label=nodeIp_label);

				ax.grid(True)
				ax.set_xlim([0, (np.max(xaxis)-np.min(xaxis))/1e6])
				ax.set_ylim([0, 150])

				fig.set_size_inches(width/my_dpi,height/my_dpi)
				plt.tight_layout()
				legend = ax.legend(loc=4)

				# #plt.show()
				# fig_filename="fig_%s.pdf" % measurement_types[meas_type_id]
				ax.set_ylabel('CW');
				ax.set_xlabel('time [s]')
				# fig.savefig(fig_filename, format='pdf')




figure_id = 0
fig=plt.figure(figure_id)
ax = fig.add_subplot(211)

#nodeIp_label=nodeIp.replace("10.8.8.1","sta")
nodeIp_label='PROTOCOL'

print("%d - %d" % (len(xaxis), len(yaxis)))

xaxis = xaxis[0:100]
yaxis = yaxis[0:100]

#ax.plot((xaxis-min_TSF)/1e6, yaxis, label=nodeIp_label);


ax.grid(True)
ax.set_xlim([0, (np.max(xaxis)-np.min(xaxis))/1e6])
ax.set_ylim([-0.5, 4.5])

fig.set_size_inches(width/my_dpi,height/my_dpi)
plt.tight_layout()
legend = ax.legend(loc=4)

#plt.show()
fig_filename="fig_%s.pdf" % 'showcase4' #measurement_types[meas_type_id]
#ax.set_ylabel('Frame/s');
#ax.set_xlabel('time [s]')
fig.savefig(fig_filename, format='pdf')
