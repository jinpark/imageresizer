from flask import Flask, send_file, request, abort
import requests
from StringIO import StringIO
from wand.image import Image
from urlparse import urlparse
from os.path import splitext, basename
from tempfile import NamedTemporaryFile
from shutil import copyfileobj
import os

app = Flask(__name__)

@app.route('/<path:url>')
def convert(url):
    querystring = request.args
    try:
        r = requests.get(url)
        filename, file_ext = splitext(basename(urlparse(url).path))
    except:
        raise 
        abort(404)
    try:
        with Image(file=StringIO(r.content)) as img:
            if 'type' in querystring.keys() and querystring['type'] in ['jpeg', 'jpg', 'png', 'gif']:
                img.format = querystring['type']
            if 'w' in querystring.keys():
                try:
                    width = int(querystring['w'])
                except:
                    pass
            else:
                width = None
            if 'h' in querystring.keys():
                try:
                    height = int(querystring['h']) 
                except:
                    pass
            else:
                height = None
            if width and height:
                img.resize(width, height)
            if width and not height:
                img.transform(resize=str(width))
            if height and not width:
                img.transform(resize='x' + height)

            temp_file = NamedTemporaryFile(mode='w+b',suffix=img.format)
            img.save(file=temp_file)
            temp_file.seek(0,0)
            response = send_file(temp_file, mimetype='image/' + img.format)
            return response
    except:
        raise
        abort(404)

if __name__ == '__main__':
    app.run(debug=True)