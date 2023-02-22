import RPi.GPIO as GPIO
from time import sleep

GPIO.setmode(GPIO.BCM)

try:
    while 1:
        count = 0
        GPIO.setup(21, GPIO.OUT)
        GPIO.output(21, GPIO.LOW)
        sleep(0.05)

        GPIO.setup(21, GPIO.IN)
        while(GPIO.input(21) == GPIO.LOW):
            count += 1
        print(count)
        sleep(1)
        
except KeyboardInterrupt:
    print ("\nCtrl-C pressed.  Program exiting...")
finally:                   
    GPIO.cleanup() # run on exit
