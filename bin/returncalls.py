#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
sys.path.append("/opt/mojobol/libs")
from mojobol import *
from datetime import *
from mojoasteriskplayer import *
import yaml,datetime
if __name__=="__main__":
	while True:
		numlist = os.popen("ls /var/spool/asterisk/pending").read().strip().split('\n')
		linefreedom=os.popen("asterisk -rx 'sip show channels' | grep 10.178.202.139").read().strip()
		linebusy=len(linefreedom)
		if linebusy:
			logging.info("Line busy...sleeping for 10 seconds")
			time.sleep(10)
			continue
		logging.info("Line free...checking for pending calls...")
		if len(numlist[0])==0:
			logging.info("No pending calls...sleeping for 10 seconds")
			time.sleep(10)
			continue
		num=numlist[0]
		if num[:3]=="+91":
			prov=num[3:][:5]
		else:
			prov=num[:5]
		#provname=os.popen("cat /opt/swara/conf/msc.csv | grep %s" %prov).read().strip().split(',')[1]
		if linebusy==0:
			#logging.info(prov+","+provname)
			#if provname=="BSNL":
			logging.info("Creating callfile...")
			os.system("cp /opt/mojobol/conf/call.skel /opt/mojobol/conf/%s.call" %num)
			os.system("perl -p -i -e 's/NUMBER/%s/g' /opt/mojobol/conf/%s.call" %(num,num))
			os.system("mv /opt/mojobol/conf/%s.call /var/spool/asterisk/outgoing" %num)
			logging.info("Removing number %s from queue..." %num)
			os.system("rm /var/spool/asterisk/pending/%s" %num)
	
