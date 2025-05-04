
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
import openai

from flask import Flask, redirect, url_for, request, render_template
from flask_cors import CORS

globalParameter['LocalPort'] = 8822

globalParameter['INPUT_DATA_OFF'] = False
globalParameter['OUTPUT_DATA_OFF'] = False
globalParameter['MAINLOOP_CONTROLLER'] = False
globalParameter['MAINWEBSERVER'] = True
globalParameter['PROCESS_JARVIS'] = None

globalParameter['openai_api'] = None

app = Flask(__name__)
CORS(app)

class ChatGPTAutomation:

    def __init__(self, openai_api):
        self.openai_api=openai_api
        print(self.openai_api)
        self.client = openai.Client(api_key=globalParameter['openai_api'])

    def getresponse_chatgpt(self, msg):

        mensagens = []
        mensagens.append({"role": "system", "content": "Por favor, retorne respostas curtas, no maximo 2 frases diretas."})
        mensagens.append({"role": "user", "content": msg})

        resposta = self.client.chat.completions.create(
            messages=mensagens,
            model="gpt-3.5-turbo-0125",
            temperature=0,
            max_tokens=1000,
            stream=False
        )

        response = resposta.choices[0].message.content 
        return response

class TestCases_Local(TestCases):
    def test_dump(self):
        check = True
        self.assertTrue(check)    

def LoadVarsIni2(config,sections):
    global globalParameter

    if('GPT' in sections):
        for key in config['GPT']:  
            for globalParameter_key in globalParameter:    
                if globalParameter_key.lower()==key.lower():
                    globalParameter[globalParameter_key]=str(config['GPT'][key])
                    print(key + "=" + str(config['GPT'][key]))   

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
    chatgpt = ChatGPTAutomation(globalParameter['openai_api'])
    loop = True    
    while(loop):
        ask = input(">")
        
        if(ask == None):
            print('...')
            continue

        res = chatgpt.getresponse_chatgpt(ask)
        print(res)

        if(ask == 'tchau'):
            loop = False
            chatgpt.quit()
            break
    pass 

def BotResponse(ask):
    CorrectLocalFunctions()
    GetCorrectPath()    
    res = None
    try:
        chatgpt = ChatGPTAutomation(globalParameter['openai_api'])
        ask = ask.replace('_', ' ')
        res = chatgpt.getresponse_chatgpt(ask)
    except:
        pass
    #print(res)
    return str(res)

def Main():
    """Integration with gptchat for selemium. Same model of chatbot, it can be used for BotIp4Learn method. Use hold4auth for make auth in chatgpt chat."""    

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
            remoteLogTargetIp = GetCorrectIp()
            if(globalParameter['LocalIp'] != '0.0.0.0'): remoteLogTargetIp = globalParameter['LocalIp']
            rl = RemoteLog()
            rl.CheckRestAPIThread(command="chatgpt -base=integration", host = str(remoteLogTargetIp),port=globalParameter['LocalPort'])            
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

    if args['bootresponse'] == True:       
        print(BotResponse(dialog))
        sys.exit()   

    if args['bootloop'] == True:       
        ChatBotLoop()
        sys.exit()           

    param = ' '.join(unknown)
    Main()
