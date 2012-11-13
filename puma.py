#!/usr/bin/python

import serial
import sys
import argparse
import time
import random

controller_script = """
^MMOD 1 3
^MMOD 2 3
~MMOD
~EMOD
"""

def portFromId(id):
    return "/dev/serial/by-id/usb-Roboteq_Motor_Controller_{0}-if00".format(id)

class Controller:
    def __init__(self, id):
        self.id = id
        self.echo = True
        self.serial = serial.Serial(portFromId(self.id),115200)

    def readLine(self):
        "Read until carriage return."
        line = []
        while True:
            c = self.serial.read(1)
            line.append(c)
            if c == '\r':
                break
        return "".join(line)

    def safeWrite(self,msg):
        "Write a string to the port and read back the echoed characters."
        self.serial.write(msg)
        if self.echo:
            echoed = self.readLine()
            if echoed != msg:
                print("ERROR: port {0} did not echo message (sent {1}, recv {2})".format(self.id,msg,echoed))

    def runQuery(self, q):
        self.safeWrite("{0}\r".format(q))
        return self.readLine()

    def setup(self):
        for command in filter(None,[x.strip() for x in controller_script.split("\n")]):
            print(command)
            print(self.runQuery(command))

    def close(self):
        self.serial.close()

class Channel:
    def __init__(self,controller,channel):
        self.cont = controller
        self.chan = channel
        self.target = 0
    def initialize(self):
        c = self.cont
    def setP(self,val):
        self.target = val
        self.cont.runQuery("!P {0} {1}".format(self.chan,val))
    def getCurrentPos(self):
        encoded=self.cont.runQuery("?C {0}".format(self.chan))
        return int(encoded[2:].strip())
    def getCurrentTarget(self):
        return self.target

# Bottom: 8D9B20625254
# CH1 : wrist rotation
# CH2 : elbow rotation
controllerC = Controller("8D9B20625254")
# Middle: 8D9021655254
# CH1 : wrist bend
# CH2 : tool rotation
controllerB = Controller("8D9021655254")
# Top: 8D8643975049
# CH1 : base rotation
# CH2 : shoulder rotation
controllerA = Controller("8D8643975049")

axisWrist = Channel(controllerC, 1)
axisElbow = Channel(controllerC, 2)
axisWristBend = Channel(controllerB, 1)
axisTool = Channel(controllerB, 2)
axisBase = Channel(controllerA, 1)
axisShoulder = Channel(controllerA, 2)

axisMap = {
    "wrist": axisWrist,
    "elbow": axisElbow,
    "bend": axisWristBend,
    "tool": axisTool,
    "base": axisBase,
    "shouler": axisShoulder
}

def printAll():
    sys.stderr.write("\x1b[2J\x1b[H")
    for key, value in axisMap.items():
        pos = value.getCurrentPos()
        target = value.getCurrentTarget()
        delta = pos - target
        print "{0:>10}:{1:>+6}/{2:<+6}   delta:{3}".format(key,pos,target,delta)
    print "\r",
    sys.stdout.flush()


if __name__ == '__main__':
    
    controllerA.setup()
    controllerB.setup()
    controllerC.setup()
    if sys.argv[1] == 'random':
        while True:
            for v in axisMap.values():
                v.setP(random.randrange(-3500,3500))
            for i in range(15):
                time.sleep(0.1)
                printAll()
    elif sys.argv[1] == 'tozero':
            for v in axisMap.values():
                v.setP(0)
            time.sleep(1.5)
            printAll()
    controllerA.close()
    controllerB.close()
    controllerC.close()



