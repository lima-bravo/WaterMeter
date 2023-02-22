#!/bin/bash
#
# This script executes the upload to the progress database on imac.
#
# It runs in an endless loop, until killed.
#
#
SLEEP=3600 # check every hour if there is any work to do
#SLEEP=10
#
DATADIR=/home/pi/Programming/WaterMeter/data
#

if [ $(pidof -x uploadData.sh| wc -w) -gt 2 ]; then 
    echo "More than 1"
    exit 1
fi

while [ 1 ]; do
        # check if there is a wmdata file in the DATADIR
        LSCNT=`ls ${DATADIR}/*| grep wmdata | wc -l`
        printf "\r%s" "`date` : WMdata file count : ${LSCNT} "
        if [ ${LSCNT} -gt 0 ]; then
		echo ""
                sleep 5 # to prevent race condition of processing a file still being moved
                python /home/pi/Programming/WaterMeter/processData/processWMdata.py
                if [ $? -eq 0 ]; then
                        echo success
                fi
        fi
	# echo "[`date`] sleeping.."
        sleep ${SLEEP}
done

