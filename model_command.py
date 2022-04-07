from glob import glob
import time
import json
import sys,os
import subprocess
import argparse
import unittest
#from model_service import * #AT YOUR OWN RISK

VALUES_INPUT = {}
VALUES_OUTPUT = {}

class TestCasesC(unittest.TestCase):
    def test_case_000(self):
        self.assertEqual('foo'.upper(), 'FOO')
        
    def test_case_001(self):
        self.assertEqual('foo'.upper(), 'FOO')       

def RunC(command, parameters=None):
    if(parameters != None):
        subprocess.Popen([command, parameters], shell=True)
    else:
        subprocess.Popen(command, shell=True)

def OpenFolder(path):
	if sys.platform == 'win32':
		RunC('explorer.exe', path)

def MainC(): 
    '''No describe'''
    
    global globalParameter
    global VALUES_INPUT
    global VALUES_OUTPUT

    VALUES_OUTPUT = VALUES_INPUT
    
    #OpenFolder(r'C:\Windows')
    #RunC(r'Calc')
    #RunC(r'C:\Program Files\Google\Chrome\Application\chrome.exe','-incognito www.google.com.br')
    #VALUES_OUTPUT['vartest'] = 'test'
    #GetCorrectPath() #from model_service
	
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=MainC.__doc__)
    parser.add_argument('-d','--description', help='Description of program', action='store_true')
    parser.add_argument('-u','--tests', help='Execute tests', action='store_true')
    parser.add_argument('-i','--file_input', help='data entry via file (path)')
    parser.add_argument('-o','--file_output', help='output data via file (path)')
    
    args, unknown = parser.parse_known_args()
    args = vars(args)
    
    if args['description'] == True:
        print(MainC.__doc__)
        sys.exit()

    if args['tests'] == True:       
        suite = unittest.TestSuite()
        suite.addTest(TestCasesC("test_case_000"))
        suite.addTest(TestCasesC("test_case_001"))
        #suite.addTest(TestCases("test_webserver_fifo")) #from model_service
        runner = unittest.TextTestRunner()
        runner.run(suite)               
        sys.exit()        

    if args['file_input']:   
        with open(args['file_input']) as json_file:
            VALUES_INPUT = json.load(json_file)

    param = ' '.join(unknown)

    MainC()
    
    if args['file_output']:
        with open(args['file_output'], "w") as outfile:                    
            json_string = json.dumps(VALUES_OUTPUT, default=lambda o: o.__dict__, sort_keys=True, indent=2)
            outfile.write(json_string)                