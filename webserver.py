#!/usr/bin/env python
"""Runs a modified web server for local tests."""
from __future__ import print_function

import CGIHTTPServer2

try:
    CGIHTTPServer2.test2()
except KeyboardInterrupt:
    print('Shutting down server')
