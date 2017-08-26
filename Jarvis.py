import os
import sqlite3
import os.path
import sys, os
import subprocess
import datetime
import shutil, errno
import socket, select
import aiml
import time
import threading
import urllib2
import requests
import getpass
import json
import glob
from random import randint
from unicodedata import normalize

#MIT License 2017 danielcorreaeng <danielcorrea.eng@gmail.com>

if sys.platform == 'win32':
	PathLocal = "C:\\Jarvis"
	PathDB = PathLocal + "\\Db\\"
	PathOutput = PathLocal + "\\Output\\"
	PyCommandDisplay = PathLocal + "\\Python_Win\\Python-Portable.exe"
	PyCommand = PathLocal + "\\Python_Win\\App\\python.exe"
	PyScripter = PathLocal + "\\Python_Win\\PyScripter-Portable.exe"
	PathBot = PathLocal + "\\Aiml\\"
elif sys.platform == 'linux2':
	PathLocal = "/home/dani/workspace/jarvis"
	PathOutput = PathLocal + "/Output/"
	PathDB = PathLocal + "/Db/"
	PyCommandDisplay = "python"
	PyCommand = "python"
	PyScripter = "notepadqq"
	PathBot = PathLocal + "/Aiml/"

BotNameForIntelligentResponse = "bot"
LocalUsername = getpass.getuser().replace(' ','_')
LocalHostname = socket.gethostname().replace(' ','_')
LocalFile = datetime.datetime.now().strftime("%Y%m%d_%H%M%S%f") + "_" + str(randint(0, 999)) + ".py"
LastCommand = ''

def GetPathLocal():
    return PathLocal

def GetPathDB():
    return PathDB
	
def GetPathOutput():
    return PathOutput

def GetPyCommand():
    return PyCommand

def GetPyCommandDisplay():
    return PyCommandDisplay

def GetPyScripter():
    return PyScripter

def GetBotNameForIntelligentResponse():
    return BotNameForIntelligentResponse

def GetPathBot():
    return PathBot

def GetUsername():
	return LocalUsername

def GetHostname():
	return LocalHostname

def GetLocalFile():
	return LocalFile

def GetLastCommand():
	return LastCommand

class MyException(Exception):
    def __init__(self, value):
        self.parameter = value
    def __str__(self):
        return repr(self.parameter)
		
class MyDb():
	class Parameters():
		def __init__(self):
			self.path = GetPathDB()
			self.db = self.path  + GetHostname() + "_" + GetUsername() + ".db"
			pass

	def __init__(self, dbParameters):
		self.dbParameters = dbParameters

	def __del__(self):
		pass

	def CheckDb(self):
		result = False

		try:
			if os.path.exists (GetPathDB())== False:
				os.mkdir (GetPathDB()) 
						
			db = self.dbParameters.db

			if(os.path.isfile(db) == False):
				conn = sqlite3.connect(db)
				cursor = conn.cursor()
				cursor.execute("CREATE TABLE tag (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, command BLOB)")
				conn.commit()
				conn.close()

			result = True
		except:
			raise MyException("MyDb : CheckDb : Internal Error.")

		return result

	def SelectCommandFromTag(self,name):
		result = None

		try:
			db = self.dbParameters.db
			conn = sqlite3.connect(db)
			cursor = conn.cursor()
			cursor.execute("SELECT id,command FROM tag WHERE name='" + name + "'")

			#_id, command = cursor.fetchone() #debug

			rows = cursor.fetchall()

			if(len(rows) > 0):
				result = rows[0][1]

			conn.close()
		except:
			raise MyException("MyDb : SelectCommandFromTag : Internal Error.")

		return result

	def InsertTagWithFile(self, tag, inputFileBin):
		result = False

		try:
			db = self.dbParameters.db
			conn = sqlite3.connect(db)
			cursor = conn.cursor()
			
			with open(inputFileBin, "rb") as input_file:
				ablob = input_file.read()
				cursor.execute("insert or replace into tag (id, name, command) values ((select id from tag where name = '"+ tag +"'),'"+ tag +"', ?)", [sqlite3.Binary(ablob)])
				conn.commit()

			conn.close()

			result = True
		except:
			raise MyException("MyDb : InsertTag : Internal Error.")

		return result

	def SelectListTagsLike(self,name):
		result = []
		temp = []

		try:
			db = self.dbParameters.db
			conn = sqlite3.connect(db)
			cursor = conn.cursor()
			
			if(name!=None):
				cursor.execute("SELECT name FROM tag WHERE name LIKE '%" + name + "%'")
			else:
				cursor.execute("SELECT name FROM tag")

			rows = cursor.fetchall()

			if(len(rows) > 0):
				temp = list(zip(*rows)[0])

			for row in temp:
				result.append(str(row))

			conn.close()
		except:
			raise MyException("MyDb : SelectListTagsLike : Internal Error.")

		return result
		
	def DeleteCommandFromTag(self,name):
		result = True

		try:
			db = self.dbParameters.db
			conn = sqlite3.connect(db)
			cursor = conn.cursor()
			sql = "DELETE FROM tag WHERE name='" + name + "'"
			cursor.execute("DELETE FROM tag WHERE name='" + name + "'")
			conn.commit()
			conn.close()
		except:
			raise MyException("MyDb : DeleteCommandFromTag : Internal Error.")
			result = False

		return result

class JarvisUtils():
    def __init__(self):
        self.log = False

    def LogFuction(self):
		try:
			ret = urllib2.urlopen('http://127.0.0.1:8800')
			if ret.code == 200:
				print("Hey. Log is online, honey.")
				id = GetLocalFile().replace("_", "").replace(".py", "")
				
				data = []
				localTime = datetime.datetime.now().strftime("%Y%m%d_%H%M%S%f")		
				data.append({'id' : id , 'user' : GetUsername() , 'host' : GetHostname() , 'command' : GetLastCommand() , 'time' : localTime , 'status' : 'start'})
				
				url = "http://localhost:8800/log"
				headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
				requests.post(url, data=json.dumps(data), headers=headers)
				
				while (self.log):
					localTime = datetime.datetime.now().strftime("%Y%m%d_%H%M%S%f")
					data[:] = []
					data.append({'id' : id , 'user' : GetUsername() , 'host' : GetHostname() , 'command' : GetLastCommand() , 'time' : localTime , 'status' : 'alive'})
					requests.post(url, data=json.dumps(data), headers=headers)
					time.sleep(2.0)
				
				data[:] = []
				localTime = datetime.datetime.now().strftime("%Y%m%d_%H%M%S%f")
				data.append({'id' : id , 'user' : GetUsername() , 'host' : GetHostname() , 'command' : GetLastCommand() , 'time' : localTime , 'status' : 'finish'})			
				requests.post(url, data=json.dumps(data), headers=headers)
				
			else:
				pass
		except:
			pass

    def LogThread(self):
	threadLog = threading.Thread(target=self.LogFuction, args=())
	threadLog.start()		

    def _Run(self,command, parameters=None):
		result = False
		proc = None
		self.log = True
		self.LogThread()
		
		try:
			if(parameters != None):
				proc = subprocess.Popen([command, parameters], stdout=subprocess.PIPE, shell=True)
			else:
				proc = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)

			(out, err) = proc.communicate()

			if(out.find("False") < 0 and out.find("NOK") < 0):
				result = True
		except:
			pass

		self.log = False
		return result


    def AimlInitialize(self, sessionId):
		os.chdir(GetPathBot())

		#python aiml 0.8.6 - https://pypi.python.org/pypi/aiml/0.8.6
		self._aiml = aiml.Kernel()
		self._aiml.verbose(False) #debug

		memory = "std-startup.xml"
		brain = "bot_brain.brn"

		if os.path.isfile(brain):
			 self._aiml.bootstrap(brainFile = brain)
		else:
			 self._aiml.bootstrap(learnFiles = memory, commands = "load aiml b")
			 self._aiml.saveBrain(brain)

		#test default values #debug
		self._aiml.setPredicate("dog", "Brandy", sessionId)
		self._aiml.setPredicate("it", GetUsername(), sessionId)
		self._aiml.setPredicate("name", GetUsername(), sessionId)
		self._aiml.setPredicate("bot name", GetBotNameForIntelligentResponse(), sessionId)

    def AimlChat(self, message, sessionId=12345):
		if os.path.exists (GetPathBot())== False:
			result = "Sorry Tiger, I lost my identity. hum... Am I Doris?"
			return result

		try:
			if(self._aiml is None):
				self.AimlInitialize(sessionId)
		except:
			self.AimlInitialize(sessionId)

		if message == "save":
			self._aiml.saveBrain(brain)
			result = "My memory is saved."
		elif message == "clean":
			os.remove(brain)
			result = "My memory is clean."
		else:
			#print "[input] : " + message #debug
			bot_response = self._aiml.respond(message,sessionId)
			result = bot_response

		return result

class Commands():
    class Parameters():
        def __init__(self):
            self.LoadVars()

            self.dbParameters = None
            self.path = GetPathLocal()
            self.pathOutput = GetPathOutput()
            self.pyCommand = GetPyCommand()
            self.pyScripter = GetPyScripter()
            pass

        def LoadVars(self):
            pass

    def __init__(self, parameters):
        self.parameters = Commands.Parameters()
        self.parameters = parameters
        self.myDb = MyDb(self.parameters.dbParameters)
        #self.myDb.CheckDb() #debug

    def __del__(self):
        pass

		
    def DoCommand(self, command):
	
		if(self._DoCommand(command) == True):
			return True

		_command = command.split(" ")

		for i in range(len(_command)-1,0,-1):
			_localParameters = " ".join(_command[i:])
			_localCommand = " ".join(_command[0:i])
			
			if(self._DoCommand(_localCommand, _localParameters) == True):
				return True
				
		return False
	
    def _DoCommand(self, command, parameters=None):

		if os.path.exists (self.parameters.pathOutput)== False:
			os.mkdir (self.parameters.pathOutput ) 

		jv = JarvisUtils()

		localFile = self.parameters.pathOutput + GetLocalFile()

		#print command
		#print parameters
		
		_command = self.myDb.SelectCommandFromTag(command)

		if(_command != None):

			fileTest = open(localFile,"wb")
			fileTest.write(_command)
			fileTest.close()

			_prog = self.parameters.pyCommand + " " + localFile

			if(parameters!=None):
				_prog = _prog + " " + parameters

			jv._Run(_prog)

			if(os.path.isfile(localFile) == True):
			   os.remove(localFile)

			return True
			
		elif(command == 'help'):
			print "Hum... Let me try : "
			print " <tag0> <tag1> : i execute the code what it have <tag0> <tag1>."
			
			print " record <tag0> <tag1> : i try open editor code and i will record it with tags."
			print " read <file> <tag0> <tag1> : give me a file and i record with <tag0> <tag1>. "
			print " white <file> <tag0> <tag1> : i save the code in <file>."
			print " find <tag0> : i try find in my memory <tag0>."
			print " findAll <tag0> : i try find in my memory <tag0> and in my others lives too."
			print " copy <base> <tag0> : i copy <tag0> to <base>."			
			print " forget <tag0> : i forget <tag>... I think this."
			print " "
			print " <tag0> <tag1> -base=<base>: i execute the code what it have tags from <base>."
			print " <tag0> <tag1> -display=true: i execute the code using the program display."
			print " <tag0> <tag1> -program=<program>: i execute the code using other program."
			print " "
			print " bot blablabla.: i will speek with you."
						
			return True
			
		elif(command == 'read' and parameters!=None):

			localFile = None

			localFile = parameters[0:parameters.index(" ")]

			print "file : " + localFile

			_parameters = parameters[parameters.index(" ")+1:]

			print "tags : " + _parameters

			if(os.path.isfile(localFile) == True):
				self.myDb.InsertTagWithFile(_parameters, localFile)
				print "Hey your record is ok."

			return True
			
		elif(command == 'write' and parameters!=None):

			localFile = None

			localFile = parameters[0:parameters.index(" ")]

			print "file : " + localFile

			_command = parameters[parameters.index(" ")+1:]

			print "tags : " + _command

			_command = self.myDb.SelectCommandFromTag(_command)

			if(_command != None):

				fileTest = open(localFile,"wb")
				fileTest.write(_command)
				fileTest.close()
				
				print "Ok. File save in " + localFile

			else:
				print "Ops. I did not find commands in this tags."

			return True
			
		elif(command == 'copy' and parameters!=None):

			dbTarget = parameters[0:parameters.index(" ")]

			print "dbTarget : " + dbTarget

			_tags = parameters[parameters.index(" ")+1:]

			print "tags : " + _tags

			_command = self.myDb.SelectCommandFromTag(_tags)

			if(_command != None):

				fileTest = open(localFile,"wb")
				fileTest.write(_command)
				fileTest.close()
				
				if(os.path.isfile(localFile) == True):									
					if(dbTarget != None):
						dbParameters = MyDb.Parameters()
						dbParameters.db = dbParameters.path  + "\\" + dbTarget + ".db"
							
						self.myDb = MyDb(dbParameters)
						self.myDb.CheckDb()
						
						self.myDb.InsertTagWithFile(_tags, localFile)	
					
				if(os.path.isfile(localFile) == True):
				   os.remove(localFile)
				
				print "Ok. Save " + _tags + " in " + dbTarget		

			else:
				print "Ops. I did not find commands in this tags."

			return True
			
		elif(command == 'find'or command == 'list'):

			_command = self.myDb.SelectListTagsLike(parameters)

			if(len(_command)>0):
				print "Hey. I find : "
				for row in _command:
					print " " + row
			else:
				print "Hum... Sorry, this order didnt find in my memory."

			_dbChecked = False
			for _dbtarget in glob.glob(GetPathDB() + "\\*.db"):	
				_dbtarget = os.path.basename(_dbtarget)			
				_dbtarget = _dbtarget.replace('.db','')

				#hide other user #todo: create protection between user
				if(_dbtarget.find(GetHostname())>=0):
					#if(_dbtarget.find(GetUsername())<0):
					continue
				
				if(_dbtarget=='log'):
					continue
				
				if(_dbChecked == False):
					print(" ")
					print("See through my other lives too : -base=<name>") 
					_dbChecked = True
				
				print(" " + _dbtarget)				
					
			return True
			
		elif(command == 'findAll'or command == 'listAll'):
			
			_dbChecked = False
			for _dbtarget in glob.glob(GetPathDB() + "\\*.db"):	
				_dbtarget = os.path.basename(_dbtarget)			
				_dbtarget = _dbtarget.replace('.db','')

				#hide other user #todo: create protection between user
				if(_dbtarget.find(GetHostname())>=0):
					if(_dbtarget.find(GetUsername())<0):
						continue
				
				if(_dbtarget=='log'):
					continue

				dbParameters = MyDb.Parameters()
				dbParameters.db = dbParameters.path  + "\\" + _dbtarget + ".db"
					
				self.myDb = MyDb(dbParameters)
				_command = self.myDb.SelectListTagsLike(parameters)
				
				if(len(_command)>0):
					if(_dbChecked == False):
						print(" ")
						print "Hey. I find : "
						_dbChecked = True					
					
					for row in _command:
						print " " + row + " -base=" + _dbtarget				
					
			return True
			
		elif(command == 'delete'or command == 'forget'):

			_command = self.myDb.DeleteCommandFromTag(parameters)

			if(_command == True):
				print "Ok ok... I forgot that."
			else:
				print "Hum... Sorry, this order didnt find in my memory."
					
			return True			
			
		elif(command == 'save' or command == 'record' and parameters!=None and sys.platform == 'win32'):

			_command = self.myDb.SelectCommandFromTag(parameters)

			fileTest = open(localFile,"wb")
				
			if(_command == None):
				_command = "import time\n"
				_command = _command + "import sys,os\n"
				_command = _command + "import subprocess\n"
				_command = _command + "\n"
				_command = _command + "def Run(command, parameters=None):\n"
				_command = _command + "\tif(parameters != None):\n"
				_command = _command + "\t\tproc = subprocess.Popen([command, parameters], shell=True)\n"
				_command = _command + "\telse:\n"
				_command = _command + "\t\tproc = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)\n"
				_command = _command + "\n"
				_command = _command + "def RunJarvis(tags):\n"
				_command = _command + "\tpythonPath='C:\\Jarvis\\Python_Win\\App\\python.exe'\n"
				_command = _command + "\tjarvisPath='C:\\Jarvis\\Jarvis.py'\n"	
				_command = _command + "\tif sys.platform == 'linux2':\n"
				_command = _command + "\t\tpythonPath='python'\n"
				_command = _command + "\t\tjarvisPath='/var/jarvis/Jarvis.py'\n"
				_command = _command + "\tRun(pythonPath + ' ' + jarvisPath + ' ' + tags)\n"
				_command = _command + "\n"				
				_command = _command + "def OpenFolder(path):\n"
				_command = _command + "\tif sys.platform == 'win32':\n"
				_command = _command + "\t\tRun('explorer.exe', path)\n"				
				_command = _command + "\n"
				_command = _command + "def Main(): \n"
				_command = _command + "\tOpenFolder('C:\\Jarvis')\n"
				_command = _command + "\t#Run('Calc')\n"
				_command = _command + "\t#Run('C:\Program Files (x86)\Google\Chrome\Application\chrome.exe','-incognito www.google.com.br')\n"
				_command = _command + "\t#RunJarvis('calc')\n"
				_command = _command + "\t\n"
				_command = _command + "if __name__ == '__main__':\n"
				_command = _command + "\tMain()\n"
				_command = _command + "\t\n"
				_command = _command + "\tparam = ' '.join(sys.argv[1:])\n"
				_command = _command + "\tprint 'param ' + param\n"
				_command = _command + "\ttime.sleep(3)\n\n"

			fileTest.write(_command)
			fileTest.close()

			jv._Run(self.parameters.pyScripter + " " + localFile)

			self.myDb.InsertTagWithFile(parameters, localFile)
			print "Hey your record is ok."

			if(os.path.isfile(localFile) == True):
				os.remove(localFile)

			return True


		return False

def main(argv):
	if(len(argv)<=0):
		print "Hello! What could I do for you??"
		return False

	_jv = JarvisUtils()
	
	global LastCommand
	LastCommand =  ' '.join(argv)

	if(argv[0].find(GetBotNameForIntelligentResponse())>=0):

		msg = ' '.join(argv[1:])
		bot_response = _jv.AimlChat(msg)
		print bot_response

		argv = argv[1:]

		lastChar = ''
		if(len(msg)-1>=0):
			lastChar = msg[len(msg)-1]

		if(lastChar == '.' or lastChar == '!' or lastChar == '?'):
			return

	idTarget = []
	dbTarget = None
	displayCommand = False
	for idArg in range(0,len(argv)):
		if(argv[idArg].find('-base=') >= 0):
			idTarget.append(idArg)
			dbTarget = argv[idArg][argv[idArg].find('-base=')+len('-base='):]
			
		if(argv[idArg].find('-program=') >= 0):
			idTarget.append(idArg)
			global PyCommand
			PyCommand = argv[idArg][argv[idArg].find('-program=')+len('-program='):]			

		if(argv[idArg].find('-display=true') >= 0):
			idTarget.append(idArg)
			displayCommand = True

		if(argv[idArg].find('-user=') >= 0):
			idTarget.append(idArg)
			global LocalUsername
			LocalUsername = argv[idArg][argv[idArg].find('-user=')+len('-user='):]
			if(LocalUsername.find('@') >= 0):
				global LocalHostname
				LocalHostname = LocalUsername.split('@')[1]
				LocalUsername = LocalUsername.split('@')[0]

	for i in reversed(idTarget):
		argv.pop(i)
		
	command = ' '.join(argv)

	parameters = Commands.Parameters()

	if(displayCommand == True):
		parameters.pyCommand =  str(GetPyCommandDisplay())
		print "Set : " + str(GetPyCommandDisplay())

	dbParameters = MyDb.Parameters()
	if(dbTarget != None):
		dbParameters.db = dbParameters.path  + "\\" + dbTarget + ".db"

	db = MyDb(dbParameters)
	parameters.dbParameters = dbParameters

	obj = Commands(parameters)

	result = db.CheckDb()
	result = result and obj.DoCommand(command)

	if(result == False):
		print "Sorry, this order didnt find in my memory."

	return result

if __name__ == "__main__":
    main(sys.argv[1:])
