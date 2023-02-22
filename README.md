# WaterMeter

This repository contains code created to read a magnetic sensor attached to a watermeter, using a Raspberry Pi

The data is collected in text files that are uploaded to a database at regular intervals.

The process to read the sensor is started using the script bin/readWM.sh
Uploading to the database is done through processData/uploadData.sh

