#!/usr/bin/python3.5

"""
.. module:: shaTools
    :synopsis: module for functions related to sha calculation.

.. moduleauthor:: Miguel Garcia <zeycus@gmail.com>
"""


import hashlib


def sha256(filename):
    """Returns the SHA-256 of a given file.

    :rtype: str

    """
    hash_sha256 = hashlib.sha256()
    with open(filename, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()
