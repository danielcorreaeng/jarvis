import time
import json
import sys,os
import subprocess
import argparse
import datetime
from random import randint
import os.path
import requests
import json
import configparser
import bs4
import requests

from jarvis_utils import *

globalParameter['INPUT_DATA_OFF'] = True
globalParameter['OUTPUT_DATA_OFF'] = True
globalParameter['MAINLOOP_CONTROLLER'] = False
globalParameter['MAINWEBSERVER'] = False
globalParameter['PROCESS_JARVIS'] = None
globalParameter['TimeRecordFile'] = 3

globalParameter['PINTEREST_IMAGECLASS'] = 'hCL kVc L4E MIw'

def get_link_from_url_pinterest(link):
    with requests.Session() as s:
        html_page = s.get(link,headers={"User-Agent":"Mozilla/5.0"})
        soup = bs4.BeautifulSoup(html_page.text,'html.parser')

        link = soup.find("img", class_=globalParameter['PINTEREST_IMAGECLASS']).get('src')

    return link    

def GetLocalFileWithoutExtension():
    localFile = os.path.join(globalParameter['PathOutput'], datetime.datetime.now().strftime("%Y%m%d_%H%M%S%f") + "_" + str(randint(0, 999)) + "_temp")
    return localFile

def GetLocalFile():
    localFile = GetLocalFileWithoutExtension() + ".py"
    return localFile

def Main(): 
    '''Get a pin from Pinterest link and save in file (base = folder, tag = name). Parameters : <base> <tag 0> <tag1> ... <link>'''
    pass
	
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=Main.__doc__)
    parser.add_argument('-d','--description', help='Description of program', action='store_true')
    parser.add_argument('-u','--unique', help='Make id unique for tag', action='store_true')
    parser.add_argument('-l','--jsonlink', help='Create a json file with the inserted link in database', action='store_true')
    parser.add_argument('-n','--jsonnote', help='Create a json file with the inserted note in database', action='store_true')
    
    args, unknown = parser.parse_known_args()
    args = vars(args)
    
    if args['description'] == True:
        print(Main.__doc__)
        sys.exit()     

    GetCorrectPath()  

    id_unique = False
    if args['unique'] == True:
        id_unique = True   

    if(len(unknown) < 3):
        print('Sorry, y need more arguments. Use -d for description.')
        sys.exit()   
        
    base = unknown[0]
    tags = unknown[1:-1]
    link = unknown[-1]
    link = get_link_from_url_pinterest(link)

    tags = ' '.join(tags)
    if(id_unique == True):
        tags = tags + " " + str(datetime.datetime.now().strftime("%Y%m%d")) + " " + str(datetime.datetime.now().strftime("%H%M%S%f"))  + " " + str(randint(0, 999))
    
    file = GetLocalFile()
    extension = os.path.splitext(link)[1]

    if args['jsonlink'] == True or args['jsonnote'] == True:
        file = file + '.json'

        data = { 'link' :  link }
        if args['jsonnote'] == True:
            link = link.replace("_", " ")
            data = { 'note' :  link }
            
        f = open(file,'w')
        json.dump(data, f, ensure_ascii=False, indent=4)
        f.close()

        time.sleep(globalParameter['TimeRecordFile'])
        cmd = 'read ' + file + ' ' + tags + ' ' + '-base=' + base
        RunJarvis(cmd)

    else:
        localpath = os.path.join(globalParameter['PathDB_All'], base)

        if(os.path.exists(localpath) == False):
            os.mkdir(localpath)

        file = os.path.join(localpath, tags + extension)
        f = open(file,'wb')
        response = requests.get(link)
        f.write(response.content)
        f.close()


    time.sleep(globalParameter['TimeRecordFile'])
    if(os.path.isfile(file)==True and (args['jsonlink'] == True or args['jsonnote'] == True)):
        os.remove(file)
        pass
