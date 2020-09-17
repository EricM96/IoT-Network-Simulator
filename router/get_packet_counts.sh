#!/bin/bash
iptables -Z echo_client_tcp_in
iptables -Z echo_client_tcp_out
period=15
sleep "$period"

packets_in=$(iptables -nvL echo_client_tcp_in | awk '/all/{print $1}')
packets_out=$(iptables -nvL echo_client_tcp_out | awk '/all/{print $1}')

echo "During the last $period seconds we saw $packets_in incoming packets and $packets_out outgoing packets"

