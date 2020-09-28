#!/bin/bash
shc_packets_out=$(iptables -nvL smart_home_controller | awk 'FNR == 3 {print $1; exit}')
shc_packets_in=$(iptables -nvL smart_home_controller | awk 'FNR == 4 {print $1; exit}')

weather_packets_out=$(iptables -nvL weather_sensor | awk 'FNR == 3 {print $1; exit}')
weather_packets_in=$(iptables -nvL weather_sensor | awk 'FNR == 4 {print $1; exit}')

thermostat_packets_out=$(iptables -nvL thermostat | awk 'FNR == 3 {print $1; exit}')
thermostat_packets_in=$(iptables -nvL thermostat | awk 'FNR == 4 {print $1; exit}')

garage_door_packets_out=$(iptables -nvL garage_door | awk 'FNR == 3 {print $1; exit}')
garage_door_packets_in=$(iptables -nvL garage_door | awk 'FNR == 4 {print $1; exit}')

fridge_packets_out=$(iptables -nvL refridgerator | awk 'FNR == 3 {print $1; exit}')
fridge_packets_in=$(iptables -nvL refridgerator | awk 'FNR == 4 {print $1; exit}')

lights_packets_out=$(iptables -nvL lights | awk 'FNR == 3 {print $1; exit}')
lights_packets_in=$(iptables -nvL lights | awk 'FNR == 4 {print $1; exit}')

motion_sensor_packets_out=$(iptables -nvL motion_sensor | awk 'FNR == 3 {print $1; exit}')
motion_sensor_packets_in=$(iptables -nvL motion_sensor | awk 'FNR == 4 {print $1; exit}')

iptables -Z smart_home_controller
iptables -Z weather_sensor
iptables -Z thermostat
iptables -Z garage_door
iptables -Z refridgerator
iptables -Z lights
iptables -Z motion_sensor

echo "$shc_packets_in $shc_packets_out $weather_packets_in $weather_packets_out $thermostat_packets_in $thermostat_packets_out $garage_door_packets_in $garage_door_packets_out $fridge_packets_in $fridge_packets_out $lights_packets_in $lights_packets_out $motion_sensor_packets_in $motion_sensor_packets_out"

