#!/bin/bash
#
#


RSYNC=/usr/bin/rsync
LOCAL=/zfs/lodewijk/Programming/WaterMeter/
REMOTE=pi@waterpi.lan:/home/pi/Programming/WaterMeter/
FLAGS="--stats --progress"


get() {
	${RSYNC} -avuz ${REMOTE} ${LOCAL} ${FLAGS}
}

put() {
	${RSYNC} -avuz ${LOCAL} ${REMOTE} ${FLAGS}
}

dget() {
	${RSYNC} -avuz ${REMOTE} ${LOCAL} ${FLAGS} --delete
}

dput() {
	${RSYNC} -avuz ${LOCAL} ${REMOTE} ${FLAGS} --delete
}

case "$1" in
	'get')
		get
		;;
	'put')
		put
		;;
	'dget')
		dget
		;;
	'dput')
		dput
		;;
	'update')
		dget
		put
		;;
	*)
		echo "Usage: $0 {get|put|dget|dput|update}"
		exit 1
		;;
esac

exit 0
