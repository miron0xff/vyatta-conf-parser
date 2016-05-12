# coding:utf-8
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import vyattaconfparser

setup(
    name='VyattaConfParser',
    version=vyattaconfparser.__version__,
    packages=['vyattaconfparser'],
    url='https://github.com/hedin/vyatta-conf-parser',
    author=vyattaconfparser.__author__,
    author_email='a.m.mironov@gmail.com',
    classifiers=(
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Development Status :: 3 - Alpha'
    ),
    description='A python config parser for Vyatta',
)
