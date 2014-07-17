#!/usr/bin/env python

import os
import sys
import httplib


if __name__ == '__main__':
    if len(sys.argv) > 1:
        searchQuery = ' '.join(sys.argv[1:])
    else:
        print 'Please specify Search Query'
        exit()
        
    h1 = httplib.HTTPConnection('127.0.0.1:8888')
    h1.request('HEAD',searchQuery)