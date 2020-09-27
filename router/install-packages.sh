#!/bin/bash

set -euo pipefail

export DEBIAN_FRONTEND=noninteractive

apt-get -y update
apt-get -y upgrade

apt-get -y install sudo
apt-get -y install --no-install-recommends iptables

apt-get clean

rm -rf /var/lib/apt/lists/*

