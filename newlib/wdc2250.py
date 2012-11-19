#!/usr/bin/python

import serial
import sys
import threading
import logging
import time
import signal

## IMPORTANT
## Check for/remove modemmanager

def portFromId(id):
    if sys.platform == 'linux2':
        return "/dev/serial/by-id/usb-Roboteq_Motor_Controller_{0}-if00".format(id)
    else:
        raise RuntimeError("No defined way to find serial port name on platform "+sys.platform)

class WDC2250:
    def __init__(self, id=None, port=None, log=None):
        self.id = id
        self.log = log
        if port:
            self.port = port
            if not id:
                self.id = port
        elif id:
            self.port = portFromId(self.id)
        try:
            self.serial = serial.Serial(self.port,115200,timeout=5)
        except:
            print("Failed to open serial port "+self.port)
            self.serial = None
        self.serialLock = threading.Lock()
        self.send("#")
        self.send("^ECHOF 0")
        self.serial.flush()
        self.channels = [WDC2250.Channel(self,1), WDC2250.Channel(self,2)]
        self.running = False
       

    def readLine(self):
        "Read until carriage return."
        self.serialLock.acquire()
        line = []
        try:
            while True:
                c = self.serial.read(1)
                line.append(c)
                if c == '' or c == '\r':
                    break
        finally:
            self.serialLock.release()
        return "".join(line)

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self.consume)
        self.thread.start()

    def stop(self):
        self.running = False
        self.thread.join()

    def consume(self):
        self.send("# C")
        self.send("?C")
        self.send("?P")
        self.send("?S")
        self.send("# 5")
        self.serial.flushInput()
        while self.running:
            line = self.readLine()
            if line[0:2] == "C=":
                self.pos = map(int,line[2:].split(":"))
                self.log.info("{0},pos,{1},{2}".format(self.id,self.pos[0],self.pos[1]))
            elif line[0:2] == "P=":
                self.power = map(int,line[2:].split(":"))
                self.log.info("{0},pow,{1},{2}".format(self.id,self.power[0],self.power[1]))
            elif line[0:2] == "S=":
                self.velocity = map(int,line[2:].split(":"))
                self.log.info("{0},vel,{1},{2}".format(self.id,self.velocity[0],self.velocity[1]))
            else:
                pass

    def send(self,msg):
        "Write a string to the port"
        self.serialLock.acquire()
        self.serial.write(msg+"\r")
        self.serialLock.release()

    def setTargetPos(self, channel, p):
        "Set the target position"
        self.send("!P {0} {1}".format(channel,p))

    def setSpeed(self, channel, speed):
        "Set the speed for closed-loop positioning"
        self.send("!S {0} {1}".format(channel,speed))

    def setAcceleration(self, channel, ac):
        "Set the acceleration for closed-loop positioning"
        self.send("!AC {0} {1}".format(channel,ac))

    def setDeceleration(self, channel, dc):
        "Set the deceleration for closed-loop positioning"
        self.send("!DC {0} {1}".format(channel,dc))
    
    def estop(self):
        self.send("!EX")

    def close(self):
        self.serial.close()

    class Channel:
        def __init__(self,controller,index):
            self.c = controller
            self.i = index
            self.targetPos = 0
            self.targetSpeed = 0

        def setTargetPos(self, p):
            "Set the target position"
            self.targetPos = p
            self.c.setTargetPos(self.i,p)

        def setSpeed(self, speed):
            "Set the speed for closed-loop positioning"
            self.targetSpeed = speed
            self.c.setSpeed(self.i,speed)

        def setAcceleration(self, ac):
            "Set the acceleration for closed-loop positioning"
            self.c.setAcceleration(self.i,ac)

        def setDeceleration(self, dc):
            "Set the deceleration for closed-loop positioning"
            self.c.setDeceleration(self.i,dc)

