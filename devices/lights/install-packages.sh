#!/bin/bash

set -euo pipefail

export DEBIAN_FRONTEND=noninteractive

apt-get update
apt-get upgrade

apt-get install -y t50

apt-get clean

rm -rf /var/lib/apt/lists/*

