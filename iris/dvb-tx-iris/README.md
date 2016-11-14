# DVB-TX-IRIS

## Introduction
This package contains the components which may be used to create
DVB-T radios with the IRIS software radio framework.

### The DVB-T waveform
DVB-T uses orthogonal frequency division multiplexing (OFDM) symbols with
cyclic prefix in order to deliver the transmitted data over the communication
channel. OFDM symbols are grouped in frames (composed of \f$N_F = 68\f$ OFDM symbols)
and superframes (composed of 4 frames): the superframe can be considered to
represent a basic group of data, as it always carries an integer number of 
transport stream (TS) packets, which constitute the payload of DVB-T and carry
compressed video and audio streams. The base-band (BB) signal samples can be
expressed as

\f[
\tilde s\left[ n \right] = \sum\limits_{m = 0}^{ + \infty } {\sum\limits_{l = 0}^{{N_F} - 1} 
{{z_{m,l}}\left[ n \right]} }  = \sum\limits_{m = 0}^{ + \infty } 
{\sum\limits_{l = 0}^{{N_F} - 1} {\sum\limits_{k = 0}^{K - 1} 
{{c_{m,l,k}}{G_k}{\psi _{m,l,k}}\left[ n \right]} } } 
\f]

where \f$m\f$ represents the frame index, \f$l\f$ is the OFDM symbol index, \f$k\f$ is the 
subcarrier index, \f$K\f$ is the number of active carriers (depending on the
transmission mode), and \f$N_F\f$ is the number of OFDM symbols per frame; the data
transported over each carrier is given by \f$c_{m,l,k}\f$ and it is a QAM (quadrature
amplitude modulation) mapped constellation symbol, carrying \f$\nu\f$ bits per symbol; 
\f$G_k\f$ is a carrier amplitude weighting factor that can be used to precompensate
linear distortions introduced by the transmitter (\f$G_k = 1\f$ in case of no
distortions), and \f$z_{m,l}\left[n\right]\f$ is the OFDM symbol in time. The modulation is performed
using \f$K\f$ out of NFFT orthogonal carriers \f$\psi_{m,l,k}\left[n\right]\f$, expressed as

\f[
\begin{array}{c}
 {\psi _{m,l,k}}\left[ n \right] = {e^{j2\pi \frac{{k - {K_2}}}{{{N_{{\rm{FFT}}}}}}\left( {n - {N_G} - \left( {l + m{N_F}} \right){N_S}} \right)}} \cdot {\Pi _{{N_S}}}\left[ {n - \left( {l + m{N_F}} \right){N_S}} \right] \\ 
 \end{array}
\f]

where \f$K_2 = K/2\f$, \f$N_G\f$ is the number of samples of the guard interval, 
\f$N_S = N_{\rm FFT} + N_G\f$ is the total number of samples of the OFDM symbol, and \f$\Pi_{N_s}[n]\f$ 
is the boxcar window, which is equal to 1 in \f$\left[0, N_S - 1\right]\f$ and to 0 elsewhere.
The BB samples are then converted into the analog domain using a sample time 
\f$T_{s,\rm DVBT}\f$ that depends on the bandwidth of the DVB-T configuration. The sample
rate \f$f_{s,\rm DVBT} = 1/T_{s,\rm DVBT}\f$, can be replaced by the DAC sample rate
\f$f_{s,\rm DAC} = 1/T_{s,\rm DAC}\f$, as expressed by

\f[
\tilde s\left( t \right) = \sum\limits_{n = 0}^\infty  {\tilde s\left[ n \right]h\left( {t - n{T_{s,{\rm{DVBT}}}}} \right)}  = \sum\limits_{n = 0}^\infty  {\tilde y\left[ n \right]{h_I}\left( {t - n{T_{s,{\rm{DAC}}}}} \right)} 
\f]

where \f$h\left(t\right) = T_{s,\rm DVBT} \textrm{sinc}\left(\Pi t/T_{s,\rm DVBT}\right)\f$ is the ideal BB reconstruction filter,
\f$h_I\left(t\right)\f$ is the DAC output filter, and \f$\tilde{y}\left[n\right]\f$ is the signal \f$\tilde{s}\left[n\right]\f$ resampled to
the DAC sample rate.
Eventually, the analog signal is up-converted, using a quadrature modulator,
to the RF carrier frequency, \f$f_c\f$, as

\f[
s\left( t \right) = {\mathop{\rm Re}\nolimits} \left\{ {\tilde s\left( t \right){e^{j2\pi {f_c}t}}} \right\}
\f]

\image html scheme.png DVB-T transmission scheme. 
\image latex scheme.png DVB-T transmission scheme. 

### IRIS

The DVB-TX-IRIS extension is an extension of the Iris framework. Iris is a
software architecture for building highly reconfigurable radio networks using 
a component-based design. The architecture comprises two repositories - 
Iris_Core and Iris_Modules. Iris_Core contains the core part of the architecture 
such as parsers, managers, and engines. Iris_Modules contain the components 
which can be used to create a software radio such as PHY-layer components and 
radio controllers. The Iris architecture, written in C++, supports all layers 
of the network stack and provides a platform for the development of not only 
reconfigurable point-to-point radio links, but complete networks of reconfigurable 
radios. Individual radios are described using an XML document. This lists the 
components which comprise the radio, gives the values to be used for their 
parameters and describes the connections between them. Iris was originally 
developed by CTVR, The Telecommunications Research Centre, based at University 
of Dublin, Trinity College. In 2013, it was released under the LGPL v3 license 
and is currently managed by Software Radio Systems (http://www.softwareradiosystems.com).

Since DVB-TX-IRIS extends Iris functionalities, there are shared requirements
that should be satisfied from the software point of view. In particular, they are:

*	Essential SW
**	Ubuntu Linux OS 32/64 bit (http://www.ubuntu.org), release 14.04 or later
**	CMake 2.6 or later (http://www.cmake.org/), an automated software build and test environment for C/C++
**	Boost 1.46 or later (http://www.boost.org/), an extensive collection of C++ libraries for accelerating common software tasks
**	Iris_Core (http://www.hostedredmine.com/projects/iris_software_radio/wiki), the core system of the Iris framework
**	Iris_Modules (http://www.hostedredmine.com/projects/iris_software_radio/wiki), additional modules for the Iris framework
**	FFTW (http://www.fftw.org/), a powerful C/C++ library for FFT transforms
**	UHD (http://code.ettus.com/redmine/ettus/projects/uhd/wiki), needed for the connection to USRP hardware
*	Optional SW
**	Qt 4.8 (http://qt-project.org/), used for building graphical widgets
**	Qwt 6 (http://qwt.sourceforge.net/), used for building graphical widgets
**	Liquid-DSP (https://github.com/jgaeddert/liquid-dsp), for some PHY components
**	Google Protocol Buffers (https://developers.google.com/protocol-buffers/), for some Stack components
**	Python (http://www.python.org/), for the PythonPlotter widget
**	Octave (http://www.octave.org/), for recreating the test vectors used during the testing phase of the build, and for running complete TX/RX simulations
**	Matlab (http://www.mathworks.com/), for the MatlabTemplate PHY component and MatlabPlotter widget
**	Doxygen (http://www.doxygen.org/), for the documentation
**	tzap (dvb-apps package) and w_scan (w-scan package), used for real-time stream quality testing with DVB-T USB receivers

From the hardware point of view, the following items are required:

*	Essential HW
**	A workstation or laptop PC equipped with a multicore CPU clocked at 2 GHz or more, 4 GB of RAM, 20 GB of free disk space, and a free Gigabit Ethernet connection
**	An Ettus USRP N210 equipped with an UHF/VHF capable daughterboard (such as the SBX or SBX120)
**	A UHF/VHF antenna (preferably directional antenna for longer communication range)
**	A DVB-T capable receiver (such as a TV set, a set-top box, or an USB dongle, provided with indoor reception antenna)
*	Optional HW
**	A spectrum analyzer for verifying the spectrum of the emitted DVB-T signal

## Compilation and installation