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
    with open('tests/images/50x200_pre.jpeg', 'r') as f:
        response.content = f.read()
        response.headers = {'content-type': 'image/jpeg'}
        return response

requests.get = MagicMock(side_effect=requests_stub)

class TestImageResizer(unittest.TestCase):
    def setUp(self):
        self.app = app.app.test_client()

    def test_resize_width(self):
        rv = self.app.get('/http://placekitten.com/g/50/200/?rwidth=100', follow_redirects=True)
        with Image(file=StringIO(rv.data)) as img:
            self.assertEqual(img.width, 100)
            self.assertEqual(img.height, 400)

    def test_resize_height(self):
        rv = self.app.get('/http://placekitten.com/g/50/200/?rheight=100', follow_redirects=True)
        with Image(file=StringIO(rv.data)) as img:
            self.assertEqual(img.width, 25)
            self.assertEqual(img.height, 100)

    def test_resize_width_and_height(self):
        rv = self.app.get('/http://placekitten.com/g/50/200/?rheight=100&rwidth=100', follow_redirects=True)
        with Image(file=StringIO(rv.data)) as img:
            self.assertEqual(img.width, 100)
            self.assertEqual(img.height, 100)

    def test_convert_type(self):
        rv = self.app.get('/http://placekitten.com/g/50/200/?type=png', follow_redirects=True)
        with Image(file=StringIO(rv.data)) as img:
            self.assertEqual(img.mimetype, "image/png")

class TestImageResizerSide(unittest.TestCase):
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
