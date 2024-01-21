#!/usr/bin/python
#
# This script reads the WaterMeter.
#
# At startup the script reads an initial value, this should be the value
# of the watermeter at startup. This value is saved regularly to accomodate
# for power-outages.
#
# 20240121-174619 : updated script to use Python3
#
import RPi.GPIO as GPIO
import os
import sys
import traceback
import time
import datetime


# Setup the detection loop
GPIO.setmode(GPIO.BCM)  # use the GPIO numbers
pin=23 # This is pin 16
GPIO.setup(pin,GPIO.IN)

# read the startvalue from the log file. The format is unixtime, value
def readStartValue():
    watermeter=0
    # find the last file wmdata file and use this to reset the watermeter.
    targetfile="wmdata.0"
    date="0"
    value="0"
    for file in os.listdir("./"):
        if file.startswith("wmdata."):
            # check if the filesize is greater than 0
            if os.stat(file).st_size>9:
                if file>targetfile:
                    print("Targetfile %s" % targetfile)
                    targetfile=file
            # print(os.path.join("./", file), targetfile)
    try:
        f=open(targetfile,'r')    # open for reading,
        line=f.readline().strip()
        while line:
            (date,value)=line.split(' ')
            watermeter=int(float(value)*1000)
            # print "Watermeter %s" % value
            line=f.readline()
        f.close()
        # now move the file to the data directory and update wmdata.0
        if targetfile!="wmdata.0":
            moveFile(targetfile)
            updateWM0(date,value)

    except:
        print("Error opening file with data")
        traceback.print_exc(file=sys.stdout)
        sys.exit()

    print("readStartValue %.4f" % float(watermeter/1000.0))
    return watermeter

def writeValue(file,val):
        # write the value to the open file
        timestamp=time.time()
        f.write("%.3f %.4f\n" % (timestamp, val/1000.0))
        print("[%.3f] Tick detected %.04f" % (timestamp,float(watermeter/1000.0)))

correctionCounter=0
correctionFile="wmdata.correct"
def readCorrectionValue(watermeter):
    global correctionCounter,correctionFile

    if (correctionCounter % 100 == 0):
        if os.path.exists(correctionFile):
            # file exists, now parse file
            try:
                f=open(correctionFile,'r')    # open for reading,
                line=f.readline().strip()
                (date,value)=line.split(' ')
                watermeter=int(float(value)*1000)
                f.close()
                os.remove(correctionFile)
                print("Corrected watermeter to",watermeter)
            except:
                print("Error opening file with data")
                traceback.print_exc(file=sys.stdout)
                sys.exit()

    return watermeter

def updateWM0(date,value):
    f=open("wmdata.0","w") # remove the unbuffered option since this is no longer supported
    f.write("%s %s" % (date,value))
    f.close()


def moveFile(filename):
    dataname=os.path.join("../data/",filename)
    os.rename(filename,dataname)
### start the main loop
#initialise a previous input variable to 0 (assume button not pressed last)

writeWM0file=True
watermeter=readStartValue()
measure=True
pin_on=1
pin_off=0
# initialize the variables for measuring
prev_input = GPIO.input(pin)
currentState = prev_input
previousState = currentState  # make this the same to prevent immediately registering a tick
#
maxSpin = 6  # the number of repeat values before the state is reached
# 20220829-174846 : reduced the maxSpin to fix measurement misses
# 20220614-154429 : updated the spin count to increase the measurement capability of the script
cycleCount = 0
if currentState==pin_on:
    spinCount = maxSpin
else:
    spinCount = 0

#
try:
    while measure:
        # create new file for saving data
        filename="wmdata."+str(int(time.time()))
        # now open the file ready for writing, in unbuffered mode!
        f = open(filename,"w") # removed the unbuffered option
        #
        # Start taking measurements for 1000 times
        measurement_counter=0
        thisFile=True




        while thisFile: # keep measuring in this file

            time.sleep(0.01) # limit the sampling rate
            # 20220616 reduced to 0.01 to increase sensitivity
            # 20190108 returned to 0.02 to make reading more sensitive
            # 20180130 lowered time to 0.02 from 0.05 to increase sample density
            #take a reading
            inputPin = GPIO.input(pin)
            #print "Value %d" % input
            #if the last reading was different, print
            cycleCount+=1
            if inputPin==pin_on:
                if spinCount<maxSpin:
                    spinCount+=1
                else:
                    currentState=pin_on

            else:
                if spinCount>0:
                    spinCount-=1
                else:
                    currentState=pin_off



            # if (prev_input !=inputPin):
            #     print "[%.3f] pin %d count %d Off %d On %d  dOff %d dOn %d" % (time.time(), inputPin, measurement_counter,countOff,countOn, deltaOff, deltaOn)
            #
            #     deltaOn=0
            #     deltaOff=0
            #
            #     prev_input=inputPin
            #
            # if inputPin==pin_on:
            #     countOn+=1
            #     deltaOn+=1
            # else:
            #     countOff+=1
            #     deltaOff+=1
            #
            #
            # if deltaOn>2:
            #     currentState=pin_on
            #     # print "[on]",
            #
            # if deltaOff>2:
            #     currentState=pin_off
            #     # print "[off]",

            # print "cS %d pS %d  on %d off %d" % (currentState,previousState, deltaOn, deltaOff)
            if currentState!=previousState:
                print("[%.3f] pin %d count %d cycles %d" % (time.time(), currentState, measurement_counter, cycleCount))

                # print "stateChange %d" % (currentState)
                # only measure when we have seen a change in state
                if currentState==pin_on:
                    watermeter+=1  # increase the value of the watermeter with 10 liters
                    writeValue(f,watermeter)
                    # decrement the counter
                    measurement_counter+=1


                # reset the velocity counters, because the state changed
                cycleCount=0
                previousState=currentState

            # if (prev_input !=inputPin):
            #     # only measure when the value becomes positive. This measures the tick
            #     # when the strip leaves the detector.
            #     print "[%.3f] pin %d count %d Off %d On %d  dOff %d dOn %d" % (time.time(), inputPin, measurement_counter,countOff,countOn, deltaOff, deltaOn)
            #     if inputPin==pin_on:
            #         # print "[%d] Off %d On %d  dOff %d dOn %d" % (measurement_counter,countOff,countOn, deltaOff, deltaOn)
            #         # now only detect a tick if the countOff counter is larger than 5, only count of the countOn timer is greater than 50
            #         if  deltaOn>1 and deltaOff>1 and countOn>50 :
            #             watermeter+=1  # increase the value of the watermeter with 10 liters
            #             writeValue(f,watermeter)
            #             # decrement the counter
            #             measurement_counter+=1
            #             # reset the velocity counters, because our measurement was succesfull
            #             countOn=0
            #             countOff=0

            #         # tracking the delta's, reset them for each measurement
            #         deltaOn=0
            #         deltaOff=0


            #     #update previous input
            #     prev_input = inputPin
            # no measurement found
            # now prevent the script from writing the file while water is actively being consumed.
            if currentState==pin_off:
                if (measurement_counter>1000):
                    if (cycleCount)>10000:
                        # it's been a while since the last tick, now process the file
                        print("[%.3f] Saving file - count %d cycles %d" % ( time.time(),  measurement_counter, cycleCount))
                        thisFile=False

                #
            if cycleCount == 8400: # updated to 3400 to move it outside the most common repeat ticks
                # update the WM0 file for good measure. Only need to do this once.
                updateWM0(time.time(), float(watermeter / 1000.0))
                    #
            if (cycleCount % 1001) == 1000:
                # check for the existence of the correction file, if it exists parse file and adjust to new value
                # only do this when it has been relatively calm, about every four seconds
                watermeter = readCorrectionValue(watermeter)

        # max measurements done, close file and continue
        f.close()
        # close the file and move it to the data location
        moveFile(filename)
        ## now make a new file

except KeyboardInterrupt:
    print("Control-C detected")
    f.close()
    moveFile(filename)
    timestamp=int(time.time())
    updateWM0(timestamp,float(watermeter/1000.0))
except:
    print("Other error detected")
    traceback.print_exc(file=sys.stdout)

finally:
    GPIO.cleanup()
    print("...exiting")
