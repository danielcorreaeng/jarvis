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

DEFAULT, TAGS, TAGS_VIDEOS = range(3)

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
    print('user:' + update.message.text)
    res = ChatBot(update.message.text)
    print('bot:' + res)
    update.message.reply_text(res)
    return DEFAULT

def photo(update: Update, context: CallbackContext) -> int:
    """Stores the photo and asks for a base|tags."""
    user = update.message.from_user
    photo_file = update.message.photo[-1].get_file()
    print(photo_file) 

    context.user_data['fileid'] = photo_file['file_path']

    update.message.reply_text(
        'Gorgeous! Now, send me <base> <tags> for i record the photo, or send /skip if you don\'t want to.'
    )
    return TAGS


def videos(update: Update, context: CallbackContext) -> int:
    """Stores video and asks for a base|tags."""
    user = update.message.from_user

    document_file=update.message.bot.get_file(update.message.video)
    print(document_file)

    context.user_data['fileid'] = document_file['file_path']

    update.message.reply_text(
        'Gorgeous! Now, send me <base> <tags> for i record the file, or send /skip if you don\'t want to.'
    )
    return TAGS_VIDEOS

def document(update: Update, context: CallbackContext) -> int:
    """Stores the document and asks for a base|tags."""
    user = update.message.from_user
    document_file=update.message.bot.get_file(update.message.document)
    print(document_file)

    context.user_data['fileid'] = document_file['file_path']

    update.message.reply_text(
        'Gorgeous! Now, send me <base> <tags> for i record the file, or send /skip if you don\'t want to.'
    )
    return TAGS    

def define_base_tag(update: Update, context: CallbackContext) -> int:
    """Bot record file."""

    print('user:' + update.message.text)

    cmd = update.message.text
    user_data = context.user_data
    if 'fileid' in user_data:
        print(context.user_data['fileid'])
        cmd = globalParameter['TypeTagPhotoOrDocs'] + " " + context.user_data['fileid'] + " [base|tags] " + update.message.text

        print(cmd)
        del user_data['fileid']

    res = ChatBot(cmd)

    print('bot:' + res)

    update.message.reply_text(res)
    return DEFAULT


def define_base_tag_videos(update: Update, context: CallbackContext) -> int:
    """Bot record videos."""

    print('user:' + update.message.text)

    cmd = update.message.text
    user_data = context.user_data
    if 'fileid' in user_data:
        print(context.user_data['fileid'])
        cmd = globalParameter['TypeTagVideo'] + " " + context.user_data['fileid'] + " [base|tags] " + update.message.text

        print(cmd)
        del user_data['fileid']

    res = ChatBot(cmd)

    print('bot:' + res)

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
                        MessageHandler(Filters.text & ~Filters.command, bot)],
                TAGS: [MessageHandler(Filters.text & ~Filters.command, define_base_tag), CommandHandler('skip', cancel)],
                TAGS_VIDEOS: [MessageHandler(Filters.text & ~Filters.command, define_base_tag_videos), CommandHandler('skip', cancel)],
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
                            MessageHandler(Filters.text & ~Filters.command, bot, Filters.user(username=globalParameter['AllowedUser']))],
                    TAGS: [MessageHandler(Filters.text & ~Filters.command, define_base_tag, Filters.user(username=globalParameter['AllowedUser'])), CommandHandler('skip', cancel, Filters.user(username=globalParameter['AllowedUser']))],
                    TAGS_VIDEOS: [MessageHandler(Filters.text & ~Filters.command, define_base_tag_videos), CommandHandler('skip', cancel)],
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