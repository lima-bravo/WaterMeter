#!/usr/bin/env python
#
# This script is written for Python 3.10
#
# This script parses the log file to look for instances where ticks may have been missed because
# the script was too slow to detect the tick. This can only happen if the tick count is <11 (before
# the measurement script was updated to deal with this issue.
#
# This script works by reading the readWM.log line by line and tracking for the fixed sequence of events
# first pin 0, then pin 1, then tick line is calculated.
# The pin count lines each have 7 elements, the tick detected line has 4. If a line does not have these counts
# it is not relevant.
#
# Observations on the pin count. pin 1 with cycles less than 11 are not counted.
# The cycle count of pin 0 is relevant here.
# The first iteration of the script should find the number of instances where we
# seem to have skipped a measurement.
# Elapsed time is a factor there too.

# we populate a standard struct to keep the most recent data available, once we have determined a tick.
#

import os, sys, math
#from pg import DB
import psycopg2
from dataclasses import dataclass

try:
    db = psycopg2.connect(
        database='sensordata',
        host='localhost',
        port=5432,
        user='sensor_main',
        password='SuperSensor'
    )
    cursor=db.cursor()

except Exception as e:
    print("Error accessing database")
    print(e)
    sys.exit()


@dataclass
class PinOut:
    ts : float
    pin : int
    cycles : int

# now create two instances of PinOut
P0=PinOut(0,0,0)
P1=PinOut(0,0,0)
Pold=PinOut(0,0,0)
Pprime=PinOut(0,0,0) # has the flow been primed
deltatick=0 # the global tick correction calculated.
is_sequence=False

def executeQuery(sql):
    try:
        cursor.execute(sql)
        print(sql)
    except Exception as e:
        print(e)
        # print "Constraints violation on "+sql
        pass


def calcDeltaTick(cycles):
    ticks=math.floor((cycles+12)/81)

    return ticks

def processPin(fields):
    global P0,P1

    ts=float(fields[0][1:14])
    pin=int(fields[2])
    cycles=int(fields[6])

    if pin==0:
        P0=PinOut(ts,pin,cycles)
    else:
        P1=PinOut(ts,pin,cycles)

def processTick(fields):
    global P0,P1,Pold,Pprime,deltatick, is_sequence

    # if Pprime.cycles<12:
    if P1.ts>1649763710 and P1.ts<1655190800: # limit it to the window where the errors where made
        # let's also focus if the are in sequence.
        if P1.cycles<12:
            if P0.cycles>100:
                dticks=calcDeltaTick(P0.cycles)
                if dticks < 20 and dticks>1:
                    dtime=P0.ts-Pold.ts
                    dflow=dticks/dtime*3.6
                    if Pold.cycles < 15 and Pprime.cycles<10000:
                        if dflow>1.846 and dflow<2.219:
                            if is_sequence:
                                # print(P0,"{} {:.3f} {:.3f}".format(dticks,dflow, dtime ))
                                deltatick+=dticks
                            else:
                                is_sequence=True
        else:
            is_sequence=False

        # now determine if we need to correct the tick
        # we must update the ticks in the database for these times
        if fields[0][0]!='C':
            ts=int(fields[0][1:11])
            val=float(fields[3])
            newval=val+(deltatick/1000.0)
            # print(ts,val,newval)
            sql="UPDATE water SET val={:.3f} WHERE ts=to_timestamp({})".format(newval,ts)
            executeQuery(sql)

    Pold=P1
    Pprime=P0

def processFile(filename):
    # start processing the file, line by line
    print(filename)
    f=open(filename,'r')
    line=f.readline()
    # now start the loop until we have completed the whole file
    while line:
        fields=line.strip().split(" ")
        # now take action based on the length of fields
        if len(fields) == 7:
            processPin(fields)
        elif len(fields) == 4:
            processTick(fields)
        else:
            # print("Skipping line {} fields : {}".format(len(fields),line))
            pass
        #
        # end of the processing, read the next line
        line=f.readline()
    # end of the while loop, now close the file
    f.close()


## main section
filename="../data/readWM.log.1655565750"
processFile(filename)
#
print("Deltaticks : {}".format(deltatick))

db.commit()
db.close()
print("Done")

