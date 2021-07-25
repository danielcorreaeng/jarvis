import time
import json
import sys,os
import subprocess
import argparse
import unittest

VALUES_INPUT = {}
VALUES_OUTPUT = {}

class TestCases(unittest.TestCase):
    def test_case_000(self):
        self.assertEqual('foo'.upper(), 'FOO')
        
    def test_case_001(self):
        self.assertEqual('foo'.upper(), 'FOO')        

def Run(command, parameters=None):
    if(parameters != None):
        subprocess.Popen([command, parameters], shell=True)
    else:
        subprocess.Popen(command, shell=True)

def OpenFolder(path):
	if sys.platform == 'win32':
		Run('explorer.exe', path)

def Main(): 
    '''No describe'''
    
    global VALUES_INPUT
    global VALUES_OUTPUT

    #print(VALUES_INPUT)    
    #VALUES_OUTPUT['test'] = 'teste inicial'
    
    #OpenFolder(r'C:\Windows')
    #Run(r'Calc')
    #Run(r'C:\Program Files\Google\Chrome\Application\chrome.exe','-incognito www.google.com.br')
	
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
        suite.addTest(TestCases("test_case_000"))
        suite.addTest(TestCases("test_case_001"))
        runner = unittest.TextTestRunner()
        runner.run(suite)               
        sys.exit()        

    if args['file_input']:
        try:        
            with open(args['file_input']) as json_file:
                VALUES_INPUT = json.load(json_file)
        except:
            pass

    param = ' '.join(unknown)

    Main()
    
    if args['file_output']:
        try:        
            with open(args['file_output'], "w") as outfile:                    
                json_string = json.dumps(VALUES_OUTPUT, default=lambda o: o.__dict__, sort_keys=True, indent=2)
                outfile.write(json_string)                
        except:
            pass