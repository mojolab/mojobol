#!/bin/bash

sudo cp -arv /etx/asterisk /etc/asterisk.orig
sudo cp /opt/mojobol/conf/extensions.conf /etc/asterisk/extensions.conf
sudo cp /opt/mojobol/conf/sip.conf /etc/asterisk/sip.conf
sudo /etc/init.d/asterisk restart
