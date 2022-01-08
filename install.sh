#!/usr/bin/bash

echo "Welcome to the Mojobol Installer"
echo "This script will install Mojobol on your system."

echo "Attemting to install dependencies..."

# Try to install dependencies, if failed, exit

apt install -y python3 python3-pip python3-dev ipython3 zsh git vim curl sudo wget build-essential libssl-dev net-tools openssh-server lame asterisk gcc g++ bison zlib1g openssl python-setuptools espeak

# If /opt/mojobol already exists, inform user else enter /opt and clone https://github.com/mojolab/mojobol
if [ -d /opt/mojobol ]; then
    echo "Mojobol is already installed. Exiting..."
    exit
else
    echo "Installing Mojobol..."
    cd /opt
    git clone https://github.com/mojolab/mojobol
fi

#If /opt/mojobol/conf/local does not exist create it
if [ ! -d /opt/mojobol/conf/local ]; then
    echo "Creating local config directory..."
    mkdir /opt/mojobol/conf/local
fi

# Run /opt/mojobol/setupasterisk.sh
cd /opt/mojobol
./setupasterisk.sh
python3 sanity-check-mojobol.py





