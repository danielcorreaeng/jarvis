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
from threading import Thread
from flask import Flask, request, jsonify
from flask import Flask, Response, redirect, url_for, request, session, abort
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user 

INPUT_DATA = []
OUTPUT_DATA = []
OUTPUT_DATA_WEBHOOK = []

globalParameter = {}
globalParameter['PathLocal'] = os.path.join("C:\\","Jarvis")
globalParameter['PathJarvis'] = os.path.join("C:\\","Jarvis","Jarvis.py")
globalParameter['PathOutput'] = os.path.join(globalParameter['PathLocal'], "Output")
globalParameter['PathExecutable'] = "python"

globalParameter['LocalPort'] = 8811
globalParameter['PreferredNetworks'] = ['192.168.15.','127.0.0.']
globalParameter['BlockedNetworks'] = ['192.168.56.', '192.168.100.']
globalParameter['LocalIp'] = socket.gethostbyname(socket.gethostname())
globalParameter['PublicIp'] = globalParameter['LocalIp']
globalParameter['LocalUsername'] = getpass.getuser().replace(' ','_')
globalParameter['LocalHostname'] = socket.gethostname().replace(' ','_')

globalParameter['INPUT_DATA_OFF'] = True
globalParameter['OUTPUT_DATA_OFF'] = True
globalParameter['MAINLOOP_CONTROLLER'] = True
globalParameter['MAINWEBSERVER'] = True
globalParameter['MAINLOOP_SLEEP_SECONDS'] = 600.0
globalParameter['PROCESS_JARVIS'] = None

globalParameter['password'] = 'ghRW8n@KVp'
globalParameter['secret_key'] = 'gVWx3*nmD@'

globalParameter['CriticalServices'] = ['chatbot -base=services', 'datalogger -base=services']

app = Flask(__name__)
app.config.update(DEBUG = False, SECRET_KEY = globalParameter['secret_key'])
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

class User(UserMixin):
    def __init__(self, id):
        self.id = id

class TestCases(unittest.TestCase):
    def test_dump(self):
        check = True
        self.assertTrue(check)    

def Run(command, parameters=None, wait=False):
    print(command)
    if(parameters != None):
        proc = subprocess.Popen([command, parameters], stdout=subprocess.PIPE, shell=True)
    else:
        proc = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)

    if(wait == True):
        proc.communicate()

def RunJarvis(tags):
    #Run(globalParameter['PathExecutable'] + ' ' + globalParameter['PathJarvis'] + ' ' + tags)  
    Run(globalParameter['PathExecutable'] + ' ' + globalParameter['PathJarvis'] + ' ' + tags)  
    print('command : ' + globalParameter['PathExecutable'] + ' ' + globalParameter['PathJarvis'] + ' ' + tags)

@app.route('/example/restricted')
@login_required
def restricted():
    return "unlock!"

@app.route("/login", methods=["GET", "POST"])
def login():
    global globalParameter

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']        
        if password == globalParameter['password']:
            id = 1
            user = User(id)
            login_user(user)
            return redirect(request.args.get("next"))
        else:
            return Response('<p>Login failed</p>')
    else:
        return makeLoginPage('login')

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return Response('<p>Logged out</p>')

@login_manager.user_loader
def load_user(userid):
    return User(userid)    

@app.route('/list/services')
@login_required
def ListServices():
    maskIp = globalParameter['LocalIp'].split('.')
    maskIp = str(maskIp[0]) + '.' + str(maskIp[1]) + '.' + str(maskIp[2]) 
    
    test = maskIp in str(request.remote_addr) 
        
    if test == True:
        print('authorized')
    else:
        print("not authorized")
        return "not authorized"

    res = makeTable()
    return res   

@app.route('/')
def index():
    return str(Main.__doc__) + " | ip server : " +  str(globalParameter['LocalIp']) + ":" + str(globalParameter['LocalPort'])

def GetCorrectIp(LocalIps):
    LocalIp = None
    
    for myip in LocalIps[2]:
        for iptest in globalParameter['PreferredNetworks']:
            if(myip.find(iptest)>=0):
                LocalIp = myip
                break
    
    if(LocalIp == None):
        ipblock = False
        for myip in LocalIps[2]:
            for iptest in globalParameter['BlockedNetworks']:
                if(myip.find(iptest)>=0):
                    ipblock = True
                    break
                
            if(ipblock == False):
                LocalIp = myip
                break
    
    if(LocalIp == None):
        LocalIp = '0.0.0.0'
    
    return LocalIp


def GetPublicIp():
    ippublic = ''
    try:
        ippublic = get('https://api.ipify.org').text
        ippublic = str(ippublic)
    except:
        pass
        
    return ippublic

def GetCorrectPath():
    global globalParameter

    dir_path = os.path.dirname(os.path.realpath(__file__)) 
    os.chdir(dir_path)

    jarvis_file = os.path.join(dir_path, 'Jarvis.py')
    ini_file = os.path.join(dir_path, 'config.ini')
    if(os.path.isfile(jarvis_file) == False):
        jarvis_file = os.path.join(dir_path, '..', 'Jarvis.py')
        ini_file = os.path.join(dir_path, '..', 'config.ini')
        if(os.path.isfile(jarvis_file) == False):
            return
    
    globalParameter['PathExecutable'] = sys.executable
    globalParameter['PathLocal'] = os.path.dirname(os.path.realpath(jarvis_file))
    globalParameter['PathJarvis'] = jarvis_file
    globalParameter['PathOutput'] = os.path.join(globalParameter['PathLocal'], "Output")

    if(os.path.isfile(ini_file) == True):
        with open(ini_file) as fp:
            config = configparser.ConfigParser()
            config.read_file(fp)
            sections = config.sections()
            if('Parameters' in sections):
                if('defaultpassword' in config['Parameters']):
                    globalParameter['password'] = config['Parameters']['defaultpassword']
                    print('password:' + globalParameter['password'])
            if('CriticalServices' in sections):
                for key in config['CriticalServices']:  
                    print(config['CriticalServices'][key])
                    globalParameter['CriticalServices'].append(config['CriticalServices'][key])

def makeTable():
    TITLE = 'CriticalServices'
    DATA =  ''
    DATA += '<div class="table-responsive"><table id="example1" class="table table-bordered table-striped">'
    DATA += '<thead>'
    DATA += '<tr><th>#</th><th>host</th><th>process</th><th>status</th></tr>'
    DATA += '</thead>'
    DATA += '<tbody>'
    #DATA += '<tr><th>#</th><th>host</th><th>process</th><th>status</th></tr>'

    list_process_checked = []
    rows = globalParameter['CriticalServices']
    count = 0
    if(len(rows) > 0):
        for row in rows:
            count = count + 1      
            process_arg_target = str(row)

            alive = False            
            if process_arg_target in list_process_checked:
                pass
            else:
                process_arg_target = str(row[0])    
                alive = CheckProcess("python", process_arg_target)
            
            DATA += '<tr><td>'
            DATA += str(count)
            DATA += '</td><td>'
            DATA += str(globalParameter['LocalHostname'])
            DATA += '</td><td>'
            DATA += str(row)
            DATA += '</td><td>'
            if(alive == True):
                DATA += "Alive"
            else:
                DATA += "Dead"
            DATA += '</td></tr>'

    DATA += '</tbody>'
    DATA += '<tfoot><tr><th>#</th><th>host</th><th>process</th><th>status</th></tr></tfoot>'
    DATA += '</table></div>'
    PAGE_SCRIPT = "<script>$(function () {$('#example1').DataTable({'paging': true,'lengthChange': false,'searching' : true,'ordering': true,'info': true,'autoWidth' : false,'order': [[ 0, 'desc' ]],dom: 'Bfrtip',buttons: ['copy', 'excel', 'pdf', 'print']})})</script>"
    return makePage(TITLE, DATA, PAGE_SCRIPT)

def makeLoginPage(TITLE):
    ext_bootstrap_css = 'https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css'
    res = '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="description" content=""><meta name="author" content="Mark Otto, Jacob Thornton, and Bootstrap contributors"><meta name="generator" content="Hugo 0.84.0"><title>' + TITLE + '</title><link rel="canonical" href="https://getbootstrap.com/docs/5.0/examples/sign-in/"><link href="' + ext_bootstrap_css + '" rel="stylesheet"><style>html,body {height: 100%;}body {display: flex;align-items: center;padding-top: 40px;padding-bottom: 40px;background-color: #f5f5f5;}.form-signin {width: 100%;max-width: 330px;padding: 15px;margin: auto;}.form-signin .checkbox {font-weight: 400;}.form-signin .form-floating:focus-within {z-index: 2;}.form-signin input[type="text"] {margin-bottom: -1px;border-bottom-right-radius: 0;border-bottom-left-radius: 0;}.form-signin input[type="password"] {margin-bottom: 10px;border-top-left-radius: 0;border-top-right-radius: 0;}</style><style>.bd-placeholder-img {font-size: 1.125rem;text-anchor: middle;-webkit-user-select: none;-moz-user-select: none;user-select: none;}@media (min-width: 768px) {.bd-placeholder-img-lg {font-size: 3.5rem;}}</style></head><body class="text-center"><main class="form-signin"><form action="" method="post"> <h1 class="h3 mb-3 fw-normal">authentication</h1><div class="form-floating"><input type="text" class="form-control" name="username" id="floatingInput" placeholder="name"><label for="floatingInput">Login</label></div><div class="form-floating"><input type="password" class="form-control" name="password" id="floatingPassword" placeholder="Password"><label for="floatingPassword">Password</label></div><button class="w-100 btn btn-lg btn-primary" type="submit" value=Login>Login</button></form></main></body></html>'
    return res    

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

def CheckProcess(process_name_target, process_arg_target):
    result = False
    for proc in psutil.process_iter():
        if str(proc.name).find(str(process_name_target))>=0:
            try:
                #print(proc.pid)
                #print(proc.cmdline())
                #print(cmdline)            
                cmdline = ' '.join(proc.cmdline())
    
                if str(cmdline).find(str(process_arg_target))>=0:
                    result = True
                    break
            except:
                pass    

    return result

def mainLoop():
    global INPUT_DATA
    global OUTPUT_DATA
    global globalParameter    

    if(globalParameter['INPUT_DATA_OFF'] == False):
        if(len(INPUT_DATA)<=0):
            return

    VirtualInput()

    if(globalParameter['OUTPUT_DATA_OFF'] == False and len(INPUT_DATA)>0):
        OUTPUT_DATA.append(mainLoopProcess(INPUT_DATA[0]))
    elif(globalParameter['OUTPUT_DATA_OFF'] == True and len(INPUT_DATA)>0):
        mainLoopProcess(INPUT_DATA[0])
    elif(globalParameter['OUTPUT_DATA_OFF'] == True and globalParameter['INPUT_DATA_OFF'] == True):
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
    global globalParameter

    jarvis_cmd = 'error handler ' + globalParameter['LocalUsername'] + '@' + globalParameter['LocalHostname'] + ' public ip : ' + globalParameter['PublicIp'] + ', local ip : ' + globalParameter['LocalIp'] + '' + ' warning Controller is alive'
    print(jarvis_cmd)
    RunJarvis(jarvis_cmd)    

    while(globalParameter['MAINLOOP_CONTROLLER']):
        try:                 
            mainLoop()
            time.sleep(globalParameter['MAINLOOP_SLEEP_SECONDS']) 
            #print('Loop')
        except:
            print('Error Loop')
    pass

def VirtualInput():
    pass

def mainLoopProcess(input_data):
    result = None

    rows = globalParameter['CriticalServices']
    if(len(rows) > 0):
        for row in rows:                
            alive = False
            process_arg_target = str(row)    
            alive = CheckProcess("python", process_arg_target)
            
            if(alive == False):
                print(process_arg_target + ' is dead')
                RunJarvis('error handler ' + globalParameter['LocalUsername'] + '@' + globalParameter['LocalHostname'] + ' error ' + process_arg_target.replace("-base=", "in base ") + ' host:' + globalParameter['LocalHostname'] + '')
                
                #reopen apps local
                print('reopen ' + process_arg_target)
                RunJarvis(process_arg_target)

                alive = CheckProcess("python", process_arg_target)
                if(alive == False):
                    print(process_arg_target + ' is real dead')
                    RunJarvis('error handler ' + globalParameter['LocalUsername'] + '@' + globalParameter['LocalHostname'] + ' it did not open ' + process_arg_target.replace("-base=", "in base ") + ' host:' + globalParameter['LocalHostname'] + '')
                else:
                    print(process_arg_target + ' is alive now')
                    RunJarvis('error handler ' + globalParameter['LocalUsername'] + '@' + globalParameter['LocalHostname'] + ' it is alive now ' + process_arg_target.replace("-base=", "in base ") + ' host:' + globalParameter['LocalHostname'] + '')

 
    return result

def Main():
    """services control | on critical failure, it reopens apps in CriticalServices list | use [CriticalServices] in config.ini | list services in web (/list/services)"""    

    global globalParameter
    
    GetCorrectPath()

    try:        
        globalParameter['LocalIp'] = GetCorrectIp(socket.gethostbyname_ex(socket.gethostname()))
        globalParameter['PublicIp'] = GetPublicIp()
    except:
        print('error ip')
        
    try:
        t = Thread(target=mainThread)
        t.start()  
    except:
        print('error mainThread')

    try:
        if(globalParameter['MAINWEBSERVER'] == True):
            #app.run(host = str(globalParameter['LocalIp']),port=globalParameter['LocalPort'], ssl_context='adhoc') 
            app.run(host = str(globalParameter['LocalIp']),port=globalParameter['LocalPort']) 
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
        suite.addTest(TestCases("test_dump")) 
        runner = unittest.TextTestRunner()
        runner.run(suite)  
        globalParameter['MAINLOOP_CONTROLLER'] = False        
        sys.exit()        

    param = ' '.join(unknown)

    Main()