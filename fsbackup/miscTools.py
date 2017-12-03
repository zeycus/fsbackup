#!/usr/bin/python3.6

"""
.. module:: miscTools
    :platform: Windows, linux
    :synopsis: module with auxiliary functions to classes HashVolume and FileDB.

.. moduleauthor:: Miguel Garcia <zeycus@gmail.com>

"""


from collections import defaultdict

def buildVolumeInfoList(container):
    """Returns, for each volume, the association {file-hash: file-size}.

    :param container: a MongoAsDict with the volume information
    :type container: MongoAsDict
    :rtype: list of pairs (volId, {sha:size}).

    """
    info = defaultdict(dict)
    for hsh, docum in container.items():
        info[docum['volume']][hsh] = docum['size']
    return sorted(info.items())
