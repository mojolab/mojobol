#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
sys.path.append("/opt/mojobol/libs")
from mojobol import *
from mojoasteriskplayer import *
if __name__=="__main__":
	env=read_agi_environment()
	ms=MojoBolResponder("/opt/mojobol/conf/sampleserver.conf")
	call=MojoBolCall(ms,env)
	call.responder.parse_workflow(call.callid)
