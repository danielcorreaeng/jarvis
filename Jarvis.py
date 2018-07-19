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
import requests
import getpass
import json
import glob
import paramiko
import getpass
from random import randint
from unicodedata import normalize

if (sys.version_info > (3, 0)):
	from configparser import ConfigParser
else:
	import ConfigParser

#MIT License 2017 danielcorreaeng <danielcorrea.eng@gmail.com>

if sys.platform == 'win32':
	PathLocal = "C:\\Jarvis"
	PathDB = PathLocal + "\\Db\\"
	PathOutput = PathLocal + "\\Output\\"

	PyCommandDisplay = PathLocal + "\\Python_Win\\Python-Portable.exe"
	#PyCommandDisplay = "py"

	PyCommand = PathLocal + "\\Python_Win\\App\\python.exe"
	#PyCommand = "py"

	PyScripter = PathLocal + "\\Python_Win\\PyScripter-Portable.exe"
	#PyScripter = "spyder3"

	PathBot = PathLocal + "\\Aiml\\"
elif sys.platform == 'linux2':
	PathLocal = "/home/jarvis/workspace/jarvis"
	PathOutput = PathLocal + "/Output/"
	PathDB = PathLocal + "/Db/"
	PyCommandDisplay = "python"
	PyCommand = "python"
	PyScripter = "notepadqq"
	PathBot = PathLocal + "/Aiml/"

ExtensionFile = ".py"
BotNameForIntelligentResponse = "bot"
LocalUsername = getpass.getuser().replace(' ','_')
LocalHostname = socket.gethostname().replace(' ','_')
LastCommand = ''
LoggerIp = '127.0.0.1:8800'

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

def GetExtensionFile():
	return ExtensionFile

def GetLocalFile():
	LocalFile = datetime.datetime.now().strftime("%Y%m%d_%H%M%S%f") + "_" + str(randint(0, 999)) + GetExtensionFile()
	return LocalFile

def GetLoggerIp():
	return LoggerIp
	
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

			for row in cursor.fetchall():
				result.append(str(row[0]))

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
			request = requests.get('http://' + GetLoggerIp())

			if request.status_code == 200:
				print("Hey. Log is online, honey.")
				id = GetLocalFile().replace("_", "").replace(GetExtensionFile(), "")

				data = []
				localTime = datetime.datetime.now().strftime("%Y%m%d_%H%M%S%f")
				data.append({'id' : id , 'user' : GetUsername() , 'host' : GetHostname() , 'command' : GetLastCommand() , 'time' : localTime , 'status' : 'start'})

				url = "http://" + GetLoggerIp() + "/log"
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
			#print("[input] : ") + message #debug
			bot_response = self._aiml.respond(message,sessionId)
			result = bot_response

		return result

class JarvisSSH():
	class Parameters():
		def __init__(self):
			self.remotePath = '/home/jarvis/workspace/jarvis/'
			self.remoteProgram = 'python'
			self.hostname = '192.168.1.100'
			self.port = 22
			self.username = 'jarvis'
			self.password = None
			pass

	def __init__(self, parameters):
		self.parameters = JarvisSSH.Parameters()
		self.parameters = parameters

	def CheckPassword(self):
		if(self.parameters.password == None):
			#self.parameters.password = str(raw_input("password : "))
			self.parameters.password = getpass.getpass()

	def GetRemoteCommand(self, tags):
		self.CheckPassword()
		dest = GetPathOutput() + GetLocalFile()
		source = self.parameters.remotePath + GetLocalFile()

		client = paramiko.SSHClient()
		client.load_system_host_keys()
		client.set_missing_host_key_policy(paramiko.client.AutoAddPolicy())

		client.connect(self.parameters.hostname, self.parameters.port, username=self.parameters.username, password=str(self.parameters.password))

		channel = client.invoke_shell()
		stdin = channel.makefile('wb')
		stdout = channel.makefile('rb')

		stdin.write('''
		cd ''' + self.parameters.remotePath + '''
		''' + self.parameters.remoteProgram + ''' Jarvis.py write ''' + source + ''' ''' + tags + '''
		exit
		''')

		st_out = stdout.read()
		#print(st_out)
		st_out = str(st_out)
		if st_out.find('File save') != -1:
			print('remote : ok')
		elif st_out.find('not find') != -1:
			print('remote : it did not find')		
			return None			
		else:
			print('remote : error')
			return None

		stdout.close()
		stdin.close()

		sftp = client.open_sftp()
		sftp.get(source, dest)
		sftp.remove(source)
	
		client.close()
		
		localFile = dest
		return localFile
				
	def PutRemoteCommand(self, tags, fileName):
		self.CheckPassword()
		destFileName = GetLocalFile()
		dest = self.parameters.remotePath + destFileName
		
		client = paramiko.SSHClient()
		client.load_system_host_keys()
		client.set_missing_host_key_policy(paramiko.client.AutoAddPolicy())

		client.connect(self.parameters.hostname, self.parameters.port, username=self.parameters.username, password=str(self.parameters.password))
	
		sftp = client.open_sftp()
		sftp.put(fileName, dest)		
		
		channel = client.invoke_shell()
		stdin = channel.makefile('wb')
		stdout = channel.makefile('rb')

		stdin.write('''
		cd ''' + self.parameters.remotePath + '''
		''' + self.parameters.remoteProgram + ''' Jarvis.py read ''' + destFileName + ''' ''' + tags + '''
		rm ''' + destFileName + '''
		exit
		''')

		st_out = stdout.read()
		#print(st_out)
		st_out = str(st_out)		
		if st_out.find('record is ok') != -1:
			print('remote : record ok')
		else:
			print('remote : error')

		stdout.close()
		stdin.close()		
		client.close()
		
class Commands():
	class Parameters():
		def __init__(self):
			self.LoadVars()

			self.dbParameters = None
			self.path = GetPathLocal()
			self.pathOutput = GetPathOutput()
			self.pyCommand = GetPyCommand()
			self.pyScripter = GetPyScripter()
			self.sshParameters = JarvisSSH.Parameters()
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
			print("Hum... Let me try : ")
			print(" <tag0> <tag1> : i execute the code what it have <tag0> <tag1>.")

			print(" record <tag0> <tag1> : i try open editor code and i will record it with tags.")
			print(" read <file> <tag0> <tag1> : give me a file and i record with <tag0> <tag1>. ")
			print(" write <file> <tag0> <tag1> : i save the code in <file>.")
			print(" find <tag0> : i try find in my memory <tag0>.")
			print(" findAll <tag0> : i try find in my memory <tag0> and in my others lives too.")
			print(" copy <base> <tag0> : i copy <tag0> to <base>.")
			print(" forget <tag0> : i forget <tag>... I think this.")
			print(" ")
			print(" <tag0> <tag1> -base=<base> : i execute the code what it have tags from <base>.")
			print(" <tag0> <tag1> -display=true : i execute the code using the program display.")
			print(" <tag0> <tag1> -program=<program> : i execute the code using other program.")
			print(" ")
			print(" bot blablabla. : i will speek with you.")

			return True

		elif(command == 'read' and parameters!=None):

			localFile = None

			localFile = parameters[0:parameters.index(" ")]

			print("file : " + localFile)

			_parameters = parameters[parameters.index(" ")+1:]

			print("tags : " + _parameters)

			if(os.path.isfile(localFile) == True):
				self.myDb.InsertTagWithFile(_parameters, localFile)
				print("Hey your record is ok.")

			return True

		elif(command == 'write' and parameters!=None):

			localFile = None

			localFile = parameters[0:parameters.index(" ")]

			print("file : " + localFile)

			_command = parameters[parameters.index(" ")+1:]

			print("tags : " + _command)

			_command = self.myDb.SelectCommandFromTag(_command)

			if(_command != None):

				fileTest = open(localFile,"wb")
				fileTest.write(_command)
				fileTest.close()

				print("Ok. File save in " + localFile)

			else:
				print("Ops. I did not find commands in this tags.")

			return True

		elif(command == 'copy' and parameters!=None):

			dbTarget = parameters[0:parameters.index(" ")]

			print("dbTarget : " + dbTarget)

			_tags = parameters[parameters.index(" ")+1:]

			print("tags : " + _tags)

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

				print("Ok. Save " + _tags + " in " + dbTarget)

			else:
				print("Ops. I did not find commands in this tags.")

			return True

		elif(command == 'find'or command == 'list'):

			_command = self.myDb.SelectListTagsLike(parameters)

			if(len(_command)>0):
				print("Hey. I find : ")
				for row in _command:
					print(" " + row)
			else:
				print("Hum... Sorry, this order didnt find in my memory.")

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
						print("Hey. I find : ")
						_dbChecked = True

					for row in _command:
						print(" " + row + " -base=" + _dbtarget)

			return True

		elif(command == 'delete'or command == 'forget'):

			_command = self.myDb.DeleteCommandFromTag(parameters)

			if(_command == True):
				print("Ok ok... I forgot that.")
			else:
				print("Hum... Sorry, this order didnt find in my memory.")

			return True
			
		elif(command == 'remote'):
			
			ssh = JarvisSSH(self.parameters.sshParameters)			
			localFile = ssh.GetRemoteCommand(parameters)
			
			if(localFile == None):
				return True
			
			_prog = self.parameters.pyCommand + " " + localFile

			jv._Run(_prog)

			if(os.path.isfile(localFile) == True):
			   os.remove(localFile)

			return True

		elif(command == 'remote get'):

			print("tags : " + parameters)
			
			ssh = JarvisSSH(self.parameters.sshParameters)			
			localFile = ssh.GetRemoteCommand(parameters)
			
			if(localFile == None):
				return True
			
			self.myDb.InsertTagWithFile(parameters, localFile)
			print("Hey your record is ok.")

			if(os.path.isfile(localFile) == True):
			   os.remove(localFile)

			return True
			
		elif(command == 'remote send'):
		
			localFile = GetPathOutput() + GetLocalFile()

			print("file : " + localFile)
			print("tags : " + parameters)

			_command = self.myDb.SelectCommandFromTag(parameters)

			if(_command == None):
				print("Ops. I did not find commands in this tags.")
				return True
				
			fileTest = open(localFile,"wb")
			fileTest.write(_command)
			fileTest.close()

			#print("temp file : " + localFile)
			
			ssh = JarvisSSH(self.parameters.sshParameters)			
			ssh.PutRemoteCommand(parameters, localFile)
			
			if(os.path.isfile(localFile) == True):
			   os.remove(localFile)						
				
			return True		
			
		elif(command == 'remote save' or command == 'remote record' and parameters!=None and sys.platform == 'win32'):

			print("tags : " + parameters)
			
			ssh = JarvisSSH(self.parameters.sshParameters)			
			localFile = ssh.GetRemoteCommand(parameters)
			
			fileTest = None

			if(localFile == None):
				localFile = GetLocalFile()
				fileTest = open(localFile,"w")
				_command = self.MakeCommandExemple()
				fileTest.write(_command)
				fileTest.close()				

			jv._Run(self.parameters.pyScripter + " " + localFile)

			ssh = JarvisSSH(self.parameters.sshParameters)			
			ssh.PutRemoteCommand(parameters, localFile)			
			
			#self.myDb.InsertTagWithFile(parameters, localFile)
			#print("Hey your local record is ok too.")

			if(os.path.isfile(localFile) == True):
				os.remove(localFile)

			return True			
						
		elif(command == 'save' or command == 'record' and parameters!=None and sys.platform == 'win32'):

			_command = self.myDb.SelectCommandFromTag(parameters)

			fileTest = None

			if(_command == None):

				fileTest = open(localFile,"w")
				_command = self.MakeCommandExemple()
			else:
				fileTest = open(localFile,"wb")

			fileTest.write(_command)
			fileTest.close()

			jv._Run(self.parameters.pyScripter + " " + localFile)

			self.myDb.InsertTagWithFile(parameters, localFile)
			print("Hey your record is ok.")

			if(os.path.isfile(localFile) == True):
				os.remove(localFile)

			return True
			
		elif(command == 'save' or command == 'record' and parameters!=None and sys.platform == 'win32'):

			_command = self.myDb.SelectCommandFromTag(parameters)

			fileTest = None

			if(_command == None):

				fileTest = open(localFile,"w")
				_command = self.MakeCommandExemple()
			else:
				fileTest = open(localFile,"wb")

			fileTest.write(_command)
			fileTest.close()

			jv._Run(self.parameters.pyScripter + " " + localFile)

			self.myDb.InsertTagWithFile(parameters, localFile)
			print("Hey your record is ok.")

			if(os.path.isfile(localFile) == True):
				os.remove(localFile)

			return True


		return False
	
	def MakeCommandExemple(self):
		_command = None
		
		if(GetExtensionFile() == ".ipynb"):
			_command = '{\n "cells": [\n  {\n   "cell_type": "code",\n   "execution_count": null,\n   "metadata": {},\n   "outputs": [],\n   "source": []\n  }\n ],\n "metadata": {\n  "kernelspec": {\n   "display_name": "Python 3",\n   "language": "python",\n   "name": "python3"\n  },\n  "language_info": {\n   "codemirror_mode": {\n    "name": "ipython",\n    "version": 3\n   },\n   "file_extension": ".py",\n   "mimetype": "text/x-python",\n   "name": "python",\n   "nbconvert_exporter": "python",\n   "pygments_lexer": "ipython3",\n   "version": "3.6.5"\n  }\n },\n "nbformat": 4,\n "nbformat_minor": 2\n}\n'
		else:
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
			_command = _command + "\tprint('param ' + param)\n"
			_command = _command + "\ttime.sleep(3)\n\n"		
			
		return _command
def main(argv):
	if(len(argv)<=0):
		print("Hello! What could I do for you??")
		return False

	_jv = JarvisUtils()

	global LastCommand
	LastCommand =  ' '.join(argv)

	if(argv[0].find(GetBotNameForIntelligentResponse())>=0):

		msg = ' '.join(argv[1:])
		bot_response = _jv.AimlChat(msg)
		print(bot_response)

		argv = argv[1:]

		lastChar = ''
		if(len(msg)-1>=0):
			lastChar = msg[len(msg)-1]

		if(lastChar == '.' or lastChar == '!' or lastChar == '?'):
			return

	idTarget = []
	dbTarget = None
	displayCommand = False
	jarvisSSHParameters = JarvisSSH.Parameters()
	
	global ExtensionFile
	global PyCommand
	global PyScripter

	fileConfiName = GetPathLocal() + "\\config.ini"
	if(os.path.isfile(fileConfiName)):

		if (sys.version_info > (3, 0)):
			fileConfig = ConfigParser()
		else:
			fileConfig = ConfigParser.RawConfigParser()

		fileConfig.read([fileConfiName])
		itens = fileConfig.items('Parameters')

		for item in itens:
			stringItem = "-" + str(item[0]) + "=" + str(item[1])
			#print(stringItem)
			argv.insert( 1, stringItem)

	for idArg in range(0,len(argv)):
		stringArg = '-base='
		if(argv[idArg].find(stringArg) >= 0):
			idTarget.append(idArg)
			dbTarget = argv[idArg][argv[idArg].find(stringArg)+len(stringArg):]
			
		stringArg = '-program='
		if(argv[idArg].find(stringArg) >= 0):
			idTarget.append(idArg)
			PyCommand = argv[idArg][argv[idArg].find(stringArg)+len(stringArg):]
			if(PyCommand == 'jupyter'):
				PyCommand = 'jupyter notebook'
				ExtensionFile = ".ipynb"
				PyScripter = PyCommand
			elif(PyCommand == 'spyder3'):
				PyCommand = 'py'
				PyScripter = 'spyder3'
			else:
				PyScripter = PyCommand
			
		stringArg = '-extension='
		if(argv[idArg].find(stringArg) >= 0):
			idTarget.append(idArg)
			ExtensionFile = argv[idArg][argv[idArg].find(stringArg)+len(stringArg):]

		stringArg = '-display=true'
		if(argv[idArg].find(stringArg) >= 0):
			idTarget.append(idArg)
			displayCommand = True

		stringArg = '-remotehostname='
		if(argv[idArg].find(stringArg) >= 0):
			idTarget.append(idArg)
			jarvisSSHParameters.hostname = argv[idArg][argv[idArg].find(stringArg)+len(stringArg):]

		stringArg = '-remoteport='
		if(argv[idArg].find(stringArg) >= 0):
			idTarget.append(idArg)
			jarvisSSHParameters.port = argv[idArg][argv[idArg].find(stringArg)+len(stringArg):]

		stringArg = '-remoteusername='
		if(argv[idArg].find(stringArg) >= 0):
			idTarget.append(idArg)
			jarvisSSHParameters.username = argv[idArg][argv[idArg].find(stringArg)+len(stringArg):]

		stringArg = '-remotepassword='
		if(argv[idArg].find(stringArg) >= 0):
			idTarget.append(idArg)
			jarvisSSHParameters.password = argv[idArg][argv[idArg].find(stringArg)+len(stringArg):]

		stringArg = '-user='
		if(argv[idArg].find(stringArg) >= 0):
			idTarget.append(idArg)
			global LocalUsername
			LocalUsername = argv[idArg][argv[idArg].find(stringArg)+len(stringArg):]
			if(LocalUsername.find('@') >= 0):
				global LocalHostname
				LocalHostname = LocalUsername.split('@')[1]
				LocalUsername = LocalUsername.split('@')[0]

	for i in reversed(idTarget):
		argv.pop(i)

	command = ' '.join(argv)

	parameters = Commands.Parameters()
	parameters.sshParameters = jarvisSSHParameters

	if(displayCommand == True):
		parameters.pyCommand =  str(GetPyCommandDisplay())
		print("Set : " + str(GetPyCommandDisplay()))

	dbParameters = MyDb.Parameters()
	if(dbTarget != None):
		dbParameters.db = dbParameters.path  + "\\" + dbTarget + ".db"

	db = MyDb(dbParameters)
	parameters.dbParameters = dbParameters

	obj = Commands(parameters)

	result = db.CheckDb()
	result = result and obj.DoCommand(command)

	if(result == False):
		print("Sorry, this order didnt find in my memory.")

	return result

if __name__ == "__main__":
    main(sys.argv[1:])
