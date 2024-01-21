#!/usr/bin/env python
#
# This script processes the Watermeter data and uploads
#
import os, sys
from pg import DB

try:
    db = DB(dbname='sensordata', host='imac.lan', port=5432, user='sensor_main', passwd='SuperSensor')
except Exception:
    print "Error accessing database"
    sys.exit()

def createDBtables():
    datatables=['water']
    # now create the datatables
    for d in datatables:
        # drop table for now
        #query="DROP TABLE %s" % (d)
        #db.query(query)
        #
        query="CREATE TABLE IF NOT EXISTS "+d
        query+=" (ts timestamp PRIMARY KEY UNIQUE, val NUMERIC(10,4))"
        print query
        db.query(query)
        # now create the index -- not needed, primary key added
        # query="CREATE INDEX IF NOT EXISTS %s_idx_ts ON %s (ts)" % (d,d)
        # print query
        # db.query(query)


def insertValue(table,ts,val):
    sql="INSERT INTO %s VALUES(to_timestamp(%.3f),%s)" % (table,ts,val)
    try:
        db.query(sql)
        #print sql
    except Exception:
        # print "Constraints violation on "+sql
        pass


def processFile(filename):
    print filename
    f=open(filename,'r')
    line=f.readline()
    # now enter the loop
    while line:
        fields=line.strip().split(" ")
        # parse the values
	# print "%s|%s\n" % (fields[0], fields[1])
        insertValue('water',float(fields[0]),fields[1])
        #
        line=f.readline()
    f.close()


## now let's start processing the directory and process all the rec files.
basedir="/home/pi/Programming/WaterMeter/data/"
#createDBtables()
for f in sorted(os.listdir(basedir)):
    if f.startswith("wmdata."):
        # processRecFile(basedir+f)
        filename=os.path.join(basedir,f)
        newfile=filename.replace("wmdata","wmproc")
        # check if the newfile exists, if so, skip
        if os.path.isfile(newfile):
            print("Skipping "+filename)
        else:
            # check if the filesize is greater than 18 bytes, this includes the single value measures.
            if os.path.getsize(filename)>18:
                processFile(filename)
            else:
                print("File too small : skipping "+filename)

            # now rename the file so we don't process it again
            print( filename,newfile)
            os.rename(filename,newfile)



db.close()
print("Done")
