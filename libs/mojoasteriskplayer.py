#interface to asterisk. Safe for import * ing.
import time
import re
import sys
import os
import pprint
import uuid
import logging
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
			sys.stderr.write("PASS (%s)\n" % result)
			sys.stderr.flush()
			return result
	else:
		sys.stderr.write("FAIL (unexpected result '%s')\n" % params)
		sys.stderr.flush()
		return -2
def hangup ():
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
		sys.stdout.write("STREAM FILE %s \"%s\"\n" % (str(fname),escapeDigits))
		sys.stdout.flush()
		result = readline()
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
	ms_timeout = int(timeout*1000)
	seconds_silenceTimeout = -1 #int(silenceTimeout)
	cmdString = "RECORD FILE %s wav %s %s BEEP s=%d\n" % (fname, \
														  stopDigits, \
														  ms_timeout, \
														  seconds_silenceTimeout)
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
	
	def __init__(self,servername,language,workflow,serverdir):
		self.workflow=workflow
		self.language=language
		self.serverdir=serverdir
		self.servername=servername
		self.logger=logging.getLogger(self.servername)
		self.logger.info("Player initialized with workflow - %s, language = %s, serverdir=%s" %(self.workflow.workflowpath,self.language,self.serverdir))
		
	def getAudioFile(self,resource):
		resourcename=resource.resourcemap['name']
		self.logger.info("Getting audio file path for resource with name %s with guid %s" %(resourcename,resource.resource_guid))
		localizedresource=resource.getLocalizedResources(language=self.language)[0]
		
		self.logger.info("Localised resource type is %s"%localizedresource.rtype)
	
		if localizedresource.rtype=="ExternalAudio":
			audiofilename=os.path.join(self.workflow.workflowpath,localizedresource.resourcemap['recorded_audio'])
			#os.system("sox %s.wav -r 8000 -c 1 %s.wav" %(audiofilename,audiofilename+"gsm"))
			#os.system("chmod a+rwx %s*" %(audiofilename+"gsm"))
			#self.logger.info("Filename is %s" %audiofilename +"gsm")
			#return audiofilename+"gsm"
			self.logger.info("Filename is %s" %audiofilename)
			return audiofilename
			
		if localizedresource.rtype=='TextLocalizedResource':
			tempfilename="/tmp/"+localizedresource.guid
			command="espeak -v hindi -s 100 -w %s.wav '%s'" %(tempfilename,localizedresource.resourcemap['text'].replace("'"," "))
			self.logger.info("Running command %s" %command)
			os.system(command)
			os.system("sox %s.wav -r 8000 -c 1 %s.wav" %(tempfilename,tempfilename+"gsm"))
			os.system("chmod a+rwx %s*" %(tempfilename+"gsm"))
			self.logger.info("Filename is %s" %tempfilename +"gsm")
			return tempfilename+"gsm"
	
	def stepPlay(self,step):
		#debugPrint("Playing "+step['resource']['guid'])
		stepresources=self.workflow.getStepResources(step)
		resource_guid=step['resource']['guid']
		resource=self.workflow.getStepResourceByGuid(stepresources,resource_guid)
		audiofile=self.getAudioFile(resource)
		play(audiofile)
		return True
	def stepCapture(self,step):
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
			#debugPrint("Captured keys ="+result)
			if result==step['valid_values']:
				#debugPrint("Valid Capture")
				return step['next']
			else:
				audiofile=self.getAudioFile(invalid_resource)
				play(audiofile)  
		print "Hanging Up"
		return None
	def executeStep(self,step):
		self.logger.info("Executing step id %s name %s" %(step['id'],step['name']))
		stepresources=self.workflow.getStepResources(step)
		if step['type']=='play':
			stepresources=self.workflow.getStepResources(step)
			resource_guid=step['resource']['guid']
			resource=self.workflow.getStepResourceByGuid(stepresources,resource_guid)
			audiofile=self.getAudioFile(resource)
			play(audiofile)
			self.logger.info("Next step will be %s" %(str(step['next'])))
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
				self.logger.info("Captured result %s" %(str(result)))
				if result==step['valid_values']:
					self.logger.info("That is a valid capture")
					self.logger.info("Next step will be %s" %(str(step['next'])))
					return step['next']
				else:
					self.logger.info("That is an invalid capture")
					audiofile=self.getAudioFile(invalid_resource)
					play(audiofile)  
			self.logger.info("Next step will be None")
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
				self.logger.info("Beginning menu loop %d" %i)
				audiofile=self.getAudioFile(options_resource)
				result=capture(audiofile,int(timeout),1)
				#debugPrint("Captured keys ="+result)
				keypress=result
				print "Got keypress ",keypress
				for option in step['options']:
					if option['number']==keypress:
						return option['next']		
				audiofile=self.getAudioFile(invalid_resource)
				play(audiofile)  
				#debugPrint("Invalid Capture")
			print "Hanging Up"
			return None
		if step['type']=='record':
			explanation_resource_guid=step['explanation_resource']['guid']
			explanation_resource=self.workflow.getStepResourceByGuid(stepresources,explanation_resource_guid)
			confirmation_resource_guid=step['confirmation_resource']['guid']
			confirmation_resource=self.workflow.getStepResourceByGuid(stepresources,confirmation_resource_guid)
			audiofile=self.getAudioFile(explanation_resource)
			play(audiofile)
			recordingfilename="callfile-"+str(uuid.uuid4())
			recordingfile=os.path.join(self.serverdir,recordingfilename)
			#debugPrint(recordingfile)
			audiofile=self.getAudioFile(explanation_resource)
			stopkey="#"+step['stop_key']
			recordlen=int(step['timeout'])
			result=record(recordingfile,stopkey,recordlen)
			#debugPrint("Result of recording = "+str(result))
			audiofile=self.getAudioFile(confirmation_resource)
			play(audiofile)
			return None
		
