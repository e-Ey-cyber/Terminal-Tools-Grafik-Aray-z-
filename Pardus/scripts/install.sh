#!/bin/bash

# System checks
check_system() {
    echo "Checking system requirements..."
    
    # Check Python version
    python3 --version || exit 1
    
    # Check disk space
    FREE_SPACE=$(df -k / | tail -1 | awk '{print $4}')
    if [ $FREE_SPACE -lt 1000000 ]; then
        echo "Not enough disk space"
        exit 1
    fi
    
    # Check memory
    FREE_MEM=$(free -m | grep Mem | awk '{print $4}')
    if [ $FREE_MEM -lt 500 ]; then
        echo "Not enough memory"
        exit 1
    fi
}

# Install dependencies
install_deps() {
    echo "Installing dependencies..."
    sudo apt update
    sudo apt install -y python3-gi python3-pip git
}

# Setup virtual environment
setup_venv() {
    echo "Setting up virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
}

# Main installation
main() {
    check_system
    install_deps
    setup_venv
    
    echo "Installing Tools Get..."
    sudo python3 setup.py install
}

main "$@"
