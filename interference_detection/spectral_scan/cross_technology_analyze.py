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

T=1000e3

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


[measurements,spectrum_features, duration_energy_det_features,duration_features,freq]=sr.get_spectrum_scan_features("experiments/20171002/lte-traffic_subframe.tlv",T)
exp_name="demo"

dd = np.array(list(map(itemgetter('duration'), duration_features)))				#duration detection via correlation
bb = np.array(list(map(itemgetter('bw'), spectrum_features)))					#bandwidth
ff2 =np.array(list(map(itemgetter('freq'), spectrum_features)))					#frequency
ed =np.array(list(map(itemgetter('duration'), duration_energy_det_features))) 	#duration via energy detection



fig = plt.figure()
fig.set_size_inches(18.5, 10.5)

#fig.suptitle(exp_name)

ax_energy_detection = fig.add_subplot(422)

# IGNORE duration < 300
ed=[i for i in ed if i >= 1000]
max_ed=max(set(ed), key=list(ed).count)
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
dd_s= np.sort(bb)
yvals=np.arange(len(dd_s))/float(len(dd_s)-1)
max_bw=max(set(bb), key=bb.count)

ax_cdf_bw.plot(dd_s,yvals)
#ax_cdf_bw.set_xlim([-130,-90])
ax_cdf_bw.set_title('Expected bw CDF size={}'.format(len(dd_s)));
ax_cdf_bw.set_xlabel('BW [MHz]')
ax_cdf_bw.set_ylabel('CDF')
ax_cdf_bw.set_xlim([0,20])
ax_cdf_bw.grid()

ax_cdf_ff = fig.add_subplot(426)
ff2=[j for i in ff2 for j in i]
max_freq=max(set(ff2), key=ff2.count)
dd_s= np.sort(ff2)
yvals=np.arange(len(dd_s))/float(len(dd_s)-1)
ax_cdf_ff.plot(dd_s,yvals)
ax_cdf_ff.set_title('Expected freq CDF');
ax_cdf_ff.set_xlabel('freq [MHz]')
ax_cdf_ff.set_ylabel('CDF')
ax_cdf_ff.grid()


ax_cdf_duration = fig.add_subplot(428)

# IGNORE duration < 300
dd=[i for i in dd if i >= 300]

max_corr=max(set(dd), key=list(dd).count)

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



print("----------------------")
print("AVERAGE FEATURES:")
print("max_bw   ={}".format(max_bw))
print("max_freq ={}".format(max_freq))
print("max_ed   ={}".format(max_ed))
print("max_corr ={}".format(max_corr))

print("----------------------")

plt.show()
