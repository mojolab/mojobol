#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
sys.path.append("/opt/mojobol/libs")
sys.path.append("/opt/LivingData/lib")
sys.path.append("/opt/MojoMail/mojomail")
from mojobol import *
from datetime import *
from mojoasteriskplayer import *
import yaml,datetime
from mojomail import *
from livdatcsvlib import *
if __name__=="__main__":
	calloutsheet=CSVFile()
	calloutsheet.importfile(sys.argv[1])
	ms=MojoBolResponder("/opt/mojobol/conf/sampleserver.conf")
	callsdir=os.path.join(ms.directory,ms.callsdir)
	reportsdir=os.path.join(ms.directory,ms.reportsdir)
	
	callsbefore=os.listdir(callsdir)
	print calloutsheet.colnames
	for row in calloutsheet.matrix:
		num=row['number']
		linefreedom=os.popen("asterisk -rx 'sip show channels' | grep 10.178.202.139").read().strip()
		linebusy=len(linefreedom)
		if linebusy:
			print "Line busy...sleeping for 10 seconds"
			time.sleep(10)
			continue
		#if num[:3]=="+91":
		#	prov=num[3:][:5]
		#else:
		#	prov=num[:5]
		#provname=os.popen("cat /opt/swara/conf/msc.csv | grep %s" %prov).read().strip().split(',')[1]
		if linebusy==0:
			#logging.info(prov+","+provname)
			#if provname=="BSNL":
			#logging.info("Creating callfile...")
			os.system("cp /opt/mojobol/conf/call.skel /opt/mojobol/conf/%s.call" %num)
			os.system("perl -p -i -e 's/NUMBER/%s/g' /opt/mojobol/conf/%s.call" %(num,num))
			os.system("mv /opt/mojobol/conf/%s.call /var/spool/asterisk/outgoing" %num)
			#logging.info("Removing number %s from queue..." %num)
			#os.system("rm /var/spool/asterisk/pending/%s" %num)
		time.sleep(60)
	calls=[]
	callsafter=os.listdir(callsdir)
	for call in callsafter:
		if call not in callsbefore:
			calls.append(call)
	print calls
	responses=[]
	for call in calls:
		print call
		userid=call.split("-"+ms.name+"-")[0]
		callstart=datetime.datetime.strptime(call.split("-"+ms.name+"-")[1],"%Y-%b-%d-%H-%M-%S")
		files=os.listdir(os.path.join(ms.directory,ms.callsdir,call))
		menuresponsefiles=[]
		for filename in files:
			if filename.startswith("menuresponsefile"):
				menuresponsefiles.append(filename)
		for filename in menuresponsefiles:
			print os.path.join(ms.directory,ms.callsdir,call,filename)
			f=open(os.path.join(ms.directory,ms.callsdir,call,filename),"r")
			menuresponses=yaml.safe_load(f)
			print menuresponses
			if menuresponses==None:
				continue
			else:
				for response in menuresponses:
					print response
					responserow={}
					responserow['id']=response['id']
					responserow['callid']=call
					responserow['user']=userid
					responserow['calldate']=callstart.strftime("%Y-%b-%d")
					responserow['calltime']=callstart.strftime("%H:%M:%S")
					responserow['menuname']=response['data']['name']
					for choice in response['data']['userchoices']:
						responserow['userchoice'+choice['attemptno']]=choice['keypress']
					responses.append(responserow)
	if responses==[]:
		print "No responses"
	else:
		report=CSVFile()
		report.colnames=responses[0].keys()
		report.matrix=responses
		for row in report.matrix:
			for key in row.keys():
				if key not in report.colnames:
					report.colnames.append(key)
		report.padrows()
		report.exportfile(os.path.join(reportsdir,"OutcallMenuResponseReport-"+datetime.datetime.now().strftime("%Y-%b-%d_%H_%M_%S")+".csv")) 

