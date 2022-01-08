
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

#if /opt/mojobol/conf/local/currentcallflow.conf exists 
# check if /opt/mojobol/conf/local/currentcallflow.conf is a simlink 
# else return False
def check_currentcallflow_conf():
    currentcallflow_conf = os.path.exists('/opt/mojobol/conf/local/currentcallflow.conf')
    if currentcallflow_conf:
        currentcallflow_conf_link = os.path.islink('/opt/mojobol/conf/local/currentcallflow.conf')
        if currentcallflow_conf_link:
            print('/opt/mojobol/conf/local/currentcallflow.conf is a simlink')
            return True
        else:
            print('/opt/mojobol/conf/local/currentcallflow.conf is not a simlink')
            return False
    else:
        print('/opt/mojobol/conf/local/currentcallflow.conf does not exist')
        return False


if __name__=="__main__":
    if check_asterisk() and check_mojobol_svr() and check_currentcallflow_conf():
        print('All sanity checks passed')
    else:
        print('Some sanity checks failed')
