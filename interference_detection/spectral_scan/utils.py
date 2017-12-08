import numpy as np
from operator import itemgetter
import matplotlib
matplotlib.use('TkAgg')

def plot_waterfall(ax,measurements,exp_name):
	csi_data = list(map(itemgetter('fft_sub'), measurements))
	timestamp = list(map(itemgetter('tsf'), measurements))
	freq = list(map(itemgetter('freq'), measurements))
	freq=list(set(freq))
	freq=freq[0]
	timestamp=np.array(timestamp)-timestamp[0]

	T=np.max(timestamp)
	N=len(timestamp)
	y=get_freq_list(freq)
	x=timestamp[0:N]
	Z=10.0 * np.log10(csi_data[0:N])
	X,Y = np.meshgrid(y,x)

	cc=ax.pcolormesh(X,Y,Z,vmin=-140, vmax=-20)
	fmin=min(y)
	fmax=max(y)
	ax.set_xlim([fmin,fmax])
	ax.set_ylim([0,T])
	ax.set_ylabel('Time [us]')
	ax.set_xlabel('freq [MHz]')
	ax.set_title(exp_name)
	return ax


def get_freq_list(freq,N=1):
	ff=[]
	for i in range(0,56):
		#if m == 0 and max_exp == 0:
		#    m = 1
		if i < 28:
		    fr = freq - (20.0 / 64) * (28 - i)
		else:
		    fr = freq + (20.0 / 64) * (i - 27)
		ff.append(fr)
	fff=[]
	for f in ff:
		for o in range(0, N):
			fff.append(f+o*(20.0/64/N))
	return fff

	#return ff



def rrc_f(T=1,beta=0.8):
	out=[]
	for f in np.linspace(-1/(2.0*T), 1/(2.0*T), num=5):
		if abs(f) <= (1-beta)/float(2.0*T):
			out.append(1.0)
		else:
			if (1-beta)/float(2.0*T) < abs(f) and abs(f) <= (1+beta)/float(2.0*T):
				v=0.5*(1+np.cos(np.pi*T/float(beta)*( abs(f)-(1-beta)/float(2.0*T) ) ))
				out.append(v)
			else:
				out.append(0)
	return out

def oversamp(d,N):
	d_ret=[]
	for cc in d:
		a=np.array([ [v]*N for v in cc])
		a=a.ravel()
		d_ret.append(a)
	return d_ret
