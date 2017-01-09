#!/usr/bin/env python3

from tkinter import *
from wishful_simple_controller import *

import pickle
import subprocess

controller_pid = None
widget = None

from tkinter import *

class AppGui():

    def __init__(self, root):

        self.vr1_pkt_recv_info, self.vr1_pkt_right_info, self.vr1_tx_amplitude = self.build_vr_menu(1, root)

        print(self.vr1_pkt_right_info)


    def build_vr_menu(self, vr_id, root):
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

        # vr tx-amplitude
        vr_tx_amplitude = DoubleVar()
        vr_tx_amplitude_frame = Frame(vr_frame)
        Label(vr_tx_amplitude_frame, text="TX Amplitude [0:1]: ").pack(side=LEFT)
        vr_tx_amplitude_scale = Scale(vr_tx_amplitude_frame, variable = vr_tx_amplitude, from_ = 0.0, to = 1.0, resolution= 0.001, orient = HORIZONTAL).pack(anchor=CENTER)
        vr_tx_amplitude_frame.pack()

        return vr_pkt_recv_info, vr_pkt_right_info, vr_tx_amplitude


def update():

    try:
        the_variables = pickle.load(open("controller_data.bin", "rb" ) )

        widget.vr1_pkt_recv_info['text']  = the_variables['rx1_pkt_rcv']
        widget.vr1_pkt_right_info['text'] = the_variables['rx1_pkt_right']

    except Exception as e:
        print(e)

    root.after(1000, update)
    

if __name__ == '__main__':
    root = Tk()
    widget = AppGui(root)

    controller_pid = subprocess.Popen('./wishful_simple_controller.py --write-to-file' , shell=True)

    root.after(1000, update)
    root.mainloop()


    controller_pid.communicate('exit\n')
    controller_pid.kill()
