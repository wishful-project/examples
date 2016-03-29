#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
from mininet.net import Mininet
from mininet.node import Controller,OVSKernelSwitch
from mininet.link import TCLink
from wishful_mininet import WishfulNode, WishfulAgent, WishfulController

def topology():
    # Create a network
    net = Mininet( controller=Controller, link=TCLink, switch=OVSKernelSwitch )

    # Create nodes
    sta1 = net.addStation( 'sta1', mac='02:00:00:00:00:00', ip='10.0.0.2/8' )
    sta2 = net.addStation( 'sta2', mac='02:00:00:00:01:00', ip='10.0.0.3/8' )
    ap1 = net.addBaseStation( 'ap1', ssid= 'new-ssid1', mode= 'g', channel= '1', position='15,50,0' ) # mac=02:00:00:00:02:00
    c1 = net.addController( 'c1', controller=Controller )

    # Create links
    net.addLink(ap1, sta1)
    net.addLink(ap1, sta2)

    # Start network
    net.build()
    c1.start()
    ap1.start( [c1] )

    # Configure IP addresses on AP for binding Wishful agent
    ap1.cmd('ifconfig ap1-eth1 20.0.0.2/8')

    # Start Wishful local controller on AP
    wf_ctrl = WishfulController(ap1, './local_controller', './config.yaml')
    wf_ctrl.start()

    # Generate traffic
    sta1.cmd('ping -c10 %s' % sta2.IP())

    # Show controller log file
    print('<log file>')
    print(wf_ctrl.read_log_file())
    print('</log file>')

    # Stop network
    wf_ctrl.stop()
    net.stop()

if __name__ == '__main__':
    topology()
