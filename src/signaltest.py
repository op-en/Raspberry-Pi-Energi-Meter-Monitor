import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BCM)
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)
oldinput = False
count=0

while (1):
    input = GPIO.input(23)
    if input != oldinput:
        print(count, input, time.time())
        oldinput = input
        count++
