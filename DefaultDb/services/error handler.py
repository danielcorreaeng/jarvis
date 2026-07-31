from glob import glob
import time
import json
import sys,os
import subprocess
import argparse
import unittest
from jarvis_utils import *

globalParameter['INPUT_DATA_OFF'] = False
globalParameter['OUTPUT_DATA_OFF'] = False
globalParameter['MAINLOOP_CONTROLLER'] = False
globalParameter['MAINWEBSERVER'] = False
globalParameter['MAINLOOP_SLEEP_SECONDS'] = 5.0
globalParameter['PROCESS_JARVIS'] = None

VALUES_INPUT = {}
VALUES_OUTPUT = {}

class TestCases_Local(TestCases):
    def test_dump(self):
        check = True
        self.assertTrue(check)        

def OpenFolder(path):
	if sys.platform == 'win32':
		Run('explorer.exe', path)

def Main(logtest): 
    '''No describe'''
    
    global globalParameter

    GetCorrectPath()

    global VALUES_INPUT
    global VALUES_OUTPUT
    VALUES_OUTPUT = VALUES_INPUT

    #OpenFolder(r'C:\Windows')
    #Run(r'Calc')
    #Run(r'C:\Program Files\Google\Chrome\Application\chrome.exe','-incognito www.google.com.br')
    #RunJarvis("Calc")
    #VALUES_OUTPUT['vartest'] = 'test'
    
    logpath = os.path.join(globalParameter['PathLocal'], "Db", "log")
    logname = os.path.join(logpath, datetime.datetime.now().strftime("%Y%m%d_%H") + ".txt")

    if not os.path.exists(logpath):
        os.makedirs(logpath)

    with open(logname, 'a') as logfile:
        logfile.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " - " + str(logtest) + "\n")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=Main.__doc__)
    parser.add_argument('-d','--description', help='Description of program', action='store_true')
    parser.add_argument('-u','--tests', help='Execute tests', action='store_true')
    
    args, unknown = parser.parse_known_args()
    args = vars(args)
    
    if args['description'] == True:
        print(Main.__doc__)
        sys.exit()

    if args['tests'] == True:       
        suite = unittest.TestSuite()
        #suite.addTest(TestCases_Local("test_webserver_fifo")) 
        suite.addTest(TestCases_Local("test_dump")) 
        runner = unittest.TextTestRunner()
        runner.run(suite)   
        globalParameter['MAINLOOP_CONTROLLER'] = False                     
        sys.exit()    

    param = ' '.join(unknown)

    Main(param)           