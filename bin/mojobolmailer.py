import sys,os
sys.path.append("/opt/MojoMail/mojomail")
from mojomail import *
sys.path.append("/opt/mojobol/libs")
from mojobol import *

if __name__=="__main__":
	configfile="/opt/mojobol/conf/sampleserver.conf"
	ms=MojoBolResponder("/opt/mojobol/conf/sampleserver.conf")
	m=MojoMailer(configfile)
	maildir=os.path.join(ms.directory,ms.maildir)
	maildirlist=os.listdir(maildir)
	callzips=[]
	for call in maildirlist:
		if call.endswith(".zip"):
			callzips.append(os.path.join(ms.directory,ms.callsdir,call))
	for callzip in callzips:
		m.sendfile(callzip,"mojoarjun@gmail.com")
	
