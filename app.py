from flask import Flask, send_file, request, abort, jsonify, send_from_directory, make_response, redirect, current_app
from StringIO import StringIO
from wand.image import Image, GRAVITY_TYPES
from wand.exceptions import MissingDelegateError
from urlparse import urlparse
from tempfile import NamedTemporaryFile
from shutil import copyfileobj
from functools import wraps, update_wrapper
from datetime import datetime
import requests
import os
import logging

from gevent import monkey; monkey.patch_all()

app = Flask(__name__)
stream_handler = logging.StreamHandler()
app.logger.addHandler(stream_handler)
app.logger.setLevel(logging.INFO)
app.logger.info('jinageresizer startup')

@app.errorhandler(400)
def custom400(error):
    response = jsonify({'message': error.description})
    return response, 400

def nocache(view):
    """
    no cache decorator. used for health check
    """
    @wraps(view)
    def no_cache(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        response.headers['Last-Modified'] = datetime.now()
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
        return response

    return update_wrapper(no_cache, view)

@app.route('/')
def home():
    return redirect("https://github.com/jinpark/imageresizer")

@app.route('/favicon.ico/')
def favicon():
    """
    I hate favicons. ugh
    """
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/png')

@app.route('/<path:url>/')
def convert(url):
    query_string = request.args
    try:
        r = requests.get(url, timeout=1)
        filename, file_ext = os.path.splitext(os.path.basename(urlparse(url).path))
        if 'image' not in r.headers['content-type']:
            app.logger.error(url + " is not an image.")
            abort(400, url + " is not an image.")
    except:
        app.logger.exception("Error while getting url: " + url)
        abort(400, "Error while getting url: " + url)
    try:
        with Image(file=StringIO(r.content)) as img:
            if query_string.get('type') in ['jpeg', 'jpg', 'png', 'pjeg']:
                img.format = query_string.get('type')

            img = resize(img, query_string.get('rwidth'), query_string.get('rheight'))

            img = crop(img, query_string.get('cwidth'), query_string.get('cheight'), query_string.get('gravity'))

            temp_file = NamedTemporaryFile(mode='w+b',suffix=img.format)
            img.save(file=temp_file)
            temp_file.seek(0,0)
            response = send_file(temp_file, mimetype=img.mimetype)
            return response
    except MissingDelegateError:
        abort(400, 'Image is unusable')




def resize(img, width=None, height=None):
    if not width and not height:
        return img
    if width:
        try:
            width = int(width)
        except ValueError:
            app.logger.exception("rwidth is invalid: " + width)
            abort(400, "rwidth is invalid: " + width)
    if height:
        try:
            height = int(height)
        except ValueError:
            app.logger.exception("rheight is invalid: " + height)
            abort(400, "rheight is invalid: " + height)
    if width and height:
        img.resize(width, height)
    if width and not height:
        img.transform(resize=str(width))
    if height and not width:
        img.transform(resize='x' + str(height))

    return img

def crop(img, width=None, height=None, gravity='north_west'):
    if not width and not height:
        return img
    if width and height:
            try:
                img.crop(width=int(width), height=int(height), gravity=gravity)
            except ValueError:
                app.logger.exception("cheight: {0} or cwidth: {1} is invalid.".format(height, width))
                abort(400, "cheight: {0} or cwidth: {1} is invalid.".format(height, width))
    if (width and not height) or (not width and height): # xor!
        abort(400, "cheight or cwidth is missing. Both are required for cropping.")
    return img


@app.route('/health/')
@nocache
def health_check():
    return jsonify({'health': 'ok', 'commit_hash': os.environ.get('COMMIT_HASH')})

if __name__ == '__main__':
    app.run()
