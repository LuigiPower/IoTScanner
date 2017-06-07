# This project is not complete (maybe even pre alpha stage)
---------

## What this project isn't
No, this does not scan the network for any IoT device. Doesn't work with any device that doesn't implement the HTTP webservice this script expects.

## What this project should be
This Python package just scans any available network to look for devices which provide an HTTP service on port 5575.

It is supposed to be the central system to a plug-and-play kind of IoT network that anyone can setup at home.
Doesn't work with ANY device that doesn't use a simple HTTP server to receive/send commands.

Works only with:
[Code for the ESP8266 which starts a web server on port 5575 and starts receiving commands (not complete)](https://github.com/LuigiPower/esp8266-web-handler)
[Android application which controls the IoT Network at home by sending commands to the central server (almost complete)](https://github.com/LuigiPower/iotremote)

The only (almost) finished part is the Android one.
This repository contains code that was used as a test for the Android application.

## Missing stuff:
- Any type of interface
- Security of any kind
- Got to finish the list of available commands
