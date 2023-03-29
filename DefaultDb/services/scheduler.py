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
import datetime

from jarvis_utils import *

globalParameter['INPUT_DATA_OFF'] = True
globalParameter['OUTPUT_DATA_OFF'] = True
globalParameter['MAINLOOP_CONTROLLER'] = False
globalParameter['MAINWEBSERVER'] = False
globalParameter['PROCESS_JARVIS'] = None
globalParameter['TimeRecordFile'] = 3
globalParameter['SchedulerTasks'] = []
globalParameter['SchedulerText'] = ""
globalParameter['SchedulerMaxLife'] = 35

def Run(command, parameters=None, wait=False):
    #print(command)
    if(parameters != None):
        proc = subprocess.Popen([command, parameters], stdout=subprocess.PIPE, shell=True)
    else:
        proc = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)

    if(wait == True):
        proc.communicate()

def RunJarvis(tags, parameters=None, wait=True):
    Run(globalParameter['PathExecutable'] + ' ' + globalParameter['PathJarvis'] + ' ' + tags, parameters, wait) 
    print('command : ' + globalParameter['PathExecutable'] + ' ' + globalParameter['PathJarvis'] + ' ' + tags) 

def MakeSchedulerCode(_schedules,_loop):
    _command = "import time\n"
    _command += "import schedule\n"
    _command += "import time\n"                
    _command += "import sys,os\n"
    _command += "import datetime\n"          
    _command += "import subprocess\n"
    _command += "\n"
    _command += "def Run(command):\n"
    _command += "\tproc = subprocess.Popen(command, shell=True)\n"
    _command += "\n"
    _command += "def Main(): \n"
    _command += "\t'''This opens pages related to tags.'''\n"	
    _command += "\t\n"        
    _command += _schedules
    _command += "\t\n"    
    _command += _loop
    _command += "\t\n"
    _command += "if __name__ == '__main__':\n"
    _command += "\tif(len(sys.argv) > 1):\n"
    _command += "\t\tif(sys.argv[len(sys.argv)-1] == '-h' or sys.argv[len(sys.argv)-1] == 'help'):\n"
    _command += "\t\t\tprint(Main.__doc__)\n"
    _command += "\t\t\tsys.exit()\n"
    _command += "\t\n"    
    _command += "\tMain()\n"    
    _command += "\t\n"
		
    return _command

def MakeSchedulerLoopToText():

    schedulesLoop = ''
    schedulesLoop +=  "\t_loop=True\n"
    schedulesLoop +=  "\tstart_time = datetime.datetime.now()\n"
    schedulesLoop +=  "\twhile _loop:\n"
    schedulesLoop +=  "\t\tschedule.run_pending()\n"
    schedulesLoop +=  "\t\ttime.sleep(1)\n"

    if(globalParameter['SchedulerMaxLife'] > 0):
        schedulesLoop += "\t\tnow_time = datetime.datetime.now()\n"
        schedulesLoop += "\t\tdelta = int((now_time- start_time).total_seconds())\n"
        schedulesLoop += "\t\tif(delta>" + str(globalParameter['SchedulerMaxLife']) + "):\n"        
        schedulesLoop += "\t\t\t_loop=False\n"

    return schedulesLoop

def MakeSchedulerTaskToText(task):

    body = task.split('.')[0:-1]
    if(body[-1] != 'do'):
        body.append('do')
    body = '.'.join(body)

    task = task.split('.')[-1].lower()
    if("jarvis" in task):
        task = task.replace("jarvis", globalParameter['PathExecutable'] + ' ' + globalParameter['PathJarvis'])

    print([task, body])

    schedulesText = "\t" + body + "(Run,r'" + task  + "')" + "\n"	    
    return schedulesText

def GetLocalFileWithoutExtension():
    localFile = os.path.join(globalParameter['PathOutput'], datetime.datetime.now().strftime("%Y%m%d_%H%M%S%f") + "_" + str(randint(0, 999)) + "_temp")
    return localFile

def GetLocalFile():
    localFile = GetLocalFileWithoutExtension() + ".py"
    return localFile

def Main(): 
    '''create a new program with a scheduling system with the tasks passed here by parameter or configuration file. the format defined by the schedule library as schedule.every(10).seconds.do.jarvis calc and other parameters'''
    
    global globalParameter

    textTest = "schedule.every(10).seconds.do.jarvis calc and other parameters"

    if(len(globalParameter['SchedulerTasks'])<=0):
        return 
    
    for task in globalParameter['SchedulerTasks']:
        globalParameter['SchedulerText'] = MakeSchedulerTaskToText(task)

    code = MakeSchedulerCode(globalParameter['SchedulerText'],MakeSchedulerLoopToText())

    file = GetLocalFile()
    print(file)

    fileTest = open(file,"w")
    fileTest.write(code)
    fileTest.close()
    time.sleep(globalParameter['TimeRecordFile'])

    '''
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
    '''
    pass
	
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=Main.__doc__)
    parser.add_argument('-d','--description', help='Description of program', action='store_true')
    parser.add_argument('-t','--task', help='Receive a task for parameter')
    parser.add_argument('-c','--config', help='Config.ini file')
    
    args, unknown = parser.parse_known_args()
    args = vars(args)
    
    if args['description'] == True:
        print(Main.__doc__)
        sys.exit()     

    GetCorrectPath()  

    if args['task'] is not None:
        print(str(args['task']))
        globalParameter['SchedulerTasks'].append(str(args['task']))

    if args['config'] is not None:
        print('Config.ini: ' + args['config'])
        globalParameter['configFile'] = args['config']          

    Main()
   
