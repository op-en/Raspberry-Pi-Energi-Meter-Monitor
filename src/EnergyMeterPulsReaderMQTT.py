#!/usr/bin/python
# Energymeter puls reader to MQTT for Raspberry PI
# by Anton Gustafsson
# 2013-09-20

import RPi.GPIO as GPIO
from time import gmtime, strftime, time, localtime, mktime, strptime
import json
import urllib2
import base64
from math import fabs, isnan
import paho.mqtt.client as mqtt
import os
import json


config = {
    'mqtt_host': os.environ.get('MQTT','localhost'),
    'mqtt_user': os.environ.get('MQTT_USER',None),
    'mqtt_pass': os.environ.get('MQTT_PASS',None),
    'mqtt_prefix': os.environ.get('MQTT_PREFIX','rpi-emm'),
    'mqtt_client': os.environ.get('MQTT_CLIENT','EnergyLogger'),
    'pin': int(os.environ.get('EMM_GPIO_PIN',23)),
    'factor': float(os.environ.get('EMM_PULSE_FACTOR',10)),
    'pulselenght': float(os.environ.get('EMM_PULSE_LEN','NaN')),
    'pulse_lenght_max_dev': float(os.environ.get('EMM_MAX_PULSE_LEN_DEV',0.005)),
    'debug': float(os.environ.get('EMM_DEBUG',False))

}


#Functions
#Time
def CurrentTime():
    return strftime("%Y-%m-%d %H:%M:%S", localtime())


#Class
class EnergyLogger(mqtt.Client):
    def __init__(self,pin=config['pin'],user = config['mqtt_user'], password=config['mqtt_pass'],server = config['mqtt_host'], prefix = config['mqtt_prefix'],client = config['mqtt_client'],
                        factor = config['factor'],debug = config['debug'],pulselenght = config['pulselenght'],
                        pulse_lenght_max_dev = config['pulse_lenght_max_dev']):

        self.Factor = factor # kWh per pulse
        self.Threshhold = 10.0 # Dont update if power didnt change more than this amount.
        self.SentThreshhold = None

        self.LastTime = 0.0
        self.EnergyCounter = 0
        self.PulseCounter = 0
        self.LastPeriod = 0.0
        self.Falling = 0.0
        self.LastPower = 0.0

        self.error_threshhold = 100000

        if isnan(pulselenght):
            self.pulse_lenght = 0.080
            self.auto_pulselenght = True
        else:
            self.pulse_lenght = pulselenght
            self.auto_pulselenght = False

        self.pulse_lenght_max_dev = pulse_lenght_max_dev
        self.pulse_lenght_buf = []


        self.pin = pin

        self.debug = debug

        self.prefix = prefix



        #Init and connect to MQTT server
        mqtt.Client.__init__(self,client)
        self.will_set( topic = "system/" + self.prefix, payload="Offline", qos=1, retain=True)

        if user != None:
            self.username_pw_set(user,password)

        self.on_connect = self.mqtt_on_connect
        self.on_message = self.mqtt_on_message

        self.connect(server,keepalive=10)
        self.publish(topic = "system/"+ self.prefix, payload="Online", qos=1, retain=True)

        GPIO.setmode(GPIO.BCM)

        # GPIO self.pin set up as inputs, pulled up to avoid false detection.
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        # when a falling or rising edge is detected on port self.pin, call callback2
        #GPIO.add_event_detect(self.pin, GPIO.BOTH, callback=self.my_callback2, bouncetime=0)

        self.loop_start()
        return

    def StartDetection(self):
        print(" ")
        print("Starting pulse detection")
        print("________________________________")
        print("Time: %.2f" % time())
        #print("Factor: %f" % self.Factor)

        print("CONFIG:")

        print(json.dumps(x, indent=2))
        print("_________________________________")

        oldtime = 0
        edges = []

        timeout = 10000

        while True:
            res = GPIO.wait_for_edge(23,GPIO.BOTH,timeout=timeout)

            now = time()

            if res != None:
                edges.append(now)
                timeout = int (self.pulse_lenght * 1000)
                if timeout < 20:
                    timeout = 20
                continue

            if len(edges) == 0:
                timeout = 10000
                continue

            #TimeStamp
            timestamp = edges[0]

            #Calculate pulse length and increase count
            pulselenght = edges[-1] - edges[0]

            #Calculate period
            period = edges[-1] - oldtime
            oldtime = edges[-1]

            #Bounces
            bounces = len(edges)

            #Clear databuffer.
            edges=[]

            self.PulseCounter += 1

            if self.auto_pulselenght:
                self.pulse_lenght_buf.append(pulselenght)
                self.pulse_lenght_buf=self.pulse_lenght_buf[-100:]
                self.pulse_lenght = sum(self.pulse_lenght_buf)/len(self.pulse_lenght_buf)
                #print self.pulse_lenght, self.pulse_lenght_buf

            #Check pulse lenght.
            PulseDeviation = fabs(pulselenght - self.pulse_lenght)

            self.SendIOEvent(str("%.3f" % timestamp),"%.2f" % period,str(self.PulseCounter),"%.3f" % pulselenght,str(bounces),"%.5f" % PulseDeviation)

            if self.debug:
                print("%.2f Pin: %i \tCount: %i \tPulse lenght: %.3f Bounces: %i \tPeriod: %.3f \tPulseDeviation: %.5f" % (timestamp, self.pin,self.PulseCounter, pulselenght, bounces ,period,PulseDeviation))

            self.CountEnergy(timestamp,pulselenght,bounces,PulseDeviation)

    def CountEnergy(self,TimeStamp,PulseLenght,Bounces,PulseDeviation):

        #Ignore first pulse since period cant be calculated with just one.
        if self.LastTime == 0:
            self.LastTime = TimeStamp
            return

        #Proceed only id pulse legnth is correct.
        if PulseDeviation >  self.pulse_lenght_max_dev:
            print("%.3f \tINFO: Skipping pulse due to pulse length deviation. Adjust EMM_MAX_PULSE_LEN_DEV if nesseary." % TimeStamp)
            print("\tPulse length: %.3f \tTarget pulse lenght: %.3f\t Deviation: %.5f Max deviation threshhold: %.5f" %(PulseLenght,self.pulse_lenght,PulseDeviation,pulse_lenght_max_dev))
            return

        #Increase counter and calculate period.
        self.EnergyCounter += 1
        Period = TimeStamp - self.LastTime

        #self.LastPeriod = Period

        #Calculate power and energy values.
        Energy = self.EnergyCounter * self.Factor
        Power = self.Factor / (Period / 3600.0) # The energy divided on the time in hours.
        Delta = fabs(Power - self.LastPower)

        #Filter exream values
        if Delta > self.error_threshhold:
            print "%.3f INFO: Skipping pulse due to that the resulting power value exceeds the error threshhold of %.0f W " % (TimeStamp, self.error_threshhold)
            print " "
            return

        #Store for future reference
        self.LastTime = TimeStamp
        self.LastPower = Power
        self.LastEnergy = Energy
        self.LastDelta = Delta

        if self.debug:
            print "EnergyCounter %i Period is: %.2f s \tPower is: %.2f W\tEnergy: %.2f kWh\tChange: %.2f " % (self.EnergyCounter,Period,Power,Energy,Delta)

        if Delta > self.Threshhold:
            self.SendMeterEvent(str(TimeStamp),str(Power),str(Energy),str(self.Threshhold))

        return

    #Posting data to couchDB
    def Update(self,sub_topic,value,timestamp = time()):

        topic = self.prefix+"/"+sub_topic

        msg = json.dumps({"time":timestamp,"value":value})

        #print "New event: " + topic
        self.publish(topic,msg,1)

        return

    def SendMeterEvent(self,timestamp,power,energy,threshhold):
        #self.Update("power",power,timestamp)
        #self.Update("counter",counter,timestamp)

        topic = self.prefix+"/meterevent"

        msg = json.dumps({"time":timestamp,"power":power,"energy":energy})

        self.publish(topic,msg,1)
        #if self.SentThreshhold != self.Threshhold:
        #    self.Update("threshhold",threshhold,timestamp)
        #    self.SentThreshhold = self.Threshhold

        return

    def SendIOEvent(self,timestamp,Period,Counter,PulseLenght,Bounces,PulseDeviation):
        topic = self.prefix+"/ioevent"
        msg = json.dumps({"time":timestamp,"counter":Counter,"period":Period,"pulselenght":PulseLenght,"bounces":Bounces,"pulsedeviation":PulseDeviation})
        self.publish(topic,msg,1)
        return

    def mqtt_on_connect(self, client, userdata, flags, rc):
        print "INFO: MQTT connected!"
        self.subscribe(self.prefix + "/#", 0)

    def mqtt_on_message(self, client, userdata, msg):
        if self.debug:
            print("INFO: RECIEVED MQTT MESSAGE: "+msg.topic + " " + str(msg.payload))

        return


if __name__ == "__main__":


    #raw_input("Press Enter when ready\n>")

    Logger = EnergyLogger()

    Logger.StartDetection()

    # try:
    #     while(1):
    #         raw_input("Press Enter to simulate pulse\n>")
    #         Logger.my_callback(1)
    #
    #         print "Waiting for rising edge on port 24"
    #         GPIO.wait_for_edge(24, GPIO.RISING)
    #         print "Rising edge detected on port 24. Here endeth the third lesson."
    #
    # except KeyboardInterrupt:
    #         GPIO.cleanup()       # clean up GPIO on CTRL+C exit
    GPIO.cleanup()           # clean up GPIO on normal exit
