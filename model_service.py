from glob import glob
import time
import json
import sys,os
import subprocess
import argparse
import unittest
import io
import operator
from jarvis_utils import *

globalParameter['LocalPort'] = 8821

globalParameter['INPUT_DATA_OFF'] = False
globalParameter['OUTPUT_DATA_OFF'] = False
globalParameter['MAINLOOP_CONTROLLER'] = True
globalParameter['MAINWEBSERVER'] = True
globalParameter['MAINLOOP_SLEEP_SECONDS'] = 5.0
globalParameter['PROCESS_JARVIS'] = None

class TestCases_Local(TestCases):
    def test_dump(self):
        check = True
        self.assertTrue(check)    

def LoadVarsIni2(config,sections):
    global globalParameter

    if('CriticalServices' in sections):
        for key in config['CriticalServices']:  
            print(config['CriticalServices'][key])

def mainThread2():
    global globalParameter

    while(globalParameter['MAINLOOP_CONTROLLER']):
        try:                 
            mainLoop()
            time.sleep(globalParameter['MAINLOOP_SLEEP_SECONDS']) 
            print('Loop')
        except:
            print('Error Loop')
    pass

def VirtualInput2():
    pass

def mainLoopProcess2(input_data):
    result = None

    if(globalParameter['PROCESS_JARVIS'] != None):
        fileInput = os.path.join(globalParameter['PathOutput'] , datetime.datetime.now().strftime("%Y%m%d_%H%M%S%f_in.json"))
        fileOutput = os.path.join(globalParameter['PathOutput'] , datetime.datetime.now().strftime("%Y%m%d_%H%M%S%f_out.json"))

        with open(fileInput, "w") as outfile:                    
            json_string = json.dumps(input_data, default=lambda o: o.__dict__, sort_keys=True, indent=2)
            outfile.write(json_string)  

        RunJarvis(globalParameter['PROCESS_JARVIS'] + " -i " + fileInput + " -o " + fileOutput)

        with open(fileOutput) as json_file:
            result = json.load(json_file)
            #print(result)
    else:
        result = copy.deepcopy(input_data)
 
    return result

def CorrectLocalFunctions():
    globalsub.subs(LoadVarsIni, LoadVarsIni2)
    globalsub.subs(VirtualInput, VirtualInput2)    
    globalsub.subs(mainLoopProcess, mainLoopProcess2)
    globalsub.subs(mainThread, mainThread2)    
    pass

def description():
    return str(Main.__doc__) + " | ip server : " +  str(globalParameter['LocalIp']) + ":" + str(globalParameter['LocalPort'])

@app.route('/')
def index():
    return description()

def Main():
    """no describe"""    

    global globalParameter

    CorrectLocalFunctions()
    GetCorrectPath()
        
    try:
        t = Thread(target=mainThread)
        t.start()  
    except:
        print('error mainThread')

    try:
        if(globalParameter['MAINWEBSERVER'] == True):
            #rl = RemoteLog()
            #remoteLogTargetIp = GetCorrectIp()
            #if(globalParameter['LocalIp'] != '0.0.0.0'): remoteLogTargetIp = globalParameter['LocalIp']
            #rl.CheckRestAPIThread(command="tags -base=xxxxxxx", host = str(remoteLogTargetIp),port=globalParameter['LocalPort'])            
            #app.run(host = str(globalParameter['LocalIp']),port=globalParameter['LocalPort'], ssl_context='adhoc') 
            app.run(host = str(globalParameter['LocalIp']),port=globalParameter['LocalPort']) 
        pass
    except:
        print('error webservice')
    
if __name__ == '__main__':   
    parser = argparse.ArgumentParser(description=Main.__doc__)
    parser.add_argument('-d','--description', help='Description of program', action='store_true')
    parser.add_argument('-u','--tests', help='Execute tests', action='store_true')
    parser.add_argument('-p','--port', help='Service running in target port')
    parser.add_argument('-i','--ip', help='Service running in target ip')
    parser.add_argument('-c','--config', help='Config.ini file')  
    
    args, unknown = parser.parse_known_args()
    args = vars(args)
    
    if args['description'] == True:
        print(Main.__doc__)
        sys.exit()

    if args['tests'] == True:       
        CorrectLocalFunctions()
        suite = unittest.TestSuite()
        suite.addTest(TestCases_Local("test_webserver_fifo")) 
        suite.addTest(TestCases_Local("test_dump")) 
        runner = unittest.TextTestRunner()
        runner.run(suite)   
        globalParameter['MAINLOOP_CONTROLLER'] = False                     
        sys.exit()    

    if args['port'] is not None:
        print('TargetPort: ' + args['port'])
        globalParameter['LocalPort'] = args['port']  

    if args['ip'] is not None:
        print('TargetIP: ' + args['ip'])
        globalParameter['LocalIp'] = args['ip']       

    if args['config'] is not None:
        print('Config.ini: ' + args['config'])
        globalParameter['configFile'] = args['config']                

    param = ' '.join(unknown)

    Main()