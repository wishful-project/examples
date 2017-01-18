__author__ = 'domenico'

from Tkinter import *
import ttk
from PIL import Image, ImageTk

import random
from socket import *    # import *, but we'll avoid name conflict
from sys import argv, exit
import demjson
import json

import subprocess
#import webbrowser
import urllib2
import base64
import StringIO
import io
import urllib
import zmq
from urllib2 import urlopen, Request, URLError
import time
from thread import start_new_thread


SUNKABLE_BUTTON1 = 'SunkableButton.TButton'
SUNKABLE_BUTTON2 = 'SunkableButton.TButton'
SUNKABLE_BUTTON3 = 'SunkableButton.TButton'

DELAY = 1000

class Adder(ttk.Frame):
    """The adders gui and functions."""
    def __init__(self, parent, *args, **kwargs):
        ttk.Frame.__init__(self, parent, *args, **kwargs)
        self.root = parent
        self.init_gui()

    def on_quit(self):
        """Exits program."""
        quit()

    def calculate(self):
        """Calculates the sum of the two inputted numbers."""
        num1 = int(self.num1_entry.get())
        num2 = int(self.num2_entry.get())
        num3 = num1 + num2
        self.answer_label['text'] = num3

    def centreWindow(self):
        w = 1400
        h = 600
        sw = self.parent.winfo_screenwidth()
        sh = self.parent.winfo_screenheight()
        #x = (sw - w)/2
        #y = (sh - h)/2
        x = (sw - w)
        y = (sh - h)
        self.parent.geometry('%dx%d+%d+%d' % (w, h, x, y))

    def send_command_sta1(self, event):
        if self.local_network :
            command_list = {'type': 'protocol', 'command': self.countryVarSta1.get(), 'ip_address': self.sta1_ipaddress}
            json_command = command_list
            print(json_command)
            self.socket_command.send_json(json_command)

    def send_command_sta2(self, event):
        if self.local_network :
            command_list = {'type': 'protocol', 'command': self.countryVarSta2.get(), 'ip_address': self.sta2_ipaddress}
            json_command = command_list
            print(json_command)
            self.socket_command.send_json(json_command)

    def send_command_sta3(self, event):
        if self.local_network :
            command_list = {'type': 'protocol', 'command': self.countryVarSta3.get(), 'ip_address': self.sta3_ipaddress}
            json_command = command_list
            print(json_command)
            self.socket_command.send_json(json_command)

    def send_command_sta4(self, event):
        if self.local_network :
            command_list = {'type': 'protocol', 'command': self.countryVarSta4.get(), 'ip_address': self.sta4_ipaddress}
            json_command = command_list
            print(json_command)
            self.socket_command.send_json(json_command)

    def stopTraffic(self):
        command = 'stop'
        if self.local_network :
            command_list = {'type': 'traffic', 'command': command}
            json_command = command_list
            print(json_command)
            self.socket_command.send_json(json_command)

        self.stopTrafficBtn.state(['pressed', 'disabled'])
        self.style.configure(SUNKABLE_BUTTON1, relief=SUNKEN, foreground='green')

        self.lowTrafficBtn.state(['!pressed', '!disabled'])
        self.style.configure(SUNKABLE_BUTTON2, relief=RAISED, foreground='red')

        self.highTrafficBtn.state(['!pressed', '!disabled'])
        self.style.configure(SUNKABLE_BUTTON3, relief=RAISED, foreground='red')

    def startTrafficLow(self):
        command = 'start_low'
        if self.local_network :
            command_list = {'type': 'traffic', 'command': command}
            json_command = command_list
            print(json_command)
            self.socket_command.send_json(json_command)

        self.lowTrafficBtn.state(['pressed', 'disabled'])
        self.style.configure(SUNKABLE_BUTTON2, relief=SUNKEN, foreground='green')

        self.stopTrafficBtn.state(['!pressed', '!disabled'])
        self.style.configure(SUNKABLE_BUTTON1, relief=RAISED, foreground='red')

        self.highTrafficBtn.state(['!pressed', '!disabled'])
        self.style.configure(SUNKABLE_BUTTON3, relief=RAISED, foreground='red')

    def startTrafficHigh(self):
        command = 'start_high'
        if self.local_network :
            command_list = {'type': 'traffic', 'command': command}
            json_command = command_list
            print(json_command)
            self.socket_command.send_json(json_command)

        self.highTrafficBtn.state(['pressed', 'disabled'])
        self.style.configure(SUNKABLE_BUTTON3, relief=SUNKEN, foreground='green')

        self.stopTrafficBtn.state(['!pressed', '!disabled'])
        self.style.configure(SUNKABLE_BUTTON1, relief=RAISED, foreground='red')

        self.lowTrafficBtn.state(['!pressed', '!disabled'])
        self.style.configure(SUNKABLE_BUTTON2, relief=RAISED, foreground='red')


    def loopCapture(self,x):
        if self.local_network :
            #location='http://10.8.19.1/crewdemo/plots/usrp.png'
            location='http://10.8.9.3/crewdemo/plots/usrp.png'
        else :
            location='http://127.0.0.1:8484/crewdemo/plots/usrp.png'

        urllib2.urlopen(location)
        import matplotlib.pyplot as plt
        import matplotlib
        matplotlib.use("TkAgg")
        from matplotlib import rcParams
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
        from matplotlib.figure import Figure
        import numpy
        import cStringIO
        rcParams.update({'figure.autolayout': True})

        plt.ion()
        f = Figure(frameon=False)
        ax = f.add_subplot(111)
        im = None

        init = 1
        while True:
            if init:
                try:
                    # import matplotlib.image as mpimg
                    # img = mpimg.imread("image.png")
                    file = cStringIO.StringIO(urllib.urlopen(location).read())
                    img = Image.open(file)

                    wpercent=50
                    basewidth = 350
                    wpercent = (basewidth/float(img.size[0]))
                    hsize = int((float(img.size[1])*float(wpercent)))
                    img = img.resize((basewidth,hsize), Image.ANTIALIAS)

                    #ax.imshow(img, aspect = 'normal')
                    im = ax.imshow(img)
                    ax.axis("off")

                    # ax.autoscale(False)
                    # ax.patch.set_visible(False)

                    my_dpi=100
                    width=1200
                    height=400
                    f.set_size_inches(width/my_dpi,height/my_dpi)


                    self.channel_frame=ttk.LabelFrame(self, text="Channel occupation", height=20, width=100)
                    self.channel_frame.grid(column=2, row=2, columnspan=1, sticky='nw')

                    canvas = FigureCanvasTkAgg(f, self.channel_frame)
                    canvas.show()
                    #canvas.get_tk_widget().configure(background='white',  highlightcolor='white', highlightbackground='white')
                    canvas.get_tk_widget().grid(column=0, row=0, columnspan=1, sticky='nw')

                except Exception as e:
                    print(e)

                init = 0

            else:
                file = cStringIO.StringIO(urllib.urlopen(location).read())
                if file:
                    try:
                        img = Image.open(file)
                        im.set_data(img)
                        f.canvas.draw()
                    except Exception as e:
                        print(e)
                        print('ERRORE open image')
                else:
                    print('ERRORE download image')


            time.sleep(1)



    line1 = None
    line2 = None
    line3 = None
    line4 = None
    f = None
    def loop_statistics(self,x):
        global line1
        global f

        init = 1
        while True:
            if init:
                try:
                    import matplotlib.pyplot as plt
                    import matplotlib
                    matplotlib.use("TkAgg")
                    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
                    from matplotlib.figure import Figure
                    import numpy
                    from matplotlib import rcParams
                    rcParams.update({'figure.autolayout': True})


                    plt.ion()
                    #f = Figure(figsize=(5,2.9), dpi=100)
                    f = Figure()
                    ax = f.add_subplot(111)


                    # self.yval.append( numpy.nan_to_num( stats.get('psucc') ) )
                    # yy=self.yval[::-1]
                    # yy=yy[0:self.Nplot]
                    # self.yval=yy[::-1]
                    ax.grid(True)
                    ax.set_xlabel('Time [s]', fontsize=12)
                    ax.set_ylabel('Protocol')

                    #self.tick=(self.tick+1) % self.Nplot

                    #ax.plot(self.xval,self.yval[::-1])
                    line1, = ax.plot(self.xval, self.sta1val)
                    line2, = ax.plot(self.xval, self.sta2val)
                    line3, = ax.plot(self.xval, self.sta3val)
                    line4, = ax.plot(self.xval, self.sta4val)

                    labels = ['', 'P1', 'P2', 'P3', 'P4', 'P5', '']
                    # set the tick labels
                    ax.set_yticklabels(labels, rotation=45)

                    ax.set_ylim([0, 6])
                    ax.patch.set_facecolor('white')
                    f.set_facecolor('white')

                    my_dpi=100
                    width=1200
                    height=400
                    f.set_size_inches(width/my_dpi,height/my_dpi)
                    #plt.tight_layout()


                    self.statistics_frame=ttk.LabelFrame(self, text="Plot statistics", height=100, width=300)
                    self.statistics_frame.grid(column=2, row=1, columnspan=1, sticky='nesw')

                    canvas = FigureCanvasTkAgg(f, self.statistics_frame)
                    canvas.show()
                    canvas.get_tk_widget().configure(background='white',  highlightcolor='white', highlightbackground='white')
                    canvas.get_tk_widget().grid(column=0, row=0, columnspan=1, sticky='nesw')

                except Exception as e:
                    print e
                    pass

                #toolbar = NavigationToolbar2TkAgg(canvas, self.statistics_frame)
                #toolbar.update()
                #canvas._tkcanvas.pack(side=Tk.TOP, fill=Tk.BOTH, expand=True)

                init = 0

            else:
                line1.set_ydata(self.sta1val)
                line2.set_ydata(self.sta2val)
                line3.set_ydata(self.sta3val)
                line4.set_ydata(self.sta4val)
                f.canvas.draw()


            time.sleep(1)

        # self.root.update_idletasks()
        # self.root.after(DELAY, self.loop_statistics(init=0))


    def receive_data_plot(self,x):

        while True:    # Run until cancelled

            parsed_json = self.socket_plot.recv_json()
            #print('parsed_json : %s' % str(parsed_json))
            #parsed_json : {u'wlan_ip_address': u'192.168.3.110', u'measure': [[2668741, 4, 0.0]]}
            remote_ipAddress = parsed_json['wlan_ip_address']
            measure = parsed_json['measure'][0]


            # len_station_dump = len(stations_dump)
            # #print 'len_station_dump %d' % len_station_dump
            #
			# # add measurement on nodes element
			# for i in range(0,len_station_dump):
             #    #print 'stations_dump[i][0] (%s) == remote_wlan_ipAddress (%s)' % (str(stations_dump[i][0]), str(remote_wlan_ipAddress) )
			# 	if stations_dump[i][0] == remote_ipAddress :
             #        stations_dump[i][2] = float(parsed_json['active'])+1	#active protocol
             #        stations_dump[i][3] = float(parsed_json['0'][0])	#protocol 1 weigth
             #        stations_dump[i][4] = parsed_json['0'][1]	#protocol 1 name

            if self.sta1_ipaddress.split('.')[3] == remote_ipAddress.split('.')[3] :
                self.sta1val.pop(0)
                self.sta1val.append( float(measure[1]) + 1 - 0.1   )
                self.sta1_log_Label.config(text="STA1 PROTOCOL={}".format(float(measure[1]) + 1))

            if self.sta2_ipaddress.split('.')[3] == remote_ipAddress.split('.')[3] :
                self.sta2val.pop(0)
                self.sta2val.append( float(measure[1]) + 1 - 0.2   )
                self.sta2_log_Label.config(text="STA2 PROTOCOL={}".format(float(measure[1]) + 1))

            if self.sta3_ipaddress.split('.')[3] == remote_ipAddress.split('.')[3] :
                self.sta3val.pop(0)
                self.sta3val.append( float(measure[1]) + 1 + 0.1   )
                self.sta3_log_Label.config(text="STA3 PROTOCOL={}".format(float(measure[1]) + 1))

            if self.sta4_ipaddress.split('.')[3] == remote_ipAddress.split('.')[3] :
                self.sta4val.pop(0)
                self.sta4val.append( float(measure[1]) + 1 + 0.2   )
                self.sta4_log_Label.config(text="STA4 PROTOCOL={}".format(float(measure[1]) + 1))



    def init_gui(self):

        #VISUALIZER CONFIGURATION
        self.local_network = 1
        self.Nplot=100
        #self.yval=[0 for x in range(0,self.Nplot)]
        self.sta1val=[1 for x in range(0,self.Nplot)]
        self.sta2val=[2 for x in range(0,self.Nplot)]
        self.sta3val=[3 for x in range(0,self.Nplot)]
        self.sta4val=[4 for x in range(0,self.Nplot)]
        self.xval=[x for x in range(0,self.Nplot)]
        self.tick=0;

        """GUI SETUP"""
        print('GUI setup')
        self.root.title('WISHFUL DEMO YEAR 2')
        self.root.option_add('*tearOff', 'FALSE')

        self.parent = self.root
        self.root.title("WISHFUL DEMO YEAR 2")
        self.style = ttk.Style()
        self.style.theme_use("default")
        self.centreWindow()
        self.pack(fill=BOTH, expand=1)

        self.grid(column=0, row=0, sticky='nsew')

        self.menubar = Menu(self.root)

        self.menu_file = Menu(self.menubar)
        self.menu_file.add_command(label='Exit', command=self.on_quit)

        self.menu_edit = Menu(self.menubar)
        self.menubar.add_cascade(menu=self.menu_file, label='File')
        self.menubar.add_cascade(menu=self.menu_edit, label='Edit')

        self.root.config(menu=self.menubar)

        # self.num1_entry = ttk.Entry(self, width=5)
        # self.num1_entry.grid(column=1, row = 2)
        #
        # self.num2_entry = ttk.Entry(self, width=5)
        # self.num2_entry.grid(column=3, row=2)
        #
        # self.calc_button = ttk.Button(self, text='Calculate', command=self.calculate)
        # self.calc_button.grid(column=0, row=3, columnspan=4)


        #IMAGE
        # bard = Image.open("header2.png")
        # bardejov = ImageTk.PhotoImage(bard)
        # label1 = Label(self, image=bardejov)
        # label1.image = bardejov
        # #label1.place(x=5, y=150)
        # #label1.grid(row=0,column=0, sticky=W+E)
        # label1.grid(row=0,column=0, columnspan=3, sticky=W+E+N+S, padx=5, pady=5)



        #Protocol FRAME
        self.protocol_frame = ttk.LabelFrame(self, text='Protocol', height=100, width=100)
        self.protocol_frame.grid(column=0, row=1, columnspan=1, sticky='nesw')

        self.LabelProtocol = Label(self.protocol_frame, text="Select Protocol")
        #self.LabelProtocol.pack(side=TOP, anchor=CENTER, expand=NO)
        self.LabelProtocol.grid(row=0, column=0, padx=5, pady=5, ipady=2, sticky=W)

        #station1
        countryLabelSta1 = Label(self.protocol_frame, text="Station 1")
        countryLabelSta1.grid(row=1, column=0, sticky=W+E)
        self.countryVarSta1 = StringVar()
        self.countryComboSta1 = ttk.Combobox(self.protocol_frame, textvariable=self.countryVarSta1)
        self.countryComboSta1['values'] = ('METAMAC', 'TDMA 1', 'TDMA 2', 'TDMA 3', 'TDMA 4', 'ALOHA')
        self.countryComboSta1.current(0)
        #self.countryComboSta1.bind("<<ComboboxSelected>>", self.send_command(self.sta1_ipaddress, self.countryVarSta1.get()))
        self.countryComboSta1.bind("<<ComboboxSelected>>", self.send_command_sta1)
        self.countryComboSta1.grid(row=1, column=1, padx=5, pady=5, ipady=2, sticky=W)
        #self.countryComboSta1.pack(side=TOP, anchor=CENTER, expand=NO)

        #station2
        countryLabelSta2 = Label(self.protocol_frame, text="Station 2")
        countryLabelSta2.grid(row=2, column=0, sticky=W+E)
        self.countryVarSta2 = StringVar()
        self.countryComboSta2 = ttk.Combobox(self.protocol_frame, textvariable=self.countryVarSta2)
        self.countryComboSta2['values'] = ('METAMAC', 'TDMA 1', 'TDMA 2', 'TDMA 3', 'TDMA 4', 'ALOHA')
        self.countryComboSta2.current(0)
        #self.countryComboSta2.bind("<<ComboboxSelected>>", self.send_command(self.sta2_ipaddress, self.countryVarSta2.get()))
        self.countryComboSta2.bind("<<ComboboxSelected>>", self.send_command_sta2)
        self.countryComboSta2.grid(row=2, column=1, padx=5, pady=5, ipady=2, sticky=W)
        #self.countryComboSta2.pack(side=TOP, anchor=CENTER, expand=NO)

        #station3
        countryLabelSta3 = Label(self.protocol_frame, text="Station 3")
        countryLabelSta3.grid(row=3, column=0, sticky=W+E)
        self.countryVarSta3 = StringVar()
        self.countryComboSta3 = ttk.Combobox(self.protocol_frame, textvariable=self.countryVarSta3)
        self.countryComboSta3['values'] = ('METAMAC', 'TDMA 1', 'TDMA 2', 'TDMA 3', 'TDMA 4', 'ALOHA')
        self.countryComboSta3.current(0)
        #self.countryComboSta3.bind("<<ComboboxSelected>>", self.send_command(self.sta3_ipaddress, self.countryVarSta3.get()))
        self.countryComboSta3.bind("<<ComboboxSelected>>", self.send_command_sta3)
        self.countryComboSta3.grid(row=3, column=1, padx=5, pady=5, ipady=2, sticky=W)
        #self.countryComboSta3.pack(side=TOP, anchor=CENTER, expand=NO)

        #station4
        countryLabelSta4 = Label(self.protocol_frame, text="Station 4")
        countryLabelSta4.grid(row=4, column=0, sticky=W+E)
        self.countryVarSta4 = StringVar()
        self.countryComboSta4 = ttk.Combobox(self.protocol_frame, textvariable=self.countryVarSta4)
        self.countryComboSta4['values'] = ('METAMAC', 'TDMA 1', 'TDMA 2', 'TDMA 3', 'TDMA 4', 'ALOHA')
        self.countryComboSta4.current(0)
        #self.countryComboSta4.bind("<<ComboboxSelected>>", self.send_command(self.sta4_ipaddress, self.countryVarSta4.get()))
        self.countryComboSta4.bind("<<ComboboxSelected>>", self.send_command_sta4)
        self.countryComboSta4.grid(row=4, column=1, padx=5, pady=5, ipady=2, sticky=W)
        #self.countryComboSta4.pack(side=TOP, anchor=CENTER, expand=NO)


        #PROTOCOL INFORMATION
        self.stats_frame = ttk.LabelFrame(self, text='Monitor Protocol', height=100, width=50)
        self.stats_frame.grid(column=1, row=1, columnspan=1, sticky='nesw')
        self.sta1_log_Label=Label(self.stats_frame, text="STA1 PROTOCOL={}".format(self.sta1val[self.Nplot-1]))
        self.sta1_log_Label.grid(column=0,row=1,sticky=W)
        self.sta2_log_Label=Label(self.stats_frame, text="STA2 PROTOCOL={}".format(self.sta2val[self.Nplot-1]))
        self.sta2_log_Label.grid(column=0,row=2,sticky=W)
        self.sta3_log_Label=Label(self.stats_frame, text="STA3 PROTOCOL={}".format(self.sta3val[self.Nplot-1]))
        self.sta3_log_Label.grid(column=0,row=3,sticky=W)
        self.sta4_log_Label=Label(self.stats_frame, text="STA4 PROTOCOL={}".format(self.sta4val[self.Nplot-1]))
        self.sta4_log_Label.grid(column=0,row=4,sticky=W)

        #TRAFFIC FRAME
        self.traffic_frame = ttk.LabelFrame(self, text='Traffic', height=100, width=50)
        self.traffic_frame.grid(column=1, row=2, columnspan=1, sticky='nesw')

        self.LabelTraffic = Label(self.traffic_frame, text="Select traffic")
        #self.LabelTraffic.pack(side=TOP, anchor=CENTER, expand=NO)
        self.LabelTraffic.grid(row=0, column=0, padx=15, pady=15, ipady=2, sticky=W)

        self.stopTrafficBtn = ttk.Button(self.traffic_frame, text="STOP", width=10, command=self.stopTraffic,  style=SUNKABLE_BUTTON1)
        #self.stopTrafficBtn.pack(side=TOP, anchor=CENTER, expand=NO)
        self.stopTrafficBtn.grid(row=1, column=0, padx=15, pady=15, ipady=2, sticky=W)
        self.lowTrafficBtn = ttk.Button(self.traffic_frame, text="LOW", width=10, command=self.startTrafficLow,  style=SUNKABLE_BUTTON2)
        #self.lowTrafficBtn.pack(side=TOP, anchor=CENTER, expand=NO)
        self.lowTrafficBtn.grid(row=2, column=0, padx=15, pady=15, ipady=2, sticky=W)
        self.highTrafficBtn = ttk.Button(self.traffic_frame, text="HIGH", width=10, command=self.startTrafficHigh,  style=SUNKABLE_BUTTON3)
        #self.highTrafficBtn.pack(side=TOP, anchor=CENTER, expand=NO)
        self.highTrafficBtn.grid(row=3, column=0, padx=15, pady=15, ipady=2, sticky=W)


        #USRP FRAME
        start_new_thread(self.loopCapture,(99,))

        #PLOT TOPOLOGY IMAGE
        self.topo_frame=ttk.LabelFrame(self, text="Network Scenario", height=100, width=100)
        self.topo_frame.grid(column=0, row=2, columnspan=1, sticky='nesw')

        img=Image.open('metamac-topology.png')
        wpercent=50
        basewidth = 350
        wpercent = (basewidth/float(img.size[0]))
        hsize = int((float(img.size[1])*float(wpercent)))
        img = img.resize((basewidth,hsize), Image.ANTIALIAS)
        im = ImageTk.PhotoImage(img)

        label_topo_img = Label(self.topo_frame, image=im)
        label_topo_img.image = im
        label_topo_img.grid(row=0,column=0, sticky=W+E)


        #NETWORK SOCKET SETUP
        print('Network socket setup')

        if self.local_network :
            self.sta1_ipaddress = '10.8.8.104'
            self.sta2_ipaddress = '10.8.8.105'
            self.sta3_ipaddress = '10.8.8.110'
            self.sta4_ipaddress = '10.8.8.111'
            self.socket_command_port = 8400
            self.sta1_server_port = self.socket_command_port
            self.sta2_server_port = self.socket_command_port
            self.sta3_server_port = self.socket_command_port
            self.sta4_server_port = self.socket_command_port
            self.context1 = zmq.Context()
            print("Connecting to server on port 8400 ... ready to send command to demo experiment node")
            self.socket_command = self.context1.socket(zmq.PAIR)
            self.socket_command.connect ("tcp://localhost:%s" % self.socket_command_port)

            self.socket_plot_port  = 8401
            self.context2 = zmq.Context()
            print("Connecting to server on port 8401 ... ready to receive protocol information from demo experiment node")
            self.socket_plot = self.context2.socket(zmq.SUB)
            self.socket_plot.connect ("tcp://localhost:%s" % self.socket_plot_port)
            self.socket_plot.setsockopt(zmq.SUBSCRIBE, '')
            start_new_thread(self.receive_data_plot,(99,))

        else :
            #global socket_visualizer
            self.server_port = 8301
            context = zmq.Context()
            print("Connecting to server on port 8301 ... ready to send command to demo nodes")
            self.socket_command = context.socket(zmq.REQ)
            self.socket_command.connect ("tcp://localhost:%s" % self.server_port)

            self.sta1_ipaddress = '10.8.8.103'
            self.sta2_ipaddress = '10.8.8.104'
            self.sta3_ipaddress = '10.8.8.105'
            self.sta4_ipaddress = '10.8.8.115'
            self.sta1_server_port = self.server_port
            self.sta2_server_port = self.server_port
            self.sta3_server_port = self.server_port
            self.sta4_server_port = self.server_port






        start_new_thread(self.loop_statistics,(99,))

        # ttk.Separator(self, orient='horizontal').grid(column=0,
        #         row=1, columnspan=4, sticky='ew')
        #
        for child in self.winfo_children():
            child.grid_configure(padx=5, pady=5)

if __name__ == '__main__':
    root = Tk()
    Adder(root)
    root.mainloop()