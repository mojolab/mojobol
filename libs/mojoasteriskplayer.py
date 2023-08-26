#interface to asterisk. Safe for import * ing.
import time
import re
import sys
import os
import pprint
import uuid
import logging
import yaml
import subprocess
import speech_recognition as sr
from os import path
from pydub import AudioSegment
import gtts
from googletrans import Translator
from playsound import playsound
import openai
import os
import threading

def read_agi_environment():
    env = {}
    tests = 0;
    while True:
        line = sys.stdin.readline().strip()
        if line == '':
            break
        key,data = line.split(':')
        if key[:4] != 'agi_':
            sys.stderr.write("Did not work!\n")
            sys.stderr.flush()
            continue
        key = key.strip()
        data = data.strip()
        if key != '':
            env[key] = data
    sys.stderr.write("AGI Environment Dump:\n")
    sys.stderr.flush()
    for key in env.keys():
        sys.stderr.write(" -- %s = %s\n" % (key, env[key]))
        sys.stderr.flush()
    return env

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
    if key==1:
        return "Skip"
    #raise KeyPressException(key)

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
            val=keyDict[c][0](*keyDict[c][1])
            if val=="Skip":
                return val
        else:
            keyDict[c]()
        return c
def play_loop(path):
        global stop_flag
        stop_flag=False
    
        while True:

            play(path) 
            if stop_flag:
                 break
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
    
    def __init__(self,servername,language,workflow,serverdir,callsdir):
        self.workflow=workflow
        self.language=language
        self.serverdir=serverdir
        self.callsdir=callsdir
        self.servername=servername
        self.logger=logging.getLogger(self.servername)
        self.logger.info("Player initialized with workflow - %s, language = %s, serverdir=%s" %(self.workflow.workflowpath,self.language,self.serverdir))
        
    def getAudioFile(self,resource):
        resourcename=resource.resourcemap['name']
        self.logger.info("Getting audio file path for resource with name %s with guid %s" %(resourcename,resource.resource_guid))
        localizedresource=resource.getLocalizedResources(language=self.language)[0]
        self.logger.info("Localised resource type is %s" %localizedresource.rtype)
        if localizedresource.rtype=="ExternalAudio":
            audiofilename=os.path.join(self.workflow.workflowpath,localizedresource.resourcemap['recorded_audio'])
            self.logger.info("Filename is %s" %audiofilename)
            return audiofilename
            
        if localizedresource.rtype=='TextLocalizedResource':
            tempfilename="/tmp/"+localizedresource.guid
            command="espeak -s 100 -w %s.wav '%s'" %(tempfilename,localizedresource.resourcemap['text'].replace("'"," "))
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
        print("Capturing")
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
        print("Hanging Up")
        return None
    def executeStep(self,step,call):
        self.logger.info("Executing step id %s name %s" %(step['id'],step['name']))
        self.calllogger=logging.getLogger(call.callid)
        stepresources=self.workflow.getStepResources(step)
        if step['type']=='play':
            stepresources=self.workflow.getStepResources(step)
            resource_guid=step['resource']['guid']
            resource=self.workflow.getStepResourceByGuid(stepresources,resource_guid)
            audiofile=self.getAudioFile(resource)
            play(audiofile)
            self.calllogger.info("Played file %s" %resource_guid)
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
            print("Capturing")
            loopcount=step['number_of_attempts']
            for i in range(0,loopcount):
                audiofile=self.getAudioFile(instructions_resource)
                result=capture(audiofile,int(timeout)*1000,int(maxdigits))
                self.logger.info("Captured result %s" %(str(result)))
                if result==step['valid_values']:
                    self.logger.info("That is a valid capture")
                    self.calllogger.info("%s is a valid input from user" %result)
                    self.logger.info("Next step will be %s" %(str(step['next'])))
                    return step['next']
                else:
                    self.logger.info("That is an invalid capture")
                    audiofile=self.getAudioFile(invalid_resource)
                    play(audiofile)  
            self.calllogger.info("Invalid or no input from user")
            self.logger.info("Next step will be None")
            return None
        if step['type']=='menu':
            f=open(call.menufile,"a")
            f.write("\n")
            
            responses=[]
            response={}
            response['id']=str(uuid.uuid4())
            self.calllogger.info("User presented with menu having options %s" %str(step['options']))
            print("Playing explanation resource", step['explanation_resource'])
            print("Playing options resource", step['options_resource'])
            options_resource_guid=step['options_resource']['guid']
            options_resource=self.workflow.getStepResourceByGuid(stepresources,options_resource_guid)
            explanation_resource_guid=step['explanation_resource']['guid']
            explanation_resource=self.workflow.getStepResourceByGuid(stepresources,explanation_resource_guid)
            invalid_resource_guid=step['invalid_resource']['guid']
            invalid_resource=self.workflow.getStepResourceByGuid(stepresources,invalid_resource_guid)
            audiofile=self.getAudioFile(explanation_resource)
            play(audiofile)
            timeout=step['timeout']
            loopcount=int(step['number_of_attempts'].strip("'"))
            step['userchoices']=[]
            for i in range(0,loopcount):
                userchoice={}
                userchoice['attemptno']=str(i)
                self.logger.info("Beginning menu loop %d" %i)
                audiofile=self.getAudioFile(options_resource)
                result=capture(audiofile,int(timeout),1)
                #debugPrint("Captured keys ="+result)
                keypress=result
                userchoice['keypress']=keypress
                print("Got keypress ",keypress)
                self.calllogger.info("User chose %s" %keypress)
                for option in step['options']:
                    if option['number']==keypress:
                        userchoice['nextstep']=option['next']
                        step['userchoices'].append(userchoice)
                        response['data']=step
                        responses.append(response)
                        f.write(yaml.dump(responses,default_flow_style=False))
                        f.write("\n")
                        f.close()
                        return option['next']		
                audiofile=self.getAudioFile(invalid_resource)
                userchoice['nextstep']=False
                step['userchoices']	.append(userchoice)
                play(audiofile)  
                self.calllogger.info("That choice is invalid")
                #debugPrint("Invalid Capture")
            response['data']=step
            responses.append(response)
            f.write(yaml.dump(responses,default_flow_style=False))
            f.write("\n")
            f.close()
            print("Hanging Up")
            return None
        if step['type']=='record':
            self.calllogger.info("Recording step")
            explanation_resource_guid=step['explanation_resource']['guid']
            explanation_resource=self.workflow.getStepResourceByGuid(stepresources,explanation_resource_guid)
            confirmation_resource_guid=step['confirmation_resource']['guid']
            confirmation_resource=self.workflow.getStepResourceByGuid(stepresources,confirmation_resource_guid)
            audiofile=self.getAudioFile(explanation_resource)
            self.calllogger.info("playing explanation")
            play(audiofile)
            recordingfilename="callfile-"+call.callid+"-"+str(uuid.uuid4())
            self.calllogger.info("file name =%s " %recordingfilename)
            recordingfile=os.path.join(self.serverdir,self.callsdir,call.callid,recordingfilename)
            self.calllogger.info("file path =%s " %recordingfile)
            self.calllogger.info("Beginning recording "+ recordingfile)
            
            #debugPrint(recordingfile)
            #audiofile=self.getAudioFile(explanation_resource)
            self.calllogger.info("Stopkey "+ step['stop_key'])
            
            stopkey="#"+step['stop_key'].strip("'")
            
            recordlen=int(step['timeout'].strip("'"))
            self.calllogger.info("recordlen "+ step['timeout'])
            result=record(recordingfile,stopkey,recordlen)
            
            #debugPrint("Result of recording = "+str(result))
            audiofile=self.getAudioFile(confirmation_resource)
            play(audiofile)
            audiofile=recordingfile
            play(audiofile)
            return None
        if step['type']=='playloop':
            self.calllogger.info("looping play")
            playloopdir=step['loop_dir']
            if os.path.isdir(playloopdir):
                self.calllogger.info('playing files in %s' %playloopdir)
                files=os.listdir(playloopdir)
                for filename in files:
                    self.calllogger.info('playing file %s' %filename) 
                    keydict=newKeyDict()
                    keydict['1']=Nop
                    val=play(os.path.join(playloopdir,filename.split(".")[0]),keydict)
                    self.calllogger.info(val)
            else:
                self.calllogger.info('Loop directory does not exist')
            return None
        if step['type']=='askgpt':
            self.calllogger.info("Recording step")
            explanation_resource_guid=step['explanation_resource']['guid']
            explanation_resource=self.workflow.getStepResourceByGuid(stepresources,explanation_resource_guid)
            confirmation_resource_guid=step['confirmation_resource']['guid']
            confirmation_resource=self.workflow.getStepResourceByGuid(stepresources,confirmation_resource_guid)
            audiofile=self.getAudioFile(explanation_resource)
            self.calllogger.info("playing explanation")
            play(audiofile)
            recordingfilename="callfile-"+call.callid+"-"+str(uuid.uuid4())
            self.calllogger.info("file name =%s " %recordingfilename)
            recordingfile=os.path.join(self.serverdir,self.callsdir,call.callid,recordingfilename)
            self.calllogger.info("file path =%s " %recordingfile)
            self.calllogger.info("Beginning recording "+ recordingfile)
            
            #debugPrint(recordingfile)
            #audiofile=self.getAudioFile(explanation_resource)
            self.calllogger.info("Stopkey "+ step['stop_key'])
            
            stopkey="#"+step['stop_key'].strip("'")
            
            recordlen=int(step['timeout'].strip("'"))
            self.calllogger.info("recordlen "+ step['timeout'])
            result=record(recordingfile,stopkey,recordlen)
            
            #debugPrint("Result of recording = "+str(result))
            audiofile=self.getAudioFile(confirmation_resource)
            play(audiofile)
            audiofile=recordingfile
            play(audiofile)
            r = sr.Recognizer()
            try:
                with sr.AudioFile(audiofile+".wav") as source:
                    audio = r.record(source)  # read the entire audio file
            except Exception as e:
                self.logger.info("audio trasciption failed becasuse"+str(e))        

            #return text from audio file asnycronously
            transcribed_text=r.recognize_google(audio)
            self.logger.info("Transcription done : "+transcribed_text)
            
            translator = Translator()
            translate_en=translator.translate(transcribed_text, dest="en").text
            self.logger.info("Translation done "+translate_en)
            openai.api_key=''
            response = openai.Completion.create(model="gpt-3.5-turbo",prompt=translate_en)
            self.logger.info("Chat done "+ response.choices[0].text)
            translate_hi=translator.translate( response.choices[0].text,dest="hi").text
            tts = gtts.gTTS(translate_hi, lang='hi')
            self.logger.info("Text to speech started with text "+translate_hi)
            try:
                tts.save("text.mp3")
                self.logger.info("audio conversion done")
            except:
         #delete the file if it exists
                if path.exists("text.mp3"):
                    os.remove("text.mp3")
                    tts.save("text.mp3")
                    self.logger.info("audio conversion done")
            
            self.logger.info("trying to covert audio into wave format")
            os.system("sox -t mp3 text.mp3 -e signed-integer -c 1 -b 16 -r 8k -t wav text.wav")
            self.logger.info("audio conversion done")
            play("text.wav")
            self.logger.info("playing gpt answer")
            return None


            






