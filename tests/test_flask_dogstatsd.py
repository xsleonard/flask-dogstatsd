from mock import patch
from unittest import TestCase
from flask import Flask
from flask_dogstatsd import DogStatsd, DOGSTATSD_METHODS


class TestDogStatsd(TestCase):

    def setUp(self):
        super(TestDogStatsd, self).setUp()
        self.app = Flask(__name__)

    # py2.6 crud
    def assertIsNone(self, thing):
        self.assertIs(thing, None)

    # py2.6 crud
    def assertIsNotNone(self, thing):
        self.assertIsNot(thing, None)

    @patch('statsd.DogStatsd.connect')
    def test_init_app(self, mock_connect):
        dog = DogStatsd()
        host = '69.69.77.77'
        port = 7053
        self.app.config['DOGSTATSD_HOST'] = host
        self.app.config['DOGSTATSD_PORT'] = port
        dog.init_app(self.app)
        mock_connect.assert_called_once_with(host, port)
        self.assertIsNotNone(dog.statsd)
        self.assertEqual(dog.app, self.app)

    @patch('statsd.DogStatsd.connect')
    def test_init_app_defaults(self, mock_connect):
        dog = DogStatsd()
        dog.init_app(self.app)
        mock_connect.assert_called_once_with('localhost', 8125)
        self.assertIsNotNone(dog.statsd)
        self.assertEqual(dog.app, self.app)

    @patch.object(DogStatsd, 'init_app')
    def test_init_with_app(self, mock_init_app):
        DogStatsd(app=self.app)
        mock_init_app.assert_called_once_with(self.app)

    @patch.object(DogStatsd, 'init_app')
    def test_init_without_app(self, mock_init_app):
        dog = DogStatsd(app=None)
        mock_init_app.assert_not_called()
        self.assertIsNone(dog.app)
        self.assertIsNone(dog.statsd)

    def test_getattribute(self):
        dog = DogStatsd(app=self.app)
        for m in DOGSTATSD_METHODS:
            v = getattr(dog, m)
            self.assertTrue(callable(v))
            self.assertEqual(v, getattr(dog.statsd, m))
        self.assertEqual(self.app, dog.app)
        self.assertIsNotNone(dog.statsd)
