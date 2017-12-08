from spectral_acquire import spectral_recorder
import numpy as np
import time



import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

sr = spectral_recorder.SpectralRecorder(load=False)
time.sleep(1)
#sr.acquire("/tmp/data.tlv")
#out=sr.extract_samples("nodezotacc1.tlv","out.json")
#print len(out)
power_ch2,ts_ch2		= sr.analyze("experiments/co-channel/data_ch2")
power_ch6,ts_ch6		= sr.analyze("experiments/co-channel/data_ch6")
power_ch2_6,ts_ch2_6		= sr.analyze("experiments/co-channel/data_ch2_ch6")
power_idle,ts_idle		= sr.analyze("experiments/co-channel/data_idle")

fig = plt.figure(1)
ax_t = fig.add_subplot(111)
ax_t.plot(ts_ch2,power_ch2,'b.',label="CH2")
ax_t.plot(ts_ch2,power_ch2,'r--')
ax_t.set_ylim([-160,-20])
ax_t.set_title('Timing');
ax_t.set_ylabel('Power [dBm]')
ax_t.set_xlabel('time [us]')
ax_t.grid()
ax_t.legend()
fig.savefig('ch2.png',dpi = 300)

fig = plt.figure(2)
ax_t = fig.add_subplot(111)
ax_t.plot(ts_ch6,power_ch6,'b.',label="CH6")
ax_t.plot(ts_ch6,power_ch6,'r--')
ax_t.set_ylim([-160,-20])
ax_t.set_title('Timing');
ax_t.set_ylabel('Power [dBm]')
ax_t.set_xlabel('time [us]')
ax_t.grid()
ax_t.legend()
fig.savefig('ch6.png',dpi = 300)

fig = plt.figure(3)
ax_t = fig.add_subplot(111)
ax_t.plot(ts_ch2_6,power_ch2_6,'b.',label="CH2+CH6")
ax_t.plot(ts_ch2_6,power_ch2_6,'r--')
ax_t.set_ylim([-160,-20])
ax_t.set_title('Timing');
ax_t.set_ylabel('Power [dBm]')
ax_t.set_xlabel('time [us]')
ax_t.grid()
ax_t.legend()
fig.savefig('ch2_6.png',dpi = 300)

fig = plt.figure(4)
ax_t = fig.add_subplot(111)
ax_t.plot(ts_idle,power_idle,'b.',label="idle")
ax_t.plot(ts_idle,power_idle,'r--')
ax_t.set_ylim([-160,-20])
ax_t.set_title('Timing');
ax_t.set_ylabel('Power [dBm]')
ax_t.set_xlabel('time [us]')
ax_t.grid()
ax_t.legend()
fig.savefig('idle.png',dpi = 300)
plt.show()
