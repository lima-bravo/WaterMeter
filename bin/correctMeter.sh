#!/bin/bash
#
# create a correct value file to update the watermeter
#
read -p "Please input the correct value: [xxx.yyy] " value
# don't check input for now
echo "0 $value" > ../readWM/wmdata.correct
echo "Done"
