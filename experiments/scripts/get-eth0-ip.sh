#!/bin/bash

# Get the IP address of the eth0 interface
ifconfig eth0 | grep 'inet ' | awk '{print $2}'
