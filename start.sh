#!/bin/bash

# Function to get current IP address
get_ip_address() {
    if ifconfig | grep -q "inet "; then
        if ifconfig | grep -q "inet 127.0.0.1"; then
            # If localhost IP is found, get the first non-localhost IP
            ip=$(ifconfig | grep -Eo 'inet (addr:)?([0-9]*\.){3}[0-9]*' | grep -Eo '([0-9]*\.){3}[0-9]*' | grep -v '127.0.0.1' | head -1)
        else
            # Otherwise, get the first IP address
            ip=$(ifconfig | grep -Eo 'inet (addr:)?([0-9]*\.){3}[0-9]*' | grep -Eo '([0-9]*\.){3}[0-9]*' | head -1)
        fi
        echo "$ip"
    else
        echo "127.0.0.1"  # Default to localhost if no IP address is found
    fi
}

# Check if conda is installed and in PATH
if command -v conda &>/dev/null; then
    # Activate conda environment
    source "$(conda info --base)/etc/profile.d/conda.sh"
    conda activate network
    echo "Conda environment activated."
else
    echo "Error: Conda is not installed or not in PATH."
fi

# Get the current IP address
host_ip=$(get_ip_address)
echo "Using IP address: $host_ip"

# Run FastAPI application with uvicorn
uvicorn main:app --host "$host_ip" --port 2024 --reload
