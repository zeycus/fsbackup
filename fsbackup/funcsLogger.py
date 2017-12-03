#!/usr/bin/python3.6

"""
.. module:: funcsLogger
    :synopsis: defines a simple standard logger.
    :platform: Windows, linux

.. moduleauthor:: Miguel Garcia <zeycus@gmail.com>
"""

import logging


def formatterStd():
    """Returns a standard formatter.

    :rtype: logging.Formatter
    """
    return logging.Formatter("%(asctime)s: %(message)s")


def loggingStdout(user='root', lev=logging.DEBUG):
    """Returns a logger with the formatterStd dumping to stdout."""
    log = logging.Logger(user)
    ch = logging.StreamHandler()
    ch.setLevel(lev)
    ch.setFormatter(formatterStd())
    log.addHandler(ch)
    return log
