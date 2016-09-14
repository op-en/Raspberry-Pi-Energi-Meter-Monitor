# This indicates what base image you are using and who maintains the Dockerfile.
FROM hypriot/rpi-python
MAINTAINER Leo Fidjeland (hello@leo.wtf)

#RUN apt-get install python-rpi.gpio

# Upgrade pip
RUN pip install --upgrade pip

# We add requirements first so that we don't have to rebuild everytime we change the source
ADD requirements.txt /opt
RUN pip install -r /opt/requirements.txt

# Add the source
ADD src /opt/eem

# We add the default config parameters to display the available options
ENV MQTT localhost
ENV MQTT_USER user
ENV MQTT_PASS password
ENV MQTT_PREFIX MainMeter
ENV MQTT_CLIENT EnergyLogger
ENV EEM_GPIO_PIN 23


# Go go go!
CMD ["python","-u","/opt/eem/EnergyMeterPulsReaderMQTT.py"]
