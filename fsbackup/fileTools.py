#!/usr/bin/python3.5


"""
.. module:: fileTools
    :platform: Windows
    :synopsis: module with a few low-level file-related funcions.

.. moduleauthor:: Miguel Garcia <zeycus@gmail.com>

"""

import os
import shutil
import uuid
from datetime import datetime


def sizeof_fmt(num, suffix='B'):
    """Returns a human-readable string for a file size.

    :param num: size of the file, in units
    :type num: int
    :param suffix: the unit. Use 'B' for bytes, the default.
    :type suffix: str
    :rtype: str

    Stolen from:

        http://stackoverflow.com/questions/1094841/reusable-library-to-get-human-readable-version-of-file-size

    """
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.2f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)


def abspath2longabspath(abspath):
    """Returns an absolute filepath than works for longer than 260 chars in Windows.

    In Windows there is seems to be no support for paths longer than 260 chrs. Files that exist are not found, cannot
    be open, etc. However, using this trick I seem to be able to access them.

    Post with the trick description:

        https://msdn.microsoft.com/en-us/library/aa365247.aspx#maxpath

    """
    if len(abspath) < 240:  # Estos no dan problemas
        return abspath
    if (abspath[0] == abspath[1] == "\\"):  # Como en \\ZEYCUS-TVS671\Multimedia
        return "\\\\?\\UNC" + abspath[1:]
    elif (abspath[0].lower() in ('cdefghijklmnopqrstuvxyz')) and abspath[1:3] == ":\\":  # Como en C:\datos\Multimedia
        return "\\\\?\\" + abspath
    else:
        raise ValueError("Path '%s' no soportado." % abspath)


def safeFileCopy(src, dst):
    """Copies a file but removes the target file if anything went wrong, before failing.

    :param src: source file
    :type src: str
    :param dst: destiny file
    :type dst: str

    """
    try:
        shutil.copy(src, dst)
    except:
        try:
            os.remove(dst)
        except:
            pass
        raise IOError("For some reason file '%s' could not be copied to '%s'. Target was deleted." % (src, dst))
