from tkinter import *

class AppGui():

    def __init__(self, root):
        vr1_pkt_recv_info, vr1_pkt_recv_info, vr1_tx_amplitude = self.build_vr_menu(1, root)


    def build_vr_menu(self, vr_id, root):
        vr_frame = LabelFrame(root, text="Virtual Radio %d" % (vr_id, ))
        vr_frame.pack(fill="both", expand="yes")

        # pkt total 
        vr_pkt_recv_frame = Frame(vr_frame)
        Label(vr_pkt_recv_frame, text="Pkt total: ").pack(side=LEFT)
        vr_pkt_recv_info = Label(vr_pkt_recv_frame, text="0").pack(side=LEFT)
        vr_pkt_recv_frame.pack()

        #pkt right
        vr_pkt_right_frame = Frame(vr_frame)
        Label(vr_pkt_right_frame, text="Pkt right: ").pack(side=LEFT)
        vr_pkt_right_info = Label(vr_pkt_right_frame, text="0").pack(side=LEFT)
        vr_pkt_right_frame.pack()

        # vr tx-amplitude
        vr_tx_amplitude = DoubleVar()
        vr_tx_amplitude_frame = Frame(vr_frame)
        Label(vr_tx_amplitude_frame, text="TX Amplitude [0:1]: ").pack(side=LEFT)
        vr_tx_amplitude_scale = Scale(vr_tx_amplitude_frame, variable = vr_tx_amplitude, from_ = 0.0, to = 1.0, resolution= 0.001, orient = HORIZONTAL).pack(anchor=CENTER)
        vr_tx_amplitude_frame.pack()

        return (vr_pkt_recv_info, vr_pkt_right_info, vr_tx_amplitude)


if __name__ == "__main__":
    root = Tk()
    AppGui(root)
    root.mainloop()
