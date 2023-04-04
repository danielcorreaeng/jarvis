import pyttsx3
import argparse

from glob import glob
import time
import json
import sys,os
import subprocess
import argparse
import unittest
#from jarvis_utils import * #AT YOUR OWN RISK

def Main(command): 
    '''Program that takes text from parameters and converts it into speech.'''
    
    global globalParameter
    #GetCorrectPath() #from jarvis_utils  

    engine = pyttsx3.init()
    engine.setProperty('rate', 150)
    engine.say(command)
    engine.runAndWait()
	
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