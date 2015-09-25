#interface to asterisk. Safe for import * ing.
import time
import re
import sys
import os
import pprint
import uuid
def debugPrint(msg):
    sys.stderr.write(msg+'\n')
    sys.stderr.flush()
    with open("/home/swara/mojobol/log/mojobol.log","a") as f:
	f.write(msg+"\n")
    f.close()

class KeyPressException(Exception):
    def __init__(self, key):
        self.key = key
    def __str__(self):
        return repr(self.key) + ' was pressed.'
        
def newKeyDict():
    return {'0':RaiseZero,'#':Nop}
def RaiseZero():
    raise KeyPressException('0')
def RaiseKey(key):
    raise KeyPressException(key)
def Nop():
    pass
def removeTempFile(fname):
    os.remove(fname)
def readline():
	result = sys.stdin.readline().strip()
	debugPrint('read line: ' + result)
	return result
def checkresult (params):
	"""
	Reads the asterisk response and returns the parse result
	"""
	params = params.rstrip()
	if re.search('^200',params):
		result = re.search('result=([\d*#]+)',params)
		if (not result):
			sys.stderr.write("FAIL ('%s')\n" % params)
			sys.stderr.flush()
			return -1
		else:
			result = result.group(1)
			#debug("Result:%s Params:%s" % (result, params))
			sys.stderr.write("PASS (%s)\n" % result)
			sys.stderr.flush()
			return result
	else:
		sys.stderr.write("FAIL (unexpected result '%s')\n" % params)
		sys.stderr.flush()
		return -2
def hangup ():
	debugPrint("HANGUP\n")
	sys.stdout.write("HANGUP\n")
	sys.stdout.flush()

def play (fname, keyDict = newKeyDict()):
	"""
	Plays the file "fname". keyDict is a dictionary mapping characters from
	the number pad to functions of zero arguments which are called in the
	case of a keypress, or tuples of functions and their arguments
	"""
	escapeDigits = ''
	for key in keyDict:
		escapeDigits += key
	done = 0
	while done == 0:
		mytime = time.time()
		debugPrint("STREAM FILE %s \"%s\"\n" % (str(fname),escapeDigits))
		sys.stdout.write("STREAM FILE %s \"%s\"\n" % (str(fname),escapeDigits))
		sys.stdout.flush()
		result = readline()
		debugPrint(result)
		result = checkresult(result)
		if time.time() - mytime > 0.1:
			done = 1
	if (not isinstance(result,str)) or result == '-1':
		return -1
	elif result == '0':
		return 0
	else:
		#if the user pressed a key...
		c = chr(int(result))
		debugPrint("USER JUST PRESSED:" + c)
		if isinstance(keyDict[c],tuple):
			keyDict[c][0](*keyDict[c][1])
		else:
			keyDict[c]()
		return c

def record (fname, stopDigits, timeout, silenceTimeout=-1):
	"""
	Records a file to the local disk.
	fname is the name of the file to record (minus .wav)
	stopDigits are keys that stop recording (not returned)
	timeout is the total time allowed for the recording in seconds
	silenceTimout is the silence time before the recording ends
	automatically in seconds
	"""

	debugPrint("STARTING RECORD FILE")
	ms_timeout = int(timeout*1000)
	seconds_silenceTimeout = -1 #int(silenceTimeout)
	cmdString = "RECORD FILE %s wav %s %s BEEP s=%d\n" % (fname, \
														  stopDigits, \
														  ms_timeout, \
														  seconds_silenceTimeout)
	debugPrint(cmdString)
	sys.stdout.write(cmdString)
	sys.stdout.flush()
	result = readline()
	result = checkresult(result)
	return result

def capture (prompt, timelimit, digcount, keyDict=newKeyDict()):

	"""
	Plays a file to the user and waits for up to digcount keypresses during
	seconds.
	"""
	timelimit = int(timelimit*1000)
	sys.stderr.write("GET DATA %s %d %d\n" % (prompt, timelimit, digcount))
	sys.stderr.flush()
	sys.stdout.write("GET DATA %s %d %d\n" % (prompt, timelimit, digcount))
	sys.stdout.flush()
	#sys.stderr.write("GET DATA BEEP %d %d\n" % (timelimit, digcount))
	#sys.stderr.flush()
	#sys.stdout.write("GET DATA BEEP %d %d\n" % (timelimit, digcount))
	#sys.stdout.flush()
	
	result = readline()
	result = checkresult(result)
	sys.stderr.write("digits are %s\n" % result)
	sys.stderr.flush()
	if isinstance(result,str):
		if result in keyDict:
			if isinstance(keyDict[result],tuple):
				keyDict[result][0](*keyDict[result][1])
			else:
				keyDict[result]()
		return result
	else:
		return ''

def sayNumber(number):
	"""
	Says number aloud to user.
	"""
	sys.stderr.write("SAY NUMBER %s \"\"\n" % str(number)) 
	sys.stderr.flush()
	sys.stdout.write("SAY NUMBER %s \"\"\n" % str(number)) 
	sys.stdout.flush() 
	result = readline() 

class MojoAsteriskPlayer:
	def __init__(self,language,workflow,serverdir):
		self.workflow=workflow
		self.language=language
		self.serverdir=serverdir
		

	def getAudioFile(self,resource):
		localizedresource=resource.getLocalizedResources(language=self.language)[0]
		if localizedresource.rtype=='TextLocalizedResource':
			tempfilename="/tmp/"+localizedresource.guid
			os.system("espeak -v hindi -s 100 -w %s.wav '%s'" %(tempfilename,localizedresource.resourcemap['text']))
			os.system("sox %s.wav -r8000 %s.wav" %(tempfilename,tempfilename+"gsm"))
			os.system("chmod a+rwx %s*" %(tempfilename+"gsm"))
			#tempfilename="/opt/swara/sounds/7316"
			return tempfilename+"gsm"
	
	def executeStep(self,step):
		stepresources=self.workflow.getStepResources(step)
		if step['type']=='play':
			debugPrint("Playing "+step['resource']['guid'])
			resource_guid=step['resource']['guid']
			resource=self.workflow.getStepResourceByGuid(stepresources,resource_guid)
			audiofile=self.getAudioFile(resource)
			play(audiofile)
			return step['next']
		if step['type']=='capture':
			instructions_resource_guid=step['instructions_resource']['guid']
			instructions_resource=self.workflow.getStepResourceByGuid(stepresources,instructions_resource_guid)
			invalid_resource_guid=step['invalid_resource']['guid']
			invalid_resource=self.workflow.getStepResourceByGuid(stepresources,invalid_resource_guid)
			timeout=step['timeout']
			mindigits=step['min_input_length']
			maxdigits=step['max_input_length']
			print "Capturing"
			loopcount=step['number_of_attempts']
			for i in range(0,loopcount):
				audiofile=self.getAudioFile(instructions_resource)
				result=capture(audiofile,int(timeout)*1000,int(maxdigits))
				debugPrint("Captured keys ="+result)
				if result==step['valid_values']:
					debugPrint("Valid Capture")
					return step['next']
				else:
					audiofile=self.getAudioFile(invalid_resource)
					play(audiofile)  
					debugPrint("Invalid Capture")
			print "Hanging Up"
			return None
		if step['type']=='menu':
			print "Playing explanation resource", step['explanation_resource']
			print "Playing options resource", step['options_resource']
			options_resource_guid=step['options_resource']['guid']
			options_resource=self.workflow.getStepResourceByGuid(stepresources,options_resource_guid)
			explanation_resource_guid=step['explanation_resource']['guid']
			explanation_resource=self.workflow.getStepResourceByGuid(stepresources,explanation_resource_guid)
			invalid_resource_guid=step['invalid_resource']['guid']
			invalid_resource=self.workflow.getStepResourceByGuid(stepresources,invalid_resource_guid)
			audiofile=self.getAudioFile(explanation_resource)
			play(audiofile)
			timeout=step['timeout']
			loopcount=step['number_of_attempts']
			for i in range(0,loopcount):
				audiofile=self.getAudioFile(options_resource)
				result=capture(audiofile,int(timeout)*1000,1)
				debugPrint("Captured keys ="+result)
				keypress=result
				print "Got keypress ",keypress
				for option in step['options']:
					if option['number']==keypress:
						return option['next']		
				audiofile=self.getAudioFile(invalid_resource)
				play(audiofile)  
				debugPrint("Invalid Capture")
			print "Hanging Up"
			return None
		if step['type']=='record':
			explanation_resource_guid=step['explanation_resource']['guid']
			explanation_resource=self.workflow.getStepResourceByGuid(stepresources,explanation_resource_guid)
			confirmation_resource_guid=step['confirmation_resource']['guid']
			confirmation_resource=self.workflow.getStepResourceByGuid(stepresources,confirmation_resource_guid)
			
			audiofile=self.getAudioFile(explanation_resource)
			play(audiofile)
			recordingfilename="/tmp/"+str(uuid.uuid4())+".wav"
			recordingfile=os.path.join(self.serverdir,recordingfilename)
			audiofile=self.getAudioFile(explanation_resource)
			stopkey="#"+step['stop_key']
			recordlen=int(step['timeout'])
			result=record(recordingfile,stopkey,recordlen)
			debugPrint("Result of recording = "+str(result))
			audiofile=self.getAudioFile(confirmation_resource)
			play(audiofile)
			return None
