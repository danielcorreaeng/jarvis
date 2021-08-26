import os
import sqlite3
import os.path
import sys, os
import subprocess
import datetime
#import shutil, errno
import socket #,select
import time
import threading
import requests
import getpass
import json
import glob
#import getpass
from random import randint

if (sys.version_info > (3, 0)):
	from configparser import ConfigParser
else:
	import ConfigParser

#MIT License 2017 danielcorreaeng <danielcorrea.eng@gmail.com>

globalParameter = {}

globalParameter['PathLocal'] = os.path.dirname(os.path.abspath(__file__))
globalParameter['PathDB'] = globalParameter['PathLocal']  + "\\Db\\"
globalParameter['PathOutput'] = globalParameter['PathLocal']  + "\\Output\\"

globalParameter['PyCommand'] = "py"
globalParameter['PyScripter'] = "spyder3"

testPlatform = "linux" in str(sys.platform)
if testPlatform == True:
	#globalParameter['PathLocal'] = "/home/jarvis/workspace/jarvis"
	globalParameter['PathOutput'] = globalParameter['PathLocal'] + "/Output/"
	globalParameter['PathDB'] = globalParameter['PathLocal'] + "/Db/"
	globalParameter['PyCommand'] = "python"
	globalParameter['PyScripter'] = "notepadqq"

globalParameter['ExtensionFile'] = ".py"
globalParameter['BotNameForIntelligentResponse'] = "mybot"
globalParameter['BotIp'] = '127.0.0.1:8805'
globalParameter['LocalUsername'] = getpass.getuser().replace(' ','_')
globalParameter['LocalHostname'] = socket.gethostname().replace(' ','_')
globalParameter['LastCommand'] = ''
globalParameter['ProgramDisplayOut'] = False
globalParameter['LoggerIp'] = str(socket.gethostbyname(socket.gethostname())) +  ':8810'

globalParameter['RemoteCmdUpload'] = 'rmt upload'
globalParameter['RemoteCmdDownload'] = 'rmt download'

globalParameter['FileCommandModel'] = globalParameter['PathLocal']  + "\\model_command.py"
globalParameter['FileServiceModel'] = globalParameter['PathLocal']  + "\\model_service.py"


def GetLocalFile():
	globalParameter['LocalFile'] = datetime.datetime.now().strftime("%Y%m%d_%H%M%S%f") + "_" + str(randint(0, 999)) + globalParameter['ExtensionFile']
	return globalParameter['LocalFile']

class MyException(Exception):
    def __init__(self, value):
        self.parameter = value
    def __str__(self):
        return repr(self.parameter)

class MyDb():
	class Parameters():
		def __init__(self):
			self.path = globalParameter['PathDB']
			self.db = self.path  + globalParameter['LocalHostname'] + "_" + globalParameter['LocalUsername'] + ".db"
			self.changed = False
			self.dbName = globalParameter['LocalHostname'] + "_" + globalParameter['LocalUsername']
			pass

	def __init__(self, dbParameters):
		self.dbParameters = dbParameters

	def __del__(self):
		pass

	def CheckDb(self):
		result = False

		try:
			if os.path.exists (globalParameter['PathDB'])== False:
				os.mkdir (globalParameter['PathDB'])

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
			sql = "SELECT id,command FROM tag WHERE name='" + name + "'"
			cursor.execute(sql)

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

		try:
			db = self.dbParameters.db
			conn = sqlite3.connect(db)
			cursor = conn.cursor()

			if(name!=None):
				cursor.execute("SELECT name, command FROM tag WHERE name LIKE '%" + name + "%'")
			else:
				cursor.execute("SELECT name, command FROM tag")

			for row in cursor.fetchall():
				result.append([str(row[0]), row[1]])
				
			conn.close()
		except:
			#raise MyException("MyDb : SelectListTagsLike : Internal Error.")
			pass

		return result

	def DeleteCommandFromTag(self,name):
		result = True

		try:
			db = self.dbParameters.db
			conn = sqlite3.connect(db)
			cursor = conn.cursor()
			sql = "DELETE FROM tag WHERE name='" + name + "'"
			cursor.execute(sql)
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
			request = requests.get('http://' + globalParameter['LoggerIp'])

			if request.status_code == 200:
				print("Hey. Log is online, honey.")
				id = GetLocalFile().replace("_", "").replace(globalParameter['ExtensionFile'], "")

				data = []
				localTime = datetime.datetime.now().strftime("%Y%m%d_%H%M%S%f")
				data.append({'id' : id , 'user' : globalParameter['LocalUsername'] , 'host' : globalParameter['LocalHostname'] , 'command' : globalParameter['LastCommand'] , 'time' : localTime , 'status' : 'start'})

				url = "http://" + globalParameter['LoggerIp'] + "/log"
				headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
				requests.post(url, data=json.dumps(data), headers=headers)

				while (self.log):
					localTime = datetime.datetime.now().strftime("%Y%m%d_%H%M%S%f")
					#print(localTime)
					data[:] = []
					data.append({'id' : id , 'user' : globalParameter['LocalUsername'] , 'host' : globalParameter['LocalHostname'] , 'command' : globalParameter['LastCommand'] , 'time' : localTime , 'status' : 'alive'})
					requests.post(url, data=json.dumps(data), headers=headers)
					time.sleep(5.0)

				data[:] = []
				localTime = datetime.datetime.now().strftime("%Y%m%d_%H%M%S%f")
				data.append({'id' : id , 'user' : globalParameter['LocalUsername'] , 'host' : globalParameter['LocalHostname'] , 'command' : globalParameter['LastCommand'] , 'time' : localTime , 'status' : 'finish'})
				requests.post(url, data=json.dumps(data), headers=headers)
			else:
				pass
		except:
			pass

	def LogThread(self):
		threadLog = threading.Thread(target=self.LogFuction, args=())
		threadLog.start()

	def _Run(self,command, activeLog=True, waitReturn=True):
		result = None
		proc = None
		self.log = True
		
		if(activeLog==True):
			self.LogThread()

		try:
			if(waitReturn==True):
				proc = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
				(out, err) = proc.communicate()
				result = out
				if(len(out)>0 and globalParameter['ProgramDisplayOut']==True):
					print(out)                
			else:                
				proc = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
				#proc = subprocess.Popen(command)		
		except:
			pass

		self.log = False
		return result

	def ChatBot(self, message):
		error = 'Hi! Sorry... No service now =('
		result = error
		try:
			request = requests.get('http://' + globalParameter['BotIp'])
			if request.status_code == 200:
				localTime = datetime.datetime.now().strftime("%Y%m%d_%H%M%S%f")
				data = {'ask' : message , 'user' : globalParameter['LocalUsername'] , 'host' : globalParameter['LocalHostname'] , 'command' : globalParameter['LastCommand'] , 'time' : localTime , 'status' : 'start'}

				url = "http://" + globalParameter['BotIp'] + "/botresponse"
				headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
				r = requests.post(url, data=json.dumps(data), headers=headers)
				result = r.text
			else:
				result = error
		except:
			result = error
			pass

		return result
		
class Commands():
	class Parameters():
		def __init__(self):
			self.dbParameters = None
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

		commandfound = False
		remotedb = False
		localbaseTemp = None

		if(_command[0] == "remote"):
			print('Accessing remote db...')

			jarvisfile = __file__

			jv = JarvisUtils()
			localbaseTemp = globalParameter['PathOutput'] + GetLocalFile().replace(".py", ".db")
			_prog = globalParameter['PyCommand'] + " " + jarvisfile + " " + globalParameter['RemoteCmdDownload'] + " " + localbaseTemp + " " + self.parameters.dbParameters.dbName + ".db"
			out = jv._Run(_prog)
			
			_error_00 = str(out).find('Sorry')>=0 
			_error_01 = str(out).find('ERROR')>=0 
			_error_02 = os.path.isfile(localbaseTemp) == False

			if(_error_00):
				print("Sorry. I don't have remote resource. Please create <" + globalParameter['RemoteCmdDownload'] + "> and <" + globalParameter['RemoteCmdUpload'] + "> in my base.")
			elif(_error_01):
				print("Sorry. Remote file error.")				
			elif(_error_02):
				print("Sorry. I don't have this base in remote.")
			else:
				remotedb=True		
				self.parameters.dbParameters.db = localbaseTemp
				_command.pop(0)

				if(self._DoCommand(' '.join(_command)) == True):
					commandfound = True

			if commandfound == False:
				for i in range(len(_command)-1,0,-1):
					_localParameters = " ".join(_command[i:])
					_localCommand = " ".join(_command[0:i])

					if(self._DoCommand(_localCommand, _localParameters) == True):
						commandfound = True
						break
		
		if(remotedb == True):
			_prog = globalParameter['PyCommand'] + " " + jarvisfile + " " + globalParameter['RemoteCmdUpload'] + " " + localbaseTemp + " " + self.parameters.dbParameters.dbName + ".db"
			out = jv._Run(_prog)			

			try:
				if(os.path.isfile(localbaseTemp) == True):
					os.remove(localbaseTemp)
			except:
				pass


		return commandfound

	def _DoCommand(self, command, parameters=None):

		if os.path.exists (globalParameter['PathOutput'])== False:
			os.mkdir (globalParameter['PathOutput'])

		jv = JarvisUtils()

		localFile = globalParameter['PathOutput'] + GetLocalFile()

		_command = self.myDb.SelectCommandFromTag(command)

		if(_command != None):

			fileTest = open(localFile,"wb")
			fileTest.write(_command)
			fileTest.close()

			_prog = globalParameter['PyCommand'] + " " + localFile

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
			print(" list <tag0> : i try find in my memory <tag0>.")
			print(" find <tag0> : i try find in my memory <tag0> and describes.")
			print(" copy <base> <tag0> : i copy <tag0> to <base>.")
			print(" forget <tag0> : i forget <tag>... I think this.")
			print(" ")
			print(" <tag0> <tag1> -base=<base> : i execute the code what it have tags from <base>.")
			print(" <tag0> <tag1> -display=true : i execute the code using the program display.")
			print(" <tag0> <tag1> -program=<program> : i execute the code using other program.")
			print(" ")
			print(" mybot blablabla. : i will speek with you.")

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

		elif(command == 'find' or command == 'list'or command == 'route'):

			_dbChecked = False
			for _dbtarget in glob.glob(globalParameter['PathDB'] + "\\*.db"):
				
				if(self.myDb.dbParameters.changed == False):										
					dbParameters = MyDb.Parameters()
					dbParameters.db = _dbtarget
					self.myDb = MyDb(dbParameters)

				_dbtarget = os.path.basename(self.myDb.dbParameters.db)
				_dbtarget = _dbtarget.replace('.db','')		
					
				#hide other user #todo: create protection between user
				if(_dbtarget.find(globalParameter['LocalHostname'])>=0):
					if(_dbtarget.find(globalParameter['LocalUsername'])<0):
						continue

				if(_dbtarget=='log'):
					continue
				
				if(_dbtarget=='bkp' and self.myDb.dbParameters.changed == False):
					continue

				rows  = self.myDb.SelectListTagsLike(parameters)

				if(len(rows)>0):
					if(_dbChecked == False):
						print("Hey. I find : ")
						_dbChecked = True
					
					print("\n base=" + _dbtarget + "\n")

					for row in rows:
						_name, _command = row
						describe = ''
						route = ''					

						if(command == 'find' or command == 'route'):	

							test_help_000 = str(_command).find("print(Main.__doc__)") >= 0
							test_help_001 = str(_command).find("if(len(sys.argv) > 1)") >= 0
							test_help_002 = str(_command).find("parser.add_argument") >= 0

							#print(test_help_000)
							#print(test_help_001)
							#print(test_help_002)

							if(test_help_000>=0 and (test_help_001 or test_help_002)):
								fileTest = open(localFile,"wb")
								fileTest.write(_command)
								fileTest.close()
								
								targetText = 'RunJarvis('								
								if(command == 'route' and str(_command).find(targetText)>=0):
									fileTest = open(localFile, "r")
									for line in fileTest:
										if(line.find('def ' + targetText)>=0):
											continue										

										if(line.find(targetText)>=0):
											start = line.find(targetText)
											stop = line.find(')')
											#print(line[start+len(targetText):stop])
											route = route + '\troute:: ' + line[start+len(targetText):-2]  + '\n'
									fileTest.close()	

								_prog = globalParameter['PyCommand'] + " " + localFile

								if(parameters!=None):
									_prog = _prog + " " + parameters

								out = ""
								if(test_help_002 == True):
									out = jv._Run(_prog + ' -d', False)
								elif(test_help_001 == True):									
									out = jv._Run(_prog + ' -h', False)

								if(os.path.isfile(localFile) == True):
								   os.remove(localFile)
								   pass
								
								describe = ""

								if(out != ""):
									describe = '-->' + str(str(str(out).split('\\n')[0]).replace('\n','').replace('\\r','').replace("b'",''))

								if(command == 'route'):
									describe = '\n\tdescribe:: ' + describe.replace('-->','')
									if(route != ''):
										describe = describe + '\n ' + route[0:-1]

						if(globalParameter['LocalHostname'] + "_" + globalParameter['LocalUsername'] == _dbtarget):
							print(" " + _name+ " " + describe)
						else:
							print(" " + _name + " -base=" + _dbtarget + " " + describe)
						if(command == 'route'):
							print("=======================================")						

				if(self.myDb.dbParameters.changed == True):
					break

			if(_dbChecked == False):
				print("Hum... Sorry, this order didnt find in my memory.")


			return True

		elif(command == 'execute all' and False):
			"""Not implemented"""
			"""
			rows  = self.myDb.SelectListTagsLike(parameters)

			if(len(rows)>0):
				filelist = []
                                
				for row in rows:
					_name, _command = row
					
					localFile = globalParameter['PathOutput']  + GetLocalFile()
                    
					fileTest = open(localFile,"wb")
					fileTest.write(_command)
					fileTest.close()

					_prog = globalParameter['PyCommand'] + " " + localFile

					out = jv._Run(_prog, False, False)
                    
					filelist.append(localFile)

					print(" " + _name)
                    
					time.sleep(1)

				for _file in filelist:
					if(os.path.isfile(_file) == True):
					   os.remove(_file)
					   pass
            """
			return True

		elif(command == 'delete'or command == 'forget'):

			_command = self.myDb.DeleteCommandFromTag(parameters)

			if(_command == True):
				print("Ok ok... I forgot that.")
			else:
				print("Hum... Sorry, this order didnt find in my memory.")

			return True
						
		elif(command == 'save' or command == 'record' or command == 'record service' and parameters!=None and sys.platform == 'win32'):

			_command = self.myDb.SelectCommandFromTag(parameters)

			fileTest = None

			if(_command == None):

				fileTest = open(localFile,"w")

				_command = self.MakeCommandExemple()

				if(command == 'record service'):
					if os.path.exists(globalParameter['FileServiceModel']) == True:
						_command = self.LoadFile(globalParameter['FileServiceModel'])
				elif os.path.exists(globalParameter['FileCommandModel']) == True:
					_command = self.LoadFile(globalParameter['FileCommandModel'])
				fileTest.write(_command)
				fileTest.close()

			else:
				fileTest = open(localFile,"wb")
				fileTest.write(_command)
				fileTest.close()

				#save bkp
				if(os.path.isfile(localFile) == True):
					dbParameters = MyDb.Parameters()
					dbParameters.db = dbParameters.path  + "\\bkp.db"

					bkpDb = MyDb(dbParameters)
					bkpDb.CheckDb()

					bkpParameters = parameters + " " + datetime.datetime.now().strftime("%Y%m%d_%H%M%S%f") + "_" + str(randint(0, 999))
					bkpDb.InsertTagWithFile(bkpParameters, localFile)

					print("Backup saved in tag '" + bkpParameters + "' in base 'bkp'")

			jv._Run(globalParameter['PyScripter'] + " " + localFile)

			self.myDb.InsertTagWithFile(parameters, localFile)
			print("Hey your record is ok.")

			if(os.path.isfile(localFile) == True):
				os.remove(localFile)

			return True		

		return False
	
	def MakeCommandExemple(self):
		_command = None
		
		if(globalParameter['ExtensionFile'] == ".ipynb"):
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
			_command = _command + "\t\tproc = subprocess.Popen(command, shell=True)\n"
			_command = _command + "\n"
			_command = _command + "def OpenFolder(path):\n"
			_command = _command + "\tif sys.platform == 'win32':\n"
			_command = _command + "\t\tRun('explorer.exe', path)\n"
			_command = _command + "\n"
			_command = _command + "def Main(): \n"
			_command = _command + "\t'''No describe'''\n"	
			_command = _command + "\tOpenFolder(r'C:\Windows')\n"
			_command = _command + "\t#Run(r'Calc')\n"
			_command = _command + "\t#Run(r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe','-incognito www.google.com.br')\n"
			_command = _command + "\t\n"
			_command = _command + "if __name__ == '__main__':\n"
			_command = _command + "\tif(len(sys.argv) > 1):\n"
			_command = _command + "\t\tif(sys.argv[len(sys.argv)-1] == '-h' or sys.argv[len(sys.argv)-1] == 'help'):\n"
			_command = _command + "\t\t\tprint(Main.__doc__)\n"
			_command = _command + "\t\t\tsys.exit()\n"
			_command = _command + "\tMain()\n"
			_command = _command + "\t\n"
			_command = _command + "\tparam = ' '.join(sys.argv[1:])\n"
			_command = _command + "\tprint('param ' + param)\n"
			
		return _command

	def LoadFile(self,pathFile):
		_command = ""
		with open(pathFile) as f:
			_command =  f.read()

		return _command

def main(argv):
	if(len(argv)<=0):
		print("Hello! What could I do for you??")
		return False

	_jv = JarvisUtils()

	globalParameter['LastCommand'] =  ' '.join(argv)

	if(argv[0].find(globalParameter['BotNameForIntelligentResponse'])>=0):

		msg = ' '.join(argv[1:])
		bot_response = _jv.ChatBot(msg)
		print(bot_response)

		argv = argv[1:]
		return

	idTarget = []
	dbTarget = None
	
	fileConfiName = globalParameter['PathLocal'] + "\\config.ini"
	if(os.path.isfile(fileConfiName)):

		if (sys.version_info > (3, 0)):
			fileConfig = ConfigParser()
		else:
			fileConfig = ConfigParser.RawConfigParser()
			pass

		fileConfig.read([fileConfiName])
		itens = fileConfig.items('Parameters')

		for item in itens:
			itemFound=False
			for globalParameter_key in globalParameter:    
				if globalParameter_key.lower()==item[0].lower():
					globalParameter[globalParameter_key]=item[1]
					itemFound=True
			if itemFound == False:
				#stringItem = "-" + str(item[0]) + "=" + str(item[1])
				#argv.insert( 1, stringItem)
				pass

	for globalParameter_key in globalParameter:    
		stringArg = '-' + globalParameter_key.lower() + '='
		for idArg in range(0,len(argv)):
			if(argv[idArg].find(stringArg) >= 0):
				idTarget.append(idArg)
				globalParameter[globalParameter_key] = argv[idArg][argv[idArg].find(stringArg)+len(stringArg):]

	for idArg in range(0,len(argv)):
		stringArg = '-base='
		if(argv[idArg].find(stringArg) >= 0):
			idTarget.append(idArg)
			dbTarget = argv[idArg][argv[idArg].find(stringArg)+len(stringArg):]
			
		stringArg = '-program='
		if(argv[idArg].find(stringArg) >= 0):
			idTarget.append(idArg)
			globalParameter['PyCommand'] = argv[idArg][argv[idArg].find(stringArg)+len(stringArg):]
			globalParameter['PyScripter'] = globalParameter['PyCommand']			
			if(globalParameter['PyCommand'] == 'jupyter'):
				globalParameter['PyCommand'] = 'jupyter notebook'
				globalParameter['ExtensionFile'] = ".ipynb"
				globalParameter['PyScripter'] = globalParameter['PyCommand']
			elif(globalParameter['PyCommand'] == 'spyder3'):
				globalParameter['PyCommand'] = 'py'
				globalParameter['PyScripter'] = 'spyder3'

			print('pyCommand : ' + globalParameter['PyCommand'])
			
		stringArg = '-extension='
		if(argv[idArg].find(stringArg) >= 0):
			idTarget.append(idArg)
			globalParameter['ExtensionFile']= argv[idArg][argv[idArg].find(stringArg)+len(stringArg):]

		stringArg = '-display=true'
		if(argv[idArg].find(stringArg) >= 0):
			idTarget.append(idArg)
			globalParameter['ProgramDisplayOut'] = True
			print("display : true")			

		stringArg = '-user='
		if(argv[idArg].find(stringArg) >= 0):
			idTarget.append(idArg)			
			globalParameter['LocalUsername'] = argv[idArg][argv[idArg].find(stringArg)+len(stringArg):]
			if(globalParameter['LocalUsername'].find('@') >= 0):				
				globalParameter['LocalHostname'] = globalParameter['LocalUsername'].split('@')[1]
				globalParameter['LocalUsername'] = globalParameter['LocalUsername'].split('@')[0]

	for i in reversed(idTarget):
		argv.pop(i)

	command = ' '.join(argv)

	parameters = Commands.Parameters()

	dbParameters = MyDb.Parameters()
	if(dbTarget != None):
		dbParameters.db = dbParameters.path  + "\\" + dbTarget + ".db"
		dbParameters.dbName = dbTarget
		dbParameters.changed = True

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
