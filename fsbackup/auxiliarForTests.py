#!/usr/bin/python3.6

"""
.. module:: auxiliarForTests
    :platform: Windows
    :synopsis: module with functions required for testing

.. moduleauthor:: Miguel Garcia <zeycus@gmail.com>

"""


import os
import filecmp

from fsbackup.fileTools import abspath2longabspath


def createTree(pathbase, nFiles):
    """Creates a dummy tree of files.

    :param pathbase: the location where the tree is created.
    :type pathbase: str
    :param nFiles: the number of files created
    :type nFiles: int

    The content of a file depends only on the last two digits of the number associated.
    That way, if nFiles > 100 same files are identical, and therefore the backup system
    creates only a copy in the volume.
    """
    for n in range(nFiles):
        nStr = str(n)
        fn_dest = os.path.join(pathbase, *nStr[:-1], nStr + ".txt")
        os.makedirs(os.path.dirname(fn_dest), exist_ok=True)
        with open(fn_dest, 'wt') as f:
            print("The last two digits of the number are '%02d'." % (n % 100), file=f)


def checkFiletreesIdentical(path1, path2):
    """Returns whether folders path1 and path2 are identical.

    I. e., they have the same files, with the same names and contents.
    And same subfolders, which are identical as well (recursively).
    """
    comp = filecmp.dircmp(path1, path2)
    return cmpdirAllEq(comp)


def cmpdirAllEq(comp):
    if comp.diff_files or comp.left_only or comp.right_only:
        return False
    for comp_sub in comp.subdirs.values():
        if not(cmpdirAllEq(comp_sub)):
            return False
    return True


