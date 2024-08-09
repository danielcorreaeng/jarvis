import time
import re
from slackclient import SlackClient
import requests
import datetime
import json
import getpass
import socket
import sys

globalParameter = {}
globalParameter['BotIp'] = '127.0.0.1:8805'
globalParameter['LocalUsername'] = getpass.getuser().replace(' ','_')
globalParameter['LocalHostname'] = socket.gethostname().replace(' ','_')
globalParameter['LastCommand'] = ''

#code example: https://www.fullstackpython.com/blog/build-first-slack-bot-python.html

SLACK_BOT_TOKEN='xxxxxxxx'

# instantiate Slack client
slack_client = SlackClient(SLACK_BOT_TOKEN)
# starterbot's user ID in Slack: value is assigned after the bot starts up
starterbot_id = None

# constants
RTM_READ_DELAY = 1 # 1 second delay between reading from RTM
EXAMPLE_COMMAND = "do"
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"

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


def parse_bot_commands(slack_events):
    """
        Parses a list of events coming from the Slack RTM API to find bot commands.
        If a bot command is found, this function returns a tuple of command and channel.
        If its not found, then this function returns None, None.
    """
    for event in slack_events:
        print(event["type"])
        if event["type"] == "message" and not "subtype" in event:
            user_id, message = parse_direct_mention(event["text"])
            print('channel : ' + str(event["channel"]))
            print('message : ' + str(event["text"]))
            print('message filter : ' + str(message))
            print('user : ' + str(user_id))
            if user_id == starterbot_id:
                print('return event')
                return message, event["channel"]
    return None, None

def parse_direct_mention(message_text):
    """
        Finds a direct mention (a mention that is at the beginning) in message text
        and returns the user ID which was mentioned. If there is no direct mention, returns None
    """
    matches = re.search(MENTION_REGEX, message_text)
    # the first group contains the username, the second group contains the remaining message
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

def handle_command(command, channel):
    """
        Executes bot command if the command is known
    """
    # Default response is help text for the user
    default_response = "Not sure what you mean. Try *{}*.".format(EXAMPLE_COMMAND)

    # Finds and executes the given command, filling in response
    response = None
    # This is where you start to implement more commands!
    if command.startswith(EXAMPLE_COMMAND):
        response = "Sure...write some more code then I can do that!"

    response = ChatBot(command)

    # Sends the response back to the channel
    slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        text=response or default_response
    )

def Main_Server(): 
    if slack_client.rtm_connect(with_team_state=False):
        print("Starter Bot connected and running!")
        # Read bot's user ID by calling Web API method `auth.test`
        global starterbot_id
        starterbot_id = slack_client.api_call("auth.test")["user_id"]
        print(starterbot_id)
        while True:
            print("Loop")
            command, channel = parse_bot_commands(slack_client.rtm_read())
            if command:
                print("Command")
                handle_command(command, channel)                
            time.sleep(RTM_READ_DELAY)
    else:
        print("Connection failed. Exception traceback printed above.")


def Main(): 
	'''Server Slack with bot of webapi'''
	Main_Server()
	
if __name__ == '__main__':
	if(len(sys.argv) > 1):
		if(sys.argv[len(sys.argv)-1] == '-h' or sys.argv[len(sys.argv)-1] == 'help'):
			print(Main.__doc__)
			exit()
	Main()
	
	param = ' '.join(sys.argv[1:])
	print('param ' + param)
