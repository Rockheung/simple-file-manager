import os
import json
import shutil
import importlib
import sys
import importlib
from flask import Flask, request, jsonify, render_template

# from django.shortcuts import render
# from django.http import HttpResponse


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

    # Overriding original upload method using django's FileSystemStorage
    def upload(self, files, dest):
        try:
            for _file in list(files):
                path = os.path.join(self.root, dest.replace('/', '', 1))
                if not path.startswith(self.root):
                     return {'result': {'success': 'false', 'error': 'Invalid path'}}

                # fs = FileSystemStorage(location=path)
                # fs.save(files.get(_file).name, files.get(_file))
        except Exception as e:
            return {'result': {'success': 'false', 'error': e.message}}
        return {'result': {'success': 'true', 'error': ''}}

fm = FlaskFileManager(os.environ['HOME'], False)

@app.route("/")
def index():
    return render_template('index.html')


@app.route("/list", methods=['GET', 'POST'])
def list_():
    return jsonify(fm.list(request.get_json()))


@app.route("/rename")
def rename():
    return jsonify(fm.rename(request.get_json()))


@app.route("/copy")
def copy():
    return jsonify(fm.copy(request.get_json()))


@app.route("/remove")
def remove():
    return jsonify(fm.remove(request.get_json()))


@app.route("/edit")
def edit():
    return jsonify(fm.edit(request.get_json()))


@app.route("/createFolder")
def createFolder():
    return jsonify(fm.createFolder(request.get_json()))


@app.route("/changePermissions")
def changePermissions():
    return jsonify(fm.changePermissions(request.get_json()))


@app.route("/compress")
def compress():
    return jsonify(fm.compress(request.get_json()))


@app.route("/downloadMultiple")
def downloadMultiple():
    ret = fm.downloadMultiple(request.GET, HttpResponse)
    os.umask(ret[1])
    shutil.rmtree(ret[2], ignore_errors=True)
    return ret[0]


@app.route("/move")
def move():
    return jsonify(fm.move(request.get_json()))


@app.route("/getContent")
def getContent():
    return jsonify(fm.getContent(request.get_json()))


@app.route("/extract")
def extract():
    return jsonify(fm.extract(request.get_json()))


@app.route("/download")
def download():
    return fm.download(request.GET['path'], HttpResponse)


@app.route("/upload", methods=['POST'])
def upload():
    return jsonify(fm.upload(request.files['file'], request.POST['destination']))

if __name__ == "__main__":
    app.run()
