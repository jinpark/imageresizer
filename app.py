from flask import Flask, send_file, request, abort, jsonify, send_from_directory, make_response, redirect
from StringIO import StringIO
from wand.image import Image
from urlparse import urlparse
from tempfile import NamedTemporaryFile
from shutil import copyfileobj
from functools import wraps, update_wrapper
from datetime import datetime
import requests
import os
import logging

# from gevent import monkey; monkey.patch_all()

app = Flask(__name__)
stream_handler = logging.StreamHandler()
app.logger.addHandler(stream_handler)
app.logger.setLevel(logging.INFO)
app.logger.info('jinageresizer startup')

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
            abort(400)
    except:
        app.logger.exception("Error while getting url: " + url)
        abort(400)
    try:
        with Image(file=StringIO(r.content)) as img:
            if 'type' in query_string.keys() and query_string['type'] in ['jpeg', 'jpg', 'png']:
                img.format = query_string['type']
            if 'rwidth' in query_string.keys():
                try:
                    resize_width = int(query_string['rwidth'])
                except:
                    app.logger.exception("rwidth is invalid: " + query_string['rwidth'])
                    bad_request('rwidth')
            else:
                resize_width = None
            if 'rheight' in query_string.keys():
                try:
                    resize_height = int(query_string['rheight'])
                except:
                    bad_request('rheight')
            else:
                resize_height = None
            if resize_width and resize_height:
                img.resize(resize_width, resize_height)
            if resize_width and not resize_height:
                img.transform(resize=str(resize_width))
            if resize_height and not resize_width:
                img.transform(resize='x' + str(resize_height))

            temp_file = NamedTemporaryFile(mode='w+b',suffix=img.format)
            img.save(file=temp_file)
            temp_file.seek(0,0)
            response = send_file(temp_file, mimetype=img.mimetype)
            return response
    except:
        app.logger.exception("Error while getting image for wand")
        abort(500)


# on hold until I can figure out gravity
# def crop(img, width, height):
#     """
#     Crops image based on left, top, bottom, right pixel sizes.
#     Default gravity is center. Options are center, north, north_east, ...
#     View http://docs.wand-py.org/en/latest/wand/image.html#wand.image.BaseImage.crop
#     for more details
#     """
#     img.transform("{}x{}".format(width,height))


@app.route('/health')
@nocache
def health_check():
    return jsonify({'health': 'ok', 'commit_hash': os.environ.get('COMMIT_HASH')})


@app.errorhandler(400)
def bad_request(bad_var_name, error=None):
    message = {
            'status': 400,
            'message': 'Bad request: {} is not valid'.format(bad_var_name),
    }
    resp = jsonify(message)
    resp.status_code = 400
    return resp

if __name__ == '__main__':
    app.run(debug=True)
