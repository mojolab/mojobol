
import os, sys

# check if asterisk is running
def check_asterisk():
    asterisk_running = os.system('ps -ef | grep asterisk | grep -v grep')
    if asterisk_running == 0:
        print('Asterisk is running')
        return True
    else:
        print('Asterisk is not running')
        return False    

#check if /usr/share/asterisk/agi-bin/mojobol contains mojobol-svr.py
def check_mojobol_svr():
    mojobol_svr = os.system('ls /usr/share/asterisk/agi-bin/mojobol | grep mojobol-svr.py')
    if mojobol_svr == 0:
        print('mojobol-svr.py is present in /usr/share/asterisk/agi-bin/mojobol')
        return True
    else:
        print('mojobol-svr.py is not present in /usr/share/asterisk/agi-bin/mojobol')
        return False

#check if /opt/mojobol/conf/local/currentcallflow.conf is a simlink 
def check_currentcallflow_conf():
    currentcallflow_conf = os.system('ls -l /opt/mojobol/conf/local/currentcallflow.conf | grep "->"')
    if currentcallflow_conf == 0:
        print('/opt/mojobol/conf/local/currentcallflow.conf is a simlink')
        return True
    else:
        print('/opt/mojobol/conf/local/currentcallflow.conf is not a simlink')
        return False