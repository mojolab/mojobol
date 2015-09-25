import os,sys,ConfigParser,yaml,pprint,time
sys.path.append("/home/swara/mojobol/libs")
from mojoasteriskplayer import *

class MojoBolServer:
	def __init__(self,configfile):
		config=ConfigParser.ConfigParser()
		config.read(configfile)
		self.directory=config.get("Server","serverdir")
		self.name=config.get("Server","servername")
		self.playertype=config.get("Server","playertype")
		self.language=config.get("Server","language")
		self.workflowpath=config.get("Server","workflowpath")
		self.workflow=MojoBolWorkflow(self.workflowpath)
	def parse_workflow(self):
		if self.playertype=="asterisk":
			self.player=MojoAsteriskPlayer(self.language,self.workflow,self.directory) 
		rootstep={}
		curstep={}
		nextstep={}
		prevstep={}
		executedsteps=[]
		for step in self.workflow.steps:
			if step['root']==True:
				rootstep=step
		if rootstep=={}:
			print "No root step"
		else:
			curstep=rootstep
			nextid=self.player.executeStep(curstep)
		while(nextid!=None):
			curstep=self.workflow.getStepByID(nextid)
			nextid=self.player.executeStep(curstep)
			time.sleep(1)
class MojoBolWorkflow:
	def __init__(self,path_to_workflow):
		yamlfile=os.popen("ls '%s'" %(os.path.join(path_to_workflow,"workflow.yml"))).read().strip()
		print yamlfile
		f=open(yamlfile,"r")
		self.steps=yaml.safe_load(f)
		f.close()
		self.workflowpath=path_to_workflow
	def printSteps(self):
		ppr=pprint.PrettyPrinter(indent=4)
		for step in self.steps:
			ppr=pprint.PrettyPrinter(indent=4)
			print "Step ID", step['id']
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
		print "**** Resources for step " + str(step['id']) + " ************"
		for resource in resourcelist:
			lresourcelist=resource.getLocalizedResources()
			for lresource in lresourcelist:
				#ppr.pprint(lresource.resourcemap)
				print lresource.rtype
	def getStepResources(self,step):
		resourcelist=[]
		for k,v in step.iteritems():
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
		
		
	
