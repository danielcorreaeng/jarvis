import pyttsx3
import argparse

from glob import glob
import time
import json
import sys,os
import subprocess
import argparse
import unittest
from jarvis_utils import * #AT YOUR OWN RISK
import gtts
from playsound import playsound
import datetime
from random import randint

globalParameter['TimeRecordFile'] = 5
globalParameter['TimeRecordFileTrash'] = 10

def GetLocalFileWithoutExtension():
    localFile = os.path.join(globalParameter['PathOutput'], datetime.datetime.now().strftime("%Y%m%d_%H%M%S%f") + "_" + str(randint(0, 999)) + "_temp")
    return localFile

def GetLocalFile():
    localFile = GetLocalFileWithoutExtension() + ".mp3"
    return localFile

def Main(command): 
    '''Program that takes text from parameters and converts it into speech.'''
    
    global globalParameter
    GetCorrectPath() #from jarvis_utils  

    tts = gtts.gTTS(command, lang="pt")
    file = GetLocalFile()
    tts.save(file)
    time.sleep(globalParameter['TimeRecordFile'])    
    playsound(file)

    time.sleep(globalParameter['TimeRecordFileTrash'])    
    if(os.path.isfile(file)==True):
        os.remove(file)
        pass
	
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=Main.__doc__)
    parser.add_argument('-d','--description', help='Description of program', action='store_true')
    
    args, unknown = parser.parse_known_args()
    args = vars(args)
    
    if args['description'] == True:
        print(Main.__doc__)
        sys.exit()     

    param = ' '.join(unknown)

    print(param)

    Main(param)