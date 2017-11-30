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
power_mean_fim,power_var_fim		= sr.analyze("experiments/flow_middle/flow-in-the-middle-FG-CA-D_l-1505384368.826742224_nodezotacg6.tlv")
power_mean_no_int,power_var_no_int	= sr.analyze("experiments/no_interference/no_interference-CA-D_l-1505384897.699383675_nodezotacg6.tlv")
power_mean_hidden,power_var_hidden  	= sr.analyze("experiments/hidden/hidden-AC-DC-C_l-1505384677.681075940_nodezotacd6.tlv")
power_mean_idle,power_var_idle		= sr.analyze("experiments/no_interference/idle_D_l-1505398712.776407626_nodezotacg6.tlv")


fig = plt.figure()
ax = fig.add_subplot(111)
ax.plot(power_mean_fim,power_var_fim,'b.',label='fim')
ax.plot(power_mean_no_int,power_var_no_int,'r.',label='no interf')
ax.plot(power_mean_hidden,power_var_hidden,'c.',label='hidden')
ax.plot(power_mean_idle,power_var_idle,'g.',label='idle')
ax.set_xlabel('power mean')
ax.set_ylabel('power var')
ax.grid()
ax.legend()
plt.tight_layout()
fig.savefig('scatter.png',dpi = 300)
plt.show()
