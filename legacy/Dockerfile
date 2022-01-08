# syntax=docker/dockerfile:1
FROM ubuntu:latest
ENV DEBIAN_FRONTEND="noninteractive" TZ="Asia/Kolkata"
# Install Mojobol Dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    ipython3 \
    python3-dev \
    zsh \
    git \
    vim \
    curl \
    sudo \
    wget \
    build-essential \
    libssl-dev \
    net-tools \
    openssh-server \
    lame \ 
    asterisk \  
    gcc \
    g++ \
    bison \
    zlib1g \
    openssl \
    python-setuptools \
    espeak \
    --fix-missing
RUN pip3 install pyyaml 
RUN mkdir -p /opt/mojobol
RUN sudo ln -s /opt/mojobol/bin /usr/share/asterisk/agi-bin/mojobol
#RUN cd /opt/mojobol && sh setupasterisk.sh