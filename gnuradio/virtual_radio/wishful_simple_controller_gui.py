#!/usr/bin/env python3

from tkinter import *
import pickle
import subprocess

import wishful_simple_controller as wsc

controller_pid = None
widget = None

from tkinter import *

class AppGui():

    def __init__(self, root):
        self.vr1_pkt_recv_info, self.vr1_pkt_right_info, self.vr1_cf_info, self.vr1_bw_info = self.build_vr_menu(1, root, self.vr1_tx_amplitude_update)



        self.vr2_pkt_recv_info, self.vr2_pkt_right_info, self.vr2_cf_info, self.vr2_bw_info = self.build_vr_menu(2, root, self.vr2_tx_amplitude_update)


    def build_vr_menu(self, vr_id, root, tx_amplitude_callback):
        vr_frame = LabelFrame(root, text="Virtual Radio %d" % (vr_id, ))
        vr_frame.pack(fill="both", expand="yes")

        # pkt total 
        vr_pkt_recv_frame = Frame(vr_frame)
        Label(vr_pkt_recv_frame, text="Pkt total: ").pack(side=LEFT)
        vr_pkt_recv_info = Label(vr_pkt_recv_frame, text="0")
        vr_pkt_recv_info.pack(side=LEFT)
        vr_pkt_recv_frame.pack()

        #pkt right
        vr_pkt_right_frame = Frame(vr_frame)
        Label(vr_pkt_right_frame, text="Pkt right: ").pack(side=LEFT)
        vr_pkt_right_info = Label(vr_pkt_right_frame, text="0")
        vr_pkt_right_info.pack(side=LEFT)
        vr_pkt_right_frame.pack()

        #center freq
        vr_cf_frame = Frame(vr_frame)
        Label(vr_cf_frame, text="Center frequency: ").pack(side=LEFT)
        vr_cf_info = Label(vr_cf_frame, text="0")
        vr_cf_info.pack(side=LEFT)
        vr_cf_frame.pack()

        # bandwidth
        vr_bw_frame = Frame(vr_frame)
        Label(vr_bw_frame, text="Bandwidth: ").pack(side=LEFT)
        vr_bw_info = Label(vr_bw_frame, text="0")
        vr_bw_info.pack(side=LEFT)
        vr_bw_frame.pack()

        # vr tx-amplitude
        vr_tx_amplitude_frame = Frame(vr_frame)
        Label(vr_tx_amplitude_frame, text="TX Amplitude [0:1]: ").pack(side=LEFT)
        scale = Scale(vr_tx_amplitude_frame, from_ = 0.0, to = 1.0, resolution= 0.001, orient = HORIZONTAL, command=tx_amplitude_callback)
        scale.pack(anchor=CENTER)
        vr_tx_amplitude_frame.pack()
        
        scale.set(0.3)



        return vr_pkt_recv_info, vr_pkt_right_info, vr_cf_info, vr_bw_info

    def vr1_tx_amplitude_update(self, val):
        sets = {}
        try:
            sets = pickle.load(open(wsc.SETTER_FILE, "rb"))
        except:
            pass

        if not 'tx' in sets:
            sets['tx'] = {}
    
        sets['tx'][wsc.VR_TX_GAIN.format(id=1)] = float(val)
        pickle.dump(sets, open(wsc.SETTER_FILE, "wb"))


    def vr2_tx_amplitude_update(self, val):
        sets = {}
        try:
            sets = pickle.load(open(wsc.SETTER_FILE, "rb"))
        except:
            pass

        if not 'tx' in sets:
            sets['tx'] = {}

        sets['tx'][wsc.VR_TX_GAIN.format(id=2)] = float(val)
        pickle.dump(sets, open(wsc.SETTER_FILE, "wb"))


def update():
    try:
        the_variables = pickle.load(open("./getter.bin", "rb"))
        widget.vr1_pkt_recv_info['text']  = the_variables['rx1_pkt_rcv'] if 'rx1_pkt_rcv' in the_variables else 'NA'
        widget.vr1_pkt_right_info['text'] = the_variables['rx1_pkt_right'] if 'rx1_pkt_right' in the_variables else 'NA'
        widget.vr1_cf_info['text'] = the_variables['rx1_center_freq'] if 'rx1_center_freq' in the_variables else 'NA'
        widget.vr1_bw_info['text'] = the_variables['rx1_bandwidth'] if 'rx1_bandwidth' in the_variables else 'NA'


        widget.vr2_pkt_recv_info['text']  = the_variables['rx2_pkt_rcv'] if 'rx2_pkt_rcv' in the_variables else 'NA'
        widget.vr2_pkt_right_info['text'] = the_variables['rx2_pkt_right'] if 'rx2_pkt_right' in the_variables else 'NA'
        widget.vr2_cf_info['text'] = the_variables['rx2_center_freq'] if 'rx2_center_freq' in the_variables else 'NA'
        widget.vr2_bw_info['text'] = the_variables['rx2_bandwidth'] if 'rx2_bandwidth' in the_variables else 'NA'


    except Exception as e:
        print(e)

    root.after(1000, update)
    
if __name__ == '__main__':
    root = Tk()
    widget = AppGui(root)

    controller_pid = subprocess.Popen('./wishful_simple_controller.py --write-to-file' , shell=True)

    root.after(5000, update)
    root.mainloop()

    controller_pid.kill()
