import os
import json
import tempfile
import shutil
import sys
import importlib
from uuid import uuid4
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

class FlaskFileManager(filemanager.FileManager):

    # Overriding original methods
    def download(self, request):
        path = os.path.abspath(self.root + request['path'])
        response = {}
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
        filename = request.get('toFilename').replace('.zip', '',1)
        saved_umask = os.umask(77)
        path = os.path.join(tmpdir, filename)
        try:
            filemanager.compress_zip(path, folders)
            response = send_file(path+".zip")

            os.umask(saved_umask)
            shutil.rmtree(tmpdir, ignore_errors=True)

            return response

        except IOError as e:
            print("IOError")
        else:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def upload(self, request):
        files = request.files.to_dict()
        dest = request.form.get('destination')
        try:
            for _file in files.values():
                path = os.path.join(self.root, dest.replace('/', '', 1))
                if not path.startswith(self.root):
                     return {'result': {'success': 'false', 'error': 'Invalid path'}}
                _file.save(os.path.join(path, _file.filename))
        except Exception as e:
            return {'result': {'success': 'false', 'error': 'true'}}
        return {'result': {'success': 'true', 'error': ''}}

fm = FlaskFileManager(os.environ['HOME'], False)
app = Flask(__name__, static_url_path='')
uniq_key = str(uuid4())
print('Go: http://localhost:5000/?key={}'.format(uniq_key))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route("/")
def index():
    incomming_uuid = request.args.to_dict().get('key')
    return render_template('index.html') if uniq_key == incomming_uuid else page_not_found(404)


@app.route("/api", methods=['GET', 'POST'])
def api():

    if request.method == 'POST':
        incomming_uuid = request.args.to_dict().get('key')
        if uniq_key != incomming_uuid:
            return page_not_found(404)

        request.on_json_loading_failed = lambda e: request
        cmd = request.get_json(force=True)

    else :
        cmd = request.args.to_dict(flat=False)
        cmd = { k: v if len(v) > 1 else v[0] for k, v in cmd.items() }

    try:
        fm_method = getattr(fm, cmd['action'])

    except TypeError :
        fm_method = getattr(fm, 'upload')

    response = fm_method(cmd)

    return jsonify(response) if type(response) is dict else response

