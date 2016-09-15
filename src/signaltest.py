import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BCM)
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)
oldinput = False

while (1):
    input = GPIO.input(23)
    if input != oldinput:
        print(input, time.time())
        oldinput = input
