#!/bin/bash
update-alternatives --set iptables /usr/sbin/iptables-legacy

iptables -N echo_client_tcp_in
iptables -N echo_client_tcp_out
iptables -A echo_client_tcp_in
iptables -A echo_client_tcp_out

iptables -A OUTPUT --destination echo-client --protocol tcp -j echo_client_tcp_out
iptables -A INPUT --source echo-client --protocol tcp -j echo_client_tcp_in

