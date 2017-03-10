#!/usr/bin/python

import sys
sys.path.append("/opt/mojomailman/mojomail")
from mojomail import *
sys.path.append("/opt/mojobol/lib")
mailer=MojoMailer("/opt/voh/mail.conf")

mailer.logintoinmail()
resp=MojoBolResponder("/opt/voh/
