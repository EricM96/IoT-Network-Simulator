#!/bin/bash
update-alternatives --set iptables /usr/sbin/iptables-legacy
echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf

iptables -N echo_client_tcp
iptables -A echo_client_tcp -s $ECHO_CLIENT
iptables -A echo_client_tcp -d $ECHO_CLIENT

iptables -N echo_server_tcp
iptables -A echo_server_tcp -s $ECHO_SERVER
iptables -A echo_server_tcp -d $ECHO_SERVER

iptables --table nat --append POSTROUTING --out-interface eth0 -j MASQUERADE
iptables -A FORWARD -s $ECHO_CLIENT -j echo_client_tcp
iptables -A FORWARD -d $ECHO_CLIENT -j echo_client_tcp

iptables -A FORWARD -s $ECHO_SERVER -j echo_server_tcp
iptables -A FORWARD -d $ECHO_SERVER -j echo_server_tcp
