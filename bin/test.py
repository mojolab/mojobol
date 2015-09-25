#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
sys.path.append("/home/swara/mojobol/libs")
from mojobol import *

if __name__=="__main__":
	ms=MojoBolServer("/home/swara/mojobol/conf/testserver.conf")
	ms.parse_workflow()
	
