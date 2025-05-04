import time
import json
import glob
import sys,os
import subprocess
import argparse
import configparser
import getpass
import datetime
import socket
import requests
import bs4
import requests
import random
from jarvis_utils import *

from telegram import Update, ForceReply,ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler

#ref.: https://raw.githubusercontent.com/python-telegram-bot/python-telegram-bot/master/examples/echobot.py

globalParameter['INPUT_DATA_OFF'] = False
globalParameter['OUTPUT_DATA_OFF'] = False
globalParameter['MAINLOOP_CONTROLLER'] = False
globalParameter['MAINWEBSERVER'] = False
globalParameter['PROCESS_JARVIS'] = None

globalParameter['LocalPort'] = 8810
globalParameter['BotIp'] = '127.0.0.1:8805'
globalParameter['PublicIp'] = ''
globalParameter['LastCommand'] = ''
globalParameter['Token'] = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxx'
globalParameter['AllowedUser'] = None
globalParameter['configFile'] = "config.ini"
globalParameter['allowedexternalrecordbase'] = "telegram"
globalParameter['maximumfileupload'] = '5'

globalParameter['PINTEREST_IMAGECLASS'] = 'hCL kVc L4E MIw'

DEFAULT, TAGS = range(2)

def get_link_from_url_pinterest(link):
    with requests.Session() as s:
        html_page = s.get(link,headers={"User-Agent":"Mozilla/5.0"})
        soup = bs4.BeautifulSoup(html_page.text,'html.parser')

        link = soup.find("img", class_=globalParameter['PINTEREST_IMAGECLASS']).get('src')

    return link   

def ChatBot(message):
    error = 'Hi! Sorry... No service now =('
    result = error
    try:
        request = requests.get('http://' + globalParameter['BotIp'])
        if request.status_code == 200:
            localTime = datetime.datetime.now().strftime("%Y%m%d_%H%M%S%f")
            data = {'ask' : message , 'user' : globalParameter['LocalUsername'] , 'host' : globalParameter['LocalHostname'] , 'command' : globalParameter['LastCommand'] , 'time' : localTime , 'status' : 'start'}
            
            url = "http://" + globalParameter['BotIp'] + "/botresponse"
            headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
            r = requests.post(url, data=json.dumps(data), headers=headers)
            result = r.text
        else:
            result = error
    except:
        result = error
    pass
    
    return result           

def LoadVarsIni2(config,sections):
    global globalParameter

    if('Telegram' in sections):
        #print('Telegram')
        for key in config['Telegram']:         
            if(key.lower()=='token'):
                globalParameter['Token'] = config['Telegram'][key]
                print('Token Loaded')
            if(key.lower()=='alloweduser'):
                globalParameter['AllowedUser'] = config['Telegram'][key]
                print('AllowedUser=' + globalParameter['AllowedUser'])
                
    if('Parameters' in sections):
        for key in config['Parameters']:         
            if(key.lower()=='botip'):     
                globalParameter['BotIp']=config['Parameters'][key]  
                print('BotIp=' + globalParameter['BotIp'])                

def start(update: Update, context: CallbackContext) -> int:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Hi {user.mention_markdown_v2()}\!',
        reply_markup=ForceReply(selective=True),
    )
    return DEFAULT

def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')

def echo(update: Update, context: CallbackContext) -> None:
    """Echo the user message."""
    print(update.message.text)
    update.message.reply_text(update.message.text)

def ip(update: Update, context: CallbackContext) -> int:
    """Send IP."""
    ip = "Local ip : " + str(globalParameter['LocalIp'] ) # + " \nPublic ip : " + str(globalParameter['PublicIp']) 
    print(ip)
    update.message.reply_text(ip)    
    return DEFAULT    

def bot(update: Update, context: CallbackContext) -> int:
    """Bot response message."""

    if context.user_data.get('fileids') == None:
        context.user_data['fileids'] = []
    if context.user_data.get('media_group_id') == None:
        context.user_data['media_group_id'] = None

    if context.user_data['media_group_id'] != None:
        update.message.reply_text('Gorgeous! Now, send me <base> <tags> for i record multi photos, or send /skip if you don\'t want to.')
        return TAGS

    print('user:' + update.message.text)
    res = ChatBot(update.message.text)
    print('bot:' + res)
    update.message.reply_text(res)
    return DEFAULT

def photo(update: Update, context: CallbackContext) -> int:
    """Stores the photo and asks for a base|tags."""
    user = update.message.from_user

    photo = update.message.photo[-1] 
    photo_file = photo.get_file()

    context.user_data['fileids'].append([photo_file['file_path'], "photo"])
    if(update.message.media_group_id != None):        
        if(context.user_data['media_group_id'] == None):
            update.message.reply_text('Im receiving multiple files, when you stop sending them, say hi.')
        context.user_data['media_group_id'] = update.message.media_group_id
        return DEFAULT
    
    update.message.reply_text('Gorgeous! Now, send me <base> <tags> for i record the photo, or send /skip if you don\'t want to.')
    return TAGS


def videos(update: Update, context: CallbackContext) -> int:
    """Stores video and asks for a base|tags."""

    try:
        user = update.message.from_user
        document_file=update.message.bot.get_file(update.message.video)
        print(document_file)

        context.user_data['fileids'].append([document_file['file_path'], "video"])
        if(update.message.media_group_id != None):        
            if(context.user_data['media_group_id'] == None):
                update.message.reply_text('Im receiving multiple files, when you stop sending them, say hi.')
            context.user_data['media_group_id'] = update.message.media_group_id
            return DEFAULT      

        update.message.reply_text('Gorgeous! Now, send me <base> <tags> for i record the file, or send /skip if you don\'t want to.')
        return TAGS
    except:
        pass

    update.message.reply_text('Ops! Something wrong happened.')
    
    return DEFAULT

def document(update: Update, context: CallbackContext) -> int:
    """Stores the document and asks for a base|tags."""
    user = update.message.from_user
    document_file=update.message.bot.get_file(update.message.document)
    print(document_file)

    context.user_data['fileids'].append([document_file['file_path'], "doc"])
    if(update.message.media_group_id != None):        
        if(context.user_data['media_group_id'] == None):
            update.message.reply_text('Im receiving multiple files, when you stop sending them, say hi.')
        context.user_data['media_group_id'] = update.message.media_group_id
        return DEFAULT
    
    update.message.reply_text(
        'Gorgeous! Now, send me <base> <tags> for i record the file, or send /skip if you don\'t want to.'
    )
    return TAGS    

def link(update: Update, context: CallbackContext) -> int:
    """Check-Stores the link and asks for a base-tags."""
    user = update.message.from_user
    text = update.message.text + str(' ')

    addr_link_start = text.find('http')
    addr_link_end = text.find(' ', addr_link_start+1)
    link = text[addr_link_start:addr_link_end]

    update.message.reply_text('link: ' + str(link))

    if 'pin.it' in link or 'pinterest.com' in link: 
        link = get_link_from_url_pinterest(link)

        if(link!=None):
            update.message.reply_text('pinterest link: ' + str(link))
            context.user_data['fileids'].append([str(link), "photo"])

            update.message.reply_text('Gorgeous! Now, send me <base> <tags> for i record the photo, or send /skip if you don\'t want to.')
            return TAGS
    else:
            update.message.reply_text('Gorgeous! Now, send me <base> <tags> for i record the link, or send /skip if you don\'t want to.')
            context.user_data['fileids'].append([str(link), "link"])
            return TAGS       

    return DEFAULT

def define_base_tag(update: Update, context: CallbackContext) -> int:
    """Bot record file."""

    print('user:' + update.message.text)

    cmd = update.message.text
    res = "..."

    if 'fileids' in context.user_data:
        for fileid, _type in context.user_data['fileids']:
            print([fileid,_type])

            tags = str(update.message.text)
            localpath = os.path.join(globalParameter['PathDB_All'], globalParameter['allowedexternalrecordbase'])            
            id_unique = str(datetime.datetime.now().strftime("%Y%m%d")) + " " + str(datetime.datetime.now().strftime("%H%M%S%f"))  + " " + str(randint(0, 999))

            if(_type == "doc" or _type == "photo" or _type == "video"):
                extension = os.path.splitext(fileid)[1]
                file = os.path.join(localpath, tags + " " + id_unique + extension)
                
                if(os.path.exists(localpath) == False):
                    os.mkdir(localpath)

                f = open(file,'wb')
                response = requests.get(fileid)
                f.write(response.content)
                f.close()    

            elif(_type == "link"):
                file = os.path.join(localpath, tags + " " + id_unique + '.json')

                if(os.path.exists(localpath) == False):
                    os.mkdir(localpath)

                data = { 'link' :  fileid }

                print(file)
                f = open(file,'w')
                json.dump(data, f, ensure_ascii=False, indent=4)
                f.close()
            else:
                continue
            print(cmd)
            res = 'got it!!!'
            print('bot:' + res)
    context.user_data['fileids'].clear()
    context.user_data['media_group_id'] = None
    update.message.reply_text(res)
    return DEFAULT

def search_command(update: Update, context: CallbackContext) -> None:
    """Search for files with specified tags and return examples."""
    # Verifica se a mensagem contém tags após o comando
    if not context.args:
        update.message.reply_text('Please, use: /search <tags>')
        return

    # Obtém as tags da pesquisa
    search_tags = ' '.join(context.args).lower()
    print(f"Searching for: {search_tags}")
    
    # Diretório onde os arquivos estão armazenados
    search_dir = os.path.join(globalParameter['PathDB_All'], globalParameter['allowedexternalrecordbase'])
    
    if not os.path.exists(search_dir):
        update.message.reply_text(f"Path dont find: {search_dir}")
        return
    
    # Lista todos os arquivos no diretório
    all_files = glob.glob(os.path.join(search_dir, "*"))
    
    # Filtra os arquivos que contêm as tags
    matches = []
    for file_path in all_files:
        file_name = os.path.basename(file_path).lower()
        if search_tags in file_name:
            matches.append(file_path)
    
    if not matches:
        update.message.reply_text(f"No files found with tags: {search_tags}")
        return
    
    update.message.reply_text(f"Found {len(matches)} file(s) with tags: {search_tags}.")

    if len(matches) > int(globalParameter['maximumfileupload']):
        matches = random.sample(matches, int(globalParameter['maximumfileupload']))
        update.message.reply_text(f"I will send {len(matches)} examples.")

    # Envia cada arquivo encontrado
    for file_path in matches:
        file_name = os.path.basename(file_path)
        file_extension = os.path.splitext(file_path)[1].lower()
        
        try:
            # Para arquivos de imagem
            if file_extension in ['.jpg', '.jpeg', '.png', '.gif']:
                with open(file_path, 'rb') as photo_file:
                    update.message.reply_photo(photo=photo_file, caption=file_name)
            
            # Para arquivos de vídeo
            elif file_extension in ['.mp4', '.avi', '.mov', '.mkv']:
                with open(file_path, 'rb') as video_file:
                    update.message.reply_video(video=video_file, caption=file_name)
            
            # Para arquivos JSON (links)
            elif file_extension == '.json':
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    if 'link' in data:
                        update.message.reply_text(f"{file_name}\nLink: {data['link']}")
                    else:
                        update.message.reply_document(document=open(file_path, 'rb'), caption=file_name)
            
            # Para outros tipos de arquivo
            else:
                with open(file_path, 'rb') as doc_file:
                    update.message.reply_document(document=doc_file, caption=file_name)
                    
        except Exception as e:
            update.message.reply_text(f"Error sending file {file_name}: {str(e)}")
    
    update.message.reply_text("Enjoy!")

def cancel(update: Update, context: CallbackContext) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    update.message.reply_text(
        'Sorry i got confused.', reply_markup=ReplyKeyboardRemove()
    )

    return DEFAULT

def Main(): 
    '''Telegram Bot. Configuration in config.ini [Telegram].token and [Telegram].alloweduser=@user'''

    global globalParameter

    globalsub.subs(LoadVarsIni, LoadVarsIni2)
    
    GetCorrectPath()

    try:        
        if(globalParameter['LocalIp'] == '0.0.0.0'):
            globalParameter['LocalIp'] = GetCorrectIp()
        globalParameter['PublicIp'] = GetPublicIp()
    except:
        print('error ip')

    # Create the Updater and pass it your bot's token.
    updater = Updater(globalParameter['Token'])

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher
    
    if(False):
        #only for example proposal 
        conv_handler = ConversationHandler(
            entry_points=[MessageHandler(Filters.text & ~Filters.command, bot), CommandHandler('start', start)],
            states={
                DEFAULT: [
                        MessageHandler(Filters.photo, photo),
                        MessageHandler(Filters.document, document),
                        MessageHandler(Filters.video, videos),
                        MessageHandler(Filters.entity('url'), link),
                        MessageHandler(Filters.text & ~Filters.command, bot)],
                TAGS: [MessageHandler(Filters.text & ~Filters.command, define_base_tag), CommandHandler('skip', cancel)],
            },
            fallbacks=[CommandHandler('cancel', cancel), CommandHandler('skip', cancel)],
        )

    if(globalParameter['AllowedUser'] != None):
            conv_handler = ConversationHandler(
                entry_points=[MessageHandler(Filters.text & ~Filters.command & Filters.user(username=globalParameter['AllowedUser']), start), CommandHandler('start', start, Filters.user(username=globalParameter['AllowedUser']))],
                states={
                    DEFAULT: [
                            MessageHandler(Filters.photo & Filters.user(username=globalParameter['AllowedUser']), photo),
                            MessageHandler(Filters.document & Filters.user(username=globalParameter['AllowedUser']), document),
                            MessageHandler(Filters.video & Filters.user(username=globalParameter['AllowedUser']), videos),
                            MessageHandler(Filters.entity('url') & Filters.user(username=globalParameter['AllowedUser']), link),
                            MessageHandler(Filters.text & ~Filters.command & Filters.user(username=globalParameter['AllowedUser']), bot)],
                    TAGS: [MessageHandler(Filters.text & ~Filters.command & Filters.user(username=globalParameter['AllowedUser']), define_base_tag), CommandHandler('skip', cancel, Filters.user(username=globalParameter['AllowedUser']))],
                },
                fallbacks=[
                    CommandHandler('cancel', cancel, Filters.user(username=globalParameter['AllowedUser'])), 
                    CommandHandler('skip', cancel, Filters.user(username=globalParameter['AllowedUser'])), 
                    CommandHandler('ip', ip, Filters.user(username=globalParameter['AllowedUser'])),
                    CommandHandler('search', search_command, Filters.user(username=globalParameter['AllowedUser']))
                ],
                    
            )

    dispatcher.add_handler(conv_handler)    

    '''
    # on different commands - answer in Telegram
    if(globalParameter['AllowedUser'] == None):
        dispatcher.add_handler(CommandHandler("start", start))
    else:
        dispatcher.add_handler(CommandHandler("start", start, Filters.user(username=globalParameter['AllowedUser'])))

    dispatcher.add_handler(CommandHandler("help", help_command))

    # on non command i.e message - echo the message on Telegram

    if(globalParameter['AllowedUser'] == None):
        dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, bot))
    else:
        dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command & Filters.user(username=globalParameter['AllowedUser']), bot))
        dispatcher.add_handler(MessageHandler(Filters.photo & Filters.user(username=globalParameter['AllowedUser']), photo ))

    dispatcher.add_handler(states={ TAGS: [MessageHandler(Filters.text & ~Filters.command, define_base_tag)], })
    '''

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=Main.__doc__)
    parser.add_argument('-d','--description', help='Description of program', action='store_true')
    parser.add_argument('-i','--file_input', help='data entry via file (path)')
    parser.add_argument('-o','--file_output', help='output data via file (path)')
    parser.add_argument('-c','--config', help='Config.ini file')       
    
    args, unknown = parser.parse_known_args()
    args = vars(args)
    
    if args['description'] == True:
        print(Main.__doc__)
        sys.exit()

    if args['config'] is not None:
        print('Config.ini: ' + args['config'])
        globalParameter['configFile'] = args['config']  

    param = ' '.join(unknown)

    Main()