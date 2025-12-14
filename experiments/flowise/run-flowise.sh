#!/bin/bash

# Flowise Startup Script
# This script handles fresh git clones by checking and installing dependencies as needed

set -e  # Exit on error

echo "Flowise Startup Script"
echo "======================"
echo ""

# Check if this is a fresh clone (node_modules doesn't exist)
if [ ! -d "node_modules" ]; then
    echo "📦 Fresh clone detected - dependencies not found"
    echo "Installing Flowise and dependencies..."
    echo ""

    # Initialize npm if package.json doesn't exist
    if [ ! -f "package.json" ]; then
        echo "Initializing npm project..."
        npm init -y
        echo ""
    fi

    # Install Flowise
    echo "Installing Flowise (this may take a few minutes)..."
    npm install flowise
    echo ""
    echo "✅ Flowise installation complete!"
    echo ""
else
    echo "✅ Dependencies found - skipping installation"
    echo ""
fi

# Get the network IP address using the get-eth0-ip.sh script
echo "Getting network IP address..."
HOST_IP=$(../scripts/get-eth0-ip.sh)

if [ -z "$HOST_IP" ]; then
    echo "❌ Error: Could not determine network IP address"
    echo "Please check that ../scripts/get-eth0-ip.sh exists and is working"
    exit 1
fi

echo "Network IP: $HOST_IP"
echo ""

# Start Flowise bound to the network IP
echo "Starting Flowise..."
echo "Access the web UI at: http://$HOST_IP:3000"
echo ""
echo "Press Ctrl+C to stop Flowise"
echo ""

# Run Flowise with npx to ensure we use the locally installed version
HOST=$HOST_IP npx flowise start --PORT=3000
