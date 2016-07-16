#!/usr/bin/env python

from flask import Flask
#from flask.ext.triangle import Triangle
from flask_triangle import Triangle

app = Flask(__name__,
        static_url_path="/static",
        static_path="/static",
        static_folder="/static",
        template_folder="/templates")
Triangle(app)

################################################################################
# SERVER STARTUP
################################################################################

if __name__ == '__main__':
    app.debug = False
    app.run(host='0.0.0.0')

import scanner.views
