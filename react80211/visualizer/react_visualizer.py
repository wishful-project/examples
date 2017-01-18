__author__ = 'domenico'

from Tkinter import *
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
import ttk


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
        w = 1500
        h = 700
        sw = self.parent.winfo_screenwidth()
        sh = self.parent.winfo_screenheight()
        #x = (sw - w)/2
        #y = (sh - h)/2
        x = (sw - w)
        y = (sh - h)
        self.parent.geometry('%dx%d+%d+%d' % (w, h, x, y))


    def stopReact(self):
        command = 'stop_react'
        if self.local_network :
            json_command = {'type': 'algorithm', 'command': command}
            print(json_command)
            self.socket_command.send_json(json_command)

        self.stopReactBtn.state(['pressed', 'disabled'])
        self.style.configure(SUNKABLE_BUTTON1, relief=SUNKEN, foreground='red')

        self.startReactBtn.state(['!pressed', '!disabled'])
        self.style.configure(SUNKABLE_BUTTON2, relief=RAISED, foreground='green')

    def startReact(self):
        command = 'start_react'
        if self.local_network :
            json_command = {'type': 'algorithm', 'command': command}
            print(json_command)
            self.socket_command.send_json(json_command)

        self.startReactBtn.state(['pressed', 'disabled'])
        self.style.configure(SUNKABLE_BUTTON2, relief=SUNKEN, foreground='red')

        self.stopReactBtn.state(['!pressed', '!disabled'])
        self.style.configure(SUNKABLE_BUTTON1, relief=RAISED, foreground='green')


    def setTraffic(self, src, val):

        if src == 'A':
            dst = self.countryVarA.get()
        elif src == 'B':
            dst = self.countryVarB.get()
        elif src == 'C':
            dst = self.countryVarC.get()
        else:
            print('bad source node')
            return

        val = int(val)
        if 500 < val and val <= 6000:
            command = 'set_traffic'
            round_val = round(val/1000)*1000
            if (val - round_val) > 500 :
                round_val += 1000
            self.command_list = {'type': 'traffic', 'command': command, 'src' : src, 'dst' : dst, 'value' : round_val}
        else:
            round_val = 0
            command = 'off_traffic'
            self.command_list = {'type': 'traffic', 'command': command, 'src' : src, 'dst' : dst}

        self.last_traffic_update_time = time.time()
        self.traffic_update_command = self.command_list

        print(self.command_list)
        #self.socket_command.send_json(self.command_list)

    def traffic_command_handles(self,x):
        while True:
            if time.time() - self.last_traffic_update_time > 1.3 and self.traffic_update_command != self.last_traffic_update_command:
                if self.local_network :
                    print('command sent %s' % str(self.command_list))
                    self.socket_command.send_json(self.command_list)
                    self.last_traffic_update_time = time.time()
                    self.last_traffic_update_command = self.traffic_update_command
            time.sleep(1)


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



    line1_psucc = None
    line2_psucc = None
    line3_psucc = None
    line4_psucc = None
    line5_psucc = None
    line6_psucc = None
    figure_psucc = None
    def plotpsucc(self,x):
        global line1_psucc
        global line2_psucc
        global line3_psucc
        global line4_psucc
        global line5_psucc
        global line6_psucc
        global figure_psucc
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
                    figure_psucc = Figure()
                    figure_psucc.set_facecolor('white')
                    ax = figure_psucc.add_subplot(111)

                    # self.yval.append( numpy.nan_to_num( stats.get('psucc') ) )
                    # yy=self.yval[::-1]
                    # yy=yy[0:self.Nplot]
                    # self.yval=yy[::-1]
                    ax.grid(True)
                    ax.set_xlabel('Time [s]', fontsize=12)
                    ax.set_ylabel('Success probability')

                    line1_psucc, = ax.plot(self.xval_psucc, self.sta1val_psucc, label='Node A')
                    line2_psucc, = ax.plot(self.xval_psucc, self.sta2val_psucc, label='Node B')
                    line3_psucc, = ax.plot(self.xval_psucc, self.sta3val_psucc, label='Node C')
                    # line4_psucc, = ax.plot(self.xval_psucc, self.sta4val_psucc, label='Node D')
                    # line5_psucc, = ax.plot(self.xval_psucc, self.sta5val_psucc, label='Node E')
                    # line6_psucc, = ax.plot(self.xval_psucc, self.sta6val_psucc, label='Node F')

                    ax.set_ylim([-0.1, 1.1])
                    ax.patch.set_facecolor('white')
                    #legend = ax.legend(loc='upper center', shadow=True, ncol=3)

                    my_dpi=100
                    width=600
                    height=400
                    figure_psucc.set_size_inches(width/my_dpi,height/my_dpi)
                    #plt.tight_layout()
                    self.statistics_psucc_frame=ttk.LabelFrame(self, text="Plot success probability", height=height, width=width)
                    self.statistics_psucc_frame.grid(column=0, row=2, columnspan=1, sticky='nesw')

                    canvas = FigureCanvasTkAgg(figure_psucc, self.statistics_psucc_frame)
                    canvas.show()
                    canvas.get_tk_widget().configure(background='white',  highlightcolor='white', highlightbackground='white')
                    canvas.get_tk_widget().grid(column=0, row=0, columnspan=1, sticky='nesw')

                except Exception as e:
                    print e
                    pass

                init = 0

            else:
                line1_psucc.set_ydata(self.sta1val_psucc)
                line2_psucc.set_ydata(self.sta2val_psucc)
                line3_psucc.set_ydata(self.sta3val_psucc)
                # line4_psucc.set_ydata(self.sta4val_psucc)
                # line5_psucc.set_ydata(self.sta5val_psucc)
                # line6_psucc.set_ydata(self.sta6val_psucc)
                figure_psucc.canvas.draw()
            time.sleep(1)


    line1_airtime = None
    line2_airtime = None
    line3_airtime = None
    line4_airtime = None
    line5_airtime = None
    line6_airtime = None
    figure_airtime = None
    def plotairtime(self,x):
        global line1_airtime
        global line2_airtime
        global line3_airtime
        global line4_airtime
        global line5_airtime
        global line6_airtime
        global figure_airtime
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
                    figure_airtime = Figure()
                    figure_airtime.set_facecolor('white')
                    ax = figure_airtime.add_subplot(111)

                    # self.yval.append( numpy.nan_to_num( stats.get('airtime') ) )
                    # yy=self.yval[::-1]
                    # yy=yy[0:self.Nplot]
                    # self.yval=yy[::-1]
                    ax.grid(True)
                    ax.set_xlabel('Time [s]', fontsize=12)
                    ax.set_ylabel('Airtime')

                    line1_airtime, = ax.plot(self.xval_airtime, self.sta1val_airtime, label='Node A')
                    line2_airtime, = ax.plot(self.xval_airtime, self.sta2val_airtime, label='Node B')
                    line3_airtime, = ax.plot(self.xval_airtime, self.sta3val_airtime, label='Node C')
                    line4_airtime, = ax.plot(self.xval_airtime, self.sta4val_airtime, label='Node D')
                    line5_airtime, = ax.plot(self.xval_airtime, self.sta5val_airtime, label='Node E')
                    line6_airtime, = ax.plot(self.xval_airtime, self.sta6val_airtime, label='Node F')

                    ax.set_ylim([-0.1, 1.1])
                    ax.patch.set_facecolor('white')
                    #legend = ax.legend(loc='upper center', shadow=True, ncol=3)

                    my_dpi=100
                    width=600
                    height=400
                    figure_airtime.set_size_inches(width/my_dpi,height/my_dpi)
                    #plt.tight_layout()
                    self.statistics_airtime_frame=ttk.LabelFrame(self, text="Plot Airtime", height=height, width=width)
                    self.statistics_airtime_frame.grid(column=1, row=2, columnspan=1, sticky='nesw')

                    canvas = FigureCanvasTkAgg(figure_airtime, self.statistics_airtime_frame)
                    canvas.show()
                    canvas.get_tk_widget().configure(background='white',  highlightcolor='white', highlightbackground='white')
                    canvas.get_tk_widget().grid(column=0, row=0, columnspan=1, sticky='nesw')

                except Exception as e:
                    print e
                    pass

                init = 0

            else:
                line1_airtime.set_ydata(self.sta1val_airtime)
                line2_airtime.set_ydata(self.sta2val_airtime)
                line3_airtime.set_ydata(self.sta3val_airtime)
                # line4_airtime.set_ydata(self.sta4val_airtime)
                # line5_airtime.set_ydata(self.sta5val_airtime)
                # line6_airtime.set_ydata(self.sta6val_airtime)
                figure_airtime.canvas.draw()

            time.sleep(1)


    line1_cw = None
    line2_cw = None
    line3_cw = None
    line4_cw = None
    line5_cw = None
    line6_cw = None
    figure_cw = None
    def plotcw(self,x):
        global line1_cw
        global line2_cw
        global line3_cw
        global line4_cw
        global line5_cw
        global line6_cw
        global figure_cw
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
                    figure_cw = Figure()
                    figure_cw.set_facecolor('white')
                    ax = figure_cw.add_subplot(111)

                    # self.yval.append( numpy.nan_to_num( stats.get('cw') ) )
                    # yy=self.yval[::-1]
                    # yy=yy[0:self.Nplot]
                    # self.yval=yy[::-1]
                    ax.grid(True)
                    ax.set_xlabel('Time [s]', fontsize=12)
                    ax.set_ylabel('Contention window')

                    line1_cw, = ax.plot(self.xval_cw, self.sta1val_cw, label='Node A')
                    line2_cw, = ax.plot(self.xval_cw, self.sta2val_cw, label='Node B')
                    line3_cw, = ax.plot(self.xval_cw, self.sta3val_cw, label='Node C')
                    # line4_cw, = ax.plot(self.xval_cw, self.sta4val_cw, label='Node D')
                    # line5_cw, = ax.plot(self.xval_cw, self.sta5val_cw, label='Node E')
                    # line6_cw, = ax.plot(self.xval_cw, self.sta6val_cw, label='Node F')

                    ax.set_ylim([0, 1100])
                    ax.patch.set_facecolor('white')
                    legend = ax.legend(loc='upper center', shadow=True, ncol=3)

                    my_dpi=100
                    width=600
                    height=400
                    figure_cw.set_size_inches(width/my_dpi,height/my_dpi)
                    #plt.tight_layout()
                    self.statistics_cw_frame=ttk.LabelFrame(self, text="Plot Contention window", height=height, width=width)
                    self.statistics_cw_frame.grid(column=2, row=2, columnspan=1, sticky='nesw')

                    canvas = FigureCanvasTkAgg(figure_cw, self.statistics_cw_frame)
                    canvas.show()
                    canvas.get_tk_widget().configure(background='white',  highlightcolor='white', highlightbackground='white')
                    canvas.get_tk_widget().grid(column=0, row=0, columnspan=1, sticky='nesw')

                except Exception as e:
                    print e
                    pass

                init = 0

            else:
                line1_cw.set_ydata(self.sta1val_cw)
                line2_cw.set_ydata(self.sta2val_cw)
                line3_cw.set_ydata(self.sta3val_cw)
                # line4_cw.set_ydata(self.sta4val_cw)
                # line5_cw.set_ydata(self.sta5val_cw)
                # line6_cw.set_ydata(self.sta6val_cw)
                figure_cw.canvas.draw()
            time.sleep(1)




    #*****************
    #reveive data plot from controller
    #*****************
    def receive_data_plot(self,x):
        while True:    # Run until cancelled
            parsed_json = self.socket_plot.recv_json()
            #print('parsed_json : %s' % str(parsed_json))
            #parsed_json : {u'label': u'C', u'measure': [[1484644417.3528204, 0.0, 0.0, 1.0, 0.0, 1023, 0, 0]], u'mac_address': u'00:0e:8e:30:9d:ee'}
            label = parsed_json['label']
            if label :
                measure = parsed_json['measure'][0]
                if label == 'A':
                    item = 'I001'
                    self.sta1val_cw.pop(0)
                    self.sta1val_cw.append( float(measure[5]) )

                    self.sta1val_psucc.pop(0)
                    self.sta1val_psucc.append( float(measure[6]) )

                    self.sta1val_airtime.pop(0)
                    self.sta1val_airtime.append( float(measure[7]) )

                    #self.sta1_log_Label.config(text="STA1 PROTOCOL={}".format(float(measure[1]) + 1))

                elif label == 'B':
                    item = 'I002'
                    self.sta2val_cw.pop(0)
                    self.sta2val_cw.append( float(measure[5]) )

                    self.sta2val_psucc.pop(0)
                    self.sta2val_psucc.append( float(measure[6]) )

                    self.sta2val_airtime.pop(0)
                    self.sta2val_airtime.append( float(measure[7]) )

                elif label == 'C':
                    item = 'I003'
                    self.sta3val_cw.pop(0)
                    self.sta3val_cw.append( float(measure[5]) )

                    self.sta3val_psucc.pop(0)
                    self.sta3val_psucc.append( float(measure[6]) )

                    self.sta3val_airtime.pop(0)
                    self.sta3val_airtime.append( float(measure[7]) )

                elif label == 'D':
                    item = 'I004'
                    self.sta4val_cw.pop(0)
                    self.sta4val_cw.append( float(measure[5]) )

                    self.sta4val_psucc.pop(0)
                    self.sta4val_psucc.append( float(measure[6]) )

                    self.sta4val_airtime.pop(0)
                    self.sta4val_airtime.append( float(measure[7]) )

                elif label == 'E':
                    item = 'I005'
                    self.sta5val_cw.pop(0)
                    self.sta5val_cw.append( float(measure[5]) )

                    self.sta5val_psucc.pop(0)
                    self.sta5val_psucc.append( float(measure[6]) )

                    self.sta5val_airtime.pop(0)
                    self.sta5val_airtime.append( float(measure[7]) )

                elif label == 'F':
                    item = 'I006'
                    self.sta6val_cw.pop(0)
                    self.sta6val_cw.append( float(measure[5]) )

                    self.sta6val_psucc.pop(0)
                    self.sta6val_psucc.append( float(measure[6]) )

                    self.sta6val_airtime.pop(0)
                    self.sta6val_airtime.append( float(measure[7]) )

                else:
                    print('Error in plot receive, wrong label present')
                    continue

                self.tv.item(item, text=label, values=(round(measure[1]*100)/100, round(measure[2]*100)/100, round(measure[3]*100)/100))
            else:
                print('Error in plot receive, no label present')


    def init_gui(self):

        #VISUALIZER CONFIGURATION
        self.local_network = 1
        self.Nplot=100

        self.last_traffic_update_time = time.time()
        self.last_traffic_update_command = None
        self.traffic_update_command = None

        #psucc
        self.sta1val_psucc=[1 for x in range(0,self.Nplot)]
        self.sta2val_psucc=[2 for x in range(0,self.Nplot)]
        self.sta3val_psucc=[3 for x in range(0,self.Nplot)]
        self.sta4val_psucc=[4 for x in range(0,self.Nplot)]
        self.sta5val_psucc=[4 for x in range(0,self.Nplot)]
        self.sta6val_psucc=[4 for x in range(0,self.Nplot)]
        self.xval_psucc=[x for x in range(-self.Nplot, 0)]

        #airtime
        self.sta1val_airtime=[1 for x in range(0,self.Nplot)]
        self.sta2val_airtime=[2 for x in range(0,self.Nplot)]
        self.sta3val_airtime=[3 for x in range(0,self.Nplot)]
        self.sta4val_airtime=[4 for x in range(0,self.Nplot)]
        self.sta5val_airtime=[4 for x in range(0,self.Nplot)]
        self.sta6val_airtime=[4 for x in range(0,self.Nplot)]
        self.xval_airtime=[x for x in range(-self.Nplot, 0)]

        #airtime
        self.sta1val_cw=[1 for x in range(0,self.Nplot)]
        self.sta2val_cw=[2 for x in range(0,self.Nplot)]
        self.sta3val_cw=[3 for x in range(0,self.Nplot)]
        self.sta4val_cw=[4 for x in range(0,self.Nplot)]
        self.sta5val_cw=[4 for x in range(0,self.Nplot)]
        self.sta6val_cw=[4 for x in range(0,self.Nplot)]
        self.xval_cw=[x for x in range(-self.Nplot, 0)]


        #NETWORK SOCKET SETUP
        print('Network socket setup')
        self.command_list = {}
        if self.local_network :
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

            self.sta1_server_port = self.server_port
            self.sta2_server_port = self.server_port
            self.sta3_server_port = self.server_port
            self.sta4_server_port = self.server_port


        """GUI SETUP"""
        print('GUI setup')
        self.root.title('WISHFUL DEMO YEAR 2')
        #self.root.option_add('*tearOff', 'FALSE')

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

        # #Protocol FRAME
        # self.protocol_frame = ttk.LabelFrame(self, text='Protocol', height=100, width=100)
        # self.protocol_frame.grid(column=0, row=1, columnspan=1, sticky='nesw')
        #
        # self.LabelProtocol = Label(self.protocol_frame, text="Select Protocol")
        # #self.LabelProtocol.pack(side=TOP, anchor=CENTER, expand=NO)
        # self.LabelProtocol.grid(row=0, column=0, padx=5, pady=5, ipady=2, sticky=W)
        #
        # #station1
        # countryLabelSta1 = Label(self.protocol_frame, text="Station 1")
        # countryLabelSta1.grid(row=1, column=0, sticky=W+E)
        # self.countryVarSta1 = StringVar()
        # self.countryComboSta1 = ttk.Combobox(self.protocol_frame, textvariable=self.countryVarSta1)
        # self.countryComboSta1['values'] = ('METAMAC', 'TDMA 1', 'TDMA 2', 'TDMA 3', 'TDMA 4', 'ALOHA')
        # self.countryComboSta1.current(0)
        # #self.countryComboSta1.bind("<<ComboboxSelected>>", self.send_command(self.sta1_ipaddress, self.countryVarSta1.get()))
        # self.countryComboSta1.bind("<<ComboboxSelected>>", self.send_command_sta1)
        # self.countryComboSta1.grid(row=1, column=1, padx=5, pady=5, ipady=2, sticky=W)
        # #self.countryComboSta1.pack(side=TOP, anchor=CENTER, expand=NO)
        #
        # #station2
        # countryLabelSta2 = Label(self.protocol_frame, text="Station 2")
        # countryLabelSta2.grid(row=2, column=0, sticky=W+E)
        # self.countryVarSta2 = StringVar()
        # self.countryComboSta2 = ttk.Combobox(self.protocol_frame, textvariable=self.countryVarSta2)
        # self.countryComboSta2['values'] = ('METAMAC', 'TDMA 1', 'TDMA 2', 'TDMA 3', 'TDMA 4', 'ALOHA')
        # self.countryComboSta2.current(0)
        # #self.countryComboSta2.bind("<<ComboboxSelected>>", self.send_command(self.sta2_ipaddress, self.countryVarSta2.get()))
        # self.countryComboSta2.bind("<<ComboboxSelected>>", self.send_command_sta2)
        # self.countryComboSta2.grid(row=2, column=1, padx=5, pady=5, ipady=2, sticky=W)
        # #self.countryComboSta2.pack(side=TOP, anchor=CENTER, expand=NO)
        #
        # #station3
        # countryLabelSta3 = Label(self.protocol_frame, text="Station 3")
        # countryLabelSta3.grid(row=3, column=0, sticky=W+E)
        # self.countryVarSta3 = StringVar()
        # self.countryComboSta3 = ttk.Combobox(self.protocol_frame, textvariable=self.countryVarSta3)
        # self.countryComboSta3['values'] = ('METAMAC', 'TDMA 1', 'TDMA 2', 'TDMA 3', 'TDMA 4', 'ALOHA')
        # self.countryComboSta3.current(0)
        # #self.countryComboSta3.bind("<<ComboboxSelected>>", self.send_command(self.sta3_ipaddress, self.countryVarSta3.get()))
        # self.countryComboSta3.bind("<<ComboboxSelected>>", self.send_command_sta3)
        # self.countryComboSta3.grid(row=3, column=1, padx=5, pady=5, ipady=2, sticky=W)
        # #self.countryComboSta3.pack(side=TOP, anchor=CENTER, expand=NO)
        #
        # #station4
        # countryLabelSta4 = Label(self.protocol_frame, text="Station 4")
        # countryLabelSta4.grid(row=4, column=0, sticky=W+E)
        # self.countryVarSta4 = StringVar()
        # self.countryComboSta4 = ttk.Combobox(self.protocol_frame, textvariable=self.countryVarSta4)
        # self.countryComboSta4['values'] = ('METAMAC', 'TDMA 1', 'TDMA 2', 'TDMA 3', 'TDMA 4', 'ALOHA')
        # self.countryComboSta4.current(0)
        # #self.countryComboSta4.bind("<<ComboboxSelected>>", self.send_command(self.sta4_ipaddress, self.countryVarSta4.get()))
        # self.countryComboSta4.bind("<<ComboboxSelected>>", self.send_command_sta4)
        # self.countryComboSta4.grid(row=4, column=1, padx=5, pady=5, ipady=2, sticky=W)
        # #self.countryComboSta4.pack(side=TOP, anchor=CENTER, expand=NO)


        #PROTOCOL INFORMATION
        self.stats_frame = ttk.LabelFrame(self, text='Monitor REACT values (Normalized)', height=100, width=150)
        self.stats_frame.grid(column=2, row=1, columnspan=1, sticky='nesw')

        # self.vb0 = ttk.Label(self.stats_frame, font=('Courier', 10))
        # self.vb1 = ttk.Label(self.stats_frame, font=('Courier', 10))
        #
        # self.vb0.pack(anchor=NW, pady=3)
        # self.vb1.pack(anchor=NW, pady=3)
        #
        # self.vb0['text'] = '{:<11} {:<8}'.format('enabled:', '1')
        # self.vb1['text'] = '{:<11} {:<8}'.format('cheese:', '2')

        self.tv = ttk.Treeview(self.stats_frame)
        self.tv['columns'] = ('starttime', 'endtime', 'status')
        self.tv.heading("#0", text='', anchor='w')
        self.tv.column("#0", anchor="w", width=50)
        self.tv.heading('starttime', text='SOURCE')
        self.tv.column('starttime', anchor='center', width=100)
        self.tv.heading('endtime', text='CLAIM')
        self.tv.column('endtime', anchor='center', width=100)
        self.tv.heading('status', text='OFFER')
        self.tv.column('status', anchor='center', width=100)
        self.tv.grid(sticky = (N,S,W,E))

        self.tv.insert('', '0', text="A", values=('0', '0', '0'))
        self.tv.insert('', '1', text="B", values=('0', '0', '0'))
        self.tv.insert('', '2', text="C", values=('0', '0', '0'))

        # cells = self.tv.get_children()
        # for item in cells: ## Changing all children from root item
        #     print(item)

        #self.tv.item('I001', text="A", values=('1', '1', '1'))

        self.startReactBtn = ttk.Button(self.stats_frame, text="START REACT", width=10, command=lambda : self.startReact(),  style=SUNKABLE_BUTTON2)
        self.startReactBtn.grid(row=1, column=0, padx=5, pady=5, ipady=2, sticky=W)
        self.stopReactBtn = ttk.Button(self.stats_frame, text="STOP REACT", width=10, command=lambda : self.stopReact(),  style=SUNKABLE_BUTTON1)
        self.stopReactBtn.grid(row=1, column=1, padx=5, pady=5, ipady=2, sticky=W)




        #TRAFFIC FRAME
        self.traffic_frame = ttk.LabelFrame(self, text='Traffic', height=100, width=50)
        self.traffic_frame.grid(column=1, row=1, columnspan=1, sticky='nesw')

        self.LabelTraffic = Label(self.traffic_frame, text="Select nodes traffic")
        #self.LabelTraffic.pack(side=TOP, anchor=CENTER, expand=NO)
        self.LabelTraffic.grid(row=0, column=0, columnspan=2, padx=1, pady=1, sticky=W)

        #traffic node A
        self.LabelTrafficA = Label(self.traffic_frame, text="A --> ")
        self.LabelTrafficA.grid(row=1, column=0, padx=2, pady=2, sticky=W)
        self.countryVarA = StringVar()
        self.countryComboA = ttk.Combobox(self.traffic_frame, textvariable=self.countryVarA, width=5)
        self.countryComboA['values'] = ('B', 'C')
        self.countryComboA.current(0)
        self.countryComboA.grid(row=1, column=1, padx=2, pady=2, sticky=W)
        self.TrafficA = Scale(self.traffic_frame, from_=0, to=6000, length=300, resolution=1000, tickinterval=3000, orient='horizontal', command= lambda value, src='A': self.setTraffic(src, value))
        self.TrafficA.grid(row=1, column=2, padx=2, pady=2, sticky=W)

        #traffic node B
        self.LabelTrafficB = Label(self.traffic_frame, text="B --> ")
        self.LabelTrafficB.grid(row=2, column=0, padx=1, pady=1, sticky=W)

        self.countryVarB = StringVar()
        self.countryComboB = ttk.Combobox(self.traffic_frame, textvariable=self.countryVarB, width=5)
        self.countryComboB['values'] = ('A', 'C')
        self.countryComboB.current(0)
        self.countryComboB.grid(row=2, column=1, padx=2, pady=2, sticky=W)
        self.TrafficB = Scale(self.traffic_frame, from_=0, to=6000, length=300, resolution=1000, tickinterval=3000, orient='horizontal', command= lambda value, src='B': self.setTraffic(src, value))
        self.TrafficB.grid(row=2, column=2, padx=2, pady=2, sticky=W)

        # #traffic node C
        self.LabelTrafficC = Label(self.traffic_frame, text="C --> ")
        self.LabelTrafficC.grid(row=3, column=0, padx=1, pady=1, sticky=W)
        self.countryVarC = StringVar()
        self.countryComboC = ttk.Combobox(self.traffic_frame, textvariable=self.countryVarC, width=5)
        self.countryComboC['values'] = ('A', 'B')
        self.countryComboC.current(0)
        self.countryComboC.grid(row=3, column=1, padx=2, pady=2, sticky=W)
        self.TrafficC = Scale(self.traffic_frame, from_=0, to=6000, length=300, resolution=1000, tickinterval=3000, orient='horizontal', command= lambda value, src='C': self.setTraffic(src, value))
        self.TrafficC.grid(row=3, column=2, padx=2, pady=2, sticky=W)


        #USRP FRAME
        #start_new_thread(self.loopCapture,(99,))

        #PLOT TOPOLOGY IMAGE
        self.topo_frame=ttk.LabelFrame(self, text="Network Scenario", height=100, width=100)
        self.topo_frame.grid(column=0, row=1, columnspan=1, sticky='nesw')

        #img=Image.open('topology-3full.png')
        #wpercent=50
        #basewidth = 350

        img=Image.open('topology-3chain.png')
        wpercent=100
        basewidth = 500


        wpercent = (basewidth/float(img.size[0]))
        hsize = int((float(img.size[1])*float(wpercent)))

        img = img.resize((basewidth,hsize), Image.ANTIALIAS)

        im = ImageTk.PhotoImage(img)
        label_topo_img = Label(self.topo_frame, image=im)
        label_topo_img.image = im
        label_topo_img.grid(row=0,column=0, sticky=W+E)


        #PLOTTER psucc
        start_new_thread(self.plotpsucc,(99,))
        #PLOTTER airtime
        start_new_thread(self.plotairtime,(99,))
        #PLOTTER cw
        start_new_thread(self.plotcw,(99,))

        #LOOP command traffic
        start_new_thread(self.traffic_command_handles,(99,))


        # ttk.Separator(self, orient='horizontal').grid(column=0,
        #         row=1, columnspan=4, sticky='ew')
        #
        for child in self.winfo_children():
            child.grid_configure(padx=5, pady=5)

if __name__ == '__main__':
    root = Tk()
    Adder(root)
    root.mainloop()