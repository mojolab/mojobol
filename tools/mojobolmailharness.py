#!/usr/bin/python

import sys
sys.path.append("/opt/mojomailman/mojomail")
from mojomail import *

m=MojoMailer("/opt/voh/mail.conf")
m.logintoinmail()
