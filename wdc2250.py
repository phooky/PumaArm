#!/usr/bin/python

import serial
import sys
import threading

## IMPORTANT
## Check for/remove modemmanager

def portFromId(id):
    if sys.platform == 'linux2':
        return "/dev/serial/by-id/usb-Roboteq_Motor_Controller_{0}-if00".format(id)
    else:
        raise RuntimeError("No defined way to find serial port name on platform "+sys.platform)

class WDC2250:
    def __init__(self, id=None, port=None):
        self.id = id
        self.echo = True
        if port:
            self.port = port
        elif id:
            self.port = portFromId(self.id)
        try:
            self.serial = serial.Serial(self.port,115200,timeout=5)
        except:
            print("Failed to open serial port "+self.port)
            self.serial = None

    def config(self,configMap):
        c = self.cont
        for key, value in configMap.items():
            print "Setting {0} to {1}...".format(key,value)
            c.runQuery("^{0} {1} {2}".format(key,self.chan,value))

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
        if self.serial == None:
            print "No serial for query"
            return ""
        else:
            self.safeWrite("{0}\r".format(q))
            return self.readLine()

    def runScript(self, script):
        for line in script.split("\n"):
            line = line.split("#",1)[0].strip()
            if line:
                self.runQuery(line)
            
    def resetToEeprom(self):
        print "Resetting to EEPROM settings... ",
        print(self.runQuery("%EELD"))

    def estop(self):
        self.runQuery("!EX")

    def close(self):
        self.serial.close()

class Channel:
    def __init__(self,controller,channel):
        self.cont = controller
        self.chan = channel
        self.target = 0

    def config(self,configMap):
        c = self.cont
        for key, value in configMap.items():
            print "Setting {0} to {1} on {2}...".format(key,value,c.id)
            c.runQuery("^{0} {1} {2}".format(key,self.chan,value))

    def setP(self,val):
        self.target = val
        self.cont.runQuery("!P {0} {1}".format(self.chan,val))

    def setSpeed(self,rpm=100):
        self.speed = rpm
        self.cont.runQuery("!S {0} {1}".format(self.chan,rpm))

    def setAccel(self,rpmps=6000):
        self.accel = rpmps
        self.cont.runQuery("!AC {0} {1}".format(self.chan,rpmps))
        self.cont.runQuery("!DC {0} {1}".format(self.chan,rpmps))

    def getCurrentPos(self):
        encoded=self.cont.runQuery("?C {0}".format(self.chan))
        return int(encoded[2:].strip())

    def getCurrentTarget(self):
        return self.target



