#!/bin/bash
client_packets_in=$(iptables -nvL echo_client_tcp | awk 'FNR == 3 {print $1; exit}')
client_packets_out=$(iptables -nvL echo_client_tcp | awk 'FNR == 4 {print $1; exit}')
server_packets_in=$(iptables -nvL echo_server_tcp | awk 'FNR == 3 {print $1; exit}')
server_packets_out=$(iptables -nvL echo_server_tcp | awk 'FNR == 4 {print $1; exit}')

echo "From client: ($client_packets_in, $client_packets_out)"
echo "From server: ($server_packets_in, $server_packets_out)"

iptables -Z echo_client_tcp
iptables -Z echo_server_tcp
