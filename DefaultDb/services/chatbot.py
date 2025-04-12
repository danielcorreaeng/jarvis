import sys,os
import argparse
import unittest
import configparser
from time import sleep
import subprocess
import requests
import datetime
import json
import getpass
import socket
import sqlite3
import numpy as np

from flask import Flask, redirect, url_for, request, render_template
from flask_cors import CORS

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
import nltk
from nltk.corpus import stopwords

globalParameter = {}
globalParameter['LocalPort'] = 8805
globalParameter['LocalIp'] = '0.0.0.0'
globalParameter['LocalUsername'] = getpass.getuser().replace(' ','_')
globalParameter['LocalHostname'] = socket.gethostname().replace(' ','_')
globalParameter['MAINWEBSERVER'] = True
globalParameter['PathDB'] = "db2.sqlite3"
globalParameter['maximum_similarity_threshold'] = 0.50
globalParameter['unanswered_answer'] = 'Não entendi'

globalParameter['FileJarvis'] = "Jarvis.py"
globalParameter['PathLocal'] = os.path.join("C:\\","Jarvis")
globalParameter['PathJarvis'] = os.path.join("C:\\","Jarvis", globalParameter['FileJarvis'])
globalParameter['PathOutput'] = os.path.join(globalParameter['PathLocal'],"Output")
globalParameter['PathExecutable'] = "python"
globalParameter['configFile'] = "config.ini"
globalParameter['allowedexternalrecordbase'] = ""
globalParameter['flaskstatic_folder'] = 'External'

globalParameter['TriggerTags'] = '[img],[file],[link],[raw],[jsonnote],[jsonlink],[jsonlinkfile],[jsonnotefile]'
globalParameter['TriggerTagsList'] = []
globalParameter['BotIp4Learn'] = None
globalParameter['BotName'] = 'Jarvis'

#chatbot jarvis updated Abril 15, 2025 - https://github.com/danielcorreaeng/jarvis

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
    command = str(globalParameter['PathExecutable']) + ' ' + str(globalParameter['PathJarvis']) + ' ' + tags
    print(command)
    Run(command, None, False)  

def ChatBotExternal(message, BotIp):
    result = None
    try:
        request = requests.get('http://' + BotIp)
        if request.status_code == 200:
            localTime = datetime.datetime.now().strftime("%Y%m%d_%H%M%S%f")
            data = {'ask' : message , 'user' : globalParameter['LocalUsername'] , 'host' : globalParameter['LocalHostname'] , 'command' : None , 'time' : localTime , 'status' : 'start'}

            url = "http://" + BotIp + "/botresponse"
            headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
            r = requests.post(url, data=json.dumps(data), headers=headers)
            result = r.text
            print(result)

            if(result == "None"):
                result = None                
        else:
            result = None
    except:
        result = None
        pass

    return result

class MyChatBot():
    def __init__(self):
        self.botname = str(globalParameter['BotName'])
        self.db_path = str(globalParameter['PathDB'])
        self.unanswered_answer = globalParameter['unanswered_answer']
        self.threshold = float(globalParameter['maximum_similarity_threshold'])
        
        # Carregar NLTK recursos necessários
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt', quiet=True)
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords', quiet=True)
            
        self.stop_words = set(stopwords.words('portuguese'))
        
        # Inicializar o vetorizador TF-IDF
        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            strip_accents='unicode',
            ngram_range=(1, 2),
            max_features=5000
        )
        
        # Verificar se o banco existe, caso contrário criar
        self.initialize_database()
        
        # Carregar dados para memória
        self.questions, self.answers = self.load_data_from_db()
        
        # Criar vetores TF-IDF se houver dados
        if len(self.questions) > 0:
            self.question_vectors = self.vectorizer.fit_transform(self.questions)
        else:
            self.question_vectors = None
    
    def __del__(self):
        pass
    
    def initialize_database(self):
        """Inicializa o banco de dados SQLite se não existir"""
        if os.path.isfile(self.db_path) == False:
            print('Criando banco de dados')
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Criar tabela para armazenar as conversas
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                botname TEXT NOT NULL
            )
            ''')
            
            conn.commit()
            conn.close()
    
    def preprocess_text(self, text):
        """Pré-processamento de texto para melhorar comparações"""
        # Converter para minúsculas
        text = text.lower()
        # Remover caracteres especiais e manter apenas letras e números
        text = re.sub(r'[^\w\s]', '', text)
        # Tokenização
        tokens = nltk.word_tokenize(text, language='portuguese')
        # Remover stopwords
        tokens = [word for word in tokens if word not in self.stop_words]
        # Juntar tokens novamente
        return ' '.join(tokens)
    
    def load_data_from_db(self):
        """Carrega os dados do banco SQLite para a memória, filtrando pelo nome do bot"""
        questions = []
        answers = []
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Consultar apenas as conversas deste bot específico
        cursor.execute("SELECT question, answer FROM conversations WHERE botname = ?", (self.botname,))
        rows = cursor.fetchall()
        
        for row in rows:
            questions.append(self.preprocess_text(row[0]))
            answers.append(row[1])
        
        conn.close()
        
        print(f"Bot '{self.botname}': Carregados {len(questions)} pares de pergunta-resposta da base.")
        return questions, answers
    
    def find_best_match(self, query):
        """Encontra a melhor correspondência para a pergunta do usuário"""
        if not self.questions or len(self.questions) == 0:
            return None, 0.0
        
        # Pré-processar a consulta
        processed_query = self.preprocess_text(query)
        
        # Transformar a consulta usando o vetorizador
        query_vector = self.vectorizer.transform([processed_query])
        
        # Calcular a similaridade com todas as perguntas
        similarity_scores = cosine_similarity(query_vector, self.question_vectors).flatten()
        
        # Encontrar o índice da melhor correspondência
        best_match_index = np.argmax(similarity_scores)
        best_match_score = similarity_scores[best_match_index]
        
        return best_match_index, best_match_score
    
    def training4conversation(self, conversation):
        """Adiciona novas conversas ao banco de dados"""
        if len(conversation) < 2:
            print("Erro: A conversa deve conter pelo menos uma pergunta e uma resposta")
            return
        
        # Extrair pergunta e resposta
        question = conversation[0]
        answer = conversation[1]
        
        # Salvar no banco
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO conversations (question, answer, botname) VALUES (?, ?, ?)", (question, answer, self.botname)
        )
        
        conn.commit()
        conn.close()
        
        # Atualizar a memória local
        processed_question = self.preprocess_text(question)
        self.questions.append(processed_question)
        self.answers.append(answer)
        
        # Atualizar os vetores
        self.question_vectors = self.vectorizer.fit_transform(self.questions)
        
        print(f"Adicionado à base: '{question}' -> '{answer}'")
    
    def training4memory(self):
        """Carrega corpus para o treinamento inicial"""
        print('training4memory')
        corpus_data = []
        
        if os.path.exists("pt") == True:
            # Carregar corpus personalizado do diretório 'pt'
            print('training4memory pt')
            for filename in os.listdir("pt"):
                if filename.endswith(".txt"):
                    file_path = os.path.join("pt", filename)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        
                    # Processar linhas como pares de pergunta-resposta
                    for i in range(0, len(lines) - 1, 2):
                        if i + 1 < len(lines):
                            question = lines[i].strip()
                            answer = lines[i + 1].strip()
                            if question and answer:
                                corpus_data.append([question, answer])
        else:
            # Usar alguns exemplos básicos em português
            print('training4memory corpus básico')
            corpus_data = [
                ["oi", "olá"],
                ["como vai?", "estou bem, e você?"],
                ["qual é o seu nome?", "meu nome é Jarvis"],
                ["tchau", "até logo"],
                ["ajuda", "como posso ajudar você?"]
            ]
        
        # Adicionar dados ao banco
        for pair in corpus_data:
            self.training4conversation(pair)
    
    def responseTriggerTags(self, ask):
        # Mantido como no código original
        print(ask)
        target = None
        flag = ''
        tags = ''

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
        elif(str(ask).lower().find('[jsonlinkfile]') >= 0):
            target = '[jsonlinkfile]'                                 
            flag = '-j'     
        elif(str(ask).lower().find('[jsonnotefile]') >= 0):
            target = '[jsonnotefile]'                                 
            flag = '-t'                        

        if(target != None and str(ask).lower().find('[base|tags]') >= 0):
            tags = ask.split('[base|tags]')[1]
            target = ask.split('[base|tags]')[0].replace(target,'')
            target = target[1:-1].replace(' ','_')
            cmd = 'bookmark -base=services -u ' + str(globalParameter['allowedexternalrecordbase']) + str(tags) + " " + str(flag) + " " + str(target)
            print(cmd)
            RunJarvis(cmd)

            result = 'got it! :P'

            if(str(globalParameter['allowedexternalrecordbase']) != ""):
                result = result + " (recorded in base " + str(globalParameter['allowedexternalrecordbase']) + ")"
            
            return result
    
    def response(self, ask):
        """Responde a uma pergunta do usuário"""
        # Verificar por tags especiais primeiro
        for triggerTags in globalParameter['TriggerTagsList']:
            if(str(ask).lower().find(triggerTags) >= 0):
                result = self.responseTriggerTags(ask)
                return result

        # Verificar se é uma solicitação de aprendizado
        if(str(ask).lower().find('[learn]') >= 0 and str(ask).lower().find('[answer]') >= 0):
            answer = ask.split('[answer]')[1]
            if answer[0] == ' ':
                answer = answer[1:]
            ask = ask.split('[answer]')[0].replace('[learn]','')            
            self.training4conversation([ask, str(answer)])
            return answer

        # Buscar a melhor correspondência
        best_match_index, best_match_score = self.find_best_match(ask)
        #print(best_match_score)
        
        # Responder com base no limiar de similaridade
        if best_match_score >= self.threshold:
            res = self.answers[best_match_index]
        else:
            res = self.unanswered_answer
            
            # Tente aprender de outro bot, se configurado
            if(globalParameter['BotIp4Learn'] is not None and str(res) == str(self.unanswered_answer)):  
                answer = ChatBotExternal(ask, globalParameter['BotIp4Learn'])
                if(answer is not None):
                    self.training4conversation([ask, str(answer)])              
                    best_match_index, best_match_score = self.find_best_match(ask)
                    if best_match_score >= self.threshold:
                        res = self.answers[best_match_index]
        
        return res          

def BotResponse(ask):
    bot = MyChatBot()
    ask = ask.replace('_', ' ')
    #print(ask)
    res = bot.response(ask)   
    #print(res) 
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

        if(Learn==True and str(res) == str(globalParameter['unanswered_answer'])):
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

        if 'tag' in data:
            ask = data['ask'] + " [" +  data['tag'] + "]" 
            response = BotResponse(ask)
            print(['tag : ' +  data['tag'], ask, response])

            if(response == globalParameter['unanswered_answer']):
                ask = data['ask']
                response = BotResponse(ask)  
                #print(['without tag response', ask, response])             
        else:
            ask = data['ask']
            response = BotResponse(ask)     

        #print(['result', ask, response])

        if 'acceptTags' in data:
            if data['acceptTags']=='1':
                return response

        response = response.split('[')[0]
        #print(['final ', ask, response])
        print([ask, response])

        #ask = str(data[0])
        #print(ask)
        return response
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

    globalParameter['TriggerTagsList'] = str(globalParameter['TriggerTags']).split(',')

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