from mock import patch
from unittest import TestCase as _TestCase
from flask import Flask
from flask_dogstatsd import DogStatsd, DOGSTATSD_METHODS


class TestCase(_TestCase):

    def assertIsNone(self, a):
        # Python2.6 compatibility
        if hasattr(super(TestCase, self), 'assertIsNone'):
            super(TestCase, self).assertIsNone(a)
        else:
            self.assertTrue(a is None)

    def assertIsNotNone(self, a):
        # Python2.6 compatibility
        if hasattr(super(TestCase, self), 'assertIsNotNone'):
            super(TestCase, self).assertIsNotNone(a)
        else:
            self.assertTrue(a is not None)


class TestDogStatsd(TestCase):

    def setUp(self):
        TestCase.setUp(self)
        self.app = Flask(__name__)

    @patch('statsd.DogStatsd.connect')
    def test_init_app(self, mock_connect):
        dog = DogStatsd()
        host = '69.69.77.77'
        port = 7053
        self.app.config['DOGSTATSD_HOST'] = host
        self.app.config['DOGSTATSD_PORT'] = port
        self.app.config['DOGSTATSD_PREFIX'] = 'test'
        dog.init_app(self.app)
        mock_connect.assert_called_once_with(host, port)
        self.assertIsNotNone(dog.statsd)
        self.assertEqual(dog.app, self.app)
        self.assertEqual(self.app.statsd, dog)
        self.assertEqual(dog.prefix, 'test')

    @patch('statsd.DogStatsd.connect')
    def test_init_app_defaults(self, mock_connect):
        dog = DogStatsd()
        dog.init_app(self.app)
        mock_connect.assert_called_once_with('localhost', 8125)
        self.assertIsNotNone(dog.statsd)
        self.assertEqual(dog.app, self.app)
        self.assertIs(dog.prefix, None)

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
            with patch.object(DogStatsd, '_apply_prefix') as mock_apply_prefix:
                v = getattr(dog, m)
                self.assertTrue(callable(v))
                method = getattr(dog.statsd, m)
                if m == 'event':
                    self.assertEqual(v, method)
                    mock_apply_prefix.assert_not_called()
                else:
                    mock_apply_prefix.assert_called_once_with(method)
        self.assertEqual(self.app, dog.app)
        self.assertIsNotNone(dog.statsd)


class TestDogStatsdPrefix(TestCase):

    def setUp(self):
        TestCase.setUp(self)
        self.prefix = 'test'
        self.app = Flask(__name__)
        self.app.config['DOGSTATSD_PREFIX'] = self.prefix
        self.dog = DogStatsd(app=self.app)

    def test_apply_prefix(self):
        metric = 'count.something'
        args = (7, 100)
        kwargs = {'c': 9}

        def fn(m, a, b, c=None):
            self.assertEqual(m, '{0}.{1}'.format(self.prefix, metric))
            self.assertEqual((a, b), args)
            self.assertEqual({'c': c}, kwargs)

        m = self.dog._apply_prefix(fn)
        m(metric, *args, **kwargs)

    @patch('statsd.DogStatsd.event')
    def test_event_untouched(self, mock_event):
        self.dog.event('count')
        mock_event.assert_called_once_with('count')

    def test_methods_prefixed(self):
        for m in filter(lambda x: x != 'event', DOGSTATSD_METHODS):
            with patch('statsd.DogStatsd.{0}'.format(m)) as mock_method:
                getattr(self.dog, m)('count')
                metric = '{0}.count'.format(self.prefix)
                mock_method.assert_called_once_with(metric)
