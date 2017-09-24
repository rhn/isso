#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import sys

from setuptools import setup, find_packages

requires = ['itsdangerous', 'misaka>=1.0,<2.0', 'html5lib==0.9999999']

if (3, 0) <= sys.version_info < (3, 3):
    raise SystemExit("Python 3.0, 3.1 and 3.2 are not supported")

setup(
    name='Marginalia',
    version='0.1',
    author='rhn',
    author_email='gihu.rhn@porcupinefactory.org',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    url='https://github.com/posativ/isso/',
    license='AGPL-3.0',
    description='Book exchange platform',
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Internet",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4"
    ],
    install_requires=requires,
    extras_require={
        ':python_version=="2.6"': ['argparse', 'ordereddict'],
        ':python_version=="2.6" or python_version=="2.7"': ['ipaddr>=2.1', 'configparser', 'werkzeug>=0.8'],
        ':python_version!="2.6" and python_version!="2.7"': ['werkzeug>=0.9']
    },
    entry_points={
        'console_scripts':
            ['isso = isso:main'],
    }
)
