#!/usr/bin/python

import sys,os
sys.path.append("/opt/mojomailman/mojomail")
from mojomail import *
sys.path.append("/opt/mojobol/lib")
from mojobol import *
mailer=MojoMailer("/opt/voh/mail.conf")
from datetime import *

mailer.logintoinmail()
resp=MojoBolResponder("/opt/voh/voh.conf")

callsdir=os.path.join(resp.directory,resp.callsdir)
calls=os.listdir(callsdir)
#print calls
messager=MojoMessager("/opt/voh/mail.conf")
for call in calls:
	
	subdict=messager.getsubdict()
	bodydict=messager.getbodydict()
	payload=""
	print call
	if resp.name in call:
		callvals=call.split(resp.name)
		userid=callvals[0].rstrip("-")
		subdict['USER']=userid
		ts=callvals[1].lstrip("-")
		timestamp=datetime.strptime(ts,resp.tsformat)
		print timestamp
		subdict['TIMESTAMP']=timestamp.strftime("%Y-%b-%d %H:%M:%S")
		subdict['MOJOMAIL']=resp.name
		subdict['TYPE']="CallRecord"
		if os.path.isdir(os.path.join(callsdir,call)):
			files=os.listdir(os.path.join(callsdir,call))
			for filename in files:
				if "callfile" in filename:
					payload=os.path.join(callsdir,call,filename)
					print "Payload",payload
					subdict['PAYLOAD']=filename
				if "log" in filename:
					logfile=os.listdir(os.path.join(callsdir,call,filename))
					print "Logfile",logfile[0]
					f=open(os.path.join(callsdir,call,filename,logfile[0]),"rb")
					bodydict['$CONTENT']+="\nCall Log\n"+f.read()
					f.close()	
				if "menuresponse" in filename:
					print "Menuresponses",filename
					f=open(os.path.join(callsdir,call,filename),"rb")
					bodydict['$CONTENT']+="\nMenu Responses\n"+f.read()
					f.close()
		if payload=="":
			subdict['META']="NOREC"
		else:
			subdict['META']="REC"
		msg=messager.composemessage(mailer.outusername,subdict,bodydict,payload)
		mailer.sendmsg(msg)
		f=open(os.path.join(callsdir,call,"mailed"),"w")
		f.write(datetime.now().strftime("%Y-%b-%d %H:%M:%S"))
		f.close()
		
