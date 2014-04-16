import statsd

DOGSTATSD_METHODS = ['gauge', 'increment', 'decrement', 'histogram', 'timing',
                     'timed', 'set', 'event']


class DogStatsd(object):

    def __init__(self, app=None):
        self.statsd = None
        self.app = None
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.app = app
        app.statsd = self
        host = app.config.get('DOGSTATSD_HOST', 'localhost')
        port = app.config.get('DOGSTATSD_PORT', 8125)
        self.statsd = statsd.DogStatsd(host, port)

    def __getattribute__(self, name):
        if name in DOGSTATSD_METHODS:
            return getattr(object.__getattribute__(self, 'statsd'), name)
        else:
            return object.__getattribute__(self, name)
