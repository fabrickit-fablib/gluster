# coding: utf-8

from fabkit import run
from fablib.base import SimpleBase


class Sample(SimpleBase):
    def __init__(self):
        print 'init'

    def setup(self):
        run('hostname')
