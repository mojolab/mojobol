#!/usr/bin/bash

echo "Welcome to the Mojobol Installer"
echo "This script will install Mojobol on your system."

echo "Attemting to install dependencies..."

# Try to install dependencies, if failed, exit

apt install -y python3 python3-pip python3-dev ipython3 zsh git vim curl sudo wget build-essential libssl-dev net-tools openssh-server lame asterisk gcc g++ bison zlib1g openssl python-setuptools espeak

# Check if current working directory is /opt/mojobol, if not, then create a soft link from /opt/mojobol to current working directory
