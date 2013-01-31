#!/usr/bin/env python
"""Runs a modified web server for local tests."""
import CGIHTTPServer2

try:
    CGIHTTPServer2.test()
except KeyboardInterrupt:
    print 'Shutting down server'
