#!/usr/bin/python

from wdc2250 import WDC2250, Channel
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

axisWrist = Channel(controllerC, 1)
axisElbow = Channel(controllerC, 2)
axisWristBend = Channel(controllerB, 1)
axisTool = Channel(controllerB, 2)
axisBase = Channel(controllerA, 1)
axisShoulder = Channel(controllerA, 2 )

axisMap = {
    "wrist": axisWrist,
    "elbow": axisElbow,
    "bend": axisWristBend,
    "tool": axisTool,
    "base": axisBase,
    "shouler": axisShoulder
}

controllers = [ controllerA, controllerB, controllerC ]

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
    for c in controllers:
        c.runScript(controller_script)
    axisBase.config({"MVEL":750})
    axisWrist.config( {
        "ELL"  :-20000,
        "EHL"  : 20000,
        "MXTRN": 10000,
        })
    for command in sys.argv[1:]:
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
        elif command == 'reset':
            for c in controllers:
                c.resetToEeprom()
    controllerA.close()
    controllerB.close()
    controllerC.close()



