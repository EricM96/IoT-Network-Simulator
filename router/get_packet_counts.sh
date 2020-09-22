#!/bin/bash
# client_packets_in=$(iptables -nvL echo_client_tcp | awk 'FNR == 3 {print $1; exit}')
# client_packets_out=$(iptables -nvL echo_client_tcp | awk 'FNR == 4 {print $1; exit}')
# server_packets_in=$(iptables -nvL echo_server_tcp | awk 'FNR == 3 {print $1; exit}')
# server_packets_out=$(iptables -nvL echo_server_tcp | awk 'FNR == 4 {print $1; exit}')

shc_packets_out=$(iptables -nvL smart_home_controller | awk 'FNR == 3 {print $1; exit}')
shc_packets_in=$(iptables -nvL smart_home_controller | awk 'FNR == 4 {print $1; exit}')

weather_packets_out=$(iptables -nvL weather_sensor | awk 'FNR == 3 {print $1; exit}')
weather_packets_in=$(iptables -nvL weather_sensor | awk 'FNR == 4 {print $1; exit}')

thermostat_packets_out=$(iptables -nvL thermostat | awk 'FNR == 3 {print $1; exit}')
thermostat_packets_in=$(iptables -nvL thermostat | awk 'FNR == 4 {print $1; exit}')

iptables -Z smart_home_controller
iptables -Z weather_sensor
iptables -Z thermostat

echo "$shc_packets_in $shc_packets_out $weather_packets_in $weather_packets_out $thermostat_packets_in $thermostat_packets_out"

