#!/usr/bin/python3.6


"""
.. module:: fsbck
    :platform: Windows
    :synopsis: the entrance point script to the backup system

.. moduleauthor:: Miguel Garcia <zeycus@gmail.com>
"""

import sys

from fsbackup.fsbckWrapper import fsbck_wrapper


if __name__ == "__main__":
    fsbck_wrapper(sys.argv[1:])