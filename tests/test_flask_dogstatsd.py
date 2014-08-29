from mock import patch
from unittest import TestCase
from flask import Flask
from flask_dogstatsd import DogStatsd, DOGSTATSD_METHODS


class TestDogStatsd(TestCase):

    def setUp(self):
        TestCase.setUp(self)
        self.app = Flask(__name__)

    @patch('dogstatsd.DogStatsd.connect')
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

    @patch('dogstatsd.DogStatsd.connect')
    def test_init_app_defaults(self, mock_connect):
        dog = DogStatsd()
        dog.init_app(self.app)
        mock_connect.assert_called_once_with('localhost', 8125)
        self.assertIsNotNone(dog.statsd)
        self.assertEqual(dog.app, self.app)
        self.assertIs(dog.prefix, None)
        self.assertTrue(dog.enabled)
        self.assertEqual(dog.port, 8125)
        self.assertEqual(dog.host, 'localhost')

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

    @patch('dogstatsd.DogStatsd.increment')
    def test_get_statsd_attr(self, mock_incr):
        dog = DogStatsd(app=self.app)
        self.assertIsNotNone(dog.statsd)
        dog.increment('count.something')
        mock_incr.assert_called_once_with('count.something')

        mock_incr.reset_mock()
        dog.statsd = None
        dog.increment('count.something')
        mock_incr.assert_not_called()

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

    @patch('dogstatsd.DogStatsd.increment')
    def test_disabled(self, mock_incr):
        self.app.config['DOGSTATSD_ENABLED'] = False
        dog = DogStatsd(app=self.app)
        self.assertIsNone(dog.statsd)
        dog.increment('count.something')
        mock_incr.assert_not_called()


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
            self.assertEqual(m, '{}.{}'.format(self.prefix, metric))
            self.assertEqual((a, b), args)
            self.assertEqual({'c': c}, kwargs)

        m = self.dog._apply_prefix(fn)
        m(metric, *args, **kwargs)

    @patch('dogstatsd.DogStatsd.event')
    def test_event_untouched(self, mock_event):
        self.dog.event('count')
        mock_event.assert_called_once_with('count')

    def test_methods_prefixed(self):
        for m in filter(lambda x: x != 'event', DOGSTATSD_METHODS):
            with patch('dogstatsd.DogStatsd.{}'.format(m)) as mock_method:
                getattr(self.dog, m)('count')
                metric = '{}.count'.format(self.prefix)
                mock_method.assert_called_once_with(metric)
