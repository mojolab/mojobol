#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys
sys.path.append("/opt/mojobol/libs")
from mojoasteriskplayer import *
from datetime import *
from mojobol import *
if __name__ == "__main__":
    env = read_agi_environment()
    ms = MojoBolResponder("/opt/mojobol/conf/local/currentcallflow.conf")
    call = MojoBolCall(ms, env)
    p = call.responder.parse_workflow(call)
    call.endcall()
    call.compresscallfile()
    call.updatedf()
