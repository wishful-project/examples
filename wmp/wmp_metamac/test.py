    #If there is no packet queued for this slot, consider all protocols to be correct
    #and thus the weights will not change
if (current_slot.packet_queued) :
    #z represents the correct decision for this slot - transmit if the channel
    #is idle (1.0) or defer if it is busy (0.0)
    z=0.0
    if (not current_slot.channel_busy):
        z = 1.0
    for p in range(suite.num_protocols) :
        d = tdma_emulate(suite.protocols[p].parameter, current_slot.slot_num, suite.slot_offset)

        exponent = suite.eta * math.fabs(d - z)
        suite.weights[p] *= math.exp(-exponent)

        if suite.weights[p]<0.01:
            suite.weights[p]=0.01

    #Normalize the weights
    s = 0
    for p in range(suite.num_protocols):
        s += suite.weights[p]
    for p in range(suite.num_protocols):
        suite.weights[p] /= s
