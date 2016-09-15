RPI-EEM
=======

Raspberry PI Energi Meter Monitor (RPI-EEM). This solution enables you to connect you Raspberry pi to the S0 port of a power meter or an light sensor on the blinking LED to monitor the power use at some site.

Defaults to pin 23 on the RPI. Pulse needs to drive the pin low in the current implementation. More features will be added.

Example 1: pin23 o --- >|--- o GND
                
         IR-fototransistor 5 mm (T13/4), SFH 300-3/4, Osram Semiconductors
         
Example 2:  
         
         pin23 o-----o +
                          | 
    RPI                   S0 pins power meter
                          |
         Gnd   o-----o - 
         
Function: The script is written to be able to handle a lot of noise and bounces that occurs during the pulses. A pulse can often be detected as 250 level changes on the Rasperry Pi port all occurring during the 1-80ms that the pulse occurs (the value depends on the brand of the meter). An algoritm stores the time of all level changed. When there has been at least a pulse length of silence it checks the length between the first and the last level change in the butter. If this is close to the expected pulse length it increased the energy counter and the buffer is cleared. It should work regardless of if the phototransistor generates an negative or positive pulse but has been tested with negative pulses only.

  Config:
  MQTT - mqtt server adress (default: localhost)
  MQTT_USER - Username for mqtt broaker (optional)
  MQTT_PASS - Password for mqtt broaker
  MQTT_PREFIX - The mqtt topic that data will be sent to (default: rpi-emm/meterevent and rpi-emm/ioevent)
  MQTT_CLIENT - Client id mqtt.
  EMM_GPIO_PIN - Raspberry pi pin to connect to meter. (default: 23)
  EMM_PULSE_FACTOR - Number of Wh each pulse represents (defaults to 10). Usually printed on power meter
  EMM_PULSE_LEN - The length of the pulse from the LED in seconds. If you don't specify this an the value will be automatically detected.
  EMM_MAX_PULSE_LEN_DEV - The maximun deviation that the pulse can have before being filtered away (in seconds, defaults to 0.005).
  EMM_DEBUG - For a lot of extra printouts in docker log CONTAINER-ID
