__author__ = 'domenico'
__author__ = 'pierluigi'


#from Tkinter import *
from PIL import Image, ImageTk
import tkinter
import random
from socket import *
from sys import argv, exit
import demjson
import json
import zmq
import time
from _thread import start_new_thread
from tkinter import ttk
from tkinter import IntVar
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
from tkinter import messagebox
import matplotlib.pyplot as plt
import numpy
import numpy as np
import networkx as nx
import matplotlib
from matplotlib import rcParams
rcParams.update({'figure.autolayout': True})

# from sklearn.externals import joblib
sklearn_enable = False

import sys
SUNKABLE_BUTTON1 = 'SunkableButton.TButton'
SUNKABLE_BUTTON2 = 'SunkableButton.TButton'
SUNKABLE_BUTTON3 = 'SunkableButton.TButton'

DELAY = 1000
MAX_SOURCE_TRAFFIC = 25000

class Adder(ttk.Frame):
    """The adders gui and functions."""
    def __init__(self, parent, *args, **kwargs):
        ttk.Frame.__init__(self, parent, *args, **kwargs)
        self.root = parent
        # add nodes
        self.all_nodes = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']
        self.network_nodes = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']
        # all_nodes = ['A', 'B', 'C', 'D', 'E', 'X', 'Y', 'Z']
        # network_nodes = ['A', 'B', 'C', 'D', 'E', 'X', 'Y', 'Z']
        self.legend_nodes = ['X', 'Y', 'Z']

        self.fixed_positions = {'A': (1800, 2000 - 2500),
                           'B': (3600, 2000 - 2000),
                           'C': (5400, 2000 - 2500),
                           'D': (600, 2000 - 200),
                           'E': (4800, 2000 - 920),
                           'F': (5990, 2000 - 200),
                           'G': (1700, 2000 - 500),
                           'H': (1600, 2000 - 800),
                           'I': (1600, 2000 - 1100),

                                # 'X': (300, 2000 - 3500),
                           # 'Y': (1800, 2000 - 3500),
                           # 'Z': (3800, 2000 - 3500)

                           }  # dict with two of the positions set

        self.init_gui()

    def on_quit(self):
        """Exits program."""
        quit()

    def start_dialog_box(self):
        messagebox.showerror("Error", "Sorry, no traffic enabled, the selected nodes are not in carrier sense range")

    def centreWindow(self):
        w = 1850
        h = 900
        sw = self.parent.winfo_screenwidth()
        sh = self.parent.winfo_screenheight()
        #x = (sw - w)/2
        #y = (sh - h)/2
        x = (sw - w)
        y = (sh - h)
        self.parent.geometry('%dx%d+%d+%d' % (w, h, x, y))

    def selectTopologyImage1(self):
        image_name = 'wilab2-topology-1.png'
        img=Image.open(image_name)
        wpercent=100
        basewidth = 490
        wpercent = (basewidth/float(img.size[0]))
        hsize = int((float(img.size[1])*float(wpercent)))
        img = img.resize((basewidth,hsize), Image.ANTIALIAS)
        im = ImageTk.PhotoImage(img)

        self.label_topo_img = Label(self.topo_frame, image=im)
        self.label_topo_img.image = im
        self.label_topo_img.grid(row=0, column=0, sticky='nesw')


    def selectTopologyImage2(self):
        image_name = 'wilab2-topology-2bis.png'
        img=Image.open(image_name)
        wpercent=100
        basewidth = 490
        wpercent = (basewidth/float(img.size[0]))
        hsize = int((float(img.size[1])*float(wpercent)))
        img = img.resize((basewidth,hsize), Image.ANTIALIAS)
        im = ImageTk.PhotoImage(img)

        self.label_topo_img = Label(self.topo_frame, image=im)
        self.label_topo_img.image = im
        self.label_topo_img.grid(row=0, column=0, sticky='nesw')

    def selectTopologyImagePortableTestbed(self):
        image_name = 'ptestbed-review-topology.png'
        img=Image.open(image_name)
        wpercent=100
        basewidth = 490
        wpercent = (basewidth/float(img.size[0]))
        hsize = int((float(img.size[1])*float(wpercent)))
        img = img.resize((basewidth,hsize), Image.ANTIALIAS)
        im = ImageTk.PhotoImage(img)

        self.label_topo_img = Label(self.topo_frame, image=im)
        self.label_topo_img.image = im
        self.label_topo_img.grid(row=0, column=0, sticky='nesw')

    # def stopReact(self):
    #     command = 'stop_react'
    #     json_command = {'type': 'algorithm', 'command': command}
    #     # print(json_command)
    #     self.socket_command_remote_network.send_json(json_command)
    #     self.stopReactBtn.state(['pressed', 'disabled'])
    #     self.style.configure(SUNKABLE_BUTTON1, relief=SUNKEN, foreground='red')
    #
    #     self.startReactBtn.state(['!pressed', '!disabled'])
    #     self.style.configure(SUNKABLE_BUTTON2, relief=RAISED, foreground='green')
    #
    # def startReact(self):
    #     command = 'start_react'
    #     json_command = {'type': 'algorithm', 'command': command}
    #     # print(json_command)
    #     self.socket_command_remote_network.send_json(json_command)
    #
    #     self.startReactBtn.state(['pressed', 'disabled'])
    #     self.style.configure(SUNKABLE_BUTTON2, relief=SUNKEN, foreground='red')
    #
    #     self.stopReactBtn.state(['!pressed', '!disabled'])
    #     self.style.configure(SUNKABLE_BUTTON1, relief=RAISED, foreground='green')

    def stopAllTraffic(self):
        self.stop_all_traffic_button.state(['pressed', 'disabled'])
        self.style.configure(SUNKABLE_BUTTON1, relief=tkinter.SUNKEN, foreground='red')
        command = 'off_traffic'
        dst = 'A'
        for label in self.all_nodes:
            stop_command = {'type': 'traffic', 'command': command, 'src': label, 'dst': dst}
            print('command sent %s' % str(stop_command))
            self.socket_command_remote_network.send_json(stop_command)
            time.sleep(1)

        self.stop_all_traffic_button.state(['!pressed', '!disabled'])
        self.style.configure(SUNKABLE_BUTTON1, relief=tkinter.RAISED, foreground='green')
        self.update_reset_traffic = True

    def setTraffic(self, src, val):
        # print(src)
        # print(val[self.all_nodes.index(src)].get())
        # print(self.countryVar[self.all_nodes.index(src)].get())

        source_rate = int(val[self.all_nodes.index(src)].get())
        dst = self.countryVar[self.all_nodes.index(src)].get()

        # dst = self.countryVarA.get()
        # val = int(val)
        # if src == 'A':
        #     dst = self.countryVarA.get()
        #     if 500 < val and val <= MAX_SOURCE_TRAFFIC:
        #         self.sta1val_traffic_activation = True
        #     else:
        #         self.sta1val_traffic_activation = False
        # elif src == 'B':
        #     dst = self.countryVarB.get()
        #     if 500 < val and val <= MAX_SOURCE_TRAFFIC:
        #         self.sta2val_traffic_activation = True
        #     else:
        #         self.sta2val_traffic_activation = False
        # elif src == 'C':
        #     dst = self.countryVarC.get()
        #     if 500 < val and val <= MAX_SOURCE_TRAFFIC:
        #         self.sta3val_traffic_activation = True
        #     else:
        #         self.sta3val_traffic_activation = False
        # elif src == 'D':
        #     dst = self.countryVarD.get()
        #     if 500 < val and val <= MAX_SOURCE_TRAFFIC:
        #         self.sta4val_traffic_activation = True
        #     else:
        #         self.sta4val_traffic_activation = False
        # elif src == 'E':
        #     dst = self.countryVarE.get()
        #     if 500 < val and val <= MAX_SOURCE_TRAFFIC:
        #         self.sta5val_traffic_activation = True
        #     else:
        #         self.sta5val_traffic_activation = False
        # elif src == 'F':
        #     dst = self.countryVarF.get()
        #     if 500 < val and val <= MAX_SOURCE_TRAFFIC:
        #         self.sta6val_traffic_activation = True
        #     else:
        #         self.sta6val_traffic_activation = False
        # else:
        #     print('bad source node')
        #     return

        command_sent = False
        # for i in range(len(self.update_topology_carrier_sense_value)):
        #     if self.update_topology_carrier_sense_value[i][2]:
                # if (self.update_topology_carrier_sense_value[i][0] == src and self.update_topology_carrier_sense_value[i][1] == dst) or (self.update_topology_carrier_sense_value[i][0] == dst and self.update_topology_carrier_sense_value[i][1] == src):

        if src != dst:
            if 500 < source_rate and source_rate <= MAX_SOURCE_TRAFFIC:
                command = 'set_traffic'
                round_val = round(source_rate/1000)*1000
                if (source_rate - source_rate) > 500 :
                    source_rate += 1000
                self.command_list = {'type': 'traffic', 'command': command, 'src' : src, 'dst' : dst, 'value' : round_val}
            else:
                round_val = 0
                command = 'off_traffic'
                self.command_list = {'type': 'traffic', 'command': command, 'src' : src, 'dst' : dst}

            self.last_traffic_update_time = time.time()
            self.traffic_update_command = self.command_list

            print('command sent %s' % str(self.command_list))
            self.socket_command_remote_network.send_json(self.command_list)
            command_sent = True

            # if not command_sent:
                # self.start_dialog_box()


    def traffic_command_handles(self,x):
        while True:
            if time.time() - self.last_traffic_update_time > 0.5 and self.traffic_update_command != self.last_traffic_update_command:
                # print('command sent %s' % str(self.command_list))
                # self.socket_command_remote_network.send_json(self.command_list)
                self.last_traffic_update_time = time.time()
                self.last_traffic_update_command = self.traffic_update_command
                self.LabelTraffic_2.config(text="Select nodes traffic : (UPI executed!)")
                self.update_network_traffic = True

            time.sleep(0.2)
            self.LabelTraffic_2.config(text="Select nodes traffic : ")

    line1_busytime = None
    line2_busytime = None
    line3_busytime = None
    line4_busytime = None
    line5_busytime = None
    line6_busytime = None
    #figure_busytime = None

    def plot_busytime(self,x):
        global line1_busytime
        global line2_busytime
        global line3_busytime
        global line4_busytime
        global line5_busytime
        global line6_busytime
        #global figure_busytime
        init = 1
        while True:
            if init:
                try:

                    # plt.ion()
                    self.figure_busytime = Figure()
                    # self.figure_busytime = plt.figure()
                    self.figure_busytime.set_facecolor('white')
                    self.ax1 = self.figure_busytime.add_subplot(1, 1, 1)
                    self.ax1.grid(True)
                    self.ax1.set_xlabel('Time [s]', fontsize=12)
                    self.ax1.set_ylabel('Busy time')

                    line1_busytime, = self.ax1.plot(self.xval_busytime, self.sta1val_busytime, label='Node A')
                    line2_busytime, = self.ax1.plot(self.xval_busytime, self.sta2val_busytime, label='Node B')
                    line3_busytime, = self.ax1.plot(self.xval_busytime, self.sta3val_busytime, label='Node C')
                    line4_busytime, = self.ax1.plot(self.xval_busytime, self.sta4val_busytime, label='Node D')
                    line5_busytime, = self.ax1.plot(self.xval_busytime, self.sta5val_busytime, label='Node E')
                    # line6_busytime, = self.ax1.plot(self.xval_busytime, self.sta6val_busytime, label='Node F')

                    self.ax1.set_ylim([-0.05, 1])
                    self.ax1.patch.set_facecolor('white')

                    my_dpi = self.my_dpi
                    width = self.width
                    height = self.height
                    self.figure_busytime.set_size_inches(width / my_dpi, height / my_dpi)
                    self.canvas1 = FigureCanvasTkAgg(self.figure_busytime, self.statistics_busytime_frame)
                    self.canvas1.show()
                    self.canvas1.get_tk_widget().configure(background='white', highlightcolor='white',highlightbackground='white')
                    self.canvas1.get_tk_widget().grid(column=0, row=0, columnspan=1, sticky='nesw')
                    self.canvas1.get_tk_widget().grid(column=0, row=0)

                except Exception as e:
                    print(e)

                init = 0

            else:
                # print('----------------')
                # print(len(self.xval_busytime))
                # print(len(self.sta1val_busytime))
                # print(self.sta1val_busytime)
                line1_busytime.set_ydata(self.sta1val_busytime)
                line2_busytime.set_ydata(self.sta2val_busytime)
                line3_busytime.set_ydata(self.sta3val_busytime)
                line4_busytime.set_ydata(self.sta4val_busytime)
                line5_busytime.set_ydata(self.sta5val_busytime)
                # line6_busytime.set_ydata(self.sta6val_busytime)
                self.figure_busytime.canvas.draw()
            time.sleep(1)

    #
    line1_numtx = None
    line2_numtx = None
    line3_numtx = None
    line4_numtx = None
    line5_numtx = None
    line6_numtx = None
    #figure_numtx = None
    def plot_numtx(self,x):
        global line1_numtx
        global line2_numtx
        global line3_numtx
        global line4_numtx
        global line5_numtx
        global line6_numtx
        #global figure_numtx
        init = 1
        while True:
            if init:
                try:

                    # plt.ion()
                    self.figure_numtx = Figure()
                    # self.figure_numtx = plt.figure()
                    self.figure_numtx.set_facecolor('white')
                    self.ax2 = self.figure_numtx.add_subplot(1,1,1)
                    self.ax2.grid(True)
                    self.ax2.set_xlabel('Time [s]', fontsize=12)
                    self.ax2.set_ylabel('Transmissions number')
                    line1_numtx, = self.ax2.plot(self.xval_numtx, self.sta1val_numtx, label='Node A')
                    line2_numtx, = self.ax2.plot(self.xval_numtx, self.sta2val_numtx, label='Node B')
                    line3_numtx, = self.ax2.plot(self.xval_numtx, self.sta3val_numtx, label='Node C')
                    line4_numtx, = self.ax2.plot(self.xval_numtx, self.sta4val_numtx, label='Node D')
                    line5_numtx, = self.ax2.plot(self.xval_numtx, self.sta5val_numtx, label='Node E')
                    line6_numtx, = self.ax2.plot(self.xval_numtx, self.sta6val_numtx, label='Node F')

                    # labels = ['',  '0.0', '', '0.5', '', '1', '']
                    # set the tick labels
                    # ax.set_yticklabels(labels, rotation=0)
                    # #
                    self.ax2.set_ylim([-0.05, 1000])
                    self.ax2.patch.set_facecolor('white')
                    #legend = ax.legend(loc='upper center', shadow=True, ncol=3)
                    # #
                    my_dpi = self.my_dpi
                    width = self.width
                    height = self.height
                    self.figure_numtx.set_size_inches(width/my_dpi,height/my_dpi)
                    self.canvas2 = FigureCanvasTkAgg(self.figure_numtx, self.statistics_numtx_frame)
                    self.canvas2.show()
                    self.canvas2.get_tk_widget().configure(background='white',  highlightcolor='white', highlightbackground='white')
                    self.canvas2.get_tk_widget().grid(column=0, row=0, columnspan=1, sticky='nesw')
                    self.canvas2.get_tk_widget().grid(column=0, row=0)

                except Exception as e:
                    print(e)
                    pass

                init = 0

            else:
                line1_numtx.set_ydata(self.sta1val_numtx)
                line2_numtx.set_ydata(self.sta2val_numtx)
                line3_numtx.set_ydata(self.sta3val_numtx)
                line4_numtx.set_ydata(self.sta4val_numtx)
                line5_numtx.set_ydata(self.sta5val_numtx)
                line6_numtx.set_ydata(self.sta6val_numtx)
                self.figure_numtx.canvas.draw()
                pass

            time.sleep(1)

    
    line1_numtx_suc = None
    line2_numtx_suc = None
    line3_numtx_suc = None
    line4_numtx_suc = None
    line5_numtx_suc = None
    line6_numtx_suc = None
    figure_numtx_suc = None

    def plot_numtx_suc(self,x):
        global line1_numtx_suc
        global line2_numtx_suc
        global line3_numtx_suc
        global line4_numtx_suc
        global line5_numtx_suc
        global line6_numtx_suc
        global figure_numtx_suc
        init = 1
        while True:
            if init:
                try:

                    # plt.ion()
                    figure_numtx_suc = Figure()
                    # figure_numtx_suc = plt.figure()
                    figure_numtx_suc.set_facecolor('white')
                    ax = figure_numtx_suc.add_subplot(111)
    
                    # self.yval.append( numpy.nan_to_num( stats.get('numtx_suc') ) )
                    # yy=self.yval[::-1]
                    # yy=yy[0:self.Nplot]
                    # self.yval=yy[::-1]
                    ax.grid(True)
                    ax.set_xlabel('Time [s]', fontsize=12)
                    ax.set_ylabel('Successful transmissions number')
    
                    # line1_numtx_suc = ax.semilogy(self.xval_numtx_suc, self.sta1val_numtx_suc, label='Node A')
                    # line2_numtx_suc = ax.semilogy(self.xval_numtx_suc, self.sta2val_numtx_suc, label='Node B')
                    # line3_numtx_suc = ax.semilogy(self.xval_numtx_suc, self.sta3val_numtx_suc, label='Node C')
                    # line4_numtx_suc = ax.semilogy(self.xval_numtx_suc, self.sta4val_numtx_suc, label='Node D')
                    # line5_numtx_suc = ax.semilogy(self.xval_numtx_suc, self.sta5val_numtx_suc, label='Node E')
                    # line6_numtx_suc = ax.semilogy(self.xval_numtx_suc, self.sta6val_numtx_suc, label='Node F')
    
                    line1_numtx_suc, = ax.plot(self.xval_numtx_suc, self.sta1val_numtx_suc, label='Node A')
                    line2_numtx_suc, = ax.plot(self.xval_numtx_suc, self.sta2val_numtx_suc, label='Node B')
                    line3_numtx_suc, = ax.plot(self.xval_numtx_suc, self.sta3val_numtx_suc, label='Node C')
                    line4_numtx_suc, = ax.plot(self.xval_numtx_suc, self.sta4val_numtx_suc, label='Node D')
                    line5_numtx_suc, = ax.plot(self.xval_numtx_suc, self.sta5val_numtx_suc, label='Node E')
                    line6_numtx_suc, = ax.plot(self.xval_numtx_suc, self.sta6val_numtx_suc, label='Node F')

                    ax.set_ylim([-0.05, 1000])
                    ax.patch.set_facecolor('white')
                    legend = ax.legend(loc='upper center', shadow=True, ncol=3)
    
                    my_dpi = self.my_dpi
                    width = self.width
                    height = self.height
                    figure_numtx_suc.set_size_inches(width/my_dpi,height/my_dpi)
                    canvas = FigureCanvasTkAgg(figure_numtx_suc, self.statistics_numtx_suc_frame)
                    canvas.show()
                    canvas.get_tk_widget().configure(background='white',  highlightcolor='white', highlightbackground='white')
                    canvas.get_tk_widget().grid(column=0, row=0, columnspan=1, sticky='nesw')
    
                except Exception as e:
                    print(e)
                    pass
    
                init = 0
    
            else:
                line1_numtx_suc.set_ydata(self.sta1val_numtx_suc)
                line2_numtx_suc.set_ydata(self.sta2val_numtx_suc)
                line3_numtx_suc.set_ydata(self.sta3val_numtx_suc)
                line4_numtx_suc.set_ydata(self.sta4val_numtx_suc)
                line5_numtx_suc.set_ydata(self.sta5val_numtx_suc)
                line6_numtx_suc.set_ydata(self.sta6val_numtx_suc)
                figure_numtx_suc.canvas.draw()
                # print("first element %s" %str(self.sta1val_numtx_suc[-1]))
            time.sleep(1)


    def plot_topology(self, x):

        def find_topology():

            self.find_topology_button.state(['pressed', 'disabled'])
            self.style.configure(SUNKABLE_BUTTON2, relief=tkinter.SUNKEN, foreground='red')

            json_command = {'type': 'find_topology', 'command': 'carrier_sense'}
            print(json_command)
            self.socket_command_remote_network.send_json(json_command)


        def draw_figure_background():
            # plt.clf()
            plt.cla()
            plt.axis('off')
            # # plt.hold(False)
            # # font = {'fontname': 'Helvetica',
            # #         'color': 'k',
            # #         'fontweight': 'bold',
            # #         'fontsize': 14}
            # # plt.title("w-iLab.t - Topology 3 hop", font)
            plt.title("w-iLab.t live experiment")
            # change font and write text (using data coordinates)
            # font = {'fontname': 'Helvetica',
            #         'color': 'r',
            #         'fontweight': 'bold',
            #         'fontsize': 14}
            # plt.text(0.5, 0.97, "edge width = # games played", horizontalalignment='center', transform=plt.gca().transAxes)
            # plt.text(0.5, 0.94, "node size = # games won", horizontalalignment='center', transform=plt.gca().transAxes)

        first_time = True
        finded_topology = False
        # print ("xxxxxxxxx = %s " %x)
        while False:
            if first_time:
                try:
                    print('init')
                    first_time = False

                    # plt.rcParams['text.usetex'] = False
                    # plt.figure(figsize=(8, 8))
                    # rcParams.update({'figure.autolayout': True})
                    # plt.ion()
                    # figure_topology = Figure()
                    self.figure_topology = plt.figure()
                    self.figure_topology.set_facecolor('white')
                    self.ax = self.figure_topology.add_subplot(111)

                    draw_figure_background()

                    #setup node graph
                    G = nx.DiGraph()
                    G.add_nodes_from(self.network_nodes)
                    #set nodes position
                    fixed_nodes = self.fixed_positions.keys()
                    pos = nx.spring_layout(G, pos=self.fixed_positions, fixed=fixed_nodes)


                    # #add nodes link
                    # # carrier_sense_edges.append(('P', 'q'))
                    # #add multi nodes link
                    carrier_sense_edges = []
                    # carrier_sense_edges = [('D', 'A'), ('A', 'B'), ('B', 'F'), ('B', 'C'), ('F', 'C'), ('F', 'E'),('E', 'C')]
                    # #add elements to carrier_sense_edges
                    # G.add_edges_from(carrier_sense_edges)
                    # nx.draw_networkx_edges(G, pos, carrier_sense_edges, edge_color='lightgray', width=2.0, arrows=False)

                    ##### add elements to transmission_edges
                    transmission_edges = {}
                    # transmission_edges = {('A', 'B'): '1Mbps', ('E', 'F'): '2Mbps', ('D', 'A'): '3Mbps'}
                    # G.add_edges_from(transmission_edges.keys())
                    # nx.draw_networkx_edges(G, pos, transmission_edges, edge_color='black', arrows=True, width=4.0)
                    # nx.draw_networkx_edge_labels(G, pos, edge_labels=transmission_edges)

                    nx.draw_networkx_nodes(G, pos, self.network_nodes, arrows=False, node_size=700, node_color='darkgray', ax=self.ax)
                    # nx.draw_networkx_nodes(G, pos, transmitting_nodes, arrows=False, node_size=300, node_color='lightgray')

                    # tx_nodes_nointerference_legend = ['X']
                    # tx_nodes_flowinthemiddle_legend = ['Y']
                    # tx_nodes_hiddennodes_legend = ['Z']
                    # G.add_nodes_from(tx_nodes_nointerference_legend)
                    # G.add_nodes_from(tx_nodes_flowinthemiddle_legend)
                    # G.add_nodes_from(tx_nodes_hiddennodes_legend)
                    # nx.draw_networkx_nodes(G, pos, tx_nodes_nointerference_legend, arrows=False, node_size=300, node_color='green', ax=self.ax)
                    # nx.draw_networkx_nodes(G, pos, tx_nodes_hiddennodes_legend, arrows=False, node_size=300, node_color='orange', ax=self.ax)
                    # nx.draw_networkx_nodes(G, pos, tx_nodes_flowinthemiddle_legend, arrows=False, node_size=300, node_color='red', ax=self.ax)

                    tx_nodes_nointerference = []
                    tx_nodes_flowinthemiddle = []
                    tx_nodes_hiddennodes = []
                    # G.add_nodes_from(tx_nodes_nointerference)
                    # G.add_nodes_from(tx_nodes_flowinthemiddle)
                    # G.add_nodes_from(tx_nodes_hiddennodes)
                    # nx.draw_networkx_nodes(G, pos, tx_nodes_nointerference, arrows=False, node_size=300, node_color='green', ax=self.ax)
                    # nx.draw_networkx_nodes(G, pos, tx_nodes_hiddennodes, arrows=False, node_size=300, node_color='orange', ax=self.ax)
                    # nx.draw_networkx_nodes(G, pos, tx_nodes_flowinthemiddle, arrows=False, node_size=300, node_color='red', ax=self.ax)

                    nx.draw_networkx_labels(G, pos, labels=None, ax=self.ax)

                    my_dpi = self.my_dpi
                    width = self.width
                    height = self.height - 30
                    self.figure_topology.set_size_inches(width / my_dpi, height / my_dpi)
                    canvas = FigureCanvasTkAgg(self.figure_topology, self.statistics_topology_frame)
                    canvas.show()
                    canvas.get_tk_widget().configure(background='white', highlightcolor='white', highlightbackground='white')
                    canvas.get_tk_widget().grid(column=0, row=0, columnspan=1, sticky='nesw')
                    #canvas.get_tk_widget().pack(side="top")

                    self.find_topology_button = ttk.Button(self.statistics_topology_frame, text="FIND TOPOLOGY", width=50, command=lambda: find_topology(), style=SUNKABLE_BUTTON2)
                    self.find_topology_button.grid(row=1, column=0, padx=5, pady=5, ipady=2, sticky='nesw')
                    self.find_topology_button.state(['!pressed', '!disabled'])
                    self.style.configure(SUNKABLE_BUTTON2, relief=tkinter.RAISED, foreground='green')

                except Exception as e:
                    print(e)

            else:
                if self.update_reset_traffic:
                    self.update_reset_traffic = False
                    print('reset transmission_edges')
                    G.remove_edges_from(transmission_edges.keys())
                    transmission_edges.clear()
                    draw_figure_background()
                    nx.draw_networkx_nodes(G, pos, self.network_nodes, arrows=False, node_size=700, node_color='darkgray', ax=self.ax)
                    # nx.draw_networkx_nodes(G, pos, transmitting_nodes, arrows=False, node_size=300, node_color='lightgray')
                    nx.draw_networkx_nodes(G, pos, tx_nodes_nointerference, arrows=False, node_size=300, node_color='green', ax=self.ax)
                    nx.draw_networkx_nodes(G, pos, tx_nodes_hiddennodes, arrows=False, node_size=300, node_color='orange', ax=self.ax)
                    nx.draw_networkx_nodes(G, pos, tx_nodes_flowinthemiddle, arrows=False, node_size=300, node_color='red', ax=self.ax)
                    nx.draw_networkx_labels(G, pos, labels=None, ax=self.ax)
                    self.figure_topology.canvas.draw()

                #update the traffic information on network topology graph, update_network is setted True when a some scale element changes its position
                if self.update_network_traffic:
                    print('update network traffic')
                    # self.command_list = {'type': 'traffic', 'command': 'set_traffic', 'src': src, 'dst': dst, 'value': round_val}
                    # self.command_list = {'type': 'traffic', 'command': 'off_traffic', 'src': src, 'dst': dst}
                    if self.last_traffic_update_command['type']=='traffic':
                        if self.last_traffic_update_command['command']=='off_traffic':
                            transmission_edges.pop((self.last_traffic_update_command['src'], self.last_traffic_update_command['dst']))
                            G.remove_edges_from(transmission_edges.keys())

                            draw_figure_background()
                            nx.draw_networkx_nodes(G, pos, self.network_nodes, arrows=False, node_size=700, node_color='darkgray', ax=self.ax)
                            # nx.draw_networkx_nodes(G, pos, transmitting_nodes, arrows=False, node_size=300, node_color='lightgray')
                            nx.draw_networkx_nodes(G, pos, tx_nodes_nointerference, arrows=False, node_size=300, node_color='green', ax=self.ax)
                            nx.draw_networkx_nodes(G, pos, tx_nodes_hiddennodes, arrows=False, node_size=300, node_color='orange', ax=self.ax)
                            nx.draw_networkx_nodes(G, pos, tx_nodes_flowinthemiddle, arrows=False, node_size=300, node_color='red', ax=self.ax)
                            nx.draw_networkx_labels(G, pos, labels=None, ax=self.ax)

                            G.add_edges_from(carrier_sense_edges)
                            nx.draw_networkx_edges(G, pos, carrier_sense_edges, edge_color='lightgray', width=2.0, arrows=False)

                        if self.last_traffic_update_command['command']=='set_traffic':

                            new_traffic = str(self.last_traffic_update_command['value']/1000)+'Mbps'
                            transmission_edges.update({(self.last_traffic_update_command['src'], self.last_traffic_update_command['dst']): new_traffic})
                            G.add_edges_from(transmission_edges.keys())
                            nx.draw_networkx_edges(G, pos, transmission_edges, edge_color='black', arrows=True, width=4.0)

                        nx.draw_networkx_edge_labels(G, pos, edge_labels=transmission_edges)
                    self.update_network_traffic = False
                    self.figure_topology.canvas.draw()

                # if self.class_updated and finded_topology:
                if self.class_updated:
                    draw_figure_background()
                    # print ("class has been updated!")
                    tx_nodes_nointerference  = [label for label, value in self.color.items() if value == 'green']
                    tx_nodes_hiddennodes = [label for label, value in self.color.items() if value == 'orange']
                    tx_nodes_flowinthemiddle = [label for label, value in self.color.items() if value == 'red']
                    # print ("------- %s\n %s\n %s\n " %( tx_nodes_nointerference, tx_nodes_hiddennodes ,tx_nodes_flowinthemiddle))

                    nx.draw_networkx_nodes(G, pos, self.network_nodes, arrows=False, node_size=700, node_color='darkgray', ax=self.ax)
                    # nx.draw_networkx_nodes(G, pos, transmitting_nodes, arrows=False, node_size=300, node_color='lightgray')

                    nx.draw_networkx_nodes(G, pos, tx_nodes_nointerference, arrows=False, node_size=300,node_color='green', ax=self.ax)
                    nx.draw_networkx_nodes(G, pos, tx_nodes_hiddennodes, arrows=False, node_size=300,node_color='orange', ax=self.ax)
                    nx.draw_networkx_nodes(G, pos, tx_nodes_flowinthemiddle, arrows=False, node_size=300,node_color='red', ax=self.ax)
                    nx.draw_networkx_labels(G, pos, labels=None, ax=self.ax)

                    nx.draw_networkx_edges(G, pos, carrier_sense_edges, edge_color='lightgray', width=2.0, arrows=False)
                    nx.draw_networkx_edges(G, pos, transmission_edges, edge_color='black', arrows=True, width=4.0)
                    nx.draw_networkx_edge_labels(G, pos, edge_labels=transmission_edges)

                    # print ("carrier_sense_edges = %s " %carrier_sense_edges)
                    self.figure_topology.canvas.draw()

                if self.update_topology_carrier_sense:
                    # print('update topology carrier sense')
                    # print(carrier_sense_edges)

                    draw_figure_background()
                    nx.draw_networkx_nodes(G, pos, self.network_nodes, arrows=False, node_size=700, node_color='darkgray', ax=self.ax)
                    # nx.draw_networkx_nodes(G, pos, transmitting_nodes, arrows=False, node_size=300, node_color='lightgray')
                    random_colors = ['green', 'orange', 'red']
                    nx.draw_networkx_nodes(G, pos, tx_nodes_nointerference, arrows=False, node_size=300, node_color=random_colors[random.randint(0, 2)], ax=self.ax)
                    nx.draw_networkx_nodes(G, pos, tx_nodes_hiddennodes, arrows=False, node_size=300, node_color='orange', ax=self.ax)
                    nx.draw_networkx_nodes(G, pos, tx_nodes_flowinthemiddle, arrows=False, node_size=300, node_color='red', ax=self.ax)
                    nx.draw_networkx_labels(G, pos, labels=None, ax=self.ax)

                    #[['A', 'B', True], ['A', 'C', True], ['B', 'C', True]]
                    carrier_sense_edges = []
                    for i in range(len(self.update_topology_carrier_sense_value)):
                        if self.update_topology_carrier_sense_value[i][2]:
                            carrier_sense_edges.append((self.update_topology_carrier_sense_value[i][0],self.update_topology_carrier_sense_value[i][1]))
                    print(carrier_sense_edges)

                    # carrier_sense_edges = [('D', 'A'), ('A', 'B'), ('B', 'F'), ('B', 'C'), ('F', 'C'), ('F', 'E'),('E', 'C')]
                    #add elements to carrier_sense_edges
                    G.add_edges_from(carrier_sense_edges)
                    nx.draw_networkx_edges(G, pos, carrier_sense_edges, edge_color='lightgray', width=2.0, arrows=False)
                    nx.draw_networkx_edges(G, pos, transmission_edges, edge_color='black', arrows=True, width=4.0)
                    nx.draw_networkx_edge_labels(G, pos, edge_labels=transmission_edges)

                    self.update_topology_carrier_sense = False
                    self.figure_topology.canvas.draw()

                    self.find_topology_button.state(['!pressed', '!disabled'])
                    self.style.configure(SUNKABLE_BUTTON2, relief=tkinter.RAISED, foreground='green')
                    finded_topology = True

            time.sleep(2)


    #*****************
    #reveive data plot from controller
    #*****************
    def receive_data_plot(self,x):

        reading_time = 1000
        reading_time_sec = 1

        # use poll for timeouts:
        poller = zmq.Poller()
        poller.register(self.socket_plot_remote_network, zmq.POLLIN)

        while True:    # Run until cancelled
            socks = dict(poller.poll(1000))
            if self.socket_plot_remote_network in socks:
                parsed_json = self.socket_plot_remote_network.recv_json()
            else:
                continue

            print('parsed_json : %s' % str(parsed_json))
            #{'measure': [1499443576.7803824, -95, 3046, 121, 138, 138, 1, 1], 'type': 'statistics', 'mac_address': '00:0e:8e:30:9c:af', 'label': 'A'}
			#               time    noise   busy, busy50, busy90, busy99, num_tx_succe, numtx
			#report_stats['reading_time'], report_stats['busy_time'], report_stats['tx_activity'], report_stats['num_tx'], report_stats['num_tx_success']
            #parsed_json: {'value': [['A', 'B', True], ['A', 'C', True], ['B', 'C', True]], 'type': 'find_topology', 'measure': 'carrier_sense_result'}
            # [1499766613.611646, -95, 2641, 68, 80, 109, 361, 20890, 88635, 0, 0]

            if 'type' in parsed_json:
                if parsed_json['type'] == 'find_topology':
                    self.update_topology_carrier_sense = True
                    self.update_topology_carrier_sense_value = parsed_json['value']

            #
            # # TODO: ONLY FOR DEBUG, REMOVE
            # if not 'type' in parsed_json:
            #     parsed_json['type']='statistics'


            if parsed_json['type']=='statistics' and parsed_json['measure']:
                label = parsed_json['label']
                if label:
                    print("%s %s" % (str(label) , str(parsed_json['measure'])))
                    measure = parsed_json['measure']


                    # if label == 'F':
                    #     print ("F received, exiting...")
                    #     sys.exit(-1)

                    if sklearn_enable:
                        # and later you can load it
                        trained_classifier = joblib.load('../classification/trained-interference-classifier-final.pkl')
                        tmpm = np.array(measure[1:])
                        print (measure[1:])
                        if len(measure[1:]) == 5:
                            y_pred = trained_classifier.predict(tmpm.reshape(1, -1))
                            print ("predicted class for node %s is %d " %(str(label), y_pred))
                        # print(measure[1:])
                        else:
                            y_pred=1
                    else:
                        y_pred=1

                    if y_pred == 1:
                        self.color[label] = 'green'
                    elif y_pred == 2:
                        self.color[label] = 'orange'
                    elif y_pred == 3:
                        self.color[label] = 'red'
                    else:
                        print ("bad classification, exiting ...")
                        sys.exit(-1)

                    self.class_updated = True
                    # print ("self.color = %s" %(str(self.color)))


                    if label == self.all_nodes[0]:
                        item = 'I001'

                        # if not self.sta1val_traffic_activation:
                            # measure[3] = 0
                            # measure[4] = 0

                        # busy_time sliding window (remove the oldest, append the newest)
                        self.sta1val_busytime.pop(0)
                        self.sta1val_busytime.append(float(measure[2] / reading_time))
                        # num_tx
                        self.sta1val_numtx.pop(0)
                        self.sta1val_numtx.append(float(measure[10])/reading_time_sec)
                        # num_tx_success
                        self.sta1val_numtx_suc.pop(0)
                        self.sta1val_numtx_suc.append(float(measure[9])/reading_time_sec)

                        self.labelBusy[0].config(text="{}%".format(float(measure[2] / reading_time)*100))

                    elif label == self.all_nodes[1]:
                        item = 'I002'

                        # if not self.sta2val_traffic_activation:
                        #     measure[3] = 0
                        #     measure[4] = 0

                        self.sta2val_busytime.pop(0)
                        self.sta2val_busytime.append(measure[2] / reading_time)
                        #
                        # num_tx
                        self.sta2val_numtx.pop(0)
                        self.sta2val_numtx.append(float(measure[10])/reading_time_sec)
                        #
                        # num_tx_success
                        self.sta2val_numtx_suc.pop(0)
                        self.sta2val_numtx_suc.append(float(measure[9])/reading_time_sec)
                        #
                        self.labelBusy[1].config(text="{}%".format(float(measure[2] / reading_time)*100))

                    elif label == self.all_nodes[2]:
                        item = 'I003'

                        # if not self.sta3val_traffic_activation:
                        #     measure[3] = 0
                        #     measure[4] = 0

                        self.sta3val_busytime.pop(0)
                        self.sta3val_busytime.append(float(measure[2] / reading_time))
                        # num_tx
                        self.sta3val_numtx.pop(0)
                        self.sta3val_numtx.append(float(measure[10])/reading_time_sec)
                        #
                        # num_tx_success
                        self.sta3val_numtx_suc.pop(0)
                        self.sta3val_numtx_suc.append(float(measure[9])/reading_time_sec)

                        #
                        self.labelBusy[2].config(text="{}%".format(float(measure[2] / reading_time)*100))


                    elif label == self.all_nodes[3]:
                        item = 'I004'

                        # if not self.sta4val_traffic_activation:
                        #     measure[3] = 0
                        #     measure[4] = 0

                        self.sta4val_busytime.pop(0)
                        self.sta4val_busytime.append(float(measure[2] / reading_time))
                        # num_tx
                        self.sta4val_numtx.pop(0)
                        self.sta4val_numtx.append(float(measure[10])/reading_time_sec)
                        #
                        # num_tx_success
                        self.sta4val_numtx_suc.pop(0)
                        self.sta4val_numtx_suc.append(float(measure[9])/reading_time_sec)
                        #
                        self.labelBusy[3].config(text="{}%".format(float(measure[2] / reading_time)*100))


                    elif label == self.all_nodes[4]:
                        item = 'I005'

                        # if not self.sta5val_traffic_activation:
                        #     measure[3] = 0
                        #     measure[4] = 0

                        self.sta5val_busytime.pop(0)
                        self.sta5val_busytime.append(float(measure[2] / reading_time))
                        # num_tx
                        self.sta5val_numtx.pop(0)
                        self.sta5val_numtx.append(float(measure[10])/reading_time_sec)
                        #
                        # num_tx_success
                        self.sta5val_numtx_suc.pop(0)
                        self.sta5val_numtx_suc.append(float(measure[9])/reading_time_sec)
                        self.labelBusy[4].config(text="{}%".format(float(measure[2] / reading_time)*100))

                    elif label == self.all_nodes[5]:
                        item = 'I006'

                        # if not self.sta6val_traffic_activation:
                        #     measure[3] = 0
                        #     measure[4] = 0

                        self.sta6val_busytime.pop(0)
                        self.sta6val_busytime.append(float(measure[2] / reading_time))
                        # num_tx
                        self.sta6val_numtx.pop(0)
                        self.sta6val_numtx.append(float(measure[10])/reading_time_sec)
                        #
                        # num_tx_success
                        self.sta6val_numtx_suc.pop(0)
                        self.sta6val_numtx_suc.append(float(measure[9])/reading_time_sec)

                        self.labelBusy[5].config(text="{}%".format(float(measure[2] / reading_time)*100))

                    elif label == self.all_nodes[6]:
                        self.labelBusy[6].config(text="{}%".format(float(measure[2] / reading_time) * 100))

                    elif label == self.all_nodes[7]:
                        self.labelBusy[7].config(text="{}%".format(float(measure[2] / reading_time) * 100))

                    elif label == self.all_nodes[8]:
                        self.labelBusy[8].config(text="{}%".format(float(measure[2] / reading_time) * 100))

                    else:
                        print('Error in plot receive, wrong label present')
                        continue

                    # self.tv.item(item, text=label, values=(round(measure[1]*100)/100, round(measure[2]*100)/100, round(measure[3]*100)/100))
                else:
                    print('Error in plot receive, no label present')

    def init_gui(self):

        #VISUALIZER CONFIGURATION
        self.Nplot=100

        self.color=dict()
        self.class_updated = False

        self.my_dpi = 100
        self.width = 600
        self.height = 400

        self.last_traffic_update_time = time.time()
        self.update_network_traffic = False
        self.update_reset_traffic = False
        self.update_topology_carrier_sense = False
        self.update_topology_carrier_sense_value = []
        self.last_traffic_update_command = None
        self.traffic_update_command = None

        #traffic active
        self.sta1val_traffic_activation = False
        self.sta2val_traffic_activation = False
        self.sta3val_traffic_activation = False
        self.sta4val_traffic_activation = False
        self.sta5val_traffic_activation = False
        self.sta6val_traffic_activation = False


        #busy time
        self.sta1val_busytime=[1 for x in range(0,self.Nplot)]
        self.sta2val_busytime=[2 for x in range(0,self.Nplot)]
        self.sta3val_busytime=[3 for x in range(0,self.Nplot)]
        self.sta4val_busytime=[4 for x in range(0,self.Nplot)]
        self.sta5val_busytime=[1.5 for x in range(0,self.Nplot)]
        self.sta6val_busytime=[2.5 for x in range(0,self.Nplot)]
        self.xval_busytime=[x for x in range(-self.Nplot, 0)]

        #tx
        self.sta1val_numtx=[1 for x in range(0,self.Nplot)]
        self.sta2val_numtx=[2 for x in range(0,self.Nplot)]
        self.sta3val_numtx=[3 for x in range(0,self.Nplot)]
        self.sta4val_numtx=[4 for x in range(0,self.Nplot)]
        self.sta5val_numtx=[4 for x in range(0,self.Nplot)]
        self.sta6val_numtx=[4 for x in range(0,self.Nplot)]
        self.xval_numtx=[x for x in range(-self.Nplot, 0)]

        # tx_success
        self.sta1val_numtx_suc = [1 for x in range(0, self.Nplot)]
        self.sta2val_numtx_suc = [2 for x in range(0, self.Nplot)]
        self.sta3val_numtx_suc = [3 for x in range(0, self.Nplot)]
        self.sta4val_numtx_suc = [4 for x in range(0, self.Nplot)]
        self.sta5val_numtx_suc = [4 for x in range(0, self.Nplot)]
        self.sta6val_numtx_suc = [4 for x in range(0, self.Nplot)]
        self.xval_numtx_suc = [x for x in range(-self.Nplot, 0)]


        #NETWORK SOCKET SETUP
        print('Network socket setup')
        self.command_list = {}

        #connect to the wilabtestbed
        self.socket_command_remote_network_port = 8500
        self.context1_remote_network = zmq.Context()
        print("Connecting to server on port 8500 ... ready to send command to demo experiment node")
        self.socket_command_remote_network = self.context1_remote_network.socket(zmq.PAIR)
        self.socket_command_remote_network.connect("tcp://localhost:%s" % self.socket_command_remote_network_port)

        self.socket_plot_remote_network_port  = 8501
        self.context2_remote_network = zmq.Context()
        print("Connecting to server on port 8501 ... ready to receive protocol information from demo experiment node")
        self.socket_plot_remote_network = self.context2_remote_network.socket(zmq.SUB)
        self.socket_plot_remote_network.connect ("tcp://localhost:%s" % self.socket_plot_remote_network_port)
        self.socket_plot_remote_network.setsockopt(zmq.SUBSCRIBE, b'')

        start_new_thread(self.receive_data_plot,(99,))


        """GUI SETUP"""
        print('GUI setup')
        # self.root.title('WISHFUL DEMO YEAR 2')
        #self.root.option_add('*tearOff', 'FALSE')

        self.parent = self.root
        self.root.title("WiSHFUL Interference Classification")
        self.style = ttk.Style()
        self.style.theme_use("default")
        self.centreWindow()
        self.pack(fill=tkinter.BOTH, expand=1)
        self.grid(column=0, row=0, sticky='nsew')

        self.menubar = tkinter.Menu(self.root)
        #menu file
        self.menu_file = tkinter.Menu(self.menubar)

        self.menu_file.add_command(label='Exit', command=self.on_quit)
        #menu edit topology
        self.menu_edit_topology = tkinter.Menu(self.menubar)
        self.menu_edit_topology.add_command(label='Topology 1 w-iLab', command=self.selectTopologyImage1)
        self.menu_edit_topology.add_command(label='Topology 2 w-iLab', command=self.selectTopologyImage2)
        self.menu_edit_topology.add_command(label='Topology portable testbed', command=self.selectTopologyImagePortableTestbed)
        #show menu
        self.menubar.add_cascade(menu=self.menu_file, label='File')
        self.menubar.add_cascade(menu=self.menu_edit_topology, label='Topology')

        self.root.config(menu=self.menubar)


        # #TRAFFIC FRAME
        # self.traffic_frame = ttk.LabelFrame(self, text='Traffic', height=50, width=50)
        # self.traffic_frame.grid(column=0, row=1, columnspan=1, sticky='nesw')
        #
        # self.LabelTraffic = tkinter.Label(self.traffic_frame, text="Selector nodes traffic")
        # self.LabelTraffic.grid(row=0, column=0, columnspan=3, padx=1, pady=1, sticky=tkinter.W)
        # # self.LabelBusy = tkinter.Label(self.traffic_frame, text="busy-time")
        # # self.LabelBusy.grid(row=0, column=3, columnspan=1, padx=1, pady=1, sticky=tkinter.W)
        #
        # #traffic node A
        # self.LabelTrafficA = tkinter.Label(self.traffic_frame, text="A --> ")
        # self.LabelTrafficA.grid(row=1, column=0, padx=2, pady=2, sticky=tkinter.W)
        # self.countryVarA = tkinter.StringVar()
        # self.countryComboA = ttk.Combobox(self.traffic_frame, textvariable=self.countryVarA, width=5)
        # self.countryComboA['values'] = ('B', 'C', 'D', 'E', 'F')
        # self.countryComboA.current(0)
        # self.countryComboA.grid(row=1, column=1, padx=2, pady=2, sticky=tkinter.W)
        # self.TrafficA = tkinter.Scale(self.traffic_frame, from_=0, to=MAX_SOURCE_TRAFFIC, length=300, resolution=1000, tickinterval=3000, orient='horizontal', command= lambda value, src='A': self.setTraffic(src, value))
        # self.TrafficA.grid(row=1, column=2, padx=2, pady=2, sticky=tkinter.W)
        # self.LabelBusyA = tkinter.Label(self.traffic_frame, text="0%", background='white')
        # self.LabelBusyA.grid(row=1, column=3, padx=1, pady=1, sticky=tkinter.W)
        #
        # #traffic node B
        # self.LabelTrafficB = tkinter.Label(self.traffic_frame, text="B --> ")
        # self.LabelTrafficB.grid(row=2, column=0, padx=1, pady=1, sticky=tkinter.W)
        #
        # self.countryVarB = tkinter.StringVar()
        # self.countryComboB = ttk.Combobox(self.traffic_frame, textvariable=self.countryVarB, width=5)
        # self.countryComboB['values'] = ('A', 'C', 'D', 'E', 'F')
        # self.countryComboB.current(0)
        # self.countryComboB.grid(row=2, column=1, padx=2, pady=2, sticky=tkinter.W)
        # self.TrafficB = tkinter.Scale(self.traffic_frame, from_=0, to=MAX_SOURCE_TRAFFIC, length=300, resolution=1000, tickinterval=3000, orient='horizontal', command= lambda value, src='B': self.setTraffic(src, value))
        # self.TrafficB.grid(row=2, column=2, padx=2, pady=2, sticky=tkinter.W)
        # self.LabelBusyB = tkinter.Label(self.traffic_frame, text="0%", background='white')
        # self.LabelBusyB.grid(row=2, column=3, padx=1, pady=1, sticky=tkinter.W)
        #
        # # #traffic node C
        # self.LabelTrafficC = tkinter.Label(self.traffic_frame, text="C --> ")
        # self.LabelTrafficC.grid(row=3, column=0, padx=1, pady=1, sticky=tkinter.W)
        # self.countryVarC = tkinter.StringVar()
        # self.countryComboC = ttk.Combobox(self.traffic_frame, textvariable=self.countryVarC, width=5)
        # self.countryComboC['values'] = ('A', 'B', 'D', 'E', 'F')
        # self.countryComboC.current(0)
        # self.countryComboC.grid(row=3, column=1, padx=2, pady=2, sticky=tkinter.W)
        # self.TrafficC = tkinter.Scale(self.traffic_frame, from_=0, to=MAX_SOURCE_TRAFFIC, length=300, resolution=1000, tickinterval=3000, orient='horizontal', command= lambda value, src='C': self.setTraffic(src, value))
        # self.TrafficC.grid(row=3, column=2, padx=2, pady=2, sticky=tkinter.W)
        # self.LabelBusyC = tkinter.Label(self.traffic_frame, text="0%", background='white')
        # self.LabelBusyC.grid(row=3, column=3, padx=1, pady=1, sticky=tkinter.W)
        #
        # # #traffic node D
        # self.LabelTrafficD = tkinter.Label(self.traffic_frame, text="D --> ")
        # self.LabelTrafficD.grid(row=4, column=0, padx=1, pady=1, sticky=tkinter.W)
        # self.countryVarD = tkinter.StringVar()
        # self.countryComboD = ttk.Combobox(self.traffic_frame, textvariable=self.countryVarD, width=5)
        # self.countryComboD['values'] = ('A', 'B', 'C', 'E', 'F')
        # self.countryComboD.current(0)
        # self.countryComboD.grid(row=4, column=1, padx=2, pady=2, sticky=tkinter.W)
        # self.TrafficD = tkinter.Scale(self.traffic_frame, from_=0, to=MAX_SOURCE_TRAFFIC, length=300, resolution=1000, tickinterval=3000, orient='horizontal', command= lambda value, src='D': self.setTraffic(src, value))
        # self.TrafficD.grid(row=4, column=2, padx=2, pady=2, sticky=tkinter.W)
        # self.LabelBusyD = tkinter.Label(self.traffic_frame, text="0%", background='white')
        # self.LabelBusyD.grid(row=4, column=3, padx=1, pady=1, sticky=tkinter.W)
        #
        # # #traffic node E
        # self.LabelTrafficE = tkinter.Label(self.traffic_frame, text="E --> ")
        # self.LabelTrafficE.grid(row=5, column=0, padx=1, pady=1, sticky=tkinter.W)
        # self.countryVarE = tkinter.StringVar()
        # self.countryComboE = ttk.Combobox(self.traffic_frame, textvariable=self.countryVarE, width=5)
        # self.countryComboE['values'] = ('A', 'B', 'D', 'F', 'C')
        # self.countryComboE.current(0)
        # self.countryComboE.grid(row=5, column=1, padx=2, pady=2, sticky=tkinter.W)
        # self.TrafficE = tkinter.Scale(self.traffic_frame, from_=0, to=MAX_SOURCE_TRAFFIC, length=300, resolution=1000, tickinterval=3000, orient='horizontal', command= lambda value, src='E': self.setTraffic(src, value))
        # self.TrafficE.grid(row=5, column=2, padx=2, pady=2, sticky=tkinter.W)
        # self.LabelBusyE = tkinter.Label(self.traffic_frame, text="0%", background='white')
        # self.LabelBusyE.grid(row=5, column=3, padx=1, pady=1, sticky=tkinter.W)
        #
        # #traffic node F
        # self.LabelTrafficF = tkinter.Label(self.traffic_frame, text="F --> ")
        # self.LabelTrafficF.grid(row=6, column=0, padx=1, pady=1, sticky=tkinter.W)
        # self.countryVarF = tkinter.StringVar()
        # self.countryComboF = ttk.Combobox(self.traffic_frame, textvariable=self.countryVarF, width=5)
        # self.countryComboF['values'] = ('A', 'B', 'C', 'D', 'E')
        # self.countryComboF.current(0)
        # self.countryComboF.grid(row=6, column=1, padx=2, pady=2, sticky=tkinter.W)
        # self.TrafficF = tkinter.Scale(self.traffic_frame, from_=0, to=MAX_SOURCE_TRAFFIC, length=300, resolution=1000, tickinterval=3000, orient='horizontal', command= lambda value, src='F': self.setTraffic(src, value))
        # self.TrafficF.grid(row=6, column=2, padx=2, pady=2, sticky=tkinter.W)
        # self.LabelBusyF = tkinter.Label(self.traffic_frame, text="0%", background='white')
        # self.LabelBusyF.grid(row=6, column=3, padx=1, pady=1, sticky=tkinter.W)


        # TRAFFIC FRAME 2
        self.traffic_frame_2 = ttk.LabelFrame(self, text='Traffic', height=50, width=50)
        self.traffic_frame_2.grid(column=0, row=1, columnspan=1, sticky='nesw')

        self.LabelTraffic_2 = tkinter.Label(self.traffic_frame_2, text="Selector nodes traffic")
        self.LabelTraffic_2.grid(row=0, column=0, columnspan=5, padx=1, pady=1, sticky=tkinter.W)
        # self.LabelBusy = tkinter.Label(self.traffic_frame, text="busy-time")
        # self.LabelBusy.grid(row=0, column=3, columnspan=1, padx=1, pady=1, sticky=tkinter.W)

        # traffic radio button
        languages = [("0", 0), ("10M", 10000), ("20M", 20000)]

        # Label(root, text="""Choose your favourite programming language:""", justify=LEFT, padx=20).pack()
        self.radiobuttons = []
        self.radiobuttons_label = []
        self.countryVar = []
        self.countryCombo = []
        self.countryVar_2 = []
        self.labelBusy = []

        radiobutton_index = 0
        row_index = 0
        for node_index in range(0, len(self.all_nodes)):
            self.radiobuttons_label.append(tkinter.Label(self.traffic_frame_2, text=self.all_nodes[node_index] + " --> "))
            self.radiobuttons_label[node_index].grid(row=node_index + 1, column=0, padx=2, pady=2, sticky=tkinter.W)
            self.countryVar.append(tkinter.StringVar())
            self.countryCombo.append(ttk.Combobox(self.traffic_frame_2, textvariable=self.countryVar[node_index], width=5))
            self.countryCombo[node_index]['values'] = self.all_nodes
            self.countryCombo[node_index].current(0)
            self.countryCombo[node_index].grid(row=node_index + 1, column=1, padx=2, pady=2, sticky=tkinter.W)

            column_index = 0
            self.countryVar_2.append(tkinter.StringVar())

            for txt, val in languages:
                # self.radiobuttons.append(tkinter.Radiobutton(self.traffic_frame_2, text=txt, padx=20, variable=self.countryVar_2[node_index], command=ShowChoice, value=val))
                self.radiobuttons.append(tkinter.Radiobutton(self.traffic_frame_2, text=txt, padx=20, variable=self.countryVar_2[node_index], value=val,
                                                             command=lambda value=self.countryVar_2, src=self.all_nodes[node_index]: self.setTraffic(src, value)))
                self.radiobuttons[radiobutton_index].grid(row=node_index + 1, column=column_index + 2, padx=2, pady=2, sticky=tkinter.W)
                radiobutton_index += 1
                column_index += 1

            self.labelBusy.append(tkinter.Label(self.traffic_frame_2, text="0%", background='white'))
            self.labelBusy[node_index].grid(row=node_index+1, column=5, padx=1, pady=1, sticky=tkinter.W)

        # traffic node stop bustton
        self.stop_all_traffic_button = ttk.Button(self.traffic_frame_2, text="Stop all traffics", width=50, command=lambda: self.stopAllTraffic(), style=SUNKABLE_BUTTON1)
        self.stop_all_traffic_button.grid(row=10, column=1, columnspan=4, padx=5, pady=5, sticky=tkinter.W)
        self.stop_all_traffic_button.state(['!pressed', '!disabled'])
        self.style.configure(SUNKABLE_BUTTON1, relief=tkinter.RAISED, foreground='green')


        #PLOTTER topology
        self.statistics_topology_frame=ttk.LabelFrame(self, text="Topology", height=50, width=50)
        self.statistics_topology_frame.grid(column=1, row=1, columnspan=1, sticky='nesw')
        start_new_thread(self.plot_topology,(99,))

        # #INTERFERENCE INFORMATION
        # self.stats_frame = ttk.LabelFrame(self, text='Interference Classification', height=50, width=70)
        # self.stats_frame.grid(column=2, row=1, columnspan=1, sticky='nesw')
        #
        # self.tv = ttk.Treeview(self.stats_frame)
        # self.tv['columns'] = ('starttime', 'endtime', 'status')
        # self.tv.heading("#0", text='', anchor='w')
        # self.tv.column("#0", anchor="w", width=50)
        # self.tv.heading('starttime', text='Flow in the middle')
        # self.tv.column('starttime', anchor='center', width=100)
        # self.tv.heading('endtime', text='Hidden nodesM')
        # self.tv.column('endtime', anchor='center', width=100)
        # self.tv.heading('status', text='No interference')
        # self.tv.column('status', anchor='center', width=100)
        # self.tv.grid(row=0, column=0, columnspan=2, padx=5, pady=5, ipady=2, sticky ='nesw')
        #
        # self.tv.insert('', '0', text="A", values=('0', '0', '0'))
        # self.tv.insert('', '1', text="B", values=('0', '0', '0'))
        # self.tv.insert('', '2', text="C", values=('0', '0', '0'))
        # self.tv.insert('', '3', text="D", values=('0', '0', '0'))
        # self.tv.insert('', '4', text="E", values=('0', '0', '0'))
        # self.tv.insert('', '5', text="F", values=('0', '0', '0'))


        # cells = self.tv.get_children()
        # for item in cells: ## Changing all children from root item
        #     print(item)

        #self.tv.item('I001', text="A", values=('1', '1', '1'))

        # self.startReactBtn = ttk.Button(self.stats_frame, text="START ", width=10, command=lambda : self.startReact(),  style=SUNKABLE_BUTTON2)
        # self.startReactBtn.grid(row=1, column=0, padx=5, pady=5, ipady=2, sticky='nesw')
        # self.stopReactBtn = ttk.Button(self.stats_frame, text="STOP ", width=10, command=lambda : self.stopReact(),  style=SUNKABLE_BUTTON1)
        # self.stopReactBtn.grid(row=1, column=1, padx=5, pady=5, ipady=2, sticky='nesw')

        # self.LabelSourceDescription = Label(self.stats_frame, text="REACT algorithm: ")
        # self.LabelSourceDescription.grid(row=2, column=0, columnspan=1, padx=1, pady=1, sticky=W)
#         self.LabelClaimDescription = Label(self.stats_frame, justify=LEFT, text="Each node runs an auctioneer that maintains an offer,\n\
# the maximum airtime consumed by any adjacent bidder.\n\
# Similarly, each node also runs a bidder that maintains a claim, \n\
# the airtime the bidder intends to consume at adjacent auctions.\n\
# Through updates of offers and claims, the auctioneers and\n\
# bidders converge on an allocation of airtime.")
#         self.LabelClaimDescription.grid(row=3, column=0, columnspan=3, padx=1, pady=1, sticky='nesw')
#         # self.LabelOfferDescription = Label(self.stats_frame, text="The OFFER ")
#         # self.LabelOfferDescription.grid(row=4, column=0, columnspan=1, padx=1, pady=1, sticky=W)



        # PLOT TOPOLOGY IMAGE
        # self.topo_frame=ttk.LabelFrame(self, text="Network Scenario", height=50, width=50)
        # self.topo_frame.grid(column=2, row=1, columnspan=1, sticky='nesw')
        #
        # image_name = '../classification/normalized-confusion-matrix-long-training.png'
        # img=Image.open(image_name)
        # wpercent=100
        # basewidth = 490
        # wpercent = (basewidth/float(img.size[0]))
        # hsize = int((float(img.size[1])*float(wpercent)))
        # img = img.resize((basewidth,hsize), Image.ANTIALIAS)
        # im = ImageTk.PhotoImage(img)
        #
        # self.label_topo_img = tkinter.Label(self.topo_frame, image=im)
        # self.label_topo_img.image = im
        # self.label_topo_img.grid(row=0, column=0, sticky='nesw')
        #
        # img=Image.open('logo.png')
        # wpercent=100
        # basewidth = 490
        # wpercent = (basewidth/float(img.size[0]))
        # hsize = int((float(img.size[1])*float(wpercent)))
        # img = img.resize((basewidth,hsize), Image.ANTIALIAS)
        # im = ImageTk.PhotoImage(img)
        #
        # label_logo_img = tkinter.Label(self.topo_frame, image=im)
        # label_logo_img.image = im
        # label_logo_img.grid(row=1,column=0, sticky=tkinter.W+tkinter.E)




        #PLOTTER busy time
        self.statistics_busytime_frame=ttk.LabelFrame(self, text="Busy Time", height=50, width=50)
        self.statistics_busytime_frame.grid(column=0, row=2, columnspan=1, sticky='nesw')
        start_new_thread(self.plot_busytime,(99,))

        #PLOTTER tx time
        self.statistics_numtx_frame=ttk.LabelFrame(self, text="Number of transmissions", height=50, width=50)
        self.statistics_numtx_frame.grid(column=1, row=2, columnspan=1, sticky='nesw')
        start_new_thread(self.plot_numtx,(99,))

        #PLOTTER numtx_suc
        self.statistics_numtx_suc_frame=ttk.LabelFrame(self, text="Number of successful transmissions", height=50, width=50)
        self.statistics_numtx_suc_frame.grid(column=2, row=2, columnspan=1, sticky='nesw')
        start_new_thread(self.plot_numtx_suc,(99,))

        #LOOP command traffic
        start_new_thread(self.traffic_command_handles,(99,))

        # ttk.Separator(self, orient='horizontal').grid(column=0, row=1, columnspan=4, sticky='ew')
        #
        for child in self.winfo_children():
            child.grid_configure(padx=5, pady=5)

if __name__ == '__main__':
    #root = Tk()
    root = tkinter.Tk()
    Adder(root)
    root.mainloop()
