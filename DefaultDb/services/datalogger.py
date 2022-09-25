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
globalParameter['PathDB'] = os.path.join(globalParameter['PathLocal'], "Db", "log.db")

globalParameter['LocalPort'] = 8810
globalParameter['PreferredNetworks'] = ['192.168.15.','127.0.0.']
globalParameter['BlockedNetworks'] = ['192.168.56.', '192.168.100.']
globalParameter['LocalIp'] = socket.gethostbyname(socket.gethostname())
globalParameter['LocalUsername'] = getpass.getuser().replace(' ','_')
globalParameter['LocalHostname'] = socket.gethostname().replace(' ','_')

globalParameter['MAINWEBSERVER'] = True

globalParameter['password'] = 'ghRW8n@KVp'
globalParameter['secret_key'] = 'gVWx3*nmD@'

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
        self.assertTrue(True)    

class MyException(Exception):
    def __init__(self, value):
        self.parameter = value
    def __str__(self):
        return repr(self.parameter)

class MyLog():
    def __init__(self):
    	pass

    def __del__(self):
    	pass

    def Insert(self, _id , _user , _host , _time , _command , _status):
        result = False

        try:
            db = globalParameter['PathDB']

            if(os.path.isfile(db) == False):
                conn = sqlite3.connect(db)
                cursor = conn.cursor()
                cursor.execute("CREATE TABLE log (localid integer PRIMARY KEY AUTOINCREMENT , id string, user string, host string, start string, finish string, alive string, command string, log string)")
                conn.commit()
                conn.close()

            conn = sqlite3.connect(db)
            cursor = conn.cursor()
            sql = ''

            if(_status == 'start'):
                sql =  "update log set user='"+ _user +"', host='"+ _host +"', command='"+ _command +"', log='"+ _status +"', start='"+ _time +"' where id='"+ _id +"'"
            elif(_status == 'finish'):
                sql =  "update log set user='"+ _user +"', host='"+ _host +"', command='"+ _command +"', log='"+ _status +"', finish='"+ _time +"' where id='"+ _id +"'"
            elif(_status == 'alive'):
                sql =  "update log set user='"+ _user +"', host='"+ _host +"', command='"+ _command +"', log='"+ _status +"', alive='"+ _time +"' where id='"+ _id +"'"
            print(sql)

            cursor.execute(sql)
            rowchange = cursor.rowcount
            cursor.execute(sql)
            conn.commit()

            if(rowchange==0):
                if(_status == 'start'):
                    sql = "insert or ignore into log (id , user , host , start, finish, alive, command , log) values ('"+ _id +"', '"+ _user +"', '"+ _host +"', '"+ _time +"','','','"+ _command +"','"+ _status +"' )"
                elif(_status == 'finish'):
                    sql =  "insert or ignore into log (id , user , host , start, finish, alive , command , log) values ('"+ _id +"','"+ _user +"', '"+ _host +"', '','"+ _time +"','','"+ _command +"','"+ _status +"' )"
                elif(_status == 'alive'):
                    sql =  "insert or ignore into log (id , user , host , start, finish, alive , command , log) values ('"+ _id +"','"+ _user +"', '"+ _host +"', '"+ _time +"','','','"+ _command +"','"+ _status +"' )"
                print(sql)
                #return
                cursor.execute(sql)
                conn.commit()
                conn.close()

            result = True
        except:
        	raise MyException("MyDb : CheckDb : Internal Error.")

        return result

    def SelectAll(self):
        result = None

        #try:
        db = globalParameter['PathDB']
        print(db)
        conn = sqlite3.connect(db)
        cursor = conn.cursor()
        sql = "SELECT * FROM log order by localid desc LIMIT 50"
        print(sql)
        cursor.execute(sql)

        result = rows = cursor.fetchall()

        if(len(rows) > 0):
            for row in rows:
                #print(row)
                pass

        conn.close()
        #except:
        #	raise MyException("MyDb : Select : Internal Error.")

        return result

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

@app.route('/log', methods=['POST'])
def Log():
    if request.method == 'POST':    
        data = request.get_json(force=True)
        print(data)
        data = data[0]        
        print(data)

        _id = data['id']
        _user = data['user']
        _host = data['host']
        _time = data['time']
        _command = data['command']
        _status = data['status']

        db = MyLog()
        db.Insert(_id , _user , _host , _time , _command , _status)
        #db.SelectAll()
        return 'ok'

@app.route('/list/log')
@login_required
def ExampleTable():

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
    globalParameter['PathDB'] = os.path.join(globalParameter['PathLocal'], 'Db','log.db')

    if(os.path.isfile(ini_file) == True):
        with open(ini_file) as fp:
            config = configparser.ConfigParser()
            config.read_file(fp)
            sections = config.sections()
            if('Parameters' in sections):
                if('defaultpassword' in config['Parameters']):
                    globalParameter['password'] = config['Parameters']['defaultpassword']
                    print('password:' + globalParameter['password'])

def makeTable():
    TITLE = 'TABLE'
    DATA =  ''
    DATA += '<div class="table-responsive"><table id="example1" class="table table-bordered table-striped">'
    DATA += '<thead>'
    DATA += '<tr><th>#</th><th>user</th><th>host</th><th>Start</th><th>Finish</th><th>Alive</th><th>Command</th><th>status</th></tr>'
    DATA += '</thead>'
    DATA += '<tbody>'

    list_process_checked = []
    db = MyLog()
    rows = db.SelectAll()

    if(len(rows) > 0):
        for row in rows:
            process_arg_target = str(row[7])
            
            alive = False
            if process_arg_target in list_process_checked:
                alive = False
            else:
                if(str(row[3]) == str(globalParameter['LocalHostname'])):
                    alive = CheckProcess("python", process_arg_target)
                list_process_checked.append(process_arg_target)
            
            DATA += '<tr><td>'
            DATA += str(row[0])
            DATA += '</td><td>'
            DATA += str(row[2])
            DATA += '</td><td>'
            DATA += str(row[3])
            DATA += '</td><td>'
            DATA += str(row[4]).replace('_',' ')
            DATA += '</td><td>'
            DATA += str(row[5]).replace('_',' ')
            DATA += '</td><td>'
            DATA += str(row[6]).replace('_',' ')
            DATA += '</td><td>'

            if(len(row[7])>50):
                DATA += str(row[7][:50]) + "..."
            else:
                DATA += str(row[7])
            DATA += '</td><td>'
            
            if(str(row[3]) != str(globalParameter['LocalHostname'])):
                DATA += "Remote"
            else:
                if(alive == True):
                    DATA += "Alive"
                else:
                    DATA += "Dead"
            
            DATA += '</td></tr>'
            pass

    DATA += '</tbody>'
    DATA += '<tfoot><tr><th>#</th><th>user</th><th>host</th><th>Start</th><th>Finish</th><th>Alive</th><th>Command</th><th>status</th></tr></tfoot>'
    DATA += '</table></div>'
    PAGE_SCRIPT = "<script>$(function () {$('#example1').DataTable({'paging': true,'lengthChange': false,'searching' : true,'ordering': true,'info': true,'autoWidth' : false,'order': [[ 5, 'desc' ]],dom: 'Bfrtip',buttons: ['copy', 'excel', 'pdf', 'print']})})</script>"
    return makePage(TITLE, DATA, PAGE_SCRIPT)

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

def Main():
    """logger of jarvis | list logs in web (/list/log)"""     

    global globalParameter
    
    GetCorrectPath()

    try:        
        globalParameter['LocalIp'] = GetCorrectIp(socket.gethostbyname_ex(socket.gethostname()))
    except:
        print('error ip')
        
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
        sys.exit()        

    param = ' '.join(unknown)

    Main()