#!/usr/bin/env python
#
# This script processes the Watermeter data and uploads
#
import os, sys
import psycopg2
from psycopg2 import sql

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

def createDBtables():
    datatables=['water']
    # now create the datatables
    for d in datatables:
        # drop table for now
        #query="DROP TABLE %s" % (d)
        #db.query(query)
        #
        query= sql.SQL("""
            CREATE TABLE IF NOT EXISTS {} (
                ts timestamp PRIMARY KEY UNIQUE, 
                val NUMERIC(10,4)
            )
        """).format(sql.Identifier(d))
        print(query)
        cur.execute(query)
        # now create the index -- not needed, primary key added
        # query="CREATE INDEX IF NOT EXISTS %s_idx_ts ON %s (ts)" % (d,d)
        # print query
        # db.query(query)


def insertValue(table,ts,val):
    query=sql.SQL("""
        INSERT INTO {} VALUES(to_timestamp(%s),%s)
        """).format(sql.Identifier(table))
    try:
        ts_rounded = round(ts, 3)
        cur.execute(query,(ts_rounded,val))
        # db.query(sql)
    except psycopg2.Error as e:
        print(query, (ts, val))
        # Handle specific PostgreSQL errors if needed
        # For now, print a generic error message
        print("Error inserting data into table:", table)
        print("Error:", e)


def processFile(filename):
    print(filename)
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
            print(f"Skipping {filename}")
        else:
            # check if the filesize is greater than 18 bytes, this includes the single value measures.
            if os.path.getsize(filename)>18:
                processFile(filename)
            else:
                print(f"File too small : skipping {filename}")
            # now rename the file so we don't process it again
            print(filename,newfile)
            os.rename(filename,newfile)



# db.close()
conn.commit()
cur.close()
conn.close()
#
print("Done")
