#!/bin/bash
#
#
COUNT=0
while [ 1 ]; do
  ping -c4 192.168.0.1 > /dev/null

  if [ $? != 0 ]
  then
    echo "`date` : No network connection, restarting wlan0"
    /sbin/ifdown 'wlan0'
    sleep 5
    /sbin/ifup --force 'wlan0'
    (( COUNT+=1 ))
    sleep 5
  else
    COUNT=0
    # network has been restored
    sleep 60
  fi

  if [ $COUNT -gt 10 ]; then
    # clearly having network issues, reboot the box
    sudo /sbin/shutdown -r now
  fi

  echo "[`date`] : count = $COUNT"
done
