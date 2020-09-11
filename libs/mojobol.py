import os,sys,configparser,yaml,pprint,time, datetime
sys.path.append("/opt/mojobol/libs")
from mojoasteriskplayer import *
import logging

class MojoBolResponder:
	def __init__(self,configfile):
		config=configparser.RawConfigParser()
		config.read(configfile)
		self.directory=config.get("Server","serverdir")
		self.maildir=config.get("Server","maildir")
		self.name=config.get("Server","servername")
		self.playertype=config.get("Server","playertype")
		self.language=config.get("Server","language")
		self.workflowpath=config.get("Server","workflowpath")
		self.loglevel=config.get("Server","loglevel")
		self.logfile=config.get("Server","logfile")
		self.callsdir=config.get("Server","callsdir")
		self.reportsdir=config.get("Server","reportsdir")
		self.callkey=config.get("Server","callkey")
		self.tsformat=config.get("Server","tsformat")
		self.workflow=MojoBolWorkflow(self.workflowpath)
		if os.path.isdir(self.directory)==False:
			try:
				os.mkdir(self.directory)
			except:
				print("Could not create server directory")
		logpath=os.path.dirname(os.path.join(self.directory,self.logfile))
		if os.path.isdir(logpath)==False:
			try:
				os.mkdir(logpath)
				f=open(os.path.join(self.directory,self.logfile),"w")
				f.write("Starting Logfile")
				f.close()
			except:
				print("Could not create server logfile")
		callpath=os.path.join(self.directory,self.callsdir)
		if os.path.isdir(callpath)==False:
			try:
				os.mkdir(callpath)
			except:
				print("Could not create server call directory")
				
		fh = logging.FileHandler(os.path.join(self.directory,self.logfile))
		self.logger=logging.getLogger(self.name)
		if self.loglevel=="debug":
			self.logger.setLevel(logging.DEBUG)
			fh.setLevel(logging.DEBUG)
		else:
			self.logger.setLevel(logging.INFO)
			fh.setLevel(logging.INFO)
		formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
		fh.setFormatter(formatter)
		self.logger.addHandler(fh)
		self.logger.info("MojoBol Server started")
	def parse_workflow(self,call):
		if self.playertype=="asterisk":
			self.player=MojoAsteriskPlayer(self.name,self.language,self.workflow,self.directory,self.callsdir) 
		rootstep={}
		curstep={}
		nextstep={}
		prevstep={}
		executedsteps=[]
		for step in self.workflow.steps:
			if step['root']==True:
				rootstep=step
		if rootstep=={}:
			print("No root step")
		else:
			curstep=rootstep
			nextid=self.player.executeStep(curstep,call)
		while(nextid!=None):
			curstep=self.workflow.getStepByID(nextid)
			nextid=self.player.executeStep(curstep,call)
			time.sleep(1)
		self.logger.info("Finished parsing workflow")
		return True

class MojoBolWorkflow:
	def __init__(self,path_to_workflow):
		yamlfile=os.popen("ls '%s'" %(os.path.join(path_to_workflow,"workflow.yml"))).read().strip()
		print(yamlfile)
		f=open(yamlfile,"r")
		self.steps=yaml.safe_load(f)
		f.close()
		self.workflowpath=path_to_workflow
	def printSteps(self):
		ppr=pprint.PrettyPrinter(indent=4)
		for step in self.steps:
			ppr=pprint.PrettyPrinter(indent=4)
			print("Step ID", step['id'])
			ppr.pprint(step)
	def getStepByID(self,stepid):
		for step in self.steps:
			if step['id']==stepid:
				return step
		return {}
	def getStepsByType(self,steptype):
		steps=[]
		for step in self.steps:
			if step['type']==steptype:
				steps.append(step)
		return steps
	def printStepResources(self,step):
		resourcelist=self.getStepResources(step)
		print("**** Resources for step " + str(step['id']) + " ************")
		for resource in resourcelist:
			lresourcelist=resource.getLocalizedResources()
			for lresource in lresourcelist:
				#ppr.pprint(lresource.resourcemap)
				print(lresource.rtype)
	def getStepResources(self,step):
		resourcelist=[]
		for k,v in step.items():
			if "resource" in k:
				resource=MojoBolWorkflowResource(self.workflowpath,v['guid'])
				resourcelist.append(resource)
		return resourcelist
	def getStepResourceByGuid(self,resourcelist,guid):
		for resource in resourcelist:
			if resource.resource_guid==guid:
				return resource
		return None
					
					
class MojoBolWorkflowResource:
	def __init__(self,workflowpath,resource_guid):
		self.workflowpath=workflowpath
		self.resource_guid=resource_guid
		self.resource_file="resource "+self.resource_guid+".yml"
		f=open(os.path.join(self.workflowpath,self.resource_file),"r")
		self.resourcemap=yaml.safe_load(f)
		f.close()
	def getLocalizedResources(self,language=""):
		localizedresources=[]
		fileprefix="localized_resource "+self.resource_guid
		for filename in os.listdir(self.workflowpath):
			if filename.startswith(fileprefix):
				localizedresource=MojoBolWorkFlowLocalizedResource(self.workflowpath,filename)
				if language!="":
					if localizedresource.language==language:
						localizedresources.append(localizedresource)
				else:
					localizedresources.append(localizedresource)
		return localizedresources
			

class MojoBolWorkFlowLocalizedResource:
	def __init__(self,workflowpath,filename):
		self.workflowpath=workflowpath
		self.filename=filename
		f=open(os.path.join(self.workflowpath,self.filename),"r")
		self.resourcemap=yaml.safe_load(f)
		f.close()
		self.language=self.resourcemap['language']
		self.rtype=self.resourcemap['type']
		self.guid=self.resourcemap['guid']
		self.resource_guid=self.resourcemap['resource_guid']	
		
		
class MojoBolCall:
	def __init__(self,responder,env):
		try:
			self.callerid = env['agi_callerid']
		except:
			self.callerid="Unknown"
		self.responder=responder
		globalcallog=os.path.join(self.responder.directory,self.responder.callsdir,"calllog")
		#self.responder.logger.info("Hello World")
		self.responder.logger.info(str(env))
		self.starttime=datetime.datetime.now()
		self.stoptime=self.starttime
		self.callid=self.callerid+"-"+self.responder.name+"-"+self.starttime.strftime("%Y-%b-%d-%H-%M-%S")
		self.loglevel=self.responder.loglevel
		#create directory for call files
		self.calldir=os.path.join(self.responder.directory,self.responder.callsdir,self.callid)
		self.menufilename="menuresponsefile-"+self.callid+".yml"
		self.menufile=os.path.join(self.responder.directory,self.responder.callsdir,self.callid,self.menufilename)
		if os.path.isdir(self.calldir)==False:
			print("Trying to make call directory", self.calldir)
			try:
				os.mkdir(self.calldir)
			except:
				print("Could not create call directory")
		self.logfile=os.path.join(self.calldir,"log",self.callid+".log")
		logpath=os.path.dirname(os.path.join(self.calldir,self.logfile))
		if os.path.isdir(logpath)==False:
			try:
				os.mkdir(logpath)
				f=open(os.path.join(self.calldir,self.logfile),"w")
				f.write("Starting Logfile")
				f.close()
			except:
				print("Could not create call logfile")
				
		fh = logging.FileHandler(os.path.join(self.calldir,self.logfile))
		self.logger=logging.getLogger(self.callid)
		if self.loglevel=="debug":
			self.logger.setLevel(logging.DEBUG)
			fh.setLevel(logging.DEBUG)
		else:
			self.logger.setLevel(logging.INFO)
			fh.setLevel(logging.INFO)
		formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
		fh.setFormatter(formatter)
		self.logger.addHandler(fh)
		self.logger.info("MojoBol call with id %s started" %self.callid)
		if os.path.exists(globalcallog):
			self.logger.info("Removing global log")
			os.remove(globalcallog)
		self.logger.info("Creating symlink")	
		print(os.path.join(self.calldir,self.logfile),globalcallog)
		os.symlink(os.path.join(self.calldir,self.logfile),globalcallog)
		
	def endcall(self):
		self.stoptime=datetime.datetime.now()
		calllength=self.stoptime-self.starttime
		self.logger.info("Call ended at %s" %(self.stoptime.strftime("%Y-%b-%d %H:%M:%S")))
		self.logger.info("Call duration: %s" %(str(calllength.seconds+1)))
	def compresscallfile(self):
		try:
			self.logger.info("Call dir %s" %self.calldir)
			maildir=os.path.join(self.responder.directory,self.responder.maildir)
			zipfile=os.path.join(maildir,self.callid+".zip")
			os.system("zip -r %s %s" %(zipfile, self.calldir))
			if os.isfile("%s" %(zipfile)):
				self.logger.info("Successfully zipped call file")
			else:
				self.logger.info("Could not compress call file")
			
				
		except:
			self.logger.error("Could not compress call file")
			
		
