#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
sys.path.append("/opt/mojobol/libs")
from mojobol import *
from datetime import *
from mojoasteriskplayer import *
import yaml,datetime
if __name__=="__main__":
	ms=MojoBolResponder("/opt/mojobol/conf/sampleserver.conf")
	reportsdir=os.path.join(ms.directory,ms.reportsdir)
	print reportsdir
	callsdir=os.path.join(ms.directory,ms.callsdir)
	calls=os.listdir(callsdir)
	responses=[]
	for call in calls:
		userid=call.split("-"+ms.name+"-")[0]
		callstart=datetime.datetime.strptime(call.split("-"+ms.name+"-")[1],"%Y-%b-%d-%H-%M-%S")
		files=os.listdir(os.path.join(ms.directory,ms.callsdir,call))
		menuresponsefiles=[]
		for filename in files:
			if filename.startswith("menuresponsefile"):
				menuresponsefiles.append(filename)
		for filename in menuresponsefiles:
			f=open(os.path.join(ms.directory,ms.callsdir,call,filename),"r")
			menuresponses=yaml.safe_load(f)
			print menuresponses
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
	
	for key in responses[0].keys():
		print key+",",
	print "\n"
	for row in responses:
		for key in row.keys():
			print row[key]+",",
		print "\n"
		
		
