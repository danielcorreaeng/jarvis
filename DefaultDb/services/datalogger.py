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

globalParameter['INPUT_DATA_OFF'] = False
globalParameter['OUTPUT_DATA_OFF'] = False
globalParameter['MAINLOOP_CONTROLLER'] = False
globalParameter['MAINWEBSERVER'] = True
globalParameter['PROCESS_JARVIS'] = None

globalParameter['LocalPort'] = 8810

class TestCases_Local(TestCases):
    def test_dump(self):
        check = True
        self.assertTrue(check)  

def FixVars():
    global globalParameter
    globalParameter['PathDB'] = os.path.join(globalParameter['PathLocal'], "Db", "log.db")

class MyLog():
    def __init__(self):
        pass

    def __del__(self):
        pass

    def CheckDb(self, db):
        result = False

        try:
            checkdb = os.path.isfile(db)          
            conn = sqlite3.connect(db)
            cursor = conn.cursor()		

            if(checkdb == False):
                sql = "CREATE TABLE log (localid integer PRIMARY KEY AUTOINCREMENT , id string, user string, host string, start string, finish string, alive string, command string, log string, tag string)"
                cursor.execute(sql)
                conn.commit()
            else:
                sql = "SELECT COUNT(*) AS CNTREC FROM pragma_table_info('log') WHERE name='tag'"
                cursor.execute(sql)
                result = cursor.fetchall()[0][0]

                if(int(result)==0):
                    sql = "ALTER TABLE log ADD tag TEXT DEFAULT command"
                    cursor.execute(sql)
                    conn.commit()
                    sql = "UPDATE log SET tag = 'command' WHERE id>0"
                    cursor.execute(sql)
                    conn.commit()

            conn.close()

            result = True
        except:
            raise MyException("MyDb : CheckDb : Internal Error.")

        return result

    #def sqlCreateLog(self):
    #    return "CREATE TABLE log (localid integer PRIMARY KEY AUTOINCREMENT , id string, user string, host string, start string, finish string, alive string, command string, log string)"

    def Insert(self, _id , _user , _host , _time , _command , _status, _tag):
        result = False

        try:
            db = globalParameter['PathDB']
            self.CheckDb(db)

            conn = sqlite3.connect(db)
            cursor = conn.cursor()
            sql = ''

            if(_status == 'start'):
                sql =  "update log set user='"+ _user +"', host='"+ _host +"', command='"+ _command +"', log='"+ _status +"', tag='"+ _tag +"', start='"+ _time +"' where id='"+ _id +"'"
            elif(_status == 'finish'):
                sql =  "update log set user='"+ _user +"', host='"+ _host +"', command='"+ _command +"', log='"+ _status +"', tag='"+ _tag +"', finish='"+ _time +"' where id='"+ _id +"'"
            elif(_status == 'alive'):
                sql =  "update log set user='"+ _user +"', host='"+ _host +"', command='"+ _command +"', log='"+ _status +"', tag='"+ _tag +"', alive='"+ _time +"' where id='"+ _id +"'"
            print(sql)

            cursor.execute(sql)
            rowchange = cursor.rowcount
            cursor.execute(sql)
            conn.commit()

            if(rowchange==0):
                if(_status == 'start'):
                    sql = "insert or ignore into log (id , user , host , tag , start, finish, alive, command , log) values ('"+ _id +"', '"+ _user +"', '"+ _host +"', '"+ _tag +"', '"+ _time +"','','','"+ _command +"','"+ _status +"' )"
                elif(_status == 'finish'):
                    sql =  "insert or ignore into log (id , user , host , tag , start, finish, alive , command , log) values ('"+ _id +"','"+ _user +"', '"+ _host +"', '"+ _tag +"', '','"+ _time +"','','"+ _command +"','"+ _status +"' )"
                elif(_status == 'alive'):
                    sql =  "insert or ignore into log (id , user , host , tag , start, finish, alive , command , log) values ('"+ _id +"','"+ _user +"', '"+ _host +"', '"+ _tag +"', '"+ _time +"','','','"+ _command +"','"+ _status +"' )"
                print(sql)
                #return
                cursor.execute(sql)
                conn.commit()
                conn.close()

            result = True
        except:
            raise MyException("MyDb : CheckDb : Internal Error.")

        return result

    def SelectAll(self, tag=None):
        result = None

        try:
            db = globalParameter['PathDB']
            self.CheckDb(db)

            print(db)
            conn = sqlite3.connect(db)
            cursor = conn.cursor()
            sql = "SELECT localid , id , user , host , start , finish , alive , command , log , tag FROM log order by localid desc LIMIT 50"
            if(tag != None):
                sql = "SELECT localid , id , user , host , start , finish , alive , command , log , tag FROM log WHERE tag='" + tag + "' order by localid desc LIMIT 50"
            print(sql)
            cursor.execute(sql)

            result = rows = cursor.fetchall()

            if(len(rows) > 0):
                for row in rows:
                    #print(row)
                    pass

            conn.close()
        except:
            raise MyException("MyDb : Select : Internal Error.")

        return result 

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
        _tag = 'command'
        if 'tag' in data.keys():
            _tag = data['tag']


        db = MyLog()
        db.Insert(_id , _user , _host , _time , _command , _status, _tag)
        #db.SelectAll()
        return 'ok'

@app.route('/list/log')
@login_required
def Table():

    maskIp = globalParameter['LocalIp'].split('.')
    maskIp = str(maskIp[0]) + '.' + str(maskIp[1]) + '.' + str(maskIp[2]) 

    test = maskIp in str(request.remote_addr) 
        
    if test == True:
        print('authorized')
    else:
        print("not authorized")
        return "not authorized"

    tag = request.args.get('tag') 
    res = makeTable(tag)

    return res    

@app.route('/')
def index():
    return str(Main.__doc__) + " | ip server : " +  str(globalParameter['LocalIp']) + ":" + str(globalParameter['LocalPort'])

def makeTable(tag):
    TITLE = 'TABLE'
    DATA =  ''
    DATA += '<div class="table-responsive"><table id="example1" class="table table-bordered table-striped">'
    DATA += '<thead>'
    DATA += '<tr><th>#</th><th>user</th><th>host</th><th>Start</th><th>Finish</th><th>Alive</th><th>Command</th><th>status</th><th>tag</th></tr>'
    DATA += '</thead>'
    DATA += '<tbody>'

    list_process_checked = []
    db = MyLog()
    rows = db.SelectAll(tag)

    if(len(rows) > 0):
        for row in rows:
            process_arg_target = str(row[7])
            
            alive = False
            if process_arg_target in list_process_checked:
                alive = False
            else:
                if(str(row[3]) == str(globalParameter['LocalHostname'])):
                    alive, method = CheckProcess("python", process_arg_target)
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

            if(len(row[7])>60):
                DATA += str(row[7][:60]) + "..."
            else:
                DATA += str(row[7])
            DATA += '</td><td>'
            
            if(str(row[3]) != str(globalParameter['LocalHostname'])):
                DATA += "Remote"
            else:
                if(alive == True):
                    DATA += "Alive | " + method
                else:
                    DATA += "Dead | " + method

            DATA += '</td><td>'
            DATA += str(row[9]).replace(' ',',')            
            DATA += '</td></tr>'
            pass

    DATA += '</tbody>'
    DATA += '<tfoot><tr><th>#</th><th>user</th><th>host</th><th>Start</th><th>Finish</th><th>Alive</th><th>Command</th><th>status</th><th>tag</th></tr></tfoot>'
    DATA += '</table></div>'
    PAGE_SCRIPT = "<script>$(function () {$('#example1').DataTable({'paging': true,'lengthChange': false,'searching' : true,'ordering': true,'info': true,'autoWidth' : false,'order': [[ 5, 'desc' ]],dom: 'Bfrtip',buttons: ['copy', 'excel', 'pdf', 'print']})})</script>"


    local_addr = 'http://' + str(globalParameter['LocalIp']) + ":" + str(globalParameter['LocalPort'])
    PAGE_MENU = '''<nav id="sidebarMenu" class="col-md-3 col-lg-2 d-md-block bg-light sidebar collapse"><div class="position-sticky pt-3"><ul class="nav flex-column"><li class="nav-item"><a class="nav-link active" aria-current="page" href="''' + local_addr + '''/list/log"><span data-feather="home"></span>Commands</a></li><li class="nav-item"><a class="nav-link" href="''' + local_addr + '''/list/log?tag=service"><span data-feather="file"></span>Services</a></li></ul></div></nav>'''

    return makePage(TITLE, DATA, PAGE_SCRIPT,'', PAGE_MENU)

def Main():
    """logger of jarvis | list logs in web (/list/log)"""     

    global globalParameter
    
    #globalsub.subs(LoadVarsIni, LoadVarsIni2)

    GetCorrectPath()
    FixVars()
        
    try:
        if(globalParameter['MAINWEBSERVER'] == True):
            remoteLogTargetIp = GetCorrectIp()
            if(globalParameter['LocalIp'] != '0.0.0.0'): remoteLogTargetIp = globalParameter['LocalIp']
            rl = RemoteLog()
            rl.CheckRestAPIThread(command="datalogger -base=services", host = str(remoteLogTargetIp),port=globalParameter['LocalPort'])
            #app.run(host = str(globalParameter['LocalIp']),port=globalParameter['LocalPort'], ssl_context='adhoc') 
            app.run(host = str(globalParameter['LocalIp']),port=globalParameter['LocalPort']) 
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
        suite.addTest(TestCases_Local("test_webserver_fifo")) 
        suite.addTest(TestCases_Local("test_dump")) 
        runner = unittest.TextTestRunner()
        runner.run(suite)             
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