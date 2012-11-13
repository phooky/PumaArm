#!/usr/bin/python

import serial
import sys
import argparse

PARAMS_CONFIG_SAFETY = [
    "ACS",
    "AMS",
    "BRUN",
    "CLIN",
    "CPRI",
    "DFC",
    "ECHOF",
    "RWD",
    "TELS",
]

PARAMS_DIO_CONFIG = [
    "DINA",
    "DINL",
    "DOA",
    "DOL",
]

PARAMS_ANALOG_INPUT_CONFIG = [
    "ACTR",
    "ADB",
    "AINA",
    "ALIN",
    "AMAX",
    "AMAXA",
    "AMIN",
    "AMINA",
    "AMOD",
    "APOL",
]

PARAMS_PULSE_INPUT_CONFIG = [
    "PCTR",
    "PDB",
    "PINA",
    "PLIN",
    "PMAX",
    "PMAXA",
    "PMIN",
    "PMINA",
    "PMOD",
    "PPOL",
]

PARAMS_ENCODER = [
    "EHL",
    "EHLA",
    "EHOME",
    "ELL",
    "ELLA",
    "EMOD",
    "EPPR",
]

PARAMS_BRUSHLESS = [
    "BHL",
    "BHLA",
    "BHOME",
    "BLFB",
    "BLL",
    "BLLA",
    "BLSTD",
    "BPOL",
]

PARAMS_POWER = [
    "BKD",
    "MXMD",
    "OVL",
    "PWMF",
    "THLD",
    "UVL",
]

PARAMS_MOTOR_CHAN = [
    "ALIM",
    "ATGA",
    "ATGD",
    "ATRIG",
    "CLERD",
    "ICAP",
    "KD",
    "KI",
    "KP",
    "MAC",
    "MDEC",
    "MMOD",
    "MVEL",
    "MXPF",
    "MXPR",
    "MXRPM",
    "MXTRN",
]

PARAMS_SEPEX = [
    "SXC",
    "SXM",
]

ALL_PARAMS = PARAMS_CONFIG_SAFETY + PARAMS_DIO_CONFIG + PARAMS_ANALOG_INPUT_CONFIG + PARAMS_PULSE_INPUT_CONFIG + PARAMS_ENCODER + PARAMS_BRUSHLESS + PARAMS_POWER + PARAMS_MOTOR_CHAN + PARAMS_SEPEX

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
                print("ERROR: port {0} did not echo message (sent {1}, recv {2})".format(id,msg,echoed))

    def runQuery(self, q):
        self.safeWrite("{0}\r".format(q))
        return self.readLine()

    def dumpConfiguration(self,f):
         for parameter in ALL_PARAMS:
            f.write(self.runQuery("~"+parameter).strip()+"\n")

    def close(self):
        self.serial.close()


class Channel:
    def __init__(self,controller,channel):
        self.cont = controller
        self.chan = channel
    def initialize(self):
        c = self.cont


    #controllerC = Controller("8D9B20625254") # bottom (wrist)
    #controllerA = Controller("8D8643975049") # top (shoulder)
    #controllerB = Controller("8D9021655254") # middle (elbow)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--id", dest="id")

    parsed = parser.parse_args(sys.argv[1:])
    
    if not parsed.id:
        print("Provide a controller ID.")
        parser.usage()
        sys.exit(1)
    else:
        controller = Controller(parsed.id)
        controller.dumpConfiguration(sys.stdout)
        controller.close()



