#!/usr/bin/python

from wdc2250 import WDC2250, Channel
import sys
import argparse
import time
import random
import serial

# Bottom: 8D9B20625254
# CH1 : wrist rotation
# CH2 : elbow rotation
controllerC = WDC2250("8D9B20625254")
# Middle: 8D9021655254
# CH1 : wrist bend
# CH2 : tool rotation
controllerB = WDC2250("8D9021655254")
# Top: 8D8643975049
# CH1 : base rotation
# CH2 : shoulder rotation
controllerA = WDC2250("8D8643975049")

axisWrist = Channel(controllerC, 2)
axisElbow = Channel(controllerC, 1)
axisWristBend = Channel(controllerB, 1)
axisTool = Channel(controllerB, 2)
axisBase = Channel(controllerA, 1)
axisShoulder = Channel(controllerA, 2 )

axisMap = {
    "A": axisWrist,
    "Z": axisElbow,
    "B": axisWristBend,
    "C": axisTool,
    "X": axisBase,
    "Y": axisShoulder,
}

controllers = [ controllerA, controllerB, controllerC ]

currentAxis = ""
jogMax = 600
controller = None
dialFactor = 8

def switchAxis(axis):
    global currentAxis
    if controller:
        controller.write(currentAxis.lower())
        controller.write(axis)
        currentAxis = axis

clock = 0
jogMode = False

def handleCommand(line):
    global currentAxis
    global clock
    global jogMode
    [buttons, relative, pot] = map(lambda x: int(x,16), line.split(","))
    relative = relative * dialFactor
    if currentAxis != "":
        axis = axisMap[currentAxis]
        axis.setSpeed((10000*pot)/(1<<10))
    else:
        axis = None
    wasJogMode = jogMode
    for i in range(0,10):
        if buttons & (1<<i):
            if i == 0:
                switchAxis("X")
            elif i == 1:
                switchAxis("Y")
            elif i == 2:
                switchAxis("Z")
            elif i == 3:
                switchAxis("A")
            elif i == 4:
                switchAxis("B")
            elif i == 5:
                pass # ignore pot switch
            elif i == 6:
                switchAxis("C")
            elif i == 7 and axis:
                axis.setP(axis.getCurrentPos() + jogMax)
                jogMode = True
            elif i == 8 and axis:
                axis.setP(axis.getCurrentPos() - jogMax)
                jogMode = True
            elif i == 9:
                currentAxis=""
                relative = 0
                pot = 0
                for key, a in axisMap:
                    a.setSpeed(0)
                return
    if wasJogMode and not jogMode:
        axis.setP(axis.getCurrentPos())
    if relative != 0 and axis:
        target = axis.getCurrentTarget() + relative
        axis.setP(target)
    newClock = time.time()
    if newClock - clock > 0.2:
        printAll()
        clock = newClock

        
def attachController(port):
    global controller
    controller = serial.Serial(port,115200,timeout=5)
    controller.write("xyzab")
    line = []
    while True:
        c = controller.read()
        if c == "\n":
            handleCommand("".join(line))
            line = []
        else:
            line.append(c)

def printAll():
    sys.stderr.write("\x1b[2J\x1b[H")
    for key, value in axisMap.items():
        pos = value.getCurrentPos()
        target = value.getCurrentTarget()
        delta = pos - target
        print "{0:>10}:{1:>+8}/{2:<+8}   delta:{3}".format(key,pos,target,delta)
    print "\r",
    sys.stdout.flush()


if __name__ == '__main__':
    attachController("/dev/ttyACM0")



