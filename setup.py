#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

#with open('LICENSE') as f:
#    license = f.read()

setup(
    name='scanner',
    version='0.0.2',
    description='IoTScanner',
    long_description=readme,
    author='Federico Giuggioloni',
    author_email='federico.giuggioloni@gmail.com',
    url='fedegiugi.noip.me',
    #license=license,
    scripts=['scripts/iotscanner-runserver'],
    include_package_data=True,
    zip_safe=False,
    packages=find_packages(exclude=('tests', 'docs')),
    install_requires=['Flask', 'Flask-Triangle']
)

