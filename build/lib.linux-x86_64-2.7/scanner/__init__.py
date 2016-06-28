#!/usr/bin/env python

from flask import Flask
from flask.ext.triangle import Triangle

app = Flask(__name__, static_path="/static")
Triangle(app)

################################################################################
# SERVER STARTUP
################################################################################

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')

import scanner.views
