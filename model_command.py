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

def Main(): 
    '''No describe'''
    
    global globalParameter

    GetCorrectPath()

    global VALUES_INPUT
    global VALUES_OUTPUT
    VALUES_OUTPUT = VALUES_INPUT

    #OpenFolder(r'C:\Windows')
    #Run(r'Calc')
    #Run(r'C:\Program Files\Google\Chrome\Application\chrome.exe','-incognito www.google.com.br')
    #VALUES_OUTPUT['vartest'] = 'test'
	
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=Main.__doc__)
    parser.add_argument('-d','--description', help='Description of program', action='store_true')
    parser.add_argument('-u','--tests', help='Execute tests', action='store_true')
    parser.add_argument('-i','--file_input', help='data entry via file (path)')
    parser.add_argument('-o','--file_output', help='output data via file (path)')
    
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

    if args['file_input']:   
        with open(args['file_input']) as json_file:
            VALUES_INPUT = json.load(json_file)

    param = ' '.join(unknown)

    Main()
    
    if args['file_output']:
        with open(args['file_output'], "w") as outfile:                    
            json_string = json.dumps(VALUES_OUTPUT, default=lambda o: o.__dict__, sort_keys=True, indent=2)
            outfile.write(json_string)                