import os
import sys
import unittest
import requests
from StringIO import StringIO
from wand.image import Image
from mock import MagicMock

topdir = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(topdir)
import app


def get_stub(*args, **kwargs):
    response = requests.get.return_value
    with open('tests/images/50x200_pre.jpeg', 'r') as f:
        response.content = f.read()
        response.headers = {'content-type': 'image/jpeg'}
        return response

requests.get = MagicMock(side_effect=get_stub)


class TestImageResizer(unittest.TestCase):
    def setUp(self):
        self.app = app.app.test_client()

    def test_entry(self):
        expected_image = open('tests/images/50x200.jpeg').read()

        rv = self.app.get('/http://placekitten.com/g/50/200/', follow_redirects=True)
        rv_image_string = rv.data
        self.assertEqual(rv.data, expected_image)

    def test_resize_width(self):
        expected_image = open('tests/images/50x200.jpeg').read()

        rv = self.app.get('/http://placekitten.com/g/50/200/?rwidth=100', follow_redirects=True)
        with Image(file=StringIO(rv.data)) as img:
            self.assertEqual(img.width, 100)
            self.assertEqual(img.height, 400)

    def test_resize_height(self):
        expected_image = open('tests/images/50x200.jpeg').read()

        rv = self.app.get('/http://placekitten.com/g/50/200/?rheight=100', follow_redirects=True)
        with Image(file=StringIO(rv.data)) as img:
            self.assertEqual(img.width, 25)
            self.assertEqual(img.height, 100)

    def test_resize_width_and_height(self):
        expected_image = open('tests/images/50x200.jpeg').read()

        rv = self.app.get('/http://placekitten.com/g/50/200/?rheight=100&rwidth=100', follow_redirects=True)
        with Image(file=StringIO(rv.data)) as img:
            self.assertEqual(img.width, 100)
            self.assertEqual(img.height, 100)

    def test_resize_width_and_height(self):
        expected_image = open('tests/images/50x200.jpeg').read()

        rv = self.app.get('/http://placekitten.com/g/50/200/?rheight=100&rwidth=100', follow_redirects=True)
        with Image(file=StringIO(rv.data)) as img:
            self.assertEqual(img.width, 100)
            self.assertEqual(img.height, 100)

    def test_convert_type(self):
        expected_image = open('tests/images/50x200.jpeg').read()

        rv = self.app.get('/http://placekitten.com/g/50/200/?type=png', follow_redirects=True)
        with Image(file=StringIO(rv.data)) as img:
            self.assertEqual(img.mimetype, "image/png")

if __name__ == '__main__':
    unittest.main()
