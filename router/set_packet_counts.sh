#!/bin/bash
update-alternatives --set iptables /usr/sbin/iptables-legacy

iptables -t nat -A PREROUTING -p tcp --source echo-client --dport 8080 -j DNAT --to-destination echo-server:8080
iptables -t nat -A PREROUTING -p tcp --source echo-server --dport 8080 -j DNAT --to-destination echo-cleint:8080

iptables -N echo_client_tcp_in
iptables -N echo_client_tcp_out
iptables -A echo_client_tcp_in
iptables -A echo_client_tcp_out

iptables -A OUTPUT --destination echo-client --protocol tcp -j echo_client_tcp_out
iptables -A INPUT --source echo-client --protocol tcp -j echo_client_tcp_in

