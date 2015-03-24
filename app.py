from flask import Flask, send_file, request, abort, jsonify
import requests
from StringIO import StringIO
from wand.image import Image
from urlparse import urlparse
from tempfile import NamedTemporaryFile
from shutil import copyfileobj
import os

app = Flask(__name__)

@app.route('/<path:url>/')
def convert(url):
    query_string = request.args
    try:
        r = requests.get(url)
        filename, file_ext = os.path.splitext(os.path.basename(urlparse(url).path))
    except:
        raise
        abort(400)
    try:
        with Image(file=StringIO(r.content)) as img:
            if 'type' in query_string.keys() and query_string['type'] in ['jpeg', 'jpg', 'png']:
                img.format = query_string['type']
            if 'rwidth' in query_string.keys():
                try:
                    resize_width = int(query_string['rwidth'])
                except:
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
                img.transform(resize='x' + resize_height)

            temp_file = NamedTemporaryFile(mode='w+b',suffix=img.format)
            img.save(file=temp_file)
            temp_file.seek(0,0)
            response = send_file(temp_file, mimetype='image/' + img.format)
            return response
    except:
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
