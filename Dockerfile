# This indicates what base image you are using and who maintains the Dockerfile.
FROM hypriot/rpi-python
MAINTAINER Anton Gustafsson (anton.gustafsson@tii.se)


# install RPI.GPIO python libs

RUN apt-get update \ 
     && apt-get install -y wget \
     && wget http://netix.dl.sourceforge.net/project/raspberry-gpio-python/raspbian-wheezy/python-rpi.gpio_0.6.2~wheezy-1_armhf.deb \
     && dpkg -i python-rpi.gpio_0.6.2~wheezy-1_armhf.deb \
     && rm python-rpi.gpio_0.6.2~wheezy-1_armhf.deb \
     && apt-get autoremove -y wget

#RUN apt-get update \
#    &&sudo apt-get install python-dev python-rpi.gpio

#RUN apt-get update \
#    && apt-get install -y --no-install-recommends gcc \
#    && rm -rf /var/lib/apt/lists/* \
#    && pip install cryptography \
#    && apt-get purge -y --auto-remove gcc

# Upgrade pip
RUN pip install --upgrade pip

# We add requirements first so that we don't have to rebuild everytime we change the source
ADD requirements.txt /opt
RUN pip install -r /opt/requirements.txt

# Add the source
ADD src /opt/eem

# We add the default config parameters to display the available options
#ENV MQTT localhost
#ENV MQTT_USER user
#ENV MQTT_PASS password
#ENV MQTT_PREFIX MainMeter
#ENV MQTT_CLIENT EnergyLogger
#ENV EEM_GPIO_PIN 23


# Go go go!
CMD ["python","-u","/opt/eem/EnergyMeterPulsReaderMQTT.py"]
