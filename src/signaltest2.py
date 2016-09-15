import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BCM)
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)
oldinput = False
count=0
oldtime = 0



def my_callback2(level):
    print("Event: ",level,time.time())
    return

GPIO.add_event_detect(23, GPIO.BOTH, callback=my_callback2)

while True:
    input = GPIO.input(23)
    if input != oldinput:
        now = time.time()
        delta = now - oldtime
        if delta > 0.020:
            print(" ")
        print(count, input, now, delta*1000)
        oldtime = now
        oldinput = input
        count += 1
