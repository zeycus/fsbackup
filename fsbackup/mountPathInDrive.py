#!/usr/bin/python3.6

"""
.. module:: mountPathInDrive
    :platform: Windows
    :synopsis: module for class :class:`MountPathInDrive <mountPathInDrive.MountPathInDrive>`.

.. moduleauthor:: Miguel Garcia <zeycus@gmail.com>
"""


import subprocess


class MountPathInDrive(object):
    """Simple context manager for temporaly mounting a path in a Windows drive.

    Usage example:

    .. code-block:: python

        with MountPathInDrive(path=r"F:\sources", driveLetter='J'):
            print(os.listdir("J:"))
    """

    def __init__(self, path, driveLetter):
        self.path = path
        self.driveLetter = driveLetter

    def __enter__(self):
        subprocess.run("subst %s: %s" % (self.driveLetter, self.path))
        return None  # Nothing interesting to return

    def __exit__(self, *args):
        subprocess.run("subst %s: /D" % self.driveLetter)

