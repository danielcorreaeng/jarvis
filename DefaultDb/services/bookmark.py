import time
import json
import sys,os
import subprocess
import argparse
import datetime
from random import randint
import os.path
import requests
import json
import configparser

from jarvis_utils import *

globalParameter['INPUT_DATA_OFF'] = True
globalParameter['OUTPUT_DATA_OFF'] = True
globalParameter['MAINLOOP_CONTROLLER'] = False
globalParameter['MAINWEBSERVER'] = False
globalParameter['PROCESS_JARVIS'] = None
globalParameter['ChromeTarget'] = "C:\Program Files\Google\Chrome\Application\chrome.exe"
globalParameter['TimeRecordFile'] = 3

def MakeCommandExemple():
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
	_command = _command + "def Main(): \n"
	_command = _command + "\t'''This opens pages related to tags.'''\n"	
	_command = _command + "\t\n"
	_command = _command + "if __name__ == '__main__':\n"
	_command = _command + "\tif(len(sys.argv) > 1):\n"
	_command = _command + "\t\tif(sys.argv[len(sys.argv)-1] == '-h' or sys.argv[len(sys.argv)-1] == 'help'):\n"
	_command = _command + "\t\t\tprint(Main.__doc__)\n"
	_command = _command + "\t\t\tsys.exit()\n"
	_command = _command + "\t\n"
		
	return _command

def GetLocalFileWithoutExtension():
    localFile = os.path.join(globalParameter['PathOutput'], datetime.datetime.now().strftime("%Y%m%d_%H%M%S%f") + "_" + str(randint(0, 999)) + "_temp")
    return localFile

def GetLocalFile():
    localFile = GetLocalFileWithoutExtension() + ".py"
    return localFile

def Main(): 
    '''Create tag that open page with link or save file from link. Parameters : <base> <tag 0> <tag1> ... <link>'''
    pass
	
if __name__ == '__main__':
    #os.chdir(os.path.dirname(__file__))

    parser = argparse.ArgumentParser(description=Main.__doc__)
    parser.add_argument('-d','--description', help='Description of program', action='store_true')
    parser.add_argument('-u','--unique', help='Make id unique for tag', action='store_true')
    parser.add_argument('-l','--jsonlink', help='Create a json file with the inserted link', action='store_true')
    parser.add_argument('-n','--jsonnote', help='Create a json file with the inserted note', action='store_true')
    parser.add_argument('-f','--keepfile', help='Create a file without database (base = folder, tag = name)', action='store_true')    
    
    args, unknown = parser.parse_known_args()
    args = vars(args)
    
    if args['description'] == True:
        print(Main.__doc__)
        sys.exit()     

    GetCorrectPath()  

    id_unique = False
    if args['unique'] == True:
        id_unique = True   

    if(len(unknown) < 3):
        print('Sorry, y need more arguments. Use -d for description.')
        sys.exit()   
        
    base = unknown[0]
    tags = unknown[1:-1]
    link = unknown[-1]

    tags = ' '.join(tags)
    if(id_unique == True):
        tags = tags + " " + str(datetime.datetime.now().strftime("%Y%m%d")) + " " + str(datetime.datetime.now().strftime("%H%M%S%f"))  + " " + str(randint(0, 999))
    
    file = GetLocalFile()
    extension = os.path.splitext(link)[1]

    if((args['jsonlink'] == False and args['keepfile'] == False and args['jsonnote'] == False) and (extension == '.jpg' or extension == '.jpeg' or extension == '.png' or extension == '.json' or extension == '.doc' or extension == '.docx' or extension == '.pdf' or extension == '.xls' or extension == '.xlsx')):
        file = GetLocalFileWithoutExtension() + extension
        f = open(file,'wb')
        response = requests.get(link)
        f.write(response.content)
        f.close()
        time.sleep(globalParameter['TimeRecordFile'])
        cmd = 'read ' + file + ' ' + tags + ' ' + '-base=' + base
        RunJarvis(cmd)  
    elif(args['keepfile'] == True):

        localpath = os.path.join(globalParameter['PathOutput'], base)

        if(os.path.exists(localpath) == False):
            os.mkdir(localpath)

        file = os.path.join(localpath, tags + extension)
        f = open(file,'wb')
        response = requests.get(link)
        f.write(response.content)
        f.close()
    else:   
        jarvislink = True

        if args['jsonlink'] == True or args['jsonnote'] == True:
            file = file + '.json'

            data = { 'link' :  link }
            if args['jsonnote'] == True:
                link = link.replace("_", " ")
                data = { 'note' :  link }
                
            f = open(file,'w')
            json.dump(data, f, ensure_ascii=False, indent=4)
            f.close()
            
        else:
            cmd = 'write ' + file.replace('.py','') + ' ' + tags + ' ' + '-base=' + base
            RunJarvis(cmd)
            time.sleep(globalParameter['TimeRecordFile'])

            if(os.path.isfile(file)==False):
                fileTest = open(file,"w")
                fileTest.write(MakeCommandExemple())
                fileTest.close()
                time.sleep(globalParameter['TimeRecordFile'])
        
            fileTest = open(file,"a")
            cmd = "\tRun(r'" + globalParameter['ChromeTarget'] + "','-incognito " + link + "')\n"
            fileTest.write(cmd)
            fileTest.close()
            
        time.sleep(globalParameter['TimeRecordFile'])
        cmd = 'read ' + file + ' ' + tags + ' ' + '-base=' + base
        RunJarvis(cmd)

    time.sleep(globalParameter['TimeRecordFile'])
    if(os.path.isfile(file)==True and args['keepfile'] == False):
        os.remove(file)
        pass
