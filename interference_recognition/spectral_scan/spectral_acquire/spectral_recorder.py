#!/usr/bin/env python
#
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import array
import struct
import sys
import time
import os
import json

from subprocess import call

import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import numpy as np


class SpectralRecorder:
	phy = "phy0"
	dev = "wlan0"
	drv= "ath9k"
	mode="manual"		#works
	fft_period=15
	spectral_count=10
	spectral_period=1
	short_repeat=1
	f0=5180e6
	def __init__(self, phy="self.phy0", dev="wlan0", drv="ath9k",
		mode="manual", fft_period=15, spectral_count=100, spectral_period=1,short_repeat=1,
		load=False,offline=True,freq=5180e6):
		self.phy 		= self.phy
		self.dev 		= self.dev
		self.drv		= drv
		self.mode		= mode
		self.fft_period		= fft_period
		self.spectral_count	= spectral_count
		self.spectral_period	= spectral_period
		self.short_repeat	= short_repeat
		self.f0			= freq #optional useful only if load is True
		#set spectral parameters
		if offline==False:
			self.set_spectral_params()
		if load:
			self.load_monitor()

	def get_spectral_params(self):
		return self.fft_period,self.spectral_count,self.spectral_period,self.short_repeat

	def load_monitor(self):
		#call("bash build.sh --load-module",shell=True)
		call("ifconfig "+self.dev+" down",shell=True)
		call("iwconfig "+self.dev+" mode monitor",shell=True)
		call("ifconfig "+self.dev+" up",shell=True)
		call("iwconfig "+self.dev+" freq "+str(self.f0),shell=True)

	def set_spectral_params(self):
		call("echo "+ self.mode		  		+ " > /sys/kernel/debug/ieee80211/" +self.phy+ "/"+ self.drv +"/spectral_scan_ctl", shell=True)
		call("echo "+ str(self.short_repeat)	  	+ " > /sys/kernel/debug/ieee80211/" +self.phy+ "/"+ self.drv +"/spectral_short_repeat",shell=True)
		call("echo "+ str(self.fft_period)	  	+ " > /sys/kernel/debug/ieee80211/" +self.phy+ "/"+ self.drv +"/spectral_fft_period",shell=True)
		call("echo "+ str(self.spectral_count-1) 	+ " > /sys/kernel/debug/ieee80211/" +self.phy+ "/"+ self.drv +"/spectral_count",shell=True)
		call("echo "+ str(self.spectral_period)		+ " > /sys/kernel/debug/ieee80211/" +self.phy+ "/"+ self.drv +"/spectral_period",shell=True)


	def acquire(self,filename="data"):
		T_acquire=1
		T=0.1
		call("cat /sys/kernel/debug/ieee80211/" + self.phy + "/"+ self.drv +"/spectral_scan0 > {}".format(filename), shell=True)
		time.sleep(T)
		t0=time.time()
		t0_a=t0
		now=t0
		now_a=t0
		while now_a-t0_a < T_acquire:
			now_a=time.time()
			while now-t0 < T:
				now=time.time()
				call("echo trigger > /sys/kernel/debug/ieee80211/" + self.phy + "/"+ self.drv +"/spectral_scan_ctl", shell=True)
			now=time.time()
			t0=now
			call("cat /sys/kernel/debug/ieee80211/" + self.phy + "/"+ self.drv +"/spectral_scan0 >> {}".format(filename), shell=True)
			#print now_a-t0_a

	def fix_timestamp_dict(self,samp_dict,T=50e3):
		ret=samp_dict
		timestamp=[v['tsf'] for v in samp_dict]
		timestamp=np.array(timestamp)-timestamp[0]
		decr=0
		if len(timestamp)!=0:

			tsf_diff=[]
			for i_t in range(0,len(timestamp)-1):
				t_=timestamp[i_t]
				t=timestamp[i_t+1]
				dt=t-t_

				print("t[{}]={}".format(i_t,t))
				print("t[{}]_={}".format(i_t,t_))
				if abs(dt) > T:
					#EMERGE ERROR, TSF chagnes
					print("[E] t[{}]={}".format(i_t,t))
					print("[E] t_[{}]={}".format(i_t,t_))
					ret.pop(i_t+1)
					decr=decr+1
				else:
					tsf_diff.append(dt)
					tsf_new=sum(tsf_diff)

					ret[i_t-decr]['tsf']=tsf_new
		else:
			print "timestamp is empty"
		ret.pop(len(ret)-1)
		return ret

	def fix_timestamp(self,timestamp,busy,x,T=50e3):
		if len(timestamp)!=0:
			timestamp=np.array(timestamp)-timestamp[0]
			tsf_diff=[]
			for i_t in range(0,len(timestamp)-1):
				t_=timestamp[i_t]
				t=timestamp[i_t+1]
				dt=t-t_

				#print("t={}".format(t))
				#print("t_={}".format(t_))
				if abs(dt) > T:
					#EMERGE ERROR, TSF chagnes
					print("t={}".format(t))
					print("t_={}".format(t_))
					busy.pop(i_t)
					x.pop(i_t)
				else:
					tsf_diff.append(dt)
			timestamp=np.cumsum(tsf_diff)
			busy=busy[0:len(timestamp)]
		else:
			print "timestamp is empty"
		return timestamp,busy,x

	def extract_samples(self,filename="data",out_file="out_samp.json"):
		y = []
		p_fft=[]
		freq_fft=[]
		busy = []
		timestamp = []
		out_samp=[]
		with open(filename, "rb") as file:

			data = file.read(76)
			now = time.time()

			while data != "":
				y_t = []
				x = []
				t, length = struct.unpack(">BH", data[0:3])
				if t != 1 or length != 73:
				    print "only 20MHz supported atm"
				    sys.exit(1)

				### metadata
				max_exp, freq, rssi, noise, max_magnitude, max_index, bitmap_weight, tsf = struct.unpack('>BHbbHBBQ', data[3:20])

				### measurements
				measurements = array.array("B")
				measurements.fromstring(data[20:])
				squaresum = sum([(m << max_exp)**2 for m in measurements])
				if squaresum == 0:
				    data = file.read(76)
				    continue
				fft_sub=[]
				for i, m in enumerate(measurements):
				    if m == 0 and max_exp == 0:
					m = 1
				    v = 10.0**((noise + rssi + 20.0 * np.log10(m << max_exp) - 10.0 * np.log10(squaresum))/10.0)
				    fft_sub.append(v)
				entry={}
				entry['tsf']=tsf
				entry['freq']=freq
				entry['rssi']=rssi
				entry['noise']=noise
				entry['fft_sub']=fft_sub

				out_samp.append(entry)
				data = file.read(76)
		#with open(out_file, 'w') as file:
		#	out_json=json.dumps(out_samp)
		#	file.write(out_json)
		return out_samp
	def get_feature(self,busy,timestamp):
		W = 1e3; #usec
		ts = timestamp-timestamp[0]
		t_= ts[0];
		t = ts[1];
		b_curr=[];
		b_mean=[];
		b_var =[];
		for b in range(0,len(busy)):
			if t-t_ < W:
				t = ts[b]
			else:
				t_= ts[b]
				b_mean.append(np.mean(b_curr))
				b_var.append(np.var(b_curr))
				b_curr=[]
			b_curr.append(busy[b])

		return b_mean, b_var

	def analyze(self,filename="data"):
		y = []
		p_fft=[]
		freq_fft=[]
		busy = []
		timestamp = []
		#TIME ANALYZE
		T = 1e6
		t0=time.time()
		with open(filename, "rb") as file:

			data = file.read(76)
			while data != "":
				    y_t = []
				    x = []
				    t, length = struct.unpack(">BH", data[0:3])
				    if t != 1 or length != 73:
					print "only 20MHz supported atm"
					sys.exit(1)

				    ### metadata
				    max_exp, freq, rssi, noise, max_magnitude, max_index, bitmap_weight, tsf = struct.unpack('>BHbbHBBQ', data[3:20])

				    #print "max_exp: "       + str(max_exp)
				    #print "freq: "          + str(freq)
				    #print "self.f0: "          + str(self.f0)
				    #print "rssi: "          + str(rssi)
				    #print "noise: "         + str(noise)
				    #print "max_magnitude: " + str(max_magnitude)
				    #print "max_index: "     + str(max_index)
				    #print "bitmap_weight: " + str(bitmap_weight)
				    #print "tsf: "           + str(tsf)

				    ### measurements
				    measurements = array.array("B")
				    measurements.fromstring(data[20:])
				    squaresum = sum([(m << max_exp)**2 for m in measurements])
				    #print "num of measurements= " + str(len(measurements))
				    #print "--------------"
				    if squaresum == 0:
					data = file.read(76)
					continue
				    for i, m in enumerate(measurements):
					if m == 0 and max_exp == 0:
					    m = 1
					v = 10.0**((noise + rssi + 20.0 * np.log10(m << max_exp) - 10.0 * np.log10(squaresum))/10.0)
					if i < 28:
					    f = freq - (20.0 / 64) * (28 - i)
					else:
					    f = freq + (20.0 / 64) * (i - 27)

					x.append(f)
					y.append(v)
					y_t.append(v)
				    p_fft.append(y_t);
				    freq_fft.append(x)

				    if len(y_t)!=0:
					timestamp.append(int(tsf))
					timestamp_diff=np.diff(timestamp)
					#y_t.sort()
					#y_t=y_t[::-1]
					#y_t_mean=(y_t[0]+y_t[55])/2
					#y_t_mean=y_t[0]
					#busy.append(y_t_mean)
				    else:
					print "y_t empty"
				    #print "timestamp_0={}".format(timestamp[0])
				    #print "len={}".format(len(timestamp))
				    #print  "timestamp_len={}".format(timestamp[len(timestamp)-1])
				    #print  "diff={}".format(timestamp[len(timestamp)-1]-timestamp[0])
				    if timestamp[len(timestamp)-1]-timestamp[0] < T:
				        data = file.read(76)
				    	continue;
				    else:
				    	break
		if len(timestamp) !=0:
			print "duration={}".format(max(np.array(timestamp)-timestamp[0]))

		timestamp,p_fft,freq_fft=self.fix_timestamp(timestamp,p_fft,freq_fft)
		p_fft_np=np.array(p_fft)
		freq_fft_np=np.array(freq_fft)
		busy=(p_fft_np[:,5]+p_fft_np[:,10])/2
		N,M=np.shape(p_fft_np)
		p_fft_plot=[]
		freq_fft_plot=[]
		for i in range(0,N):
			for j in range(0,M):
				p_fft_plot.append(p_fft_np[i,j])
				freq_fft_plot.append(freq_fft_np[i,j])


		# ----- PLOTS -----


		fmin=self.f0/1e6-15
		fmax=self.f0/1e6+15

		p_fft_db=[10.0 * np.log10(val) for val in p_fft_plot]
		busy_db=[10.0 * np.log10(val) for val in busy]

		return busy_db, timestamp

		fig = plt.figure()
		ax_t = fig.add_subplot(111)
		ax_t.plot(timestamp,busy_db,'b.')
		ax_t.plot(timestamp,busy_db,'r--')
		ax_t.set_ylim([-160,-20])
		ax_t.set_title('Timing');
		ax_t.set_ylabel('Power [dBm]')
		ax_t.set_xlabel('time [us]')
		ax_t.grid()

		plt.tight_layout()
		plt.show()


		"""
		fig = plt.figure()
		ax_cdf = fig.add_subplot(211)
		busy_db_sorted= np.sort(busy_db)
		yvals=np.arange(len(busy_db_sorted))/float(len(busy_db_sorted)-1)
		ax_cdf.plot(busy_db_sorted,yvals)
		ax_cdf.set_xlim([-130,-90])
		ax_cdf.set_title('busy CDF');
		ax_cdf.set_xlabel('power [dBm]')
		ax_cdf.set_ylabel('CDF')
		ax_cdf.grid()
		
		ax_t = fig.add_subplot(212)
		ax_t.plot(timestamp,busy_db,'b.')
		ax_t.plot(timestamp,busy_db,'r--')
		ax_t.set_ylim([-160,-20])
		ax_t.set_title('Timing');
		ax_t.set_ylabel('Power [dBm]')
		ax_t.set_xlabel('time [us]')
		ax_t.grid()
		plt.tight_layout()
		fig.savefig('{}.png'.format(filename),dpi = 300)
		plt.show()
		"""

		"""
		fig = plt.figure()
		ax = fig.add_subplot(311)
		ax_t = fig.add_subplot(312)
		#ax_cdf = fig.add_subplot(313)

		ax_t.plot(timestamp,busy_db,'b.')
		ax_t.plot(timestamp,busy_db,'r--')
		ax_t.set_ylim([-160,-20])
		ax_t.set_title('Timing');
		ax_t.set_ylabel('Power [dBm]')
		ax_t.set_xlabel('time [us]')
		ax_t.grid()
		ax.plot(freq_fft_plot,p_fft_db,'b.')
		ax.set_xlim([fmin, fmax]) 
		ax.set_ylim([-160, -20])
		ax.set_title('Spectrum');
		ax.set_xlabel('frequency [MHz]')
		ax.set_ylabel('Power [dBm]')
		ax.grid()


		timestamp_diff=np.diff(timestamp)
		timestamp_sorted = np.sort(timestamp_diff)
		timestamp_sorted=timestamp_sorted[ np.where( timestamp_sorted > 50 ) ]


		yvals=np.arange(len(timestamp_sorted))/float(len(timestamp_sorted)-1)
		ax_cdf.plot(timestamp_sorted,yvals)
		ax_cdf.set_title('timestamp CDF');
		ax_cdf.set_xlabel('time [us]')
		ax_cdf.set_ylabel('CDF')
		ax_cdf.grid()
		plt.tight_layout()
		fig.savefig('{}.png'.format(filename),dpi = 300)
		plt.show()
		"""

		busy_mean,busy_var=self.get_feature(busy,timestamp);
		return busy_mean,busy_var
