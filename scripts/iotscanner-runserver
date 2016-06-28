#!/usr/bin/env python
from scanner import app
import sys

print "testing"

def start_flask():
    app.debug = True
    app.run(host='0.0.0.0')

start_flask()

from scanner.views import kill_scanner
kill_scanner()

print "All done, closing..."
