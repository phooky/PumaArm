#!/usr/bin/python

import serial
import sys
import argparse

from wdc2250 import WDC2250

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


def dumpConfiguration(controller,f,raw):
    for parameter in ALL_PARAMS:
        response = controller.runQuery("~"+parameter).strip()
        if raw:
            f.write(response+"\n")
        else:
            [param,value] = response.split("=",1)
            values = value.strip().split(":")
            if len(values) == 1:
                if values[0]:
                    f.write("^{0} {1}\n".format(param,value))
                else:
                    f.write('^{0} ""\n'.format(param))
            else:
                for n in range(len(values)):
                    f.write("^{0} {1} {2}\n".format(param,1+n,values[n]))

def loadConfiguration(controller,f):
    controller.runScript(f.read())

    #controllerC = Controller("8D9B20625254") # bottom (wrist)
    #controllerA = Controller("8D8643975049") # top (shoulder)
    #controllerB = Controller("8D9021655254") # middle (elbow)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--id", dest="id")
    parser.add_argument("--port", dest="port")
    parser.add_argument("--raw", action="store_true")
    parser.add_argument("--load", action="store_true")

    parsed = parser.parse_args(sys.argv[1:])
    
    if not parsed.port and not parsed.id:
        print("Provide a serial port name or id.")
        parser.usage()
        sys.exit(1)
    else:
        if parsed.port:
            controller = WDC2250(port=parsed.port)
        else:
            controller = WDC2250(id=parsed.id)
        if parsed.load:
            loadConfiguration(controller,sys.stdin)
        else:
            dumpConfiguration(controller,sys.stdout,parsed.raw)
        controller.close()



