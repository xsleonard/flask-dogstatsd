import dogstatsd

DOGSTATSD_METHODS = ['gauge', 'increment', 'decrement', 'histogram', 'timing',
                     'timed', 'set', 'event']


class DogStatsd(object):

    def __init__(self, app=None):
        self.statsd = None
        self.app = None
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.statsd = self
        self.app = app
        self.prefix = app.config.get('DOGSTATSD_PREFIX')
        host = app.config.get('DOGSTATSD_HOST', 'localhost')
        port = app.config.get('DOGSTATSD_PORT', 8125)
        self.statsd = dogstatsd.DogStatsd(host, port)

    def _apply_prefix(self, method):
        def prefixed_method(metric, *args, **kwargs):
            if self.prefix:
                metric = '{}.{}'.format(self.prefix, metric)
            return method(metric, *args, **kwargs)
        return prefixed_method

    def __getattribute__(self, name):
        if name in DOGSTATSD_METHODS:
            method = getattr(self.statsd, name)
            if name == 'event':
                return method
            else:
                return self._apply_prefix(method)
        else:
            return object.__getattribute__(self, name)
