
from glob import glob
import time
import json
import sys,os
import subprocess
import socket
import argparse
import unittest
import io
import operator
from jarvis_utils import *
import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service

from flask import Flask, redirect, url_for, request, render_template
from flask_cors import CORS

globalParameter['LocalPort'] = 8815

globalParameter['INPUT_DATA_OFF'] = False
globalParameter['OUTPUT_DATA_OFF'] = False
globalParameter['MAINLOOP_CONTROLLER'] = False
globalParameter['MAINWEBSERVER'] = True
globalParameter['PROCESS_JARVIS'] = None

globalParameter['URLTargetChatGpt'] = r"https://chat.openai.com"
globalParameter['chrome_driver_path'] = r"C:\ChromeDriver\chromedriver-win64\chromedriver.exe"
globalParameter['chrome_path'] = r'"C:\ChromeDriver\chrome-win64\chrome.exe"'
globalParameter['wait4auth'] = 5
globalParameter['timeResponse'] = 10
globalParameter['removeText'] = "ChatGPT\n"

app = Flask(__name__)
CORS(app)

#suitability of 
#https://github.com/Michelangelo27/chatgpt_selenium_automation
class ChatGPTAutomation:

    def __init__(self, chrome_path, chrome_driver_path):
        """
        This constructor automates the following steps:
        1. Open a Chrome browser with remote debugging enabled at a specified URL.
        2. Prompt the user to complete the log-in/registration/human verification, if required.
        3. Connect a Selenium WebDriver to the browser instance after human verification is completed.

        :param chrome_path: file path to chrome.exe (ex. C:\\Users\\User\\...\\chromedriver.exe)
        :param chrome_driver_path: file path to chrome.exe (ex. C:\\Users\\User\\...\\chromedriver.exe)
        """

        self.chrome_path = chrome_path
        self.chrome_driver_path = chrome_driver_path

        url = globalParameter['URLTargetChatGpt']
        free_port = self.find_available_port()
        self.launch_chrome_with_remote_debugging(free_port, url)
        self.wait_for_human_verification()
        self.driver = self.setup_webdriver(free_port)

    @staticmethod
    def find_available_port():
        """ This function finds and returns an available port number on the local machine by creating a temporary
            socket, binding it to an ephemeral port, and then closing the socket. """

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 0))
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            return s.getsockname()[1]

    def launch_chrome_with_remote_debugging(self, port, url):
        """ Launches a new Chrome instance with remote debugging enabled on the specified port and navigates to the
            provided url """

        def open_chrome():
            chrome_cmd = f"{self.chrome_path} --remote-debugging-port={port} --user-data-dir=remote-profile {url}"
            os.system(chrome_cmd)

        chrome_thread = threading.Thread(target=open_chrome)
        chrome_thread.start()

    def setup_webdriver(self, port):
        """  Initializes a Selenium WebDriver instance, connected to an existing Chrome browser
             with remote debugging enabled on the specified port"""

        service = Service()
        chrome_options = webdriver.ChromeOptions()
        chrome_options.binary_location = self.chrome_driver_path
        chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{port}")
        driver = webdriver.Chrome(options=chrome_options)
        return driver

    def send_prompt_to_chatgpt(self, prompt):
        """ Sends a message to ChatGPT and waits for 10 seconds for the response """

        input_box = self.driver.find_element(by=By.XPATH, value='//textarea[contains(@id, "prompt-textarea")]')
        self.driver.execute_script(f"arguments[0].value = '{prompt}';", input_box)
        input_box.send_keys(Keys.RETURN)
        input_box.submit()
        time.sleep(globalParameter['timeResponse'])

    def return_chatgpt_conversation(self):
        """
        :return: returns a list of items, even items are the submitted questions (prompts) and odd items are chatgpt response
        """

        return self.driver.find_elements(by=By.CSS_SELECTOR, value='div.text-base')

    def save_conversation(self, file_name):
        """
        It saves the full chatgpt conversation of the tab open in chrome into a text file, with the following format:
            prompt: ...
            response: ...
            delimiter
            prompt: ...
            response: ...

        :param file_name: name of the file where you want to save
        """

        directory_name = "conversations"
        if not os.path.exists(directory_name):
            os.makedirs(directory_name)

        delimiter = "|^_^|"
        chatgpt_conversation = self.return_chatgpt_conversation()
        with open(os.path.join(directory_name, file_name), "a") as file:
            for i in range(0, len(chatgpt_conversation), 2):
                file.write(
                    f"prompt: {chatgpt_conversation[i].text}\nresponse: {chatgpt_conversation[i + 1].text}\n\n{delimiter}\n\n")

    def return_last_response(self):
        """ :return: the text of the last chatgpt response """

        response_elements = self.driver.find_elements(by=By.CSS_SELECTOR, value='div.text-base')
        return response_elements[-1].text

    @staticmethod
    def wait_for_human_verification():
        #change for automatization - need improve
        time.sleep(globalParameter['wait4auth'])

    def quit(self):
        """ Closes the browser and terminates the WebDriver session."""
        print("Closing the browser...")
        self.driver.close()
        self.driver.quit()

class TestCases_Local(TestCases):
    def test_dump(self):
        check = True
        self.assertTrue(check)    

def LoadVarsIni2(config,sections):
    global globalParameter

    if('CriticalServices' in sections):
        for key in config['CriticalServices']:  
            print(config['CriticalServices'][key])

def CorrectLocalFunctions():
    globalsub.subs(LoadVarsIni, LoadVarsIni2)
    pass

def description():
    return str(Main.__doc__) + " | ip server : " +  str(globalParameter['LocalIp']) + ":" + str(globalParameter['LocalPort'])

@app.route('/')
def index():
    return description()


@app.route('/botresponse',methods = ['POST', 'GET'])
def botresponse():
    if request.method == 'POST':
        data = request.get_json(force=True)  
        ask = data['ask']
        response = BotResponse(ask)
        return response
    else:
        ask = request.args.get('ask')
        return BotResponse(ask)

def ChatBotLoop():    
    chatgpt = ChatGPTAutomation(globalParameter['chrome_path'], globalParameter['chrome_driver_path'])
    loop = True    
    
    while(loop):
        ask = input(">")
        
        if(ask == None):
            print('...')
            continue

        chatgpt.send_prompt_to_chatgpt(ask)
        res = str(chatgpt.return_last_response()).replace(globalParameter['removeText'],"",1)

        print(res)

        if(ask == 'tchau'):
            loop = False
            chatgpt.quit()
            break
    pass 

def BotResponse(ask):
    res = None
    try:
        chatgpt = ChatGPTAutomation(globalParameter['chrome_path'], globalParameter['chrome_driver_path'])
        ask = ask.replace('_', ' ')
        chatgpt.send_prompt_to_chatgpt(ask)
        res = str(chatgpt.return_last_response()).replace(globalParameter['removeText'],"",1)
        chatgpt.quit()
    except:
        pass
    return str(res)

def Main():
    """Integraca"""    

    global globalParameter

    CorrectLocalFunctions()
    GetCorrectPath()

    try:
        if(globalParameter['LocalIp'] == None):        
            globalParameter['LocalIp'] = GetCorrectIp(socket.gethostbyname_ex(socket.gethostname()))
    except:
        print('error ip')
        
    try:
        t = Thread(target=mainThread)
        t.start()  
    except:
        print('error mainThread')

    try:
        if(globalParameter['MAINWEBSERVER'] == True):
            rl = RemoteLog()
            rl.CheckRestAPIThread(command="chatgpt -base=integration", host = str(globalParameter['LocalIp']),port=globalParameter['LocalPort'])            
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
    parser.add_argument('-a','--hold4auth', help='Wait 40 seconds for authentication', action='store_true')      
    parser.add_argument('-r','--bootresponse', help='Chatbot response input', action='store_true')    
    parser.add_argument('-l','--bootloop', help='Chatbot in loop', action='store_true')    
    
    args, unknown = parser.parse_known_args()
    args = vars(args)
    dialog = ' '.join(unknown)
    
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

    if args['hold4auth'] == True:       
        globalParameter['wait4auth'] = 40

    if args['bootresponse'] == True:       
        print(BotResponse(dialog))
        sys.exit()   

    if args['bootloop'] == True:       
        ChatBotLoop()
        sys.exit()           

    param = ' '.join(unknown)
    Main()
