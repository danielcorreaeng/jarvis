import sys,os
import argparse
import unittest
import configparser
from time import sleep
import subprocess

from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer, ListTrainer
from chatterbot.comparisons import levenshtein_distance

from flask import Flask, redirect, url_for, request, render_template
from flask_cors import CORS

globalParameter = {}
globalParameter['LocalPort'] = 8805
globalParameter['LocalIp'] = "0.0.0.0"
globalParameter['MAINWEBSERVER'] = True
globalParameter['PathDB'] = "db.sqlite3"
globalParameter['maximum_similarity_threshold'] = 0.80

globalParameter['FileJarvis'] = "Jarvis.py"
globalParameter['PathLocal'] = os.path.join("C:\\","Jarvis")
globalParameter['PathJarvis'] = os.path.join("C:\\","Jarvis", globalParameter['FileJarvis'])
globalParameter['PathOutput'] = os.path.join(globalParameter['PathLocal'],"Output")
globalParameter['PathExecutable'] = "python"
globalParameter['configFile'] = "config.ini"
globalParameter['allowedexternalrecordbase'] = ""
globalParameter['flaskstatic_folder'] = 'External'

#chatbot jarvis updated Feb 4th, 2023 - https://github.com/danielcorreaeng/jarvis

app = Flask(__name__, static_url_path="/" + globalParameter['flaskstatic_folder'], static_folder=globalParameter['flaskstatic_folder'])
CORS(app)

class TestCases(unittest.TestCase):
    def test_dump(self):
        check = True
        self.assertTrue(check)

def Run(command, parameters=None, wait=False):
    if(globalParameter['PathJarvis'] == None):
        return

    if(parameters != None):
        proc = subprocess.Popen([command, parameters], stdout=subprocess.PIPE, shell=True)
    else:
        proc = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)

    if(wait == True):
        proc.communicate()

def RunJarvis(tags):
	Run(globalParameter['PathExecutable'] + ' ' + globalParameter['PathJarvis'] + ' ' + tags, None, False)  

class MyChatBot():
    def __init__(self):
        noob = False        
        if os.path.isfile(str(globalParameter['PathDB'])) == False:
            noob = True
            print('mode noob')
        else:
            print('mode noob off')
        
        self.chatbot = ChatBot(
            'Jarvis',
            storage_adapter='chatterbot.storage.SQLStorageAdapter',
            database_uri='sqlite:///' + str(globalParameter['PathDB']),
            logic_adapters=[
                {
                    'import_path': 'chatterbot.logic.BestMatch',
                    'default_response': 'Não entendi',
                    'maximum_similarity_threshold': globalParameter['maximum_similarity_threshold']
                }
            ]
        )

        if noob == True:
            self.training4memory()
		
    def __del__(self):
        pass

    def training4conversation(self, conversation):
        #conversation = ["oi","olá", "Tchau","Até logo", "=)","Legal"]
        trainer = ListTrainer(self.chatbot)
        trainer.train(conversation)
    
    def training4memory(self):
        trainer = ChatterBotCorpusTrainer(self.chatbot)
        #trainer.train("chatterbot.corpus.english")
        #trainer.train("chatterbot.corpus.portuguese")

        print('training4memory')
        if(os.path.exists("pt")==True):
            trainer.train("pt")
            print('training4memory pt')
        else:
            trainer.train("chatterbot.corpus.portuguese")
            print('training4memory corpus.portuguese')

    def response(self, ask):
        target = None
        flag = ''

        if(str(ask).lower().find('[img]') >= 0):
            target = '[img]'
        elif(str(ask).lower().find('[file]') >= 0):
            target = '[file]'
        elif(str(ask).lower().find('[link]') >= 0):
            target = '[link]'     
        elif(str(ask).lower().find('.mp4') >= 0):
            target = '[raw]'         
            flag = '-f'    
        elif(str(ask).lower().find('[raw]') >= 0):
            target = '[raw]'         
            flag = '-f'                
        elif(str(ask).lower().find('[jsonnote]') >= 0):
            target = '[jsonnote]'  
            flag = '-n'
        elif(str(ask).lower().find('[jsonlink]') >= 0):
            target = '[jsonlink]'                                 
            flag = '-l'

        if(target != None and str(ask).lower().find('[base|tags]') >= 0):
            tags = ask.split('[base|tags]')[1]
            target = ask.split('[base|tags]')[0].replace(target,'')
            target = target[1:-1].replace(' ','_')
            #print(tags)
            #print(target)
            cmd = 'bookmark -base=services -u ' + str(globalParameter['allowedexternalrecordbase']) + str(tags) + " " + str(flag) + " " + str(target)
            print(cmd)
            RunJarvis(cmd)

            result = 'got it! :P'

            if(str(globalParameter['allowedexternalrecordbase']) != ""):
                result = result + " (recorded in base " + str(globalParameter['allowedexternalrecordbase']) + ")"

            return result

        if(str(ask).lower().find('[learn]') >= 0 and str(ask).lower().find('[answer]') >= 0):
            answer = ask.split('[answer]')[1]
            ask = ask.split('[answer]')[0].replace('[learn]','')            
            self.training4conversation([ask, str(answer)])          

        res = self.chatbot.get_response(ask)

        return res            

def BotResponse(ask):
    bot = MyChatBot()
    ask = ask.replace('_', ' ')
    #print(ask)
    res = bot.response(ask)   
    print(res) 
    return str(res)

def ChatBotLoop(Learn = False):    
    bot = MyChatBot()
    loop = True    
    
    while(loop):
        ask = input(">")
        
        if(ask == None):
            print('...')
            continue

        res = bot.response(ask)

        print(res)

        if(Learn==True and str(res) == "Não entendi"):
            print("Deseja que eu aprenda?")
            res = input(">")
            if(res == 'sim'):
                print(ask)
                res4train = input(">")
                bot.training4conversation([ask, str(res4train)])          
        else:
            pass

        if(ask == 'tchau'):
            loop = False
            break
    pass 

@app.route('/botresponse',methods = ['POST', 'GET'])
def botresponse():
    if request.method == 'POST':
        data = request.get_json(force=True)  
        #ask = str(data[0])
        #print(ask)
        return BotResponse(data['ask'])
    else:
        ask = request.args.get('ask')
        return BotResponse(ask)

def description():
    return str(Main.__doc__) + " | ip server : " +  str(globalParameter['LocalIp']) + ":" + str(globalParameter['LocalPort'])

@app.route('/')
def index():
    return description()

def LoadVarsIni(config,sections):
    pass

def GetCorrectPath():
    global globalParameter

    dir_path = os.path.dirname(os.path.realpath(__file__)) 
    os.chdir(dir_path)

    jarvis_file = os.path.join(dir_path, globalParameter['FileJarvis'])
    ini_file = os.path.join(dir_path, globalParameter['configFile'])
    if(os.path.isfile(ini_file) == False):
        jarvis_file = os.path.join(dir_path, '..', globalParameter['FileJarvis'])
        ini_file = os.path.join(dir_path, '..', globalParameter['configFile'])
        if(os.path.isfile(ini_file) == False):
            jarvis_file = os.path.join(dir_path, '..', '..', globalParameter['FileJarvis'])
            ini_file = os.path.join(dir_path, '..', '..', globalParameter['configFile'])
            if(os.path.isfile(ini_file) == False):
                return
    
    globalParameter['PathExecutable'] = sys.executable
    globalParameter['PathLocal'] = os.path.dirname(os.path.realpath(jarvis_file))
    globalParameter['PathJarvis'] = jarvis_file
    globalParameter['PathOutput'] = os.path.join(globalParameter['PathLocal'], "Output")

    if(os.path.isfile(ini_file) == True):
        with open(ini_file) as fp:
            config = configparser.ConfigParser()
            config.read_file(fp)
            sections = config.sections()
            if('Parameters' in sections):
                for key in config['Parameters']:  
                    for globalParameter_key in globalParameter:    
                        if globalParameter_key.lower()==key.lower():
                            globalParameter[globalParameter_key]=str(config['Parameters'][key])
                            print(key + "=" + str(config['Parameters'][key]))  
            LoadVarsIni(config,sections)      

    jarvis_file = globalParameter['PathJarvis']
    if(os.path.isfile(jarvis_file) == False):
        globalParameter['PathJarvis'] = None
    else:
        print("Jarvis command enabled")          

def Main():
    """api chat bot aiml | Optional parameters: -p (--port) to select target port"""

    global globalParameter

    GetCorrectPath()

    try:
        if(globalParameter['MAINWEBSERVER'] == True):
            #app.run(host = str(globalParameter['LocalIp']),port=globalParameter['LocalPort'], ssl_context='adhoc') 
            app.run(host = str(globalParameter['LocalIp']),port=globalParameter['LocalPort']) 
        pass
    except:
        print('error webservice')
    
if __name__ == '__main__':   
    os.chdir(os.path.dirname(__file__))   

    parser = argparse.ArgumentParser(description=Main.__doc__)
    parser.add_argument('-d','--description', help='Description of program', action='store_true')
    parser.add_argument('-u','--tests', help='Execute tests', action='store_true')
    parser.add_argument('-t','--train', help='Active autotrain', action='store_true')
    parser.add_argument('-l','--bootloop', help='Chatbot in loop', action='store_true')
    parser.add_argument('-r','--bootresponse', help='Chatbot response input', action='store_true')
    parser.add_argument('-p','--port', help='Service running in target port')
    parser.add_argument('-c','--config', help='Config.ini file')
    parser.add_argument('-i','--ip', help='Service running in target ip') 
    
    
    args, unknown = parser.parse_known_args()
    args = vars(args)
    train = False 

    param = ' '.join(unknown)
    dialog = ' '.join(unknown)
    
    if args['description'] == True:
        print(Main.__doc__)
        sys.exit()

    if args['tests'] == True:       
        suite = unittest.TestSuite()
        suite.addTest(TestCases("test_dump")) 
        runner = unittest.TextTestRunner()
        runner.run(suite)          
        sys.exit()     

    if args['train'] == True:       
        train = True 

    if args['bootloop'] == True:       
        ChatBotLoop(train)
        sys.exit()           

    if args['bootresponse'] == True:       
        print(BotResponse(dialog))
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

    Main()