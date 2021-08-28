import sys,os
import sqlite3
import getpass
import socket
import time
import psutil
import subprocess
from requests import get
import argparse
import unittest
import copy
import requests
import json
import datetime
import configparser

from flask import Flask, request, jsonify
from threading import Thread

LocalPort = 8821
PreferredNetworks = ['192.168.15.','127.0.0.']
BlockedNetworks = ['192.168.56.', '192.168.100.']
LocalIp = socket.gethostbyname(socket.gethostname())
app = Flask(__name__)

PathLocal = "C:\\Jarvis"
PathJarvis = "C:\\Jarvis\\Jarvis.py"
PathOutput = PathLocal + "\\Output"
PathExecutable = "python"

INPUT_DATA = []
OUTPUT_DATA = []
OUTPUT_DATA_WEBHOOK = []
INPUT_DATA_OFF = False
OUTPUT_DATA_OFF = False
MAINLOOP_CONTROLLER = True
MAINWEBSERVER = True
MAINLOOP_SLEEP_SECONDS = 5.0
PROCESS_JARVIS = None

class TestCases(unittest.TestCase):
    def test_webserver_fifo(self):
        global INPUT_DATA
        global OUTPUT_DATA
        global MAINLOOP_SLEEP_SECONDS
        global MAINLOOP_CONTROLLER
        global MAINWEBSERVER
        global OUTPUT_DATA_WEBHOOK
        global PROCESS_JARVIS
        global app

        INPUT_DATA.clear()
        OUTPUT_DATA.clear()
        OUTPUT_DATA_WEBHOOK.clear()
        MAINLOOP_SLEEP_SECONDS = 1
        MAINLOOP_CONTROLLER = True
        MAINWEBSERVER = False
        PROCESS_JARVIS = 'testcases_intern'

        RunJarvis('record ' + PROCESS_JARVIS + ' -program=dump')

        Main()

        value00 = 'data00'
        value01 = 'data01'

        app = app.test_client()

        data = []
        localTime = datetime.datetime.now().strftime("%Y%m%d_%H%M%S%f")
        data.append({'time' : localTime , 'value' : value00})        
        url = "http://" + LocalIp + ":" + str(LocalPort) + "/exemple/input"
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        data=json.dumps(data)

        response = app.post(url, data=data, headers=headers)

        data = []
        localTime = datetime.datetime.now().strftime("%Y%m%d_%H%M%S%f")
        data.append({'time' : localTime , 'value' : value01})
        data=json.dumps(data)
        
        response = app.post(url, data=data, headers=headers)
    
        time.sleep(MAINLOOP_SLEEP_SECONDS+5)
        time.sleep(MAINLOOP_SLEEP_SECONDS+5)

        url = "http://" + LocalIp + ":" + str(LocalPort) + "/exemple/output"
        response = app.get(url)
        data = response.data
        data = json.loads(data.decode("utf-8"))

        MAINLOOP_CONTROLLER = False
        time.sleep(MAINLOOP_SLEEP_SECONDS+5)     

        check = True
        check = check and OUTPUT_DATA[0]['value'] == value01
        check = check and len(OUTPUT_DATA) == 1
        check = check and len(INPUT_DATA) == 0
        self.assertTrue(check)    

def Run(command, parameters=None, wait=False):
    #print(command)
    if(parameters != None):
    	proc = subprocess.Popen([command, parameters], stdout=subprocess.PIPE, shell=None)
    else:
    	proc = subprocess.Popen(command, stdout=subprocess.PIPE, shell=None)

    if(wait == True):
        proc.communicate()

def RunJarvis(tags):
	Run(PathExecutable + ' ' + PathJarvis + ' ' + tags, None, True)  

@app.route('/exemple/table')
def ExampleTable():
    res = makeTable()
    return res    

@app.route('/exemple/chart')
def ExampleChart():
    res = makeChart()
    return res

@app.route('/exemple/input', methods=['POST'])
def ExempleInput():
    global INPUT_DATA
    data = {}

    if request.method == 'POST':    
        data = request.get_json(force=True)
        data = data[0]        
        #print(data)
        INPUT_DATA.append(data)
    return jsonify(data)

@app.route('/exemple/output')
def ExempleOutput():
    global OUTPUT_DATA
    result = {}

    if(len(OUTPUT_DATA)>0):    
        result = OUTPUT_DATA[0]
        OUTPUT_DATA.pop(0)

    return jsonify(result)

@app.route('/exemple/webhook', methods=['POST'])
def ExempleWebhook():
    global OUTPUT_DATA_WEBHOOK
    data = {}

    if request.method == 'POST':    
        data = request.get_json(force=True)
        data = data[0]        
        OUTPUT_DATA_WEBHOOK.append(data['webhook'])
    return jsonify(data)

@app.route('/exemple/post', methods=['POST'])
def ExemplePost():
    data = {}

    if request.method == 'POST':    
        data = request.get_json(force=True)
        data = data[0]        
        print(data)
    return jsonify(data)

@app.route('/')
def index():
    return str(Main.__doc__) + " | ip server : " +  LocalIp

def GetCorrectIp(LocalIps):
    LocalIp = None
    
    for myip in LocalIps[2]:
        for iptest in PreferredNetworks:
            if(myip.find(iptest)>=0):
                LocalIp = myip
                break
    
    if(LocalIp == None):
        ipblock = False
        for myip in LocalIps[2]:
            for iptest in BlockedNetworks:
                if(myip.find(iptest)>=0):
                    ipblock = True
                    break
                
            if(ipblock == False):
                LocalIp = myip
                break
    
    if(LocalIp == None):
        LocalIp = '0.0.0.0'
    
    return LocalIp

def GetCorrectPath():
    global PathExecutable
    global PathLocal
    global PathOutput
    global PathJarvis

    dir_path = os.path.dirname(os.path.realpath(__file__)) 
    os.chdir(dir_path)

    jarvis_file = dir_path + '\\Jarvis.py'
    ini_file = dir_path + '\\config.ini'
    if(os.path.isfile(jarvis_file) == False):
        jarvis_file = dir_path + '\\..\\Jarvis.py'
        ini_file = dir_path + '\\..\\config.ini'
        if(os.path.isfile(jarvis_file) == False):
            return
    
    PathExecutable = sys.executable
    PathLocal = os.path.dirname(os.path.realpath(jarvis_file))
    PathJarvis = jarvis_file
    PathOutput = PathLocal + "\\Output"

    if(os.path.isfile(ini_file) == True):
        with open(ini_file) as fp:
            config = configparser.ConfigParser()
            config.read_file(fp)
            sections = config.sections()
            #for key in config['CriticalServices']:  
            #    #print(config['CriticalServices'][key])

def makeTable():
    TITLE = 'TABLE'
    DATA =  ''
    DATA += '<div class="table-responsive"><table id="example1" class="table table-bordered table-striped">'
    DATA += '<thead>'
    DATA += '<tr><th>Orçamento</th><th>Cliente</th><th>Comercial</th><th>Data Entrada</th><th>Deadline</th><th>ID</th><th>Tipo</th><th>Status</th></tr>'
    DATA += '</thead>'
    DATA += '<tbody>'
    DATA += '<tr><th>Orçamento1</th><th>Cliente2</th><th>Comercial2</th><th>Data Entrada2</th><th>Deadline2</th><th>ID2</th><th>Tipo2</th><th>Status1</th></tr>'
    DATA += '<tr><th>Orçamento2</th><th>Cliente2</th><th>Comercial2</th><th>Data Entrada2</th><th>Deadline2</th><th>ID2</th><th>Tipo2</th><th>Status3</th></tr>'
    DATA += '<tr><th>Orçamento3</th><th>Cliente2</th><th>Comercial2</th><th>Data Entrada2</th><th>Deadline2</th><th>ID2</th><th>Tipo2</th><th>Status5</th></tr>'
    DATA += '<tr><th>Orçamento1</th><th>Cliente2</th><th>Comercial2</th><th>Data Entrada2</th><th>Deadline2</th><th>ID2</th><th>Tipo2</th><th>Status1</th></tr>'
    DATA += '<tr><th>Orçamento2</th><th>Cliente2</th><th>Comercial2</th><th>Data Entrada2</th><th>Deadline2</th><th>ID2</th><th>Tipo2</th><th>Status3</th></tr>'
    DATA += '<tr><th>Orçamento3</th><th>Cliente2</th><th>Comercial2</th><th>Data Entrada2</th><th>Deadline2</th><th>ID2</th><th>Tipo2</th><th>Status5</th></tr>'
    DATA += '<tr><th>Orçamento1</th><th>Cliente2</th><th>Comercial2</th><th>Data Entrada2</th><th>Deadline2</th><th>ID2</th><th>Tipo2</th><th>Status1</th></tr>'
    DATA += '<tr><th>Orçamento2</th><th>Cliente2</th><th>Comercial2</th><th>Data Entrada2</th><th>Deadline2</th><th>ID2</th><th>Tipo2</th><th>Status3</th></tr>'
    DATA += '<tr><th>Orçamento3</th><th>Cliente2</th><th>Comercial2</th><th>Data Entrada2</th><th>Deadline2</th><th>ID2</th><th>Tipo2</th><th>Status5</th></tr>'
    DATA += '<tr><th>Orçamento1</th><th>Cliente2</th><th>Comercial2</th><th>Data Entrada2</th><th>Deadline2</th><th>ID2</th><th>Tipo2</th><th>Status1</th></tr>'
    DATA += '<tr><th>Orçamento2</th><th>Cliente2</th><th>Comercial2</th><th>Data Entrada2</th><th>Deadline2</th><th>ID2</th><th>Tipo2</th><th>Status3</th></tr>'
    DATA += '<tr><th>Orçamento3</th><th>Cliente2</th><th>Comercial2</th><th>Data Entrada2</th><th>Deadline2</th><th>ID2</th><th>Tipo2</th><th>Status5</th></tr>'
    DATA += '</tbody>'
    DATA += '<tfoot><tr><th>Orçamento</th><th>Cliente</th><th>Comercial</th><th>Data Entrada</th><th>Deadline</th><th>ID</th><th>Tipo</th><th>Status</th></tr></tfoot>'
    DATA += '</table></div>'
    PAGE_SCRIPT = "<script>$(function () {$('#example1').DataTable({'paging': true,'lengthChange': false,'searching' : true,'ordering': true,'info': true,'autoWidth' : false,'order': [[ 5, 'desc' ]],dom: 'Bfrtip',buttons: ['copy', 'excel', 'pdf', 'print']})})</script>"
    return makePage(TITLE, DATA, PAGE_SCRIPT)

def makeChart():
    TITLE = 'CHART'
    DATA = '<canvas class="my-4 w-100" id="myChart" width="900" height="380"></canvas>'
    LABELS = "'Sunday',  'Monday',  'Tuesday',  'Wednesday',  'Thursday',  'Friday',  'Saturday'"
    VALUES = '15339,10,18483,24003,23489,24092,12034'
    PAGE_SCRIPT = "<script>(function () {  feather.replace({ 'aria-hidden': 'true' });  var ctx = document.getElementById('myChart');  var myChart = new Chart(ctx, {type: 'line',data: {labels: [  " + LABELS + "],datasets: [{  data: [" + VALUES + "  ],  lineTension: 0,  backgroundColor: 'transparent',  borderColor: '#007bff',  borderWidth: 4,  pointBackgroundColor: '#007bff'}]},options: {scales: {  yAxes: [{ticks: {beginAtZero: false}  }]},legend: {  display: false}}  });})();</script>"
    return makePage(TITLE, DATA, PAGE_SCRIPT)

def makePage(TITLE, DATA, PAGE_SCRIPT = ''):
    ext_bootstrap_css = 'https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css'
    ext_jquery_js = 'https://ajax.googleapis.com/ajax/libs/jquery/3.6.0/jquery.min.js'
    ext_dataTables_css = 'https://cdn.datatables.net/1.10.25/css/jquery.dataTables.min.css'
    ext_bootstrap_js = 'https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/js/bootstrap.bundle.min.js'
    ext_feather_js = 'https://cdn.jsdelivr.net/npm/feather-icons@4.28.0/dist/feather.min.js'
    ext_chart_js = 'https://cdn.jsdelivr.net/npm/chart.js@2.9.4/dist/Chart.min.js'
    ext_datatable_js = 'https://cdn.datatables.net/1.10.25/js/jquery.dataTables.min.js'
    ext_dataTables_buttons_js = 'https://cdn.datatables.net/buttons/1.7.1/js/dataTables.buttons.min.js'
    ext_buttons_flash_js = 'https://cdn.datatables.net/buttons/1.7.1/js/buttons.flash.min.js'
    ext_jszip_js = 'https://cdnjs.cloudflare.com/ajax/libs/jszip/3.1.3/jszip.min.js'
    ext_pdfmake_js = 'https://cdnjs.cloudflare.com/ajax/libs/pdfmake/0.1.53/pdfmake.min.js'
    ext_vfs_fonts = 'https://cdnjs.cloudflare.com/ajax/libs/pdfmake/0.1.53/vfs_fonts.js'
    ext_buttons_html5_js = 'https://cdn.datatables.net/buttons/1.7.1/js/buttons.html5.min.js'
    ext_buttons_print_js = 'https://cdn.datatables.net/buttons/1.7.1/js/buttons.print.min.js'

    DEFAULT_PAGE_MENU = '<nav id="sidebarMenu" class="col-md-3 col-lg-2 d-md-block bg-light sidebar collapse"><div class="position-sticky pt-3"><ul class="nav flex-column"><li class="nav-item"><a class="nav-link active" aria-current="page" href="#"><span data-feather="home"></span>Dashboard</a></li><li class="nav-item"><a class="nav-link" href="#"><span data-feather="file"></span>Outros</a></li></ul></div></nav>'
    
    DEFAULT_PAGE_HEADER = '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="description" content=""><meta name="author" content="Mark Otto, Jacob Thornton, and Bootstrap contributors"><meta name="generator" content="Hugo 0.84.0"><title></title><link rel="canonical" href="https://getbootstrap.com/docs/5.0/examples/dashboard/"><link href="' + ext_bootstrap_css + '" rel="stylesheet" crossorigin="anonymous"><script src="' + ext_jquery_js + '"></script><link href="' + ext_dataTables_css + '" rel="stylesheet"><style>.bd-placeholder-img {font-size: 1.125rem;text-anchor: middle;-webkit-user-select: none;-moz-user-select: none;user-select: none;}@media (min-width: 768px) {.bd-placeholder-img-lg {font-size: 3.5rem;}}</style><style>body {font-size: .875rem;}.feather {width: 16px;height: 16px;vertical-align: text-bottom;}/** Sidebar*/.sidebar {position: fixed;top: 0;/* rtl:raw:right: 0;*/bottom: 0;/* rtl:remove */left: 0;z-index: 100; /* Behind the navbar */padding: 48px 0 0; /* Height of navbar */box-shadow: inset -1px 0 0 rgba(0, 0, 0, .1);}@media (max-width: 767.98px) {.sidebar {top: 5rem;}}.sidebar-sticky {position: relative;top: 0;height: calc(100vh - 48px);padding-top: .5rem;overflow-x: hidden;overflow-y: auto; /* Scrollable contents if viewport is shorter than content. */}.sidebar .nav-link {font-weight: 500;color: #333;}.sidebar .nav-link .feather {margin-right: 4px;color: #727272;}.sidebar .nav-link.active {color: #2470dc;}.sidebar .nav-link:hover .feather,.sidebar .nav-link.active .feather {color: inherit;}.sidebar-heading {font-size: .75rem;text-transform: uppercase;}/** Navbar*/.navbar-brand {padding-top: .75rem;padding-bottom: .75rem;font-size: 1rem;background-color: rgba(0, 0, 0, .25);box-shadow: inset -1px 0 0 rgba(0, 0, 0, .25);}.navbar .navbar-toggler {top: .25rem;right: 1rem;}.navbar .form-control {padding: .75rem 1rem;border-width: 0;border-radius: 0;}.form-control-dark {color: #fff;background-color: rgba(255, 255, 255, .1);border-color: rgba(255, 255, 255, .1);}.form-control-dark:focus {border-color: transparent;box-shadow: 0 0 0 3px rgba(255, 255, 255, .25);}th{font-weight: normal;}</style></head><body><header class="navbar navbar-dark sticky-top bg-dark flex-md-nowrap p-0 shadow"><a class="navbar-brand col-md-3 col-lg-2 me-0 px-3" href="#">Data dash</a><button class="navbar-toggler position-absolute d-md-none collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#sidebarMenu" aria-controls="sidebarMenu" aria-expanded="false" aria-label="Toggle navigation"><span class="navbar-toggler-icon"></span></button><!--<input class="form-control form-control-dark w-100" type="text" placeholder="Search" aria-label="Search">--><div class="navbar-nav"><div class="nav-item text-nowrap"><a class="nav-link px-3" href="#"></a></div></div></header><div class="container-fluid"><div class="row">'
    DEFAULT_PAGE_HEADER += DEFAULT_PAGE_MENU 
    DEFAULT_PAGE_HEADER += '<main class="col-md-9 ms-sm-auto col-lg-10 px-md-4"><div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom"><h1 class="h2">' + TITLE + '</h1></div>'
    DEFAULT_PAGE_FOOTER_00 = '</main></div></div><script src="'+ ext_bootstrap_js +'" crossorigin="anonymous"></script><script src="' + ext_feather_js + '" crossorigin="anonymous"></script><script src="' + ext_chart_js + '" crossorigin="anonymous"></script><script src="' + ext_datatable_js + '" crossorigin="anonymous"></script>'
    DEFAULT_PAGE_SCRIPT_00 = '<script src="' + ext_dataTables_buttons_js + '"></script><script src="' + ext_buttons_flash_js + '"></script><script src="' + ext_jszip_js +  '"></script><script src="' + ext_pdfmake_js + '"></script><script src="' + ext_vfs_fonts + '"></script><script src="' + ext_buttons_html5_js + '"></script><script src="' + ext_buttons_print_js + '"></script>'        
    DEFAULT_PAGE_FOOTER_01 = '</body></html>'

    res = DEFAULT_PAGE_HEADER
    res += DATA
    res += DEFAULT_PAGE_FOOTER_00
    res += DEFAULT_PAGE_SCRIPT_00
    res += PAGE_SCRIPT
    res += DEFAULT_PAGE_FOOTER_01
    return res

def mainLoop():
    global INPUT_DATA
    global INPUT_DATA_OFF
    global OUTPUT_DATA
    global OUTPUT_DATA_OFF

    if(INPUT_DATA_OFF == False):
        if(len(INPUT_DATA)<=0):
            return

    VirtualInput()

    if(OUTPUT_DATA_OFF == False and len(INPUT_DATA)>0):
        OUTPUT_DATA.append(mainLoopProcess(INPUT_DATA[0]))
    elif(OUTPUT_DATA_OFF == True and len(INPUT_DATA)>0):
        mainLoopProcess(INPUT_DATA[0])
    elif(OUTPUT_DATA_OFF == True and INPUT_DATA_OFF == True):
        mainLoopProcess(None) 

    if(len(INPUT_DATA)>0):    
        INPUT_DATA.pop(0)

    if(len(OUTPUT_DATA_WEBHOOK)>0):
        for webhook in OUTPUT_DATA_WEBHOOK:
            #print(webhook)
            data = []
            data.append(OUTPUT_DATA[0])

            url = webhook
            headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

            try:
                requests.post(url, data=json.dumps(data), headers=headers)
            except:
                pass

            if(len(OUTPUT_DATA)>0):    
                OUTPUT_DATA.pop(0)
     
def mainThread():
    global MAINLOOP_CONTROLLER

    while(MAINLOOP_CONTROLLER):
        try:                 
            mainLoop()
            time.sleep(MAINLOOP_SLEEP_SECONDS) 
            #print('Loop')
        except:
            print('Error Loop')
    pass

def VirtualInput():
    pass

def mainLoopProcess(input_data):
    result = None

    if(PROCESS_JARVIS != None):
        fileInput = PathOutput + "\\" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S%f_in.json")
        fileOutput = PathOutput + "\\" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S%f_out.json")

        with open(fileInput, "w") as outfile:                    
            json_string = json.dumps(input_data, default=lambda o: o.__dict__, sort_keys=True, indent=2)
            outfile.write(json_string)  

        RunJarvis(PROCESS_JARVIS + " -i " + fileInput + " -o " + fileOutput)

        with open(fileOutput) as json_file:
            result = json.load(json_file)
            #print(result)
    else:
        result = copy.deepcopy(input_data)
 
    return result

def Main():
    """no describe"""    

    global LocalIp
    global MAINWEBSERVER
    global MAINLOOP_CONTROLLER
    
    GetCorrectPath()

    try:        
        LocalIp = GetCorrectIp(socket.gethostbyname_ex(socket.gethostname()))
    except:
        print('error ip')
        
    try:
        t = Thread(target=mainThread)
        t.start()  
    except:
        print('error mainThread')

    try:
        if(MAINWEBSERVER == True):
            app.run(host = str(LocalIp),port=LocalPort) 
        pass
    except:
        print('error webservice')
    
if __name__ == '__main__':   
    parser = argparse.ArgumentParser(description=Main.__doc__)
    parser.add_argument('-d','--description', help='Description of program', action='store_true')
    parser.add_argument('-u','--tests', help='Execute tests', action='store_true')
    
    args, unknown = parser.parse_known_args()
    args = vars(args)
    
    if args['description'] == True:
        print(Main.__doc__)
        sys.exit()

    if args['tests'] == True:       
        suite = unittest.TestSuite()
        suite.addTest(TestCases("test_webserver_fifo")) 
        runner = unittest.TextTestRunner()
        runner.run(suite)  
        MAINLOOP_CONTROLLER = False             
        sys.exit()        

    param = ' '.join(unknown)

    Main()