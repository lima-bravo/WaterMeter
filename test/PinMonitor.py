import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)  # use the GPIO numbers

pin=23 # This is pin 16
GPIO.setup(pin,GPIO.IN)

#initialise a previous input variable to 0 (assume button not pressed last)
prev_input = 1

try:
    while True:
        #take a reading
        input = GPIO.input(pin)
        time.sleep(0.05) # limit the sampling rate
        #print "Value %d" % input
        #if the last reading was different, print
        if (prev_input !=input):
            print("Button pressed %d" % input)
            #update previous input
            prev_input = input
            #slight pause to debounce
            #time.sleep(0.05)

except KeyboardInterrupt:
    print "Control-C detected"

except:
    print "Other error detected"

finally:
    GPIO.cleanup()
