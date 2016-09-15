import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BCM)
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)

oldinput = False
count=0
oldtime = 0
edges = []

timeout = 10000

while True:
    res = GPIO.wait_for_edge(23,GPIO.BOTH,timeout=timeout)

    now = time.time()

    if res != None:
        edges.append(now)
        timeout = 20
        continue

    if len(edges) == 0:
        timeout = 10000
        continue

    #Calculate pulse length and increase count
    pulselenght = edges[-1] - edges[0]

    #Condition
    count += 1

    #Calculate period
    period = edges[-1] - oldtime
    oldtime = edges[-1]

    print("Count: %i \tPulse lenght: %.3f Bounces: %i \tPeriod: %.3f" % (count, pulselenght, len(edges),period) )

    #Clear databuffer.
    edges=[]




def my_callback2(level):

    global oldinput,count,oldtime

    input = GPIO.input(23)
    #if input != oldinput:
    now = time.time()
    delta = now - oldtime
    if delta > 0.020:
        print(" ")
    print(count, input, now, delta*1000)
    oldtime = now
    oldinput = input
    count += 1


    return

#GPIO.add_event_detect(23, GPIO.BOTH, callback=my_callback2)

while True:
    time.sleep(1000)

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
