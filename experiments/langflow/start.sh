#!/bin/bash
#
# Check if venv exists, create and set it up if it doesn't
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Creating one..."
    python3 -m venv venv
    echo "Installing dependencies from requirements.txt..."
    venv/bin/pip install --upgrade pip
    venv/bin/pip install -r requirements.txt
    echo "Virtual environment setup complete."
fi

source venv/bin/activate

# Get the network IP address
HOST_IP=$(../scripts/get-eth0-ip.sh)

# Start langflow bound to the network IP
langflow run --host $HOST_IP
