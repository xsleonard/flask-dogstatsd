flask-dogstatsd
===============

[![PyPI version](https://badge.fury.io/py/Flask-DogStatsd.png)](http://badge.fury.io/py/Flask-DogStatsd)
[![Build Status](https://travis-ci.org/xsleonard/flask-dogstatsd.png)](https://travis-ci.org/xsleonard/flask-dogstatsd)
[![Coverage Status](https://coveralls.io/repos/xsleonard/flask-dogstatsd/badge.png)](https://coveralls.io/r/xsleonard/flask-dogstatsd)

Flask extension for [dogstatsd-python-fixed](https://github.com/xsleonard/dogstatsd-python)

Compatible with Python 2.7, 3.3 and pypy

Installation
============

```
pip install flask-dogstatsd
```

Tests
=====

```
pip install -r requirements.txt
pip install -r tests/requirements.txt
./setup.py develop
./setup.py test
```

Example
=======

```python
# app.py
from flask import Flask
from flask.ext.dogstatsd import DogStatsd

app = Flask(__name__)
app.config['DOGSTATSD_HOST'] = 'localhost' # This is the default
app.config['DOGSTATSD_PORT'] = 8125 # This is the default
app.config['DOGSTATSD_PREFIX'] = 'app' # False-y values disable prefixing

dogstatsd = DogStatsd(app)

@app.route('/'):
def index():
    # See dogstatsd-python for the full API.  
    # Methods are forwarded to that.
    # Since our prefix is 'app', the full key will be 'app.index.views'
    dogstatsd.increment('index.views')
    return 'Home'
```
