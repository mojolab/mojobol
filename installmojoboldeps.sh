#!/bin/bash

sudo apt-get install asterisk python-setuptools git espeak wget lame mysql-server gcc g++ php5-mysql php5 apache2 python python-mysqldb geany libsox-fmt-mp3 sox ipython zip
sudo easy_install pyyaml pytz xlrd

cd /opt
git clone https://github.com/mojolab/livingdata.git
git clone https://github.com/mojolab/mojomailman
