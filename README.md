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
