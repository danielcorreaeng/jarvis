import time
import json
import sys,os
import subprocess
import argparse
import unittest
import smtplib
import imaplib
import email
from os.path import basename
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.utils import COMMASPACE, formatdate
import configparser

globalParameter = {}
globalParameter['PathLocal'] = os.path.join("C:\\","Jarvis")
globalParameter['PathJarvis'] = os.path.join("C:\\","Jarvis","Jarvis.py")
globalParameter['PathOutput'] = os.path.join(globalParameter['PathLocal'], "Output")
globalParameter['PathExecutable'] = "python"

globalParameter['EMAIL_SENDER'] = 'xxxxx@xxxxx.xxx'
globalParameter['EMAIL_PWD'] = 'xxxxx'
globalParameter['EMAIL_SERVER'] = 'smtp.gmail.com'
globalParameter['EMAIL_PORT'] = 587

VALUES_INPUT = {}
VALUES_OUTPUT = {}

class TestCases(unittest.TestCase):
    def test_case_000(self):
        self.assertEqual('foo'.upper(), 'FOO')
        
    def test_case_001(self):
        self.assertEqual('foo'.upper(), 'FOO')        

def SendEmail(EMAIL_SENDER, EMAIL_PWD, TARGET_EMAIL, SUBJECT, ATTACH, MESSAGE, EMAIL_SERVER, EMAIL_PORT):
    
    print(EMAIL_SERVER)
    print(EMAIL_PORT)
    
    mailServer = smtplib.SMTP(EMAIL_SERVER, EMAIL_PORT)
    mailServer.ehlo()
    mailServer.starttls()
    mailServer.ehlo()
    print(EMAIL_SENDER)
    print(EMAIL_PWD)
    mailServer.login(EMAIL_SENDER, EMAIL_PWD)

    message = MESSAGE
    msg = MIMEMultipart('related')
    msg['From'] = EMAIL_SENDER
    msg['To'] = TARGET_EMAIL
    msg['Subject'] = SUBJECT
    msg.preamble = 'This is a multi-part  message in MIME format.'
    msg.attach(MIMEText(message))

    files = []

    _filesTest = ATTACH.split(',')

    for val in _filesTest:
        print(val)
        if(os.path.isfile(val) == True):
            print('ok')
            files.append(val)

    for f in files or []:
        with open(f, "rb") as fil:
            part = MIMEApplication(
                fil.read(),
                Name=basename(f)
            )
            part['Content-Disposition'] = 'attachment; filename="%s"' % basename(f)
            msg.attach(part)

    mailServer.sendmail(EMAIL_SENDER, TARGET_EMAIL, msg.as_string())
    mailServer.quit()#mailServer.close()


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
    #print(globalParameter['PathJarvis'])
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

def Main(TARGET_EMAIL, SUBJECT, ATTACH, MESSAGE): 
    """send email script (version 2.2). Parameters: <TARGET_EMAIL> <SUBJECT> <ATTACH> <MESSAGE> -r=<EMAIL_SENDER> -w=<EMAIL_PWD> -s=<EMAIL_SERVER> -p=<EMAIL_PORT>"""
    
    global VALUES_INPUT
    global VALUES_OUTPUT

    VALUES_OUTPUT = VALUES_INPUT

    VALUES_OUTPUT['EMAIL_SENDER'] = globalParameter['EMAIL_SENDER']
    VALUES_OUTPUT['EMAIL_PWD'] = globalParameter['EMAIL_PWD']
    VALUES_OUTPUT['TARGET_EMAIL'] = TARGET_EMAIL
    VALUES_OUTPUT['SUBJECT'] = SUBJECT
    VALUES_OUTPUT['ATTACH'] = ATTACH
    VALUES_OUTPUT['MESSAGE'] = MESSAGE
    VALUES_OUTPUT['EMAIL_SERVER'] = globalParameter['EMAIL_SERVER']
    VALUES_OUTPUT['EMAIL_PORT'] = globalParameter['EMAIL_PORT']

    try:
        SendEmail(globalParameter['EMAIL_SENDER'], globalParameter['EMAIL_PWD'], TARGET_EMAIL, SUBJECT, ATTACH, MESSAGE, globalParameter['EMAIL_SERVER'], globalParameter['EMAIL_PORT'])
    except:
        pass

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=Main.__doc__)
    parser.add_argument('-d','--description', help='Description of program', action='store_true')
    parser.add_argument('-u','--tests', help='Execute tests', action='store_true')
    parser.add_argument('-i','--file_input', help='data entry via file (path)')
    parser.add_argument('-o','--file_output', help='output data via file (path)')
    parser.add_argument('-s','--EMAIL_SERVER', help='post server')
    parser.add_argument('-p','--EMAIL_PORT', help='post server port')
    parser.add_argument('-r','--EMAIL_SENDER', help='sender')
    parser.add_argument('-w','--EMAIL_PWD', help='password')
    
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
        with open(args['file_input']) as json_file:
            VALUES_INPUT = json.load(json_file)

    GetCorrectPath()    
     
    TARGET_EMAIL = unknown[0]
    SUBJECT = unknown[1]
    ATTACH = unknown[2]
    MESSAGE = ' '.join(unknown[3:])

    if args['EMAIL_SENDER']:
        globalParameter['EMAIL_SENDER'] = args['EMAIL_SENDER']

    if args['EMAIL_PWD']:
        globalParameter['EMAIL_PWD'] = args['EMAIL_PWD']

    if args['EMAIL_SERVER']:
        globalParameter['EMAIL_SERVER'] = args['EMAIL_SERVER']

    if args['EMAIL_PORT']:
        globalParameter['EMAIL_PORT'] = args['EMAIL_PORT']

    Main(TARGET_EMAIL, SUBJECT, ATTACH, MESSAGE)
    
    if args['file_output']:
        try:
            with open(args['file_output'], "w") as outfile:                    
                json_string = json.dumps(VALUES_OUTPUT, default=lambda o: o.__dict__, sort_keys=True, indent=2)
                outfile.write(json_string)
        except:
            pass

