#!/bin/bash
#
# This script should be run by the /etc/rc.local script at startup inside a GNU screen
#
#
BASEDIR=/home/pi/Programming/WaterMeter/readWM/
TEEFILE="readWM.log"
COMMAND="/usr/bin/python -u ./readWaterMeter.py"
RUNNING=-1

checkIfRunning() {
  RESULT=`ps -ef | grep "${COMMAND}" | grep -v grep`

  if [ "${RESULT}" == "" ]; then
    echo "Not running"
    RUNNING=0
  else
    echo "${COMMAND} running"
    RUNNING=1
  fi

}


loop() {
  while [ 1 ]; do
    if [ -e ${TEEFILE} ]; then
      DATESTRING=`date +'%s'`
      mv ${TEEFILE} ../data/${TEEFILE}.${DATESTRING}
    fi
    ${COMMAND} | tee ${TEEFILE}
    echo "Control-C now to exit loop"
    sleep 2
  done
}


#
# Main Body
#
cd ${BASEDIR}

checkIfRunning

if [ ${RUNNING} -eq 0 ]; then
  loop
fi
