from spectral_acquire import spectral_recorder
import numpy as np
import time
from operator import itemgetter
import matplotlib
matplotlib.use('TkAgg')
#matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn import preprocessing
from utils import *

sr = spectral_recorder.SpectralRecorder(load=False)
time.sleep(1)
#sr.acquire("/tmp/data.tlv")

T=1500e3

# measurements = sr.extract_samples(filename="experiments/20171002/zigbee_near.tlv",out_file="not-in-use.json",T=T)
# exp_name='ZIGBEE (NEAR)'
# filename='zigbee_near'

# measurements = sr.extract_samples(filename="experiments/20171002/lte-traffic_subframe.tlv",out_file="not-in-use.json",T=T)
# exp_name='LTE (Traffic subframe 6ms)'
# filename='lte_traffic_6'

# measurements = sr.extract_samples(filename="experiments/20171002/zigbee.tlv",out_file="not-in-use.json",T=T)
# exp_name='ZIGBEE (~FAR)'
# filename='zigbee_far'

# measurements = sr.extract_samples(filename="experiments/20171002/uwave-empty.tlv",out_file="not-in-use.json",T=T)
# exp_name='MICROWAVE (EMPTY)'
# filename='uwave_empty'





measurements = sr.extract_samples(filename="demo.tlv",out_file="not-in-use.json")
exp_name='DEMO'
filename='demo'


# measurements = sr.extract_samples(filename="experiments/20171020/wifi_2457.tlv",out_file="not-in-use.json",T=T)
# exp_name='WIFI (2457MHz)'
# filename='wifi_2457'


csi_data = list(map(itemgetter('fft_sub'), measurements))
csi_data=np.array(csi_data)
#OVERSAMPLING
#N_o=1
#csi_data_over=[]
#csi_data_over=oversamp(csi_data,N_o)

#csi_data=(csi_data-np.min(csi_data))/(np.max(csi_data)-np.min(csi_data))
freq = list(map(itemgetter('freq'), measurements))
tsf = list(map(itemgetter('tsf'), measurements))
freq=list(set(freq))

freq=freq[0]

ff=get_freq_list(freq)
#ff_over=get_freq_list(freq,N_o)


#csi_data=csi_data_over
#ff=ff_over

y=np.array(csi_data[0])
y_=y
y_nofilt_= y
tt=tsf[0]
tt_=tt;
PLOT=True
y_cont=[]

if PLOT:
	fig = plt.figure();
	plt.ion()
	plt.show()
start_corr=True
start_energy_det=True
corr_duration = 0;
energy_det_duration = 0;

t_corr_start = 0;
t_energy_det_start = 0;




spectrum_features = []
duration_features = []
duration_energy_det_features = []

# ::::::::::::::::::::::::::::::::::::::::::
# MAIN
# ::::::::::::::::::::::::::::::::::::::::::
csi_data=csi_data[310:len(csi_data)]
for ii, cc in enumerate(csi_data):
	skip=False
	thr_bw			= 0.06
	thr_corr		= 1e-10
	thr_corr_mean 	= 1
	P_thr_db		= -90
	P_thr 			= 10 **(P_thr_db/10.0)


	dt_thr = 1500
	yy = []
	start_f = []
	stop_f  = []
	START_BW=True
	y_pow = []
	bw_meas = []
	freq_meas = []

	y = np.array(cc)


	tt = tsf[ii]
	dt = tt - tt_

	y_nofilt = y
	weights=rrc_f()
	#weights = [1,1,1]

	y = np.convolve(y, np.array(weights)[::-1], 'same')

	min_max_scaler = preprocessing.MinMaxScaler()
	y_det = min_max_scaler.fit_transform(y.reshape(-1,1))
	y_det_ = min_max_scaler.fit_transform(y_.reshape(-1,1))
	y_det_nofilt = min_max_scaler.fit_transform(y_nofilt.reshape(-1, 1))
	y_det_nofilt_ = min_max_scaler.fit_transform(y_nofilt_.reshape(-1, 1))

	y_det = y_det[:,0]
	y_det_ = y_det_[:, 0]
	y_det_nofilt = y_det_nofilt[:, 0]
	y_det_nofilt_ = y_det_nofilt_[:, 0]
	#P_av = np.mean(y_pow)
	#P_av = np.median(y)
	P_av = np.mean(y)

	#strongest_P=np.sort(y)
	#strongest_P = strongest_P[::-1]
	#P_av = np.median(strongest_P[0:10])

	# ENERGY DETECTION
	if dt >= dt_thr:
		start_energy_det = True
		energy_det_duration = 0
	else:
		if P_av >= P_thr:

			if start_energy_det:

				t_energy_det_start = tt;
				start_energy_det = False

			else:


				energy_det_duration = tt - t_energy_det_start


				# energy_det_duration = tt - t_energy_det_start
			# print "t_corr_start={}; t_corr_stop={};energy_det_duration={}".format(t_energy_det_start-tsf[0],t_energy_det_start-tsf[0]+energy_det_duration,energy_det_duration)


		else:

			if start_energy_det == False:
				energy_det_duration = tt - t_energy_det_start
				start_energy_det = True
				if energy_det_duration != 0:
					duration_energy_det_features.append({"tsf": t_energy_det_start, "duration": energy_det_duration})
				print("-----------------------------")
				print("t_corr_start={}; t_corr_stop={};energy_det_duration={}".format(t_energy_det_start-tsf[0],t_energy_det_start-tsf[0]+energy_det_duration,energy_det_duration))
				print("-----------------------------")
				energy_det_duration = 0


	yy=y_det

	N_av = 5
	if len(y_cont) >= N_av:
		y_cont.pop()

	# EXTRACT BW-start and BW-stop

	if P_av >= P_thr :
		print "MA CI ENTRO?!?!?"
		print len(y_cont)
		#collect some consecutive samples and average it!
		y_cont.append(yy)
		yy=np.mean(y_cont,axis=0)

		if len(y_cont) == N_av:
			for i in range(0,len(yy)):

				if yy[i] > thr_bw and i < len(yy)-1 :
					y_pow.append(yy[i])
					if START_BW:
						#print "START"
						start_f.append(ff[i])
						START_BW=False

				else:
					if not START_BW:
						stop_f.append(ff[i-1])
						START_BW = True
	else:
		y_cont=[]
	# EXTRACT BW and FREQ
	for i in range(0,min(len(start_f),len(stop_f))):
		bw_meas.append(stop_f[i]-start_f[i])
		freq_meas.append((stop_f[i] + start_f[i])/2.0)


	#CORRELATION

	y_corr = np.correlate(y_det, y_det_, "same")
	#y_corr = np.correlate(y_det_nofilt, y_det_nofilt_, "same")

	if dt >= dt_thr:
		start_corr = True
		corr_duration = 0
	else:

		#if np.median(y_corr) <= thr_corr_mean and P_av >= P_thr:
		if np.median(y_corr) <= thr_corr_mean:
			if start_corr:
				t_corr_start = tt;
				start_corr = False
			else:

				corr_duration = tt - t_corr_start
		else:


			if start_corr == False:
				start_corr = True
				if corr_duration != 0:
					duration_features.append({"tsf": t_corr_start,"duration": corr_duration})
					# print("---------------------")
					# print("SAVE DURATION")
					# print("dt={}".format(dt))
					# print("dt={}".format(dt))
					# print("duration={}".format(corr_duration))
					# print("---------------------")

					# raw_input("got a duration, continue...")
				corr_duration = 0
		#print "P_av={} P_thr={}".format(P_av,P_thr)

	#update state variables, ready for next round
	tt_ = tt
	y_ = y
	y_nofilt_ = y_nofilt

	if P_av <= P_thr:
		skip=True
		# print"-----------------------------"
		# print "NOISE"
		# print "Mean:{}".format(np.median(y_corr))
		# print "Deviation:{}".format(np.std(y_corr))
		# print"-----------------------------"
	else:
		spectrum_features.append({"tsf":tsf[ii],"bw":bw_meas,"freq":freq_meas})
		if PLOT:
			print("-----------------------------")
			print("SIGNAL")
			print("i={}".format(ii))
			print("dt={}".format(dt))
			print("time={}".format(tsf[ii]-tsf[0]))
			print("P_av={}".format(P_av))
			print("bw_meas={}".format(bw_meas))
			print("freq_meas={}".format(freq_meas))
			print("central_freq={}".format(freq))
			print("Correlation info:")
			#print "Mean:{}".format(np.median(y_corr))
			#print "Deviation:{}".format(np.std(y_corr))
			#print "corr_duration:{}".format(corr_duration)
			#print "t_corr_start:{}".format(t_corr_start)
			print("-----------------------------")

	#print spectrum_features

	if PLOT:
		# Plot result
		if ii==0:
			ax_t		 = fig.add_subplot(411)
			ax_t_ 		 = fig.add_subplot(412)
			ax_corr 	 = fig.add_subplot(413)
			ax_enery_det = fig.add_subplot(414)
			fig.set_size_inches(1600 / 100.0, 800 / 100.0)

		else:
			ax_t.cla();
			ax_t_.cla();
			ax_corr.cla();
			ax_enery_det.cla();

		ax_t.plot(ff,  y_det,'g.--')
		ax_t.plot(ff, y_det_nofilt,'b.',markersize=15)
		ax_t.plot(ff, yy,'r.',markersize=15)

		ax_t.plot(ff, np.array([1] * len(y)) * thr_bw,'r--')
		ax_t.set_ylim([0,1])
		ax_t.set_xlim([ff[0], ff[-1]])
		ax_t_.plot(ff, y_det_, 'g.--')
		ax_t_.plot(ff, y_det_nofilt_, 'b.')
		ax_t_.set_ylim([0, 1])
		ax_t_.set_xlim([ff[0], ff[-1]])
		ax_corr.plot(np.arange(1, len(y_corr) + 1), y_corr)
		ax_corr.plot(np.arange(1, len(y_corr) + 1), np.array([1] * len(y_corr)) * np.median(y_corr),'g.--')

		ax_corr.plot(np.arange(1, len(y_corr) + 1), np.array([1] * len(y_corr)) * thr_corr,'r--')

		ax_enery_det.plot(np.arange(1, len(y) + 1), y)
		ax_enery_det.plot(np.arange(1, len(y) + 1), np.array([1] * len(y)) * P_av,'g.--')
		ax_enery_det.plot(np.arange(1, len(y) + 1), np.array([1] * len(y)) * P_thr, 'r--')
		#ax_enery_det.plot(np.arange(1, len(y) + 1), y_nofilt)
		#ax_enery_det.plot(np.arange(1, len(y_nofilt) + 1), np.array([1] * len(y_nofilt)) * P_av, 'g--')
		#ax_enery_det.plot(np.arange(1, len(y_nofilt) + 1), np.array([1] * len(y_nofilt)) * P_thr, 'r--')
		ax_t.grid()
		ax_t_.grid()
		ax_corr.grid()
		ax_enery_det.grid()
		plt.tight_layout()
		plt.show(False)
		plt.draw()
		plt.pause(1e-10)  # Note this correction

		#fig.canvas.draw();
		if skip==True:
			continue
		raw_input('continue...\n');




[measurements,spectrum_features, duration_energy_det_features,duration_features]=sr.get_spectrum_scan_features()
exp_name="demo"
dd = np.array(list(map(itemgetter('duration'), duration_features)))
bb = np.array(list(map(itemgetter('bw'), spectrum_features)))
ff2 =np.array(list(map(itemgetter('freq'), spectrum_features)))

ed =np.array(list(map(itemgetter('duration'), duration_energy_det_features)))

fig = plt.figure()
fig.set_size_inches(18.5, 10.5)

#fig.suptitle(exp_name)

ax_energy_detection = fig.add_subplot(422)

# IGNORE duration < 300
#ed=[i for i in ed if i >= 1000]

dd_s= np.sort(ed)
yvals=np.arange(len(dd_s))/float(len(dd_s)-1)
ax_energy_detection.plot(dd_s,yvals)
#ax_energy_detection.set_xlim([-130,-90])
ax_energy_detection.set_title('energy detection CDF size={}'.format(len(dd_s)));
ax_energy_detection.set_xlabel('Duration [us]')
ax_energy_detection.set_ylabel('CDF')
ax_energy_detection.grid()

ax_cdf_bw = fig.add_subplot(424)
bb=[j for i in bb for j in i]
print(bb)
dd_s= np.sort(bb)

yvals=np.arange(len(dd_s))/float(len(dd_s)-1)
ax_cdf_bw.plot(dd_s,yvals)
#ax_cdf_bw.set_xlim([-130,-90])
ax_cdf_bw.set_title('Expected bw CDF size={}'.format(len(dd_s)));
ax_cdf_bw.set_xlabel('BW [MHz]')
ax_cdf_bw.set_ylabel('CDF')
ax_cdf_bw.set_xlim([0,20])
ax_cdf_bw.grid()

ax_cdf_ff = fig.add_subplot(426)
ff2=[j for i in ff2 for j in i]
dd_s= np.sort(ff2)
yvals=np.arange(len(dd_s))/float(len(dd_s)-1)
ax_cdf_ff.plot(dd_s,yvals)
ax_cdf_ff.set_title('Expected freq CDF');
ax_cdf_ff.set_xlabel('freq [MHz]')
ax_cdf_ff.set_ylabel('CDF')
ax_cdf_ff.grid()


ax_cdf_duration = fig.add_subplot(428)

# IGNORE duration < 300
#dd=[i for i in dd if i >= 300]


dd_s= np.sort(dd)
yvals=np.arange(len(dd_s))/float(len(dd_s)-1)
ax_cdf_duration.plot(dd_s,yvals)
ax_cdf_duration.set_title('correlation CDF size={}'.format(len(dd)));
ax_cdf_duration.set_xlabel('Duration [us]')
ax_cdf_duration.set_ylabel('CDF')
ax_cdf_duration.grid()

ax_waterfall = fig.add_subplot(121)


ax_waterfall=plot_waterfall(ax_waterfall,measurements,exp_name)

plt.tight_layout()




#fig.savefig("{}.png".format(filename),dpi=(200))
plt.show()
