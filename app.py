import os
import json
import tempfile
import shutil
import sys
import importlib
from flask import Flask, request, jsonify, render_template, make_response, send_file


# To import filemanager.py in django example app named filemanager_app.
# Now we can import original python script without installing django package or deleting any lines on original file.
# We are not going to FileSystemStorage in django.

class faked_django():
    class FileSystemStorage():
        pass

sys.modules["django.core.files.storage"] = faked_django

# Using importlib library, we don't have to rename original name including hyphen
filemanager = importlib.import_module("angular-filemanager.bridges.python.django.filemanager_app.filemanager")


app = Flask(__name__, static_url_path='')

class FlaskFileManager(filemanager.FileManager):

    # Overriding original methods
    def upload(self, files, dest):
        try:
            for _file in files.values():
                path = os.path.join(self.root, dest.replace('/', '', 1))
                if not path.startswith(self.root):
                     return {'result': {'success': 'false', 'error': 'Invalid path'}}
                _file.save(os.path.join(path, _file.filename))
        except Exception as e:
            return {'result': {'success': 'false', 'error': 'true'}}
        return {'result': {'success': 'true', 'error': ''}}

    def download(self, path):
        path = os.path.abspath(self.root + path)
        if path.startswith(self.root) and os.path.isfile(path):
            try:
                with open(path, 'rb') as f:
                    response = make_response(f.read())
                    response.headers['Content-Type'] = "application/octet-stream"
                    response.headers['Content-Disposition'] = 'inline; filename=' + os.path.basename(path)
            except Exception as e:
                pass
                #raise Http404
        return response

    def downloadMultiple(self, request):
        items = request['items']
        folders = []
        for item in items:
            _path = os.path.join(self.root + os.path.expanduser(item))
            if not ( (os.path.exists(_path) or os.path.isfile(_path) ) and _path.startswith(self.root)):
                continue
            folders.append(_path)
        tmpdir = tempfile.mkdtemp()
        filename = request.get('toFilename')[0].replace('.zip', '',1)
        saved_umask = os.umask(77)
        path = os.path.join(tmpdir, filename)
        try:
            filemanager.compress_zip(path, folders)
            response = send_file(path+".zip")
            return [response, saved_umask, tmpdir]
        except IOError as e:
            print("IOError")
        else:
            shutil.rmtree(tmpdir, ignore_errors=True)

fm = FlaskFileManager(os.environ['HOME'], False)

@app.route("/")
def index():
    return render_template('index.html')


@app.route("/list", methods=['POST'])
def list_():
    return jsonify(fm.list(request.get_json()))


@app.route("/rename", methods=['POST'])
def rename():
    return jsonify(fm.rename(request.get_json()))


@app.route("/copy", methods=['POST'])
def copy():
    return jsonify(fm.copy(request.get_json()))


@app.route("/remove", methods=['POST'])
def remove():
    return jsonify(fm.remove(request.get_json()))


@app.route("/edit", methods=['POST'])
def edit():
    return jsonify(fm.edit(request.get_json()))


@app.route("/createFolder", methods=['POST'])
def createFolder():
    return jsonify(fm.createFolder(request.get_json()))


@app.route("/changePermissions", methods=['POST'])
def changePermissions():
    return jsonify(fm.changePermissions(request.get_json()))


@app.route("/compress", methods=['POST'])
def compress():
    return jsonify(fm.compress(request.get_json()))


@app.route("/download")
def download():
    return fm.download(request.args.get('path'))


@app.route("/downloadMultiple")
def downloadMultiple():
    ret = fm.downloadMultiple(request.args.to_dict(flat=False))
    os.umask(ret[1])
    shutil.rmtree(ret[2], ignore_errors=True)
    return ret[0]


@app.route("/move", methods=['POST'])
def move():
    return jsonify(fm.move(request.get_json()))


@app.route("/getContent", methods=['POST'])
def getContent():
    return jsonify(fm.getContent(request.get_json()))


@app.route("/extract", methods=['POST'])
def extract():
    return jsonify(fm.extract(request.get_json()))


@app.route("/upload", methods=['POST'])
def upload():
    return jsonify(fm.upload(request.files.to_dict(), request.form.get('destination')))

if __name__ == "__main__":
    app.run()
