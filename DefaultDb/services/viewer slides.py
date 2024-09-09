from glob import glob
import time
import json
import sys,os
import subprocess
import argparse
import unittest
import io
import operator
from jarvis_utils import *
from os.path import join

globalParameter['INPUT_DATA_OFF'] = False
globalParameter['OUTPUT_DATA_OFF'] = False
globalParameter['MAINLOOP_CONTROLLER'] = False
globalParameter['MAINWEBSERVER'] = True
globalParameter['PROCESS_JARVIS'] = None

globalParameter['LocalPort'] = 8870

globalParameter['TargetPath'] = None

globalParameter['TargetDB'] = globalParameter['LocalHostname'] + "_" + globalParameter['LocalUsername']
globalParameter['PathDB'] = os.path.join(globalParameter['PathLocal'], "Db", globalParameter['TargetDB'] + ".db")
globalParameter['TAG_LINK_LINK'] = 'http' 
globalParameter['TAG_LINK_POINTS'] = '__' 
globalParameter['TAG_LINK_BAR'] = '___'


class TestCases_Local(TestCases):
    def test_dump(self):
        check = True
        self.assertTrue(check)    

@app.route('/')
def index():
    return str(Main.__doc__) + " | ip server : " +  str(globalParameter['LocalIp']) + ":" + str(globalParameter['LocalPort'])

@app.route('/carousel')
def Carousel():
    res = makeCarousel()
    return res    

def makeCarousel():
    TITLE = 'Gallery'
    PAGE_PAGE_CSS = ''''''
    PAGE_PAGE_CSS += ''''''
    DATA =  ''''''

    files = []
    for ext in ('*.png', '*.jpg', '*.jpeg', '*.gif'):
        files.extend(glob(join(globalParameter['TargetPath'], ext)))

    idcount = -1
    buttons = ''''''
    items = ''''''
    for _localfile in files:
        idcount = idcount + 1
        name = os.path.splitext(os.path.basename(_localfile))[0]
        filetype = _localfile.split(".")[-1]
        filepath = request.url_root + 'External/' + os.path.basename(_localfile)

        link='#'
        if globalParameter['TAG_LINK_LINK'] in filepath:
            link = os.path.basename(_localfile)
            link = link.replace('.' + filetype, '') 
            link = link.replace(globalParameter['TAG_LINK_LINK'], 'http://') 
            link = link.replace(globalParameter['TAG_LINK_BAR'], '/')
            link = link.replace(globalParameter['TAG_LINK_POINTS'], ':')

        buttons += '''
            <button type="button" data-bs-target="#carouselExampleIndicators" data-bs-slide-to="'''+ str(idcount) + '''" 
        '''
        if idcount==0:
            buttons += '''
            class="active" aria-current="true" 
        '''            
        buttons += '''
         aria-label="Slide ''' + str(idcount) + '''"></button>
        '''
        items += '''
            <div class="carousel-item 
        '''
        if idcount==0:
            items += '''    
                 active 
            '''    
        items += '''    
            ">  
            <a href="''' + link + '''" target="_blank">
                <img src="''' + filepath + '''" class="d-block w-100" alt="...">
            </a>
            </div>
        '''            

    DATA += '''
        <div id="carouselExampleIndicators" class="carousel slide" data-bs-ride="carousel">
            <div class="carousel-indicators"> ''' + buttons + '''
            </div>
            <div class="carousel-inner"> ''' + items + '''
            </div>
            <button class="carousel-control-prev" type="button" data-bs-target="#carouselExampleIndicators" data-bs-slide="prev">
              <span class="carousel-control-prev-icon" aria-hidden="true"></span>
              <span class="visually-hidden">Previous</span>
            </button>
            <button class="carousel-control-next" type="button" data-bs-target="#carouselExampleIndicators" data-bs-slide="next">
              <span class="carousel-control-next-icon" aria-hidden="true"></span>
              <span class="visually-hidden">Next</span>
            </button>
        </div>
    '''
    DATA += ''''''

    PAGE_SCRIPT = ''''''

    return makePage_carousel(TITLE, DATA, PAGE_SCRIPT,PAGE_PAGE_CSS) 

def makePage_carousel(TITLE, DATA, PAGE_SCRIPT = '', PAGE_PAGE_CSS = ''):
    ext_bootstrap_css = 'https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css'
    ext_bootstrap_min_js = 'https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/js/bootstrap.min.js'
    ext_jquery_js = 'https://ajax.googleapis.com/ajax/libs/jquery/3.6.0/jquery.min.js'
    ext_bootstrap_js = 'https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/js/bootstrap.bundle.min.js'
    ext_popper = 'https://cdn.jsdelivr.net/npm/@popperjs/core@2.9.2/dist/umd/popper.min.js'

    DEFAULT_PAGE_HEADER = '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="description" content=""><title>' + TITLE + '</title>'
    DEFAULT_PAGE_HEADER += '''
    <link href="''' + ext_bootstrap_css + '''" rel="stylesheet" crossorigin="anonymous">
    <script src="''' + ext_bootstrap_js + '''"></script>''' + PAGE_PAGE_CSS + '''</head><body>
    '''
    DEFAULT_PAGE_FOOTER_00 = '''</main>
    <script src="''' + ext_popper + '''" crossorigin="anonymous"></script>
    <script src="''' + ext_bootstrap_min_js + '''" crossorigin="anonymous"></script>
    <script src="''' + ext_jquery_js + '''"></script>    
    '''
    DEFAULT_PAGE_SCRIPT_00 = ''        
    DEFAULT_PAGE_FOOTER_01 = '</body></html>'

    res = DEFAULT_PAGE_HEADER
    res += DATA
    res += DEFAULT_PAGE_FOOTER_00
    res += DEFAULT_PAGE_SCRIPT_00
    res += PAGE_SCRIPT
    res += DEFAULT_PAGE_FOOTER_01
    return res

def Main():
    """view the image carousel from path in web (/carousel). Optional parameters: -t (--target) to select a base -p (--port) to select target port """    

    global globalParameter

    #globalsub.subs(LoadVarsIni, LoadVarsIni2)
    
    GetCorrectPath()

    try:
        if(globalParameter['MAINWEBSERVER'] == True):
            remoteLogTargetIp = GetCorrectIp()
            if(globalParameter['LocalIp'] != '0.0.0.0'): remoteLogTargetIp = globalParameter['LocalIp']
            rl = RemoteLog()
            rl.CheckRestAPIThread(command="viewer slides -base=services -t " + globalParameter['TargetPath'], host = str(remoteLogTargetIp),port=globalParameter['LocalPort'])
            #app.run(host = str(globalParameter['LocalIp']),port=globalParameter['LocalPort'], ssl_context='adhoc') 
            app.run(host = str(globalParameter['LocalIp']),port=globalParameter['LocalPort']) 
            pass
        pass
    except:
        print('error webservice')

@app.route('/External/<path:filename>')
def base_static(filename):
    #print(app.root_path)
    return send_from_directory(globalParameter['TargetPath'] + '/', filename, conditional=True)
    #return send_from_directory('C:\\temp\\', filename, conditional=True)


if __name__ == '__main__':    
    parser = argparse.ArgumentParser(description=Main.__doc__)
    parser.add_argument('-d','--description', help='Description of program', action='store_true')
    parser.add_argument('-u','--tests', help='Execute tests', action='store_true')
    parser.add_argument('-t','--target', help='Path target (use fullpath)')
    parser.add_argument('-p','--port', help='Service running in target port')
    parser.add_argument('-i','--ip', help='Service running in target ip')
    parser.add_argument('-c','--config', help='Config.ini file')

    args, unknown = parser.parse_known_args()
    args = vars(args)
    
    if args['description'] == True:
        print(Main.__doc__)
        sys.exit()

    if args['tests'] == True:       
        suite = unittest.TestSuite()
        #suite.addTest(TestCases_Local("test_webserver_fifo")) 
        suite.addTest(TestCases_Local("test_dump")) 
        runner = unittest.TextTestRunner()
        runner.run(suite)             
        sys.exit()    

    globalParameter['TargetPath'] = os.path.join(globalParameter['PathOutput'])
    os.chdir(os.path.dirname(__file__))  
    if args['target'] is not None:
        globalParameter['TargetPath'] = args['target']
        os.chdir(os.path.dirname(globalParameter['TargetPath']))
    print('Path Target: ' + globalParameter['TargetPath'])        

    if args['port'] is not None:
        print('TargetPort: ' + args['port'])
        globalParameter['LocalPort'] = args['port']  

    if args['ip'] is not None:
        print('TargetIP: ' + args['ip'])
        globalParameter['LocalIp'] = args['ip']       

    if args['config'] is not None:
        print('Config.ini: ' + args['config'])
        globalParameter['configFile'] = args['config']               

    param = ' '.join(unknown)

    Main()
    