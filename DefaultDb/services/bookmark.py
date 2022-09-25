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

globalParameter = {}
globalParameter['PathLocal'] = os.path.join("C:\\","Jarvis")
globalParameter['PathJarvis'] = os.path.join("C:\\","Jarvis","Jarvis.py")
globalParameter['PathOutput'] = os.path.join(globalParameter['PathLocal'], "Output")
globalParameter['PathExecutable'] = "python"
globalParameter['ChromeTarget'] = "C:\Program Files\Google\Chrome\Application\chrome.exe"
globalParameter['TimeRecordFile'] = 3

def Run(command, parameters=None, wait=False):
    #print(command)
    if(parameters != None):
        proc = subprocess.Popen([command, parameters], stdout=subprocess.PIPE, shell=True)
    else:
        proc = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)

    if(wait == True):
        proc.communicate()

def RunJarvis(tags):
	Run(globalParameter['PathExecutable'] + ' ' + globalParameter['PathJarvis'] + ' ' + tags)  

def GetCorrectPath():
    global globalParameter

    dir_path = os.path.dirname(os.path.realpath(__file__)) 
    os.chdir(dir_path)

    jarvis_file = os.path.join(dir_path, 'Jarvis.py')
    ini_file = os.path.join(dir_path, 'config.ini')
    if(os.path.isfile(jarvis_file) == False):
        jarvis_file = os.path.join(dir_path, '..', 'Jarvis.py')
        ini_file = os.path.join(dir_path, '..', 'config.ini')
        if(os.path.isfile(jarvis_file) == False):
            return
    
    globalParameter['PathExecutable'] = sys.executable
    globalParameter['PathLocal'] = os.path.dirname(os.path.realpath(jarvis_file))
    globalParameter['PathJarvis'] = jarvis_file
    globalParameter['PathOutput'] = os.path.join(globalParameter['PathLocal'], "Output")

    if(os.path.isfile(ini_file) == True):
        with open(ini_file) as fp:
            config = configparser.ConfigParser()
            config.read_file(fp)
            sections = config.sections()
            if('Parameters' in sections):
                if('defaultpassword' in config['Parameters']):
                    globalParameter['password'] = config['Parameters']['defaultpassword']
                    print('password:' + globalParameter['password'])
                for key in config['Parameters']:                    
                    for globalParameter_key in globalParameter:    
                        if globalParameter_key.lower()==key.lower():
                            globalParameter[globalParameter_key]=str(config['Parameters'][key])
                            print(key + "=" + str(config['Parameters'][key]))

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


def GetLocalFile():
    localFile = os.path.join(globalParameter['PathOutput'], datetime.datetime.now().strftime("%Y%m%d_%H%M%S%f") + "_" + str(randint(0, 999)) + "_temp.py")
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
    
    args, unknown = parser.parse_known_args()
    args = vars(args)
    
    if args['description'] == True:
        print(Main.__doc__)
        sys.exit()     

    GetCorrectPath()  

    id_unique = False
    if args['unique'] == True:
        id_unique = True   
        
    base = unknown[0]
    tags = unknown[1:-1]
    link = unknown[-1]

    tags = ' '.join(tags)
    if(id_unique == True):
        tags = tags + " " + str(datetime.datetime.now().strftime("%Y%m%d")) + " " + str(datetime.datetime.now().strftime("%H%M%S%f"))  + " " + str(randint(0, 999))
    
    file = GetLocalFile()
    extension = os.path.splitext(link)[1]

    if((args['jsonlink'] == False and args['jsonnote'] == False) and (extension == '.jpg' or extension == '.jpeg' or extension == '.png' or extension == '.json' or extension == '.doc' or extension == '.docx' or extension == '.pdf' or extension == '.xls' or extension == '.xlsx')):
        file = file + extension
        f = open(file,'wb')
        response = requests.get(link)
        f.write(response.content)
        f.close()
        time.sleep(globalParameter['TimeRecordFile'])
        cmd = 'read ' + file + ' ' + tags + ' ' + '-base=' + base
        RunJarvis(cmd)        
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
    if(os.path.isfile(file)==True):
        os.remove(file)
