#===============================================================================
# Setting up logging
#===============================================================================
# How do I use the logging module to write to a log file?
#
# Excerpt from https://www.loggly.com/ultimate-guide/python-logging-basics/
#
# Python comes with a logging module in the standard library that provides a 
# flexible framework for emitting log messages from Python programs. This module 
# is widely used by libraries and is the first go-to point for most developers
# when it comes to logging.
#
# The module provides a way for applications to configure different log handlers
# and a way of routing log messages to these handlers. This allows for a highly
# flexible configuration that can deal with a lot of different use cases.
#
# Not all log messages are created equal. Logging levels are listed here in 
# the Python documentation; we’ll include them here for reference. When you
# set a logging level in Python using the standard module, you’re telling the
# library you want to handle all events from that level on up. If you set the
# log level to INFO, it will include INFO, WARNING, ERROR, and CRITICAL
# messages. NOTSET and DEBUG messages will not be included here.
#
# Level	Numeric value
# CRITICAL	50
# ERROR	    40
# WARNING	30
# INFO	    20
# DEBUG	    10
# NOTSET	0
# 
#===============================================================================
# Written for Python 3.7
# By Dan Fourquet
#===============================================================================

import logging

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG) # Set the debug level here
fileHandler = logging.FileHandler(f'my.log', mode='w')
log.addHandler(fileHandler)

log.debug('Message to write to log')