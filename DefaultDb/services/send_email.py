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
from jarvis_utils import *

globalParameter['INPUT_DATA_OFF'] = False
globalParameter['OUTPUT_DATA_OFF'] = False
globalParameter['MAINLOOP_CONTROLLER'] = False
globalParameter['MAINWEBSERVER'] = False

globalParameter['EMAIL_SENDER'] = 'xxxxx@xxxxx.xxx'
globalParameter['EMAIL_PWD'] = 'xxxxx'
globalParameter['EMAIL_SERVER'] = 'smtp.gmail.com'
globalParameter['EMAIL_PORT'] = 587

class TestCases_Local(TestCases):
    def test_dump(self):
        check = True
        self.assertTrue(check)        

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

def Main(TARGET_EMAIL, SUBJECT, ATTACH, MESSAGE): 
    """send email script (version 2.2). Parameters: <TARGET_EMAIL> <SUBJECT> <ATTACH> <MESSAGE> -r=<EMAIL_SENDER> -w=<EMAIL_PWD> -s=<EMAIL_SERVER> -p=<EMAIL_PORT>"""
    
    global INPUT_DATA
    global OUTPUT_DATA

    INPUT_DATA = {}
    OUTPUT_DATA = {}

    OUTPUT_DATA = INPUT_DATA

    OUTPUT_DATA['EMAIL_SENDER'] = globalParameter['EMAIL_SENDER']
    OUTPUT_DATA['EMAIL_PWD'] = globalParameter['EMAIL_PWD']
    OUTPUT_DATA['TARGET_EMAIL'] = TARGET_EMAIL
    OUTPUT_DATA['SUBJECT'] = SUBJECT
    OUTPUT_DATA['ATTACH'] = ATTACH
    OUTPUT_DATA['MESSAGE'] = MESSAGE
    OUTPUT_DATA['EMAIL_SERVER'] = globalParameter['EMAIL_SERVER']
    OUTPUT_DATA['EMAIL_PORT'] = globalParameter['EMAIL_PORT']

    try:
        SendEmail(globalParameter['EMAIL_SENDER'], globalParameter['EMAIL_PWD'], TARGET_EMAIL, SUBJECT, ATTACH, MESSAGE, globalParameter['EMAIL_SERVER'], globalParameter['EMAIL_PORT'])
        pass
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
    parser.add_argument('-c','--config', help='Config.ini file')    
    
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
        sys.exit()    

    if args['file_input']:   
        with open(args['file_input']) as json_file:
            INPUT_DATA = json.load(json_file)

    if args['config'] is not None:
        print('Config.ini: ' + args['config'])
        globalParameter['configFile'] = args['config']   

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
                json_string = json.dumps(OUTPUT_DATA, default=lambda o: o.__dict__, sort_keys=True, indent=2)
                outfile.write(json_string)
                #print(json_string)
        except:
            pass

