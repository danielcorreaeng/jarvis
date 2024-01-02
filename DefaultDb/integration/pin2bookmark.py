from glob import glob
import time
import json
import sys,os
import subprocess
import argparse
import unittest
from jarvis_utils import *
import bs4
import requests

globalParameter['INPUT_DATA_OFF'] = False
globalParameter['OUTPUT_DATA_OFF'] = False
globalParameter['MAINLOOP_CONTROLLER'] = False
globalParameter['MAINWEBSERVER'] = False
globalParameter['MAINLOOP_SLEEP_SECONDS'] = 5.0
globalParameter['PROCESS_JARVIS'] = None

globalParameter['PINTEREST_IMAGECLASS'] = 'hCL kVc L4E MIw'

def get_link_from_url_pinterest(link):
    with requests.Session() as s:
        html_page = s.get(link,headers={"User-Agent":"Mozilla/5.0"})
        soup = bs4.BeautifulSoup(html_page.text,'html.parser')

        link = soup.find("img", class_=globalParameter['PINTEREST_IMAGECLASS']).get('src')

    return link   

def Main(tags, link): 
    '''Get a pin from Pinterest link and save in file (base = folder, tag = name) for bookmark command. Parameters : <base> <tag 0> <tag1> ... <link>'''
    
    global globalParameter

    GetCorrectPath()

    link = get_link_from_url_pinterest(link)  
    command = 'bookmark -f -u -base=services ' + tags + ' ' + link
    print(command)
    RunJarvis(command)

	
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=Main.__doc__)
    parser.add_argument('-d','--description', help='Description of program', action='store_true')
    
    args, unknown = parser.parse_known_args()
    args = vars(args)
    
    if args['description'] == True:
        print(Main.__doc__)
        sys.exit()

    if(len(unknown) < 3):
        print('Sorry, y need more arguments. Use -d for description.')
        sys.exit()   
        
    tags = unknown[0:-1]
    tags = ' '.join(tags)
    link = unknown[-1]    

    print(tags)

    Main(tags, link)
