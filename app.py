import os
import json
import shutil
import importlib
import sys
import importlib
from flask import Flask, request

# from django.shortcuts import render
# from django.shortcuts import render_to_response
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



urlpatterns = [
    url(r'^$', fm.index),
    url(r'^list$', fm.list_),
    url(r'^rename$', fm.rename),
    url(r'^move$', fm.move),
    url(r'^copy$', fm.copy),
    url(r'^remove$', fm.remove),
    url(r'^edit$', fm.edit),
    url(r'^getContent$', fm.getContent),
    url(r'^createFolder$', fm.createFolder),
    url(r'^changePermissions$', fm.changePermissions),
    url(r'^compress$', fm.compress),
    url(r'^extract$', fm.extract),
    url(r'^downloadMultiple$', fm.downloadMultiple),
    url(r'^download$', fm.download),
    url(r'^upload$', fm.upload),
]


app = Flask(__name__)
class FlaskFileManager(filemanager.FileManager):

    # Overriding original upload method using django's FileSystemStorage
    def upload(self, files, dest):
        try:
            for _file in list(files):
                path = os.path.join(self.root, dest.replace('/', '', 1))
                if not path.startswith(self.root):
                     return {'result': {'success': 'false', 'error': 'Invalid path'}}
                fs = FileSystemStorage(location=path)
                fs.save(files.get(_file).name, files.get(_file))
        except Exception as e:
            return {'result': {'success': 'false', 'error': e.message}}
        return {'result': {'success': 'true', 'error': ''}}

fm = FlaskFileManager(os.environ['HOME'], False)

@app.route("/")
def hello():
    return "Hello World!"




def index(request):
    return render(request, 'filemanager_app/index.html')


def list_(request):
    return HttpResponse(json.dumps(fm.list(json.loads(request.body.decode('utf-8')))))


def rename(request):
    return HttpResponse(json.dumps(fm.rename(json.loads(request.body.decode('utf-8')))))


def copy(request):
    return HttpResponse(json.dumps(fm.copy(json.loads(request.body.decode('utf-8')))))


def remove(request):
    return HttpResponse(json.dumps(fm.remove(json.loads(request.body.decode('utf-8')))))


def edit(request):
    return HttpResponse(json.dumps(fm.edit(json.loads(request.body.decode('utf-8')))))


def createFolder(request):
    return HttpResponse(json.dumps(fm.createFolder(json.loads(request.body.decode('utf-8')))))


def changePermissions(request):
    return HttpResponse(json.dumps(fm.changePermissions(json.loads(request.body.decode('utf-8')))))


def compress(request):
    return HttpResponse(json.dumps(fm.compress(json.loads(request.body.decode('utf-8')))))


def downloadMultiple(request):
    ret = fm.downloadMultiple(request.GET, HttpResponse)
    os.umask(ret[1])
    shutil.rmtree(ret[2], ignore_errors=True)
    return ret[0]


def move(request):
    return HttpResponse(json.dumps(fm.move(json.loads(request.body.decode('utf-8')))))


def getContent(request):
    return HttpResponse(json.dumps(fm.getContent(json.loads(request.body.decode('utf-8')))))


def extract(request):
    return HttpResponse(json.dumps(fm.extract(json.loads(request.body.decode('utf-8')))))


def download(request):
    return fm.download(request.GET['path'], HttpResponse)


def upload(request):
    return HttpResponse(json.dumps(fm.upload(request.FILES, request.POST['destination'])))

if __name__ == "__main__":
    app.run()
