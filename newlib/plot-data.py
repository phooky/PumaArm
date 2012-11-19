#!/usr/bin/python

import matplotlib.pyplot as plt
import sys

# We have one graph per channel.
channels = {}

def store(channel,dat_type,time_ms,value):
    if not channel in channels:
        channels[channel] = {
            "pow" : ([],[]),
            "pos" : ([],[]),
            "vel" : ([],[])
            }
    chanmap = channels[channel]
    (xs,ys) = chanmap[dat_type]
    xs.append(time_ms)
    ys.append(value)

for line in sys.stdin.readlines():
    dat = line.split(",")
    time_ms = int(dat[0])
    c_id = dat[1]
    dat_type = dat[2]
    ch1 = int(dat[3])
    ch2 = int(dat[4])
    store(c_id+"-1",dat_type,time_ms,ch1)
    store(c_id+"-2",dat_type,time_ms,ch2)

for (name, chan) in channels.items():
    for dtype in ["pow","pos","vel"]:

        (xs,ys) = chan[dtype]
        plt.plot(xs,ys,"-")
plt.show()
    
