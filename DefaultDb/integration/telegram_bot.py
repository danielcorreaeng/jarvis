import time
import json
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

from telegram import Update, ForceReply,ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler

#ref.: https://raw.githubusercontent.com/python-telegram-bot/python-telegram-bot/master/examples/echobot.py

globalParameter = {}
globalParameter['BotIp'] = '127.0.0.1:8805'
globalParameter['LocalUsername'] = getpass.getuser().replace(' ','_')
globalParameter['LocalHostname'] = socket.gethostname().replace(' ','_')
globalParameter['LastCommand'] = ''
globalParameter['PathLocal'] = os.path.join("C:\\", "Jarvis")
globalParameter['PathJarvis'] = os.path.join("C:\\", "Jarvis", "Jarvis.py")
globalParameter['PathOutput'] = os.path.join(globalParameter['PathLocal'], "Output")
globalParameter['PathExecutable'] = "python"
globalParameter['Token'] = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxx'
globalParameter['AllowedUser'] = None
globalParameter['configFile'] = "config.ini"
globalParameter['TypeTagPhotoOrDocs'] = "[raw]" #"[file]" 
globalParameter['TypeTagVideo'] = "[raw]"

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


def GetCorrectPath():
    global globalParameter

    dir_path = os.path.dirname(os.path.realpath(__file__)) 
    os.chdir(dir_path)
    #print(dir_path)      

    ini_file = os.path.join(dir_path, globalParameter['configFile'])
    #print(ini_file)
    if(os.path.isfile(ini_file) == False):
        ini_file = os.path.join(dir_path, '..', globalParameter['configFile'])
        if(os.path.isfile(ini_file) == False):
            ini_file = os.path.join(dir_path, '..', '..', globalParameter['configFile'])
            if(os.path.isfile(ini_file) == False):
                return
    #print('Found ini')  

    globalParameter['PathExecutable'] = sys.executable
    globalParameter['PathOutput'] = os.path.join(globalParameter['PathLocal'], "Output")

    if(os.path.isfile(ini_file) == True):
        #print('Found ini')
        with open(ini_file) as fp:
            config = configparser.ConfigParser()
            config.read_file(fp)
            sections = config.sections()
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
    """Check\Stores the link and asks for a base|tags."""
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

    return DEFAULT

def define_base_tag(update: Update, context: CallbackContext) -> int:
    """Bot record file."""

    print('user:' + update.message.text)

    cmd = update.message.text
    if 'fileids' in context.user_data:
        for fileid, _type in context.user_data['fileids']:
            print([fileid,_type])
            if(_type == "doc" or _type == "photo"):
                cmd = globalParameter['TypeTagPhotoOrDocs'] + " " + fileid + " [base|tags] " + update.message.text
            elif(_type == "video"):
                cmd = globalParameter['TypeTagVideo'] + " " + fileid + " [base|tags] " + update.message.text
            else:
                continue
            print(cmd)
            res = ChatBot(cmd)
            print('bot:' + res)
    context.user_data['fileids'].clear()
    context.user_data['media_group_id'] = None
    update.message.reply_text(res)
    return DEFAULT

def cancel(update: Update, context: CallbackContext) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    update.message.reply_text(
        'Sorry i got confused.', reply_markup=ReplyKeyboardRemove()
    )

    return DEFAULT

def Main(): 
    '''Telegram Bot. Configuration in config.ini [Telegram].token and [Telegram].alloweduser=@user'''
    
    # Create the Updater and pass it your bot's token.
    updater = Updater(globalParameter['Token'])

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher
    
    if(False):
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
                entry_points=[MessageHandler(Filters.text & ~Filters.command, bot, Filters.user(username=globalParameter['AllowedUser'])), CommandHandler('start', start, Filters.user(username=globalParameter['AllowedUser']))],
                states={
                    DEFAULT: [
                            MessageHandler(Filters.photo, photo, Filters.user(username=globalParameter['AllowedUser'])),
                            MessageHandler(Filters.document, document, Filters.user(username=globalParameter['AllowedUser'])),
                            MessageHandler(Filters.video, videos, Filters.user(username=globalParameter['AllowedUser'])),
                            MessageHandler(Filters.entity('url'), link, Filters.user(username=globalParameter['AllowedUser'])),
                            MessageHandler(Filters.text & ~Filters.command, bot, Filters.user(username=globalParameter['AllowedUser']))],
                    TAGS: [MessageHandler(Filters.text & ~Filters.command, define_base_tag, Filters.user(username=globalParameter['AllowedUser'])), CommandHandler('skip', cancel, Filters.user(username=globalParameter['AllowedUser']))],
                },
                fallbacks=[CommandHandler('cancel', cancel, Filters.user(username=globalParameter['AllowedUser'])), CommandHandler('skip', cancel, Filters.user(username=globalParameter['AllowedUser']))],
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

    GetCorrectPath()

    Main()