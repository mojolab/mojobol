#!/bin/bash

sudo cp -arv /etc/asterisk /etc/asterisk.orig
sudo cp /opt/mojobol/conf/extensions.conf /etc/asterisk/extensions.conf
sudo cp /opt/mojobol/conf/sip.conf /etc/asterisk/sip.conf
sudo /etc/init.d/asterisk restart

sudo ln -s /opt/mojobol/bin /usr/share/asterisk/agi-bin/mojobol
sudo chmod a+rwx -R /opt/mojobol

