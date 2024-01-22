#!/usr/bin/env python3
#
# This script processes the Watermeter data and uploads
#
import os, sys
import psycopg2
from psycopg2 import sql

# Global variables
Add=0
Tot=0
#

try:
    # db = DB(dbname='sensordata', host='imac.lan', port=5432, user='sensor_main', passwd='SuperSensor')
    # Connect to the PostgreSQL database
    conn = psycopg2.connect(
        host="imac.lan",
        port="5432",
        dbname="sensordata",
        user="sensor_main",
        password="SuperSensor"
    )
    cur = conn.cursor()
except psycopg2.Error as e:
    # Handle specific PostgreSQL errors if needed
    # For now, print a generic error message
    print("Error connecting to the database:", e)
    sys.exit()



def insertValue(table,ts,val):
    global Add, Tot
    query=sql.SQL("""
        INSERT INTO {} VALUES(to_timestamp(%s),%s)
        ON CONFLICT (ts) DO NOTHING
        """).format(sql.Identifier(table))
    try:
        Tot+=1
        ts_rounded = round(ts, 3)
        cur.execute(query,(ts_rounded,val))
        if cur.rowcount > 0:  # something was inserted into the database
            Add += cur.rowcount
    except psycopg2.Error as e:
        print(query, (ts, val))
        print("Error:", e)


def processFile(filename):
    # print(filename)
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
basedir="/zfs/lodewijk/Programming/HomeAutomation/WaterMeter/data/"
fileset = os.listdir(basedir)
fileset.sort()
for f in fileset:
    if f.startswith("wm"):
        # processRecFile(basedir+f)
        filename=os.path.join(basedir,f)
        Add = 0
        Tot = 0
        # check if the newfile exists, if so, skip
        processFile(filename)
        if Add > 0:
            print(f"{filename} - Total {Tot} , Added {Add}")
            # conn.commit()  # commit the transaction
            cur.connection.commit()



# db.close()
conn.commit()
cur.close()
conn.close()
#
print("Done")
