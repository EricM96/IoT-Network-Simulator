#!/bin/bash
update-alternatives --set iptables /usr/sbin/iptables-legacy
echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf

iptables -N smart_home_controller
iptables -A smart_home_controller -s $SH_CONTROLLER
iptables -A smart_home_controller -d $SH_CONTROLLER

iptables -N weather_sensor
iptables -A weather_sensor -s $WEATHER_SENSOR
iptables -A weather_sensor -d $WEATHER_SENSOR

iptables -N thermostat
iptables -A thermostat -s $THERMOSTAT
iptables -A thermostat -d $THERMOSTAT

iptables -N garage_door
iptables -A garage_door -s $GARAGE_DOOR
iptables -A garage_door -d $GARAGE_DOOR

iptables -N refridgerator
iptables -A refridgerator -s $FRIDGE
iptables -A refridgerator -d $FRIDGE

iptables -N lights
iptables -A lights -s $LIGHTS
iptables -A lights -d $LIGHTS

iptables -N motion_sensor
iptables -A motion_sensor -s $MOTION_SENSOR
iptables -A motion_sensor -d $MOTION_SENSOR

iptables -N rate_limit
iptables -A rate_limit --match limit --limit 1000/sec --limit-burst 20 -j ACCEPT
iptables -A rate_limit -j DROP

iptables --table nat --append POSTROUTING --out-interface eth0 -j MASQUERADE

iptables -A FORWARD -s $SH_CONTROLLER -p tcp -j smart_home_controller
iptables -A FORWARD -d $SH_CONTROLLER -p tcp -j smart_home_controller

iptables -A FORWARD -s $WEATHER_SENSOR -p tcp -j weather_sensor
iptables -A FORWARD -d $WEATHER_SENSOR -p tcp -j weather_sensor

iptables -A FORWARD -s $THERMOSTAT -p tcp -j thermostat
iptables -A FORWARD -d $THERMOSTAT -p tcp -j thermostat

iptables -A FORWARD -s $GARAGE_DOOR -p tcp -j garage_door
iptables -A FORWARD -d $GARAGE_DOOR -p tcp -j garage_door

iptables -A FORWARD -s $FRIDGE -p tcp -j refridgerator
iptables -A FORWARD -d $FRIDGE -p tcp -j refridgerator

iptables -A FORWARD -s $LIGHTS -p tcp -j lights
iptables -A FORWARD -d $LIGHTS -p tcp -j lights

iptables -A FORWARD -s $MOTION_SENSOR -p tcp -j motion_sensor
iptables -A FORWARD -d $MOTION_SENSOR -p tcp -j motion_sensor

iptables -A FORWARD rate_limit
