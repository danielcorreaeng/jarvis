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
import shutil

globalParameter['INPUT_DATA_OFF'] = False
globalParameter['OUTPUT_DATA_OFF'] = False
globalParameter['MAINLOOP_CONTROLLER'] = False
globalParameter['MAINWEBSERVER'] = True
globalParameter['PROCESS_JARVIS'] = None

globalParameter['LocalPort'] = 8812

globalParameter['TargetPath'] = None

globalParameter['TargetDB'] = globalParameter['LocalHostname'] + "_" + globalParameter['LocalUsername']
globalParameter['PathDB'] = os.path.join(globalParameter['PathLocal'], "Db", globalParameter['TargetDB'] + ".db")
globalParameter['TAG_SEPARATOR'] = '_' 
globalParameter['TAG_SEPARATOR_EXTRA'] = ' ' 

class TestCases_Local(TestCases):
    def test_dump(self):
        check = True
        self.assertTrue(check)    

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

@app.route('/rename', methods=['POST'])
@login_required
def rename_file():
    try:
        old_name = request.form.get('old_filename')
        new_name = request.form.get('new_filename')
        file_ext = request.form.get('file_ext')
        
        if not old_name or not new_name or not file_ext:
            return jsonify({"status": "error", "message": "Missing required parameters"})
        
        old_path = os.path.join(globalParameter['TargetPath'], old_name + "." + file_ext)
        new_path = os.path.join(globalParameter['TargetPath'], new_name + "." + file_ext)
        
        if not os.path.exists(old_path):
            return jsonify({"status": "error", "message": "File not found"})
            
        if os.path.exists(new_path):
            return jsonify({"status": "error", "message": "A file with this name already exists"})
        
        # Rename the file
        shutil.move(old_path, new_path)
        
        return jsonify({"status": "success", "message": "File renamed successfully", "redirect": request.referrer})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

def makeTable():
    TITLE = 'TABLE'
    DATA =  ''
    DATA += '<div class="table-responsive"><table id="example1" class="table table-bordered table-striped">'
    DATA += '<thead>'
    DATA += '<tr><th>Tags</th><th>Type</th><th>Action</th></tr>'
    DATA += '</thead>'
    DATA += '<tbody>'

    files = []
    for ext in ('*.png', '*.jpg', '*.jpeg', '*.json', '*.mp4', '*.gif'):
        files.extend(glob(join(globalParameter['TargetPath'], ext)))

    idcount = 0
    for _localfile in files:
        idcount = idcount + 1
        name = os.path.splitext(os.path.basename(_localfile))[0]
        filetype = _localfile.split(".")[-1]
        filepath = request.url_root + 'External/' + os.path.basename(_localfile)
        name_tags = name.replace(globalParameter['TAG_SEPARATOR_EXTRA'], globalParameter['TAG_SEPARATOR'])

        DATA += '''<tr><th><span class='badge bg-primary'>''' + name_tags.replace(globalParameter['TAG_SEPARATOR'], "</span>&nbsp;<span class='badge bg-primary'>") + '''</span></th><th>''' + filetype + '''</th><th><a data-bs-toggle="modal" data-bs-target="#modal1" href="#" onclick="FileToModal(''' + str(idcount) + ''');return false;"><span class='badge bg-primary'>view</span></a></th></tr>'''

    DATA += '</tbody>'
    DATA += '<tfoot><tr><th>Tags</th><th>Type</th><th>Action</th></tr></tfoot>'
    DATA += '</table></div>'

    DATA += '''<div class="modal fade" id="modal1" tabindex="1000" role="dialog" aria-labelledby="exampleModalLabel" aria-hidden="true">
    <div class="modal-dialog" role="document">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title" id="modalTitle"></h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
                <div id="divmodal1"></div>
                <form id="renameForm" class="mt-3" style="display: none;">
                    <div class="mb-3">
                        <label for="fileName" class="form-label">Editar nome do arquivo:</label>
                        <input type="text" class="form-control" id="fileName" name="new_filename">
                        <input type="hidden" id="oldFileName" name="old_filename">
                        <input type="hidden" id="fileExt" name="file_ext">
                    </div>
                </form>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-warning" id="editButton" onclick="toggleEditForm()">Editar</button>
                <button type="button" class="btn btn-primary" id="saveButton" onclick="renameFile()" style="display: none;">Salvar</button>
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Fechar</button>
            </div>
        </div>
    </div>
</div>'''

    PAGE_SCRIPT = '''    <script>
    var myModal = new bootstrap.Modal(document.getElementById('modal1'));
    
    function toggleEditForm() {
        var form = document.getElementById('renameForm');
        var editButton = document.getElementById('editButton');
        var saveButton = document.getElementById('saveButton');
        
        if (form.style.display === 'none') {
            form.style.display = 'block';
            editButton.classList.remove('btn-warning');
            editButton.classList.add('btn-secondary');
            editButton.textContent = 'Cancelar';
            saveButton.style.display = 'inline-block';
        } else {
            form.style.display = 'none';
            editButton.classList.remove('btn-secondary');
            editButton.classList.add('btn-warning');
            editButton.textContent = 'Editar';
            saveButton.style.display = 'none';
        }
    }
    
    function showRenameAlert(type, message) {
        var alertDiv = document.createElement('div');
        alertDiv.classList.add('alert', 'alert-' + type, 'alert-dismissible', 'fade', 'show');
        alertDiv.setAttribute('role', 'alert');
        alertDiv.innerHTML = message + 
            '<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>';
        
        document.querySelector('.modal-body').prepend(alertDiv);
        
        // Auto dismiss after 5 seconds
        setTimeout(function() {
            alertDiv.remove();
        }, 5000);
    }
    
    function renameFile() {
        var formData = new FormData(document.getElementById('renameForm'));
        
        fetch('/rename', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                showRenameAlert('success', data.message);
                setTimeout(function() {
                    window.location.reload();
                }, 2000);
            } else {
                showRenameAlert('danger', data.message);
            }
        })
        .catch(error => {
            showRenameAlert('danger', 'Erro ao renomear arquivo: ' + error);
        });
    }
    </script>'''
    
    PAGE_SCRIPT += '''<script>$(function () {$('#example1').DataTable({'paging': true,'lengthChange': false,'searching' : true,'ordering': true,'info': true,'autoWidth' : false, dom: 'Bfrtip',buttons: []})})</script>'''
    PAGE_SCRIPT += '''<script>'''
    PAGE_SCRIPT += '''var dict = {};'''
    PAGE_SCRIPT += '''var fileNames = {};'''
    PAGE_SCRIPT += '''var fileExts = {};'''

    # Função auxiliar para escapar strings JavaScript
    def escape_js_string(s):
        """Escapa strings para uso seguro em JavaScript"""
        if s is None:
            return ''
        return (str(s)
                .replace('\\', '\\\\')
                .replace("'", "\\'")
                .replace('"', '\\"')
                .replace('\n', '\\n')
                .replace('\r', '\\r')
                .replace('\t', '\\t'))

    idcount = 0
    for _localfile in files:
        idcount = idcount + 1
        name = os.path.splitext(os.path.basename(_localfile))[0]
        filetype = _localfile.split(".")[-1]
        filepath = request.url_root + 'External/' + os.path.basename(_localfile)
        
        # Escapar os nomes dos arquivos para JavaScript
        name_escaped = escape_js_string(name)
        filepath_escaped = escape_js_string(filepath)
        
        # Store the file name and extension for the renaming functionality
        PAGE_SCRIPT += '''fileNames[''' + str(idcount) + '''] = "''' + name_escaped + '''";'''
        PAGE_SCRIPT += '''fileExts[''' + str(idcount) + '''] = "''' + escape_js_string(filetype) + '''";'''

        if(filetype.lower() == "mp4"):
            PAGE_SCRIPT += '''dict[''' + str(idcount) + '''] = '<video width="100%" controls><source src="''' + filepath_escaped +  '''" type="video/mp4">Error =S</video>';'''
        elif(filetype.lower() == 'png' or  filetype.lower() == 'jpg'  or  filetype.lower() == 'jpeg'  or  filetype.lower() == 'gif'):
            PAGE_SCRIPT += '''dict[''' + str(idcount) + '''] = '<img id="img''' + str(idcount) + '''" style="width:100%" src="''' + filepath_escaped +  '''">';'''
        elif(filetype.lower() == 'json'):
            try:
                data = ''
                with open(_localfile, 'r', encoding='utf-8') as json_file:
                    data = json.load(json_file)
                    print(data)               

                form = "<form>"
                form += "<input type='hidden' name='id_name' value='"+ escape_js_string(name) + "'>"
                
                for key in data:
                    value = data[key]
                    key_escaped = escape_js_string(key)
                    value_escaped = escape_js_string(value)
                    
                    form += """<div class='form-group'>"""                            
                    form += """<label for=""" + key_escaped + """>""" + key_escaped + """:</label>"""
                    form += """<div class='input-group'>"""                        

                    if(key == "link"):
                        if 'http' not in str(value):
                            value = "http://" + str(value)
                            value_escaped = escape_js_string(value)
                        form += """<div class='input-group-prepend'>"""
                        form += """<a href='""" + value_escaped + """' target='_blank'><button class='btn btn-outline-secondary' type='button'>Link</button></a>"""
                        form += """</div>"""

                    form += """<input type='input' class='form-control' name='""" + key_escaped + """' id='""" + key_escaped + """' value='""" + value_escaped + """'>"""

                    form += """</div>"""
                    form += """</div><br>&nbsp<br>"""
                form += "</form>"

                # Escapar o HTML do formulário para JavaScript
                form_escaped = escape_js_string(form)
                PAGE_SCRIPT += '''dict[''' + str(idcount) + '''] = "''' + form_escaped + '''";'''
                
            except Exception as e:
                print(f"Erro ao processar arquivo JSON {_localfile}: {e}")
                PAGE_SCRIPT += '''dict[''' + str(idcount) + '''] = "Erro ao carregar arquivo JSON";'''
        else:
            PAGE_SCRIPT += '''dict[''' + str(idcount) + '''] = "Formato não suportado";'''

    PAGE_SCRIPT += '''function FileToModal(id) { 
        document.getElementById("divmodal1").innerHTML=dict[id];
        document.getElementById("fileName").value = fileNames[id];
        document.getElementById("oldFileName").value = fileNames[id];
        document.getElementById("fileExt").value = fileExts[id];
        document.getElementById("modalTitle").textContent = fileNames[id] + "." + fileExts[id];
        
        // Reset edit form state
        var form = document.getElementById('renameForm');
        var editButton = document.getElementById('editButton');
        var saveButton = document.getElementById('saveButton');
        
        form.style.display = 'none';
        editButton.classList.remove('btn-secondary');
        editButton.classList.add('btn-warning');
        editButton.textContent = 'Editar';
        saveButton.style.display = 'none';
    }'''    
    PAGE_SCRIPT += '''</script>'''

    PAGE_MENU = '<nav id="sidebarMenu" class="col-md-3 col-lg-2 d-md-block bg-light sidebar collapse"><div class="position-sticky pt-3"><ul class="nav flex-column"><li class="nav-item"><a class="nav-link active" aria-current="page" href="' + str(request.url_root) + 'table"><span data-feather="home"></span>Table</a></li><li class="nav-item"><a class="nav-link" href="' + str(request.url_root) + 'gallery"><span data-feather="file"></span>Gallery</a></li></ul></div></nav>'

    return makePage(TITLE, DATA, PAGE_SCRIPT, '', PAGE_MENU)

def makeGallery():
    TITLE = 'Gallery'
    PAGE_PAGE_CSS = '''<style>.column000 {  float: left;  width: 33.33%;  display: none;} .show000 {  display: block;} </style>'''
    PAGE_PAGE_CSS += '''<style>.search { position: relative;box-shadow: 0 0 40px rgba(51, 51, 51, .1)}.search input {height: 60px;text-indent: 25px;border: 2px solid #d6d4d4}.search input:focus {box-shadow: none;border: 2px solid blue}.search .fa-search {position: absolute;top: 20px;left: 16px}.search button {position: absolute;top: 5px;right: 5px;height: 50px;width: 110px;background: blue}</style>'''
    DATA =  ''''''
    DATA += '''<div class="container"><div class="row"><div class="row">'''

    files = []
    for ext in ('*.png', '*.jpg', '*.jpeg', '*.gif'):
        files.extend(glob(join(globalParameter['TargetPath'], ext)))

    tags = {}

    idcount = 0
    for _localfile in files:
        idcount = idcount + 1
        name = os.path.splitext(os.path.basename(_localfile))[0]
        filetype = _localfile.split(".")[-1]
        filepath = request.url_root + 'External/' + os.path.basename(_localfile)

        name_tags = name.replace(globalParameter['TAG_SEPARATOR_EXTRA'], globalParameter['TAG_SEPARATOR'])

        tags_local = name_tags.split(globalParameter['TAG_SEPARATOR'])

        for tag in tags_local:
                if tag in tags.keys(): 
                    value = tags[tag]
                    tags[tag] = value + 1
                else: 
                    tags[tag] = 1

        DATA += '''<div class=" col-lg-3 col-md-4 col-xs-6 thumb column000 people ''' + name + '''"><div class="content"><a data-bs-toggle="modal" data-bs-target="#modal1" href="#" onclick="ImageToModal(''' + str(idcount) + ''');return false;"><img  id="img''' + str(idcount) + '''" style="width:100%" src="''' + filepath  +  '''"></a><h4></h4><p><span class='badge bg-primary'>''' + name_tags.replace(globalParameter['TAG_SEPARATOR'], "</span>&nbsp;<span class='badge bg-primary'>") + '''</span></p></div></div>'''  

    DATA += '''</div></div></div>'''  
    DATA += '''<div class="modal fade" id="modal1" tabindex="1000" role="dialog" aria-labelledby="exampleModalLabel" aria-hidden="true">
    <div class="modal-dialog" role="document">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title" id="modalTitle"></h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
                <div id="divmodal1"><img id="imgmodal1" style="width:100%"></div>
                <form id="renameForm" class="mt-3" style="display: none;">
                    <div class="mb-3">
                        <label for="fileName" class="form-label">Editar nome do arquivo:</label>
                        <input type="text" class="form-control" id="fileName" name="new_filename">
                        <input type="hidden" id="oldFileName" name="old_filename">
                        <input type="hidden" id="fileExt" name="file_ext">
                    </div>
                </form>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-warning" id="editButton" onclick="toggleEditForm()">Editar</button>
                <button type="button" class="btn btn-primary" id="saveButton" onclick="renameFile()" style="display: none;">Salvar</button>
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Fechar</button>
            </div>
        </div>
    </div>
</div>'''

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
    PAGE_SCRIPT = '''    <script>
    var myModal = new bootstrap.Modal(document.getElementById('modal1'));
    
    function toggleEditForm() {
        var form = document.getElementById('renameForm');
        var editButton = document.getElementById('editButton');
        var saveButton = document.getElementById('saveButton');
        
        if (form.style.display === 'none') {
            form.style.display = 'block';
            editButton.classList.remove('btn-warning');
            editButton.classList.add('btn-secondary');
            editButton.textContent = 'Cancelar';
            saveButton.style.display = 'inline-block';
        } else {
            form.style.display = 'none';
            editButton.classList.remove('btn-secondary');
            editButton.classList.add('btn-warning');
            editButton.textContent = 'Editar';
            saveButton.style.display = 'none';
        }
    }
    
    function showRenameAlert(type, message) {
        var alertDiv = document.createElement('div');
        alertDiv.classList.add('alert', 'alert-' + type, 'alert-dismissible', 'fade', 'show');
        alertDiv.setAttribute('role', 'alert');
        alertDiv.innerHTML = message + 
            '<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>';
        
        document.querySelector('.modal-body').prepend(alertDiv);
        
        // Auto dismiss after 5 seconds
        setTimeout(function() {
            alertDiv.remove();
        }, 5000);
    }
    
    function renameFile() {
        var formData = new FormData(document.getElementById('renameForm'));
        
        fetch('/rename', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                showRenameAlert('success', data.message);
                setTimeout(function() {
                    window.location.reload();
                }, 2000);
            } else {
                showRenameAlert('danger', data.message);
            }
        })
        .catch(error => {
            showRenameAlert('danger', 'Erro ao renomear arquivo: ' + error);
        });
    }
    </script>'''
    
    PAGE_SCRIPT += '''<script>filterSelection("all");function filterSelection(c) {  var x, i;  x = document.getElementsByClassName("column000");  if (c == "all") c = "";  for (i = 0; i < x.length; i++) {    w3RemoveClass(x[i], "show000");    if (x[i].className.indexOf(c) > -1) w3AddClass(x[i], "show000");  }}function w3AddClass(element, name) {  var i, arr1, arr2;  arr1 = element.className.split(" ");  arr2 = name.split(" ");  for (i = 0; i < arr2.length; i++) {    if (arr1.indexOf(arr2[i]) == -1) {      element.className += " " + arr2[i];    }  }}function w3RemoveClass(element, name) {  var i, arr1, arr2;  arr1 = element.className.split(" ");  arr2 = name.split(" ");  for (i = 0; i < arr2.length; i++) {    while (arr1.indexOf(arr2[i]) > -1) {      arr1.splice(arr1.indexOf(arr2[i]), 1);    }  }  element.className = arr1.join(" ");} '''
    
    PAGE_SCRIPT += '''var fileNames = {};'''
    PAGE_SCRIPT += '''var fileExts = {};'''
    
    idcount = 0
    for _localfile in files:
        idcount = idcount + 1
        name = os.path.splitext(os.path.basename(_localfile))[0]
        filetype = _localfile.split(".")[-1]
        
        # Store the file name and extension for the renaming functionality
        PAGE_SCRIPT += '''fileNames[''' + str(idcount) + '''] = "''' + name + '''";'''
        PAGE_SCRIPT += '''fileExts[''' + str(idcount) + '''] = "''' + filetype + '''";'''
    
    PAGE_SCRIPT += '''function ImageToModal(id) { 
        document.getElementById("imgmodal1").src=document.getElementById("img" + id).src;
        document.getElementById("fileName").value = fileNames[id];
        document.getElementById("oldFileName").value = fileNames[id];
        document.getElementById("fileExt").value = fileExts[id];
        document.getElementById("modalTitle").textContent = fileNames[id] + "." + fileExts[id];
        
        // Reset edit form state
        var form = document.getElementById('renameForm');
        var editButton = document.getElementById('editButton');
        var saveButton = document.getElementById('saveButton');
        
        form.style.display = 'none';
        editButton.classList.remove('btn-secondary');
        editButton.classList.add('btn-warning');
        editButton.textContent = 'Editar';
        saveButton.style.display = 'none';
    }'''
    PAGE_SCRIPT += '''function SearchFunction(){var searchvalue = document.getElementById('search_input').value; filterSelection(searchvalue);}</script>'''

    PAGE_MENU = '<nav id="sidebarMenu" class="col-md-3 col-lg-2 d-md-block bg-light sidebar collapse"><div class="position-sticky pt-3"><ul class="nav flex-column"><li class="nav-item"><a class="nav-link active" aria-current="page" href="' + str(request.url_root) + 'table"><span data-feather="home"></span>Table</a></li><li class="nav-item"><a class="nav-link" href="' + str(request.url_root) + 'gallery"><span data-feather="file"></span>Gallery</a></li></ul></div></nav>'

    return makePage(TITLE, DATA, PAGE_SCRIPT,PAGE_PAGE_CSS,PAGE_MENU)

def Main():
    """view the images from path in web (/table). Optional parameters: -t (--target) to select a base -p (--port) to select target port """    

    global globalParameter

    #globalsub.subs(LoadVarsIni, LoadVarsIni2)
    
    GetCorrectPath()

    try:
        if(globalParameter['MAINWEBSERVER'] == True):
            remoteLogTargetIp = GetCorrectIp()
            if(globalParameter['LocalIp'] != '0.0.0.0'): remoteLogTargetIp = globalParameter['LocalIp']
            rl = RemoteLog()
            rl.CheckRestAPIThread(command="viewer files -base=services -t " + globalParameter['TargetPath'], host = str(remoteLogTargetIp),port=globalParameter['LocalPort'])
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
    parser.add_argument('-t','--target', help='Path target')
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