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


globalParameter['LocalPort'] = 8811

globalParameter['INPUT_DATA_OFF'] = True
globalParameter['OUTPUT_DATA_OFF'] = True
globalParameter['MAINLOOP_CONTROLLER'] = True
globalParameter['MAINWEBSERVER'] = True
globalParameter['MAINLOOP_SLEEP_SECONDS'] = 600.0
globalParameter['PROCESS_JARVIS'] = None

globalParameter['CriticalServices'] = ['chatbot -base=services', 'datalogger -base=services']

class TestCases_Local(TestCases):
    def test_dump(self):
        check = True
        self.assertTrue(check)  

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

def LoadVarsIni2(config,sections):
    global globalParameter

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
     
def mainThread2():
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

def mainLoopProcess2(input_data):
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

    globalsub.subs(LoadVarsIni, LoadVarsIni2)
    globalsub.subs(mainLoopProcess, mainLoopProcess2)
    globalsub.subs(mainThread, mainThread2)
    
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
        pass
    except:
        print('error webservice')
    
if __name__ == '__main__':   
    parser = argparse.ArgumentParser(description=Main.__doc__)
    parser.add_argument('-d','--description', help='Description of program', action='store_true')
    parser.add_argument('-u','--tests', help='Execute tests', action='store_true')
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
        globalParameter['MAINLOOP_CONTROLLER'] = False                     
        sys.exit()    

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