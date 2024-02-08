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

globalParameter['LocalPort'] = 8812

globalParameter['TargetDB'] = globalParameter['LocalHostname'] + "_" + globalParameter['LocalUsername']
globalParameter['PathDB'] = os.path.join(globalParameter['PathLocal'], "Db", globalParameter['TargetDB'] + ".db")

class TestCases_Local(TestCases):
    def test_dump(self):
        check = True
        self.assertTrue(check)    

class MyDB_view(MyDB):
    def Select(self, type="filetype='jpg' or filetype='jpeg' or filetype='png'", id=None):
        result = None

        try:
            db = globalParameter['PathDB']
            conn = sqlite3.connect(db)
            cursor = conn.cursor()

            sql = "SELECT id,name,command,filetype FROM tag WHERE (" + type + ") order by id desc"
            if (id!=None):
                sql = "SELECT id,name,command,filetype FROM tag WHERE id=" + id +  " and (" + type + ") order by id desc" 
            
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

    def InsertTagWithJson(self, tag, inputJson):
        result = False

        #try:
        db = globalParameter['PathDB']
        conn = sqlite3.connect(db)
        cursor = conn.cursor()

        cursor.execute("insert or replace into tag (id, name, filetype, command) values ((select id from tag where name = '"+ tag +"'),'"+ tag +"','json', ?)", [inputJson])
        conn.commit()

        conn.close()

        result = True
        #except:
        #raise MyException("MyDb : InsertTag : Internal Error.")

        return result        

@app.route('/')
def index():
    return str(Main.__doc__) + " | ip server : " +  str(globalParameter['LocalIp']) + ":" + str(globalParameter['LocalPort'])

@app.route('/gallery')
@login_required
def Gallery():
    res = makeGallery()
    return res    

@app.route('/table')
@login_required
def Table():
    res = makeTable()
    return res   

@app.route('/update', methods = ['POST'])
@login_required
def TableResponse():

    if request.method == 'POST':

        request_local = request.form.to_dict(flat=False)

        new_json = {}
        update_id = None
        for key in request_local:

            if key == "id_name":
                update_id = request_local[key][0]
            else:
                new_json[key] = request_local[key][0]

        if(update_id != None):
            db = MyDB_view()
            db.InsertTagWithJson(update_id, json.dumps(new_json, indent = 4))

    res = makeTable()
    return res   

def makeTable():
    TITLE = 'TABLE'
    DATA =  ''
    DATA += '<div class="table-responsive"><table id="example1" class="table table-bordered table-striped">'
    DATA += '<thead>'
    DATA += '<tr><th>Tags</th><th>Type</th><th>Action</th></tr>'
    DATA += '</thead>'
    DATA += '<tbody>'

    db = MyDB_view()
    rows = db.Select(type="filetype='jpg' or filetype='jpeg' or filetype='png' or filetype='json'")

    tags = {}

    if(len(rows) > 0):
        idcount = 0
        for row in rows:
            id = row[0]
            name = row[1]
            raw = row[2]
            filetype = row[3]
            idcount = idcount + 1
    
            DATA += '''<tr><th><span class='badge bg-primary'>''' + name.replace(" ", "</span>&nbsp;<span class='badge bg-primary'>") + '''</span></th><th>''' + filetype + '''</th><th><a data-bs-toggle="modal" data-bs-target="#modal1" href="#" onclick="FileToModal(''' + str(idcount) + ''');return false;"><span class='badge bg-primary'>view</span></a></th></tr>'''

    DATA += '</tbody>'
    DATA += '<tfoot><tr><th>Tags</th><th>Type</th><th>Action</th></tr></tfoot>'
    DATA += '</table></div>'

    DATA += '''<div class="modal fade" id="modal1" tabindex="1000" role="dialog" aria-labelledby="exampleModalLabel" aria-hidden="true"><div class="modal-dialog" role="document"><div class="modal-content"><div class="modal-header"></div><div class="modal-body"><div id="divmodal1"></div><div class="modal-footer"><button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Fechar</button></div></div></div></div>'''

    PAGE_SCRIPT = '''<script>var myModal = new bootstrap.Modal(document.getElementById('modal1'));</script>'''
    PAGE_SCRIPT += '''<script>$(function () {$('#example1').DataTable({'paging': true,'lengthChange': false,'searching' : true,'ordering': true,'info': true,'autoWidth' : false, dom: 'Bfrtip',buttons: []})})</script>'''
    PAGE_SCRIPT += '''<script>'''
    PAGE_SCRIPT += '''var dict = {};'''

    if(len(rows) > 0):
        idcount = 0
        for row in rows:
            id = row[0]
            name = row[1]
            raw = row[2]
            filetype = row[3]
            idcount = idcount + 1
            
            if(filetype == 'jpg' or filetype == 'jpeg' or filetype == 'png' or filetype == 'bmp'):
                PAGE_SCRIPT += '''dict[''' + str(idcount) + '''] = '<img id="img''' + str(idcount) + '''" style="width:100%" src="data:image/''' + str(filetype) + ''';base64,''' + base64.b64encode(raw).decode('ascii') +  '''">';'''
            elif(filetype == 'json'):
                data = json.loads(raw)

                #form = "<form  action='" + str(request.base_url) + "/response' method='post'>"
                form = "<form action='" + str(request.url_root) + "update' method='post'>"
                form += "<input type='hidden' name='id_name' value='"+ str(name) + "'>"
                
                for key in data:
                        value = data[key]
                        form += """<div class='form-group'>"""                            
                        form += """<label for=""" + str(key) + """>""" + str(key) + """:</label>"""
                        form += """<div class='input-group'>"""                        

                        if(key == "link"):
                            if 'http' not in value:
                                value = "http://" + str(value)
                            form += """<div class='input-group-prepend'>"""
                            form += """<a href='""" + str(value) + """' target='_blank'><button class='btn btn-outline-secondary' type='button'>Link</button></a>"""
                            form += """</div>"""

                        form += """<input type='input' class='form-control' name='""" + str(key) + """' id='""" + str(key) + """' value='""" + str(value) + """'>"""

                        form += """</div>"""
                        form += """</div><br>&nbsp<br>"""
                form += """<input type='submit' class='btn pull-right btn-primary' value='Enviar'><br>&nbsp<br>"""
                form += "</form>"

                PAGE_SCRIPT += '''dict[''' + str(idcount) + '''] = "''' + form + '''";'''
            else:
                PAGE_SCRIPT += '''no suported'''
    
    PAGE_SCRIPT += '''function FileToModal(id) { document.getElementById("divmodal1").innerHTML=dict[id]; }'''    
    PAGE_SCRIPT += '''</script>'''
    return makePage(TITLE, DATA, PAGE_SCRIPT)

def makeGallery():
    TITLE = 'Gallery'
    PAGE_PAGE_CSS = '''<style>.column000 {  float: left;  width: 33.33%;  display: none;} .show000 {  display: block;} </style>'''
    PAGE_PAGE_CSS += '''<style>.search { position: relative;box-shadow: 0 0 40px rgba(51, 51, 51, .1)}.search input {height: 60px;text-indent: 25px;border: 2px solid #d6d4d4}.search input:focus {box-shadow: none;border: 2px solid blue}.search .fa-search {position: absolute;top: 20px;left: 16px}.search button {position: absolute;top: 5px;right: 5px;height: 50px;width: 110px;background: blue}</style>'''
    DATA =  ''''''
    DATA += '''<div class="container"><div class="row"><div class="row">'''

    db = MyDB_view()
    rows = db.Select()

    tags = {}

    if(len(rows) > 0):
        idcount = 0
        for row in rows:
            id = row[0]
            name = row[1]
            image = row[2]
            filetype = row[3]
            idcount = idcount + 1

            tags_local = name.split()

            for tag in tags_local:
                    if tag in tags.keys(): 
                        value = tags[tag]
                        tags[tag] = value + 1
                    else: 
                        tags[tag] = 1

            DATA += '''<div class=" col-lg-3 col-md-4 col-xs-6 thumb column000 people ''' + name + '''"><div class="content"><a data-bs-toggle="modal" data-bs-target="#modal1" href="#" onclick="ImageToModal(''' + str(idcount) + ''');return false;"><img  id="img''' + str(idcount) + '''" style="width:100%" src="data:image/''' + filetype + ''';base64,''' + base64.b64encode(image).decode('ascii') +  '''"></a><h4></h4><p><span class='badge bg-primary'>''' + name.replace(" ", "</span>&nbsp;<span class='badge bg-primary'>") + '''</span></p></div></div>'''  

    DATA += '''</div></div></div>'''  
    DATA += '''<div class="modal fade" id="modal1" tabindex="1000" role="dialog" aria-labelledby="exampleModalLabel" aria-hidden="true"><div class="modal-dialog" role="document"><div class="modal-content"><div class="modal-header"></div><div class="modal-body"><div id="divmodal1"><img id="imgmodal1" style="width:100%"></div></div><div class="modal-footer"><button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Fechar</button></div></div></div></div>'''

    tags = {k: v for k, v in sorted(tags.items(), key=lambda item: item[1])}
    tags = dict(sorted(  tags.items(), key=operator.itemgetter(1), reverse=True))

    BUTTONS =   '''<div class="container"><div class="row height d-flex justify-content-center align-items-center"><div class="col-md-8"><div class="search" > <i class="fa fa-search"></i> <input type="text" id="search_input" class="form-control" placeholder="Busca"> <button class="btn btn-primary" onclick="SearchFunction()">Busca</button> </div></div></div></div>'''
    BUTTONS +=  "<br>&nbsp;<br>" 
    BUTTONS +=  '''<div id="myBtnContainer"><button type="button" class="btn btn-primary" onclick="filterSelection('all')"> Show all</button>&nbsp;'''

    count = 0
    for tag in tags:
        BUTTONS +=  """<button type="button" class="btn btn-primary" onclick="filterSelection('""" + tag + """')">""" + tag + """</button>&nbsp;"""
        count = count + 1
        if(count>10):
            break

    DATA = BUTTONS + "<br>&nbsp;<br>" + DATA
    PAGE_SCRIPT = '''<script>var myModal = new bootstrap.Modal(document.getElementById('modal1'));</script>'''
    PAGE_SCRIPT += '''<script>filterSelection("all");function filterSelection(c) {  var x, i;  x = document.getElementsByClassName("column000");  if (c == "all") c = "";  for (i = 0; i < x.length; i++) {    w3RemoveClass(x[i], "show000");    if (x[i].className.indexOf(c) > -1) w3AddClass(x[i], "show000");  }}function w3AddClass(element, name) {  var i, arr1, arr2;  arr1 = element.className.split(" ");  arr2 = name.split(" ");  for (i = 0; i < arr2.length; i++) {    if (arr1.indexOf(arr2[i]) == -1) {      element.className += " " + arr2[i];    }  }}function w3RemoveClass(element, name) {  var i, arr1, arr2;  arr1 = element.className.split(" ");  arr2 = name.split(" ");  for (i = 0; i < arr2.length; i++) {    while (arr1.indexOf(arr2[i]) > -1) {      arr1.splice(arr1.indexOf(arr2[i]), 1);    }  }  element.className = arr1.join(" ");} '''
    PAGE_SCRIPT += '''function ImageToModal(id) { document.getElementById("imgmodal1").src=document.getElementById("img" + id).src; }'''
    PAGE_SCRIPT += '''function SearchFunction(){var searchvalue = document.getElementById('search_input').value; filterSelection(searchvalue);}</script>'''

    return makePage(TITLE, DATA, PAGE_SCRIPT,PAGE_PAGE_CSS)

def Main():
    """view the images from the database in web (/gallery or /table). Optional parameters: -t (--target) to select a base -p (--port) to select target port """    

    global globalParameter

    #globalsub.subs(LoadVarsIni, LoadVarsIni2)
    
    GetCorrectPath()

    target = globalParameter['PathDB']
    globalParameter['PathDB'] = os.path.join(globalParameter['PathLocal'], "Db", globalParameter['TargetDB'] + ".db")

    try:        
        if(globalParameter['LocalIp'] == None):
            globalParameter['LocalIp'] = GetCorrectIp(socket.gethostbyname_ex(socket.gethostname()))
    except:
        print('error ip')

    try:
        if(globalParameter['MAINWEBSERVER'] == True):
            rl = RemoteLog()
            rl.CheckRestAPIThread(command="viewer base -base=services -t " + target, host = str(globalParameter['LocalIp']),port=globalParameter['LocalPort'])
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
    parser.add_argument('-t','--target', help='target base')
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

    if args['target'] is not None:
        print('TargetDB: ' + args['target'])
        globalParameter['TargetDB'] = args['target']      

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
    