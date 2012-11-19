#!/usr/bin/python

from wdc2250 import WDC2250
import sys
import argparse
import time
import random
import serial
import logging
import signal

# Bottom: 8D9B20625254
# CH1 : wrist rotation
# CH2 : elbow rotation

if __name__ == '__main__':
    logger = logging.getLogger('store')
    logger.setLevel(logging.DEBUG)

    handler = logging.FileHandler('./armdata.log')
    formatter = logging.Formatter('%(relativeCreated)d,%(message)s')
    #handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    controller = WDC2250("8D9B20625254", log=logger)
    controller.start()
    def signal_handler(signal, frame):
        controller.stop()
        sys.exit(0)
    signal.signal(signal.SIGINT,signal_handler)
    controller.channels[0].setSpeed(8000)
    controller.channels[0].setAcceleration(60000)
    controller.channels[0].setDeceleration(60000)
    while True:
        time.sleep(1.5)
        controller.channels[0].setTargetPos(3000)
        time.sleep(1.5)
        controller.channels[0].setTargetPos(-3000)
        time.sleep(1.5)
        controller.channels[0].setTargetPos(0)



