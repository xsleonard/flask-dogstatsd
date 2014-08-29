import dogstatsd

DOGSTATSD_METHODS = ['gauge', 'increment', 'decrement', 'histogram', 'timing',
                     'timed', 'set', 'event']


class DogStatsd(object):

    def __init__(self, app=None):
        self.statsd = None
        self.app = None
        self.prefix = ''
        self.host = 'localhost'
        self.port = 8125
        self.enabled = False  # Will be set to True once initialized
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.statsd = self
        self.app = app
        self.prefix = app.config.get('DOGSTATSD_PREFIX')
        self.enabled = app.config.get('DOGSTATSD_ENABLED', True)
        self.host = app.config.get('DOGSTATSD_HOST', self.host)
        self.port = app.config.get('DOGSTATSD_PORT', self.port)
        if self.enabled:
            self.statsd = dogstatsd.DogStatsd(self.host, self.port)

    def _apply_prefix(self, method):
        def prefixed_method(metric, *args, **kwargs):
            if method is None:
                return
            if self.prefix:
                metric = '{}.{}'.format(self.prefix, metric)
            method(metric, *args, **kwargs)
        return prefixed_method

    def _get_statsd_attr(self, name):
        if self.statsd is not None:
            return getattr(self.statsd, name)

    def __getattribute__(self, name):
        if name in DOGSTATSD_METHODS:
            method = self._get_statsd_attr(name)
            if name == 'event':
                return method
            else:
                return self._apply_prefix(method)
        else:
            return object.__getattribute__(self, name)
