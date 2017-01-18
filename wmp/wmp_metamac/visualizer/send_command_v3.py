__author__ = 'domenico'

from Tkinter import *
import ttk
from PIL import Image, ImageTk

import random
from socket import *    # import *, but we'll avoid name conflict
from sys import argv, exit
import demjson

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
        w = 1600
        h = 350
        sw = self.parent.winfo_screenwidth()
        sh = self.parent.winfo_screenheight()
        #x = (sw - w)/2
        #y = (sh - h)/2
        x = (sw - w)
        y = (sh - h)
        self.parent.geometry('%dx%d+%d+%d' % (w, h, x, y))

    def send_command_sta1(self, event):
        if self.local_network :
            command_list = [{'command': self.countryVarSta1.get()}]
            json_command = demjson.encode(command_list)
            print(self.sta1_ipaddress + ' ' + json_command)
            self.sock.sendto(json_command, (self.sta1_ipaddress, self.sta1_server_port))
        else :
            command_list = {'type': 'protocol', 'command': self.countryVarSta1.get(), 'ip_address': self.sta1_ipaddress}
            json_command = command_list
            print(json_command)
            self.socket_command.send_json(json_command)
            message = self.socket_command.recv()
            print("Received reply ", "[", message, "]")


    def send_command_sta2(self, event):
        if self.local_network :
            command_list = [{'command': self.countryVarSta2.get()}]
            json_command = demjson.encode(command_list)
            print(self.sta2_ipaddress + ' ' + json_command)
            self.sock.sendto(json_command, (self.sta2_ipaddress, self.sta2_server_port))
        else :
            command_list = {'type': 'protocol', 'command': self.countryVarSta2.get(), 'ip_address': self.sta2_ipaddress}
            json_command = command_list
            print(json_command)
            self.socket_command.send_json(json_command)
            message = self.socket_command.recv()
            print("Received reply ", "[", message, "]")

    def send_command_sta3(self, event):
        if self.local_network :
            command_list = [{'command': self.countryVarSta3.get()}]
            json_command = demjson.encode(command_list)
            print(self.sta1_ipaddress + ' ' + json_command)
            self.sock.sendto(json_command, (self.sta3_ipaddress, self.sta3_server_port))
        else :
            command_list = {'type': 'protocol', 'command': self.countryVarSta3.get(), 'ip_address': self.sta3_ipaddress}
            json_command = command_list
            print(json_command)
            self.socket_command.send_json(json_command)
            message = self.socket_command.recv()
            print("Received reply ", "[", message, "]")

    def send_command_sta4(self, event):
        if self.local_network :
            command_list = [{'command': self.countryVarSta4.get()}]
            json_command = demjson.encode(command_list)
            print(self.sta4_ipaddress + ' ' + json_command)
            self.sock.sendto(json_command, (self.sta4_ipaddress, self.sta4_server_port))
        else :
            command_list = {'type': 'protocol', 'command': self.countryVarSta4.get(), 'ip_address': self.sta4_ipaddress}
            json_command = command_list
            print(json_command)
            self.socket_command.send_json(json_command)
            message = self.socket_command.recv()
            print("Received reply ", "[", message, "]")

    def stopTraffic(self):
        command = 'fab -u root -H alix02,alix03,alix04,alix05,alix15 stop_iperf'

        if self.local_network :
            nl_output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        else :
            command_list = {'type': 'traffic', 'command': command}
            json_command = command_list
            print(json_command)
            self.socket_command.send_json(json_command)
            message = self.socket_command.recv()
            print("Received reply ", "[", message, "]")


        self.stopTrafficBtn.state(['pressed', 'disabled'])
        self.style.configure(SUNKABLE_BUTTON1, relief=SUNKEN, foreground='green')

        self.lowTrafficBtn.state(['!pressed', '!disabled'])
        self.style.configure(SUNKABLE_BUTTON2, relief=RAISED, foreground='red')

        self.highTrafficBtn.state(['!pressed', '!disabled'])
        self.style.configure(SUNKABLE_BUTTON3, relief=RAISED, foreground='red')


    def startTrafficLow(self):
        command = 'fab -u root -H alix02 start_iperf_server:0'
        if self.local_network :
            nl_output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        else :
            command_list = {'type': 'traffic', 'command': command}
            json_command = command_list
            print(json_command)
            self.socket_command.send_json(json_command)
            message = self.socket_command.recv()
            print("Received reply ", "[", message, "]")

        time.sleep(2)

        command = 'fab -u root -H alix03,alix04,alix05,alix15 start_iperf_client:alix02,600,0.25M,1200'
        if self.local_network :
            nl_output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        else :
            command_list = {'type': 'traffic', 'command': command}
            json_command = command_list
            print(json_command)
            self.socket_command.send_json(json_command)
            message = self.socket_command.recv()
            print("Received reply ", "[", message, "]")


        self.lowTrafficBtn.state(['pressed', 'disabled'])
        self.style.configure(SUNKABLE_BUTTON2, relief=SUNKEN, foreground='green')

        self.stopTrafficBtn.state(['!pressed', '!disabled'])
        self.style.configure(SUNKABLE_BUTTON1, relief=RAISED, foreground='red')

        self.highTrafficBtn.state(['!pressed', '!disabled'])
        self.style.configure(SUNKABLE_BUTTON3, relief=RAISED, foreground='red')

    def startTrafficHigh(self):
        command = 'fab -u root -H alix02 start_iperf_server:0'
        if self.local_network :
            nl_output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        else :
            command_list = {'type': 'traffic', 'command': command}
            json_command = command_list
            print(json_command)
            self.socket_command.send_json(json_command)
            message = self.socket_command.recv()
            print("Received reply ", "[", message, "]")
        #
        time.sleep(2)
        #
        command = 'fab -u root -H alix03,alix04,alix05,alix15 start_iperf_client:alix02,600,1.5M,1200'
        if self.local_network :
            nl_output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        else :
            command_list = {'type': 'traffic', 'command': command}
            json_command = command_list
            print(json_command)
            self.socket_command.send_json(json_command)
            message = self.socket_command.recv()
            print("Received reply ", "[", message, "]")


        self.highTrafficBtn.state(['pressed', 'disabled'])
        self.style.configure(SUNKABLE_BUTTON3, relief=SUNKEN, foreground='green')

        self.stopTrafficBtn.state(['!pressed', '!disabled'])
        self.style.configure(SUNKABLE_BUTTON1, relief=RAISED, foreground='red')

        self.lowTrafficBtn.state(['!pressed', '!disabled'])
        self.style.configure(SUNKABLE_BUTTON2, relief=RAISED, foreground='red')


    def loopCapture(self):
        """
            location='http://127.0.0.1:8484/crewdemo/only_usrp.html'

        """
        #location='https://lab.tti.unipa.it/crewdemo/plots/usrp.png'
        if self.local_network :
            location='http://10.8.19.1/crewdemo/plots/usrp.png'
        else :
            location='http://127.0.0.1:8484/crewdemo/plots/usrp.png'

        # image = open('image.png', 'wb')
        # image.write(urllib.urlopen(location).read())
        # image.close()

        # try:
        #     urllib2.urlopen(req)
        # except URLError as e:
        #     #print e.reason
        try:
            urllib2.urlopen(location)
            u = urllib.urlopen(location)
            raw_data = u.read()
            u.close()

            #import base64
            b64_data = base64.encodestring(raw_data)
            bardejov = PhotoImage(data=b64_data)

        except URLError as e:
            print e.reason
            bard = Image.open("image.png")
            bardejov = ImageTk.PhotoImage(data=bard)


        label_usrp = Label(self.channel_frame, image=bardejov)
        label_usrp.image = bardejov
        #label1.place(x=5, y=150)
        label_usrp.grid(row=0,column=0, sticky=W+E)

        self.root.update_idletasks()
        self.root.after(DELAY, self.loopCapture)


    def init_gui(self):
        #SOCKET SETUP
        print('Network setup')
        self.local_network = 1
        if self.local_network :
            self.sock = socket(AF_INET, SOCK_DGRAM)
            self.sta1_ipaddress = '10.8.8.103'
            self.sta2_ipaddress = '10.8.8.104'
            self.sta3_ipaddress = '10.8.8.105'
            self.sta4_ipaddress = '10.8.8.115'
            self.server_port = 8400
            self.sta1_server_port = self.server_port
            self.sta2_server_port = self.server_port
            self.sta3_server_port = self.server_port
            self.sta4_server_port = self.server_port
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


        """Builds GUI."""
        print('GUI setup')
        self.root.title('WINTECH DEMO 2016')
        self.root.option_add('*tearOff', 'FALSE')

        self.parent = self.root
        self.root.title("Wintech 2016 DEMO")
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



        #TRAFFIC FRAME
        self.traffic_frame = ttk.LabelFrame(self, text='Traffic')
        self.traffic_frame.grid(column=1, row=1, columnspan=1, sticky='nesw')

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
        self.channel_frame = ttk.LabelFrame(self, text='Channel occupation', height=100, width=100)
        self.channel_frame.grid(column=2, row=1, columnspan=1, sticky='nesw')

        # self.answer_label2 = ttk.Label(self.traffic_frame, text='prova2 ')
        # self.answer_label2.grid(column=0, row=0)

        # create canvas for drawing

        # canvas = Canvas(self.channel_frame, width = 640, height = 480)
        # canvas.place_configure(x = 0, y = 0, width = 640, height = 480)

        # load image with PIL and draw to canvas

        # image = ImageTk.PhotoImage(file = 'image.png')
        # canvas.create_image(10, 10, image = image, anchor = NW)

        self.loopCapture()

        # ttk.Separator(self, orient='horizontal').grid(column=0,
        #         row=1, columnspan=4, sticky='ew')
        #
        for child in self.winfo_children():
            child.grid_configure(padx=5, pady=5)

if __name__ == '__main__':
    root = Tk()
    Adder(root)
    root.mainloop()