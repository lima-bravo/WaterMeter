#!/usr/bin/env python

#imports
import time
import RPi.GPIO as GPIO
import json
import urllib2
import threading

#vars
GET_URL = 'http://localhost:8080/json.htm?type=devices&rid=%d'
SET_URL = 'http://localhost:8080/json.htm?type=command&param=udevice&idx=%d&svalue=%d'
GAS_DELTA = 0
GAS_IDX = 3
GAS_GPIO = 26
GAS_COUNTER_LOCK = threading.Lock()
ELEC_DELTA = 0
ELEC_IDX = 4
ELEC_GPIO = 16
ELEC_COUNTER_LOCK = threading.Lock()

def gpio_intr(pin):
    if pin == GAS_GPIO:
        global GAS_DELTA
        with GAS_COUNTER_LOCK:
            GAS_DELTA += 1
        print 'Gas counter tick: %d' % GAS_DELTA

    if pin == ELEC_GPIO:
        global ELEC_DELTA
        with ELEC_COUNTER_LOCK:
            ELEC_DELTA += 1
        print 'Electricity counter tick: %d' % ELEC_DELTA

def main():
    global GAS_DELTA
    global ELEC_DELTA

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(GAS_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.add_event_detect(GAS_GPIO, GPIO.RISING, callback=gpio_intr, bouncetime=100)
    GPIO.setup(ELEC_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.add_event_detect(ELEC_GPIO, GPIO.RISING, callback=gpio_intr, bouncetime=100)

    while True:
        time.sleep(5)

        GAS_DELTA_POST = GAS_DELTA

        if GAS_DELTA_POST != 0:
            try:
                res = json.load(urllib2.urlopen(SET_URL % (GAS_IDX, GAS_DELTA_POST)))
                if res['status'] != 'OK':
                    raise Exception('Domoticz json error')
                with GAS_COUNTER_LOCK:
                    GAS_DELTA -= GAS_DELTA_POST
            except Exception as e:
                print e

        ELEC_DELTA_POST = ELEC_DELTA

        if ELEC_DELTA_POST != 0:
            try:
                res = json.load(urllib2.urlopen(SET_URL % (ELEC_IDX, ELEC_DELTA_POST)))
                if res['status'] != 'OK':
                    raise Exception('Domoticz json error')
                with ELEC_COUNTER_LOCK:
                    ELEC_DELTA -= ELEC_DELTA_POST
            except Exception as e:
                print e

        print 'Gas delta %d; Elec delta %d' % (GAS_DELTA_POST, ELEC_DELTA_POST)

if __name__=="__main__":
    main() 
