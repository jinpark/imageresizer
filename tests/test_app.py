import os
import sys
import unittest
import requests
from freezegun import freeze_time
from datetime import datetime
from StringIO import StringIO
from wand.image import Image
from mock import MagicMock


topdir = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(topdir)
import app


def requests_stub(*args, **kwargs):
    response = requests.get.return_value
    if args[0] == "http://badrequest.com/g/50/200":
        raise
    elif args[0] == "http://notanimage.com/g/50/200":
        response.content = "thisisavideonotanimage"
        response.headers = {'content-type': 'video/avi'}
        return response
    elif args[0] == "http://badimage.com/g/50/200":
        response.content = "this is some bad image data"
        response.headers = {'content-type': 'image/jpeg'}
        return response
    else:
        with open('tests/images/50x200_pre.jpeg', 'r') as f:
            response.content = f.read()
            response.headers = {'content-type': 'image/jpeg'}
            return response

requests.get = MagicMock(side_effect=requests_stub)

class TestImageResizerImageEdits(unittest.TestCase):
    def setUp(self):
        self.app = app.app.test_client()

    def test_resize_width(self):
        rv = self.app.get('/http://placekitten.com/g/50/200/?rwidth=100')
        with Image(file=StringIO(rv.data)) as img:
            self.assertEqual(img.width, 100)
            self.assertEqual(img.height, 400)

    def test_resize_height(self):
        rv = self.app.get('/http://placekitten.com/g/50/200/?rheight=100')
        with Image(file=StringIO(rv.data)) as img:
            self.assertEqual(img.width, 25)
            self.assertEqual(img.height, 100)

    def test_resize_width_and_height(self):
        rv = self.app.get('/http://placekitten.com/g/50/200/?rheight=100&rwidth=100')
        with Image(file=StringIO(rv.data)) as img:
            self.assertEqual(img.width, 100)
            self.assertEqual(img.height, 100)

    def test_convert_type(self):
        rv = self.app.get('/http://placekitten.com/g/50/200/?type=png')
        with Image(file=StringIO(rv.data)) as img:
            self.assertEqual(img.mimetype, "image/png")

    def test_bad_request(self):
        rv = self.app.get('/http://badrequest.com/g/50/200/?rwidth=100')
        self.assertEqual(rv.status, "400 BAD REQUEST")

    def test_not_an_image(self):
        rv = self.app.get('/http://notanimage.com/g/50/200/?rwidth=100')
        self.assertEqual(rv.status, "400 BAD REQUEST")

    def test_bad_width(self):
        rv = self.app.get('/http://placekitten.com/g/50/200/?rwidth=cat')
        self.assertEqual(rv.status, "400 BAD REQUEST")

    def test_bad_height(self):
        rv = self.app.get('/http://placekitten.com/g/50/200/?rheight=cat')
        self.assertEqual(rv.status, "400 BAD REQUEST")

    def test_crop(self):
        rv = self.app.get('/http://placekitten.com/g/50/200/?cwidth=20&cheight=100')
        with Image(file=StringIO(rv.data)) as img:
            self.assertEqual(img.width, 20)
            self.assertEqual(img.height, 100)

    def test_crop_bad_width_or_height(self):
        rv = self.app.get('/http://placekitten.com/g/50/200/?cheight=cat&cwidth=meow')
        self.assertEqual(rv.status, "400 BAD REQUEST")

    def test_crop_only_height(self):
        rv = self.app.get('/http://placekitten.com/g/50/200/?cheight=100')
        with Image(file=StringIO(rv.data)) as img:
            self.assertEqual(img.width, 50)
            self.assertEqual(img.height, 100)

    def test_crop_only_width(self):
        rv = self.app.get('/http://placekitten.com/g/50/200/?cwidth=25')
        with Image(file=StringIO(rv.data)) as img:
            self.assertEqual(img.width, 25)
            self.assertEqual(img.height, 200)

class TestImageResizerExtras(unittest.TestCase):
    def setUp(self):
        self.app = app.app.test_client()

    def test_home_redirect(self):
        rv = self.app.get('/', follow_redirects=False)
        self.assertEqual(rv.location, "https://github.com/jinpark/imageresizer")

    def test_health_check(self):
        rv = self.app.get('/health/')
        self.assertEqual(rv.data, '{\n  "commit_hash": null, \n  "health": "ok"\n}')

    @freeze_time("2015-03-29")
    def test_health_check_uncached(self):
        rv = self.app.get('/health/')
        headers = rv.headers
        datetime_now = datetime(2015, 3, 29)
        self.assertEqual(headers['Last-Modified'], str(datetime_now))
        self.assertEqual(headers['Cache-Control'], 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0')
        self.assertEqual(headers['Pragma'], 'no-cache')
        self.assertEqual(headers['Expires'], '-1')

    def test_favicon(self):
        rv = self.app.get('/favicon.ico/')
        self.assertEqual(rv.mimetype, 'image/png')

if __name__ == '__main__':
    unittest.main()
