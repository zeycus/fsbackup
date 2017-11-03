#!/usr/bin/python3.6

"""
.. module:: hashVolume
    :platform: Windows
    :synopsis: module for class :class:`HashVolume <hashVolume.HashVolume>`.

.. moduleauthor:: Miguel Garcia <zeycus@gmail.com>
"""


import os
import re
import shutil
import bisect
import random

from fsbackup.shaTools import sha256
from fsbackup.fileTools import sizeof_fmt, abspath2longabspath
from fsbackup.diskTools import getVolumeInfo


class HashVolume(object):
    """Class that handles a backup volume.


    """
    def __init__(self, logger, locationPath, container, volId=None):
        """Constructor.

        :param logger: internally stored logger, for feedback.
        :param locationPath: root path for the volume. Usually something like ``'G:\'``
        :type locationPath: str
        :param container: database information regarding which hashes are stored in which volume.
        :type container: Mongo_shelve
        :param volId: volume id. Currently, the volume SerialNumber, but the hard-drive SerialNumber might be a better choice.
               It is optional, if ``None``, it is obtained by the OS.
        :type volId: str

        """
        self.logger = logger
        self.locationPath = locationPath
        self.container = container
        if volId is None:
            self.volId = getVolumeInfo(locationPath[0])['VolumeSerialNumber']
        else:
            self.volId = volId

    def allVolumesHashes(self):
        """Returns the set of all hashes in any volume, according to the DDBB.

        :rtype: set
        """
        return set(self.container)

    def recalculateContainer(self):
        """Rebuilds the DDBB volume information, traversing the files in the volume.

        .. note::
            This is something ordinarily you don't need to do, because the DDBB
            is kept synchronized with the files in the volume. This method is to be used
            in case for some reason the synchronization was broken.
        """
        self.logger.debug("Rebuilding DDBB info for volume '%s'." % self.volId)
        result = self.container.remove(dict(volume=self.volId))
        self.logger.debug("Removed all (%s) documents." % result['n'])
        result = self.container.insert([dict(volume=self.volId, hash=fn, size=size) for (fn, size) in self.traverseFiles()])
        self.logger.debug("Created %s new documents." % len(result))

    def fnForHash(self, sha):
        """Returns the absolute path of the file for a given hash.

        The first three letters in the hash are used to create a 3-levels folder system,
        for instance hash ``4c07766937a4d241fafd3104426766f07c3ce9de7e577a76ad61eba512433cea``
        corresponds to file

            :file:`self.locationPath/4/c/0/4c07766937a4d241fafd3104426766f07c3ce9de7e577a76ad61eba512433cea`

        :param sha: any valid SHA
        :type sha: str
        :rtype: str
        """
        return os.path.join(self.locationPath, sha[0], sha[1], sha[2], sha)

    def storeFilename(self, filename, size, sha=None):
        """Creates a file in the volume.

        The filename in the volume is the sha, not the original filename.

        :param filename: location of the original file
        :type filename: str
        :param size: size in bytes of the original file
        :type size: int
        :param sha: the hash for the file. If not provided, it is calculated now

        """
        filename = abspath2longabspath(filename)
        if sha is None:
            sha = sha256(filename)
        fn_dest = self.fnForHash(sha)
        os.makedirs(os.path.dirname(fn_dest), exist_ok=True)  # Si el directorio no existe, lo crea.
        shutil.copyfile(
            src=filename,
            dst=fn_dest,
        )
        self.container[sha] = dict(volume=self.volId, size=size)

    def retrieveFilename(self, sha, filename):
        """Extracts a file from the volume, given its hash.

        :param sha: the given hash
        :type sha: str
        :param filename: the filename of the file to be created
        :type filename: str

        """
        fn_source = abspath2longabspath(self.fnForHash(sha))
        os.makedirs(os.path.dirname(filename), exist_ok=True)  # Si el directorio no existe, lo crea.
        shutil.copyfile(
            src=fn_source,
            dst=filename,
        )

    def remove(self, sha):
        """Deletes the file with a given hash.

        :param sha: the given hash
        :type sha: str

        """
        os.remove(self.fnForHash(sha))
        del self.container[sha]

    def getAvailableSpace(self):
        """Returns the available free space in the volume drive, in bytes.

        :rtype: int
        """
        return shutil.disk_usage(self.locationPath).free

    def augmentWithFiles(self, fDB):
        """Include in the volume backup for the files that need it.

        It is done until all files are backed-up, on until the volume is full.

        :param fDB: filesystem information in DDBB.
        :type fDB: FileDB
        :rtype: a pair (isFinished, hashList)

           * isFinished tells whether the backup is complete. It is False if there are still
             files that are not backed-up in any volume.
           * hashList is the list of hashes of the created files.

        .. note::
            The strategy to choose which file to backup next is the following, but there are no
            strong reasons for this, it should be changed if another is found better.

            * While there is plenty of room in the volume (threshold currently set to 20GB) and there is room
              for the biggest file that requires backup, files are chosen randomly.
              The reason is that usually there are folders with huge files, others with only tiny files.
              If files were processed by their folder order, a volume could end up with millions
              of small files, while another could contain just hundreds of heavy files. Not that it would
              be a problem in principle, but I thought it might be better to balance volumes, and
              a simple strategy is the random choice.
            * When the previous condition fails, choose the biggest file that fits, until none does.


        """
        shasStored = self.allVolumesHashes()
        filesizes = [(info['size'], fn, info['hash']) for (fn, info) in fDB if info['hash'] not in shasStored]
        filesizes.sort()
        shasAugmented = []
        avail = self.getAvailableSpace()
        while filesizes:
            if avail < filesizes[0][0] + 100000:  # Avoiding to use the very last free byte, just in case.
                return shasAugmented, False
            # Choice of file to backup.
            if (avail > 20 * 2**30) and (avail > filesizes[-1][0]):
                pos = random.randint(0, len(filesizes) - 1)
            else:
                pos = bisect.bisect_right(filesizes, (avail, '', '') ) - 1  # The biggest file that fits
            if not (0 <= pos < len(filesizes)):  # Just checking, this should never happen
                raise Exception("File chosen out of range")
            sizeFound, fnFound, shaFound = filesizes[pos]
            self.storeFilename(
                filename=fnFound,
                size=sizeFound,
                sha=shaFound,
            )
            avail = self.getAvailableSpace()
            self.logger.debug("Included new file '%s (%s)'. Available: %s" % (fnFound, sizeof_fmt(sizeFound), sizeof_fmt(avail)) )
            del filesizes[pos]
            shasAugmented.append(shaFound)
        return shasAugmented, True

    def cleanOldHashes(self, totalHashesNeeded):
        """Removes files that are no longer necessary.

        Returns the number of files removed.

        :param totalHashesNeeded: hashes of files that need to be backed-up.
        :type totalHashesNeeded: set
        :rtype: int

        """
        nbDeleted = 0
        for sha, _ in self:
            if sha not in totalHashesNeeded:
                self.remove(sha)
                nbDeleted += 1
        return nbDeleted

    def checkout(self, fDB, sourcePath, destPath):
        """Rebuilds the filesystem, or a subfolder, from the backup content.

        Returns a list of the filenames (in the original filesystem) that were restored.

        :param fDB: filesystem information in DDBB.
        :type fDB: FileDB
        :param sourcePath: path in the filesystem that you want restored
        :type sourcePath: str
        :param destPath: location where you want the files created
        :type destPath: str
        :rtype: list of str

        """
        hashesVolume = set(sha for sha, size in self)
        filesFound = []
        nbFilesToCheck = len(fDB)  # Numero total ficheros en fDB, no todos estaran en sourcePath.
        for ind, (fn, info) in enumerate(fDB):
            if info['hash'] in hashesVolume:  # Este volumen contiene el fichero buscado
                relP = os.path.relpath(fn, sourcePath)
                if relP[0] != '.':  # fn esta en el path del que hacemos checkout
                    destFn = os.path.join(destPath, relP)
                    self.logger.debug("File %d of %d, copying '%s' to '%s'" % (ind+1, nbFilesToCheck, fn, destFn))
                    self.retrieveFilename(
                        sha=info['hash'],
                        filename=destFn,
                    )
                    filesFound.append(fn)
        return filesFound

    def traverseFiles(self):
        """Iterator over pairs (hash, size) for the present volume, checking which actual files are stored in it."""
        for root, _, files in os.walk(self.locationPath):
            for fn in files:
                if re.match(r"^[a-fA-F0-9]{64}$", fn):  # Por filtrar los tipicos ficheros que crea el SO y no son de SHA-256
                    fnComp = os.path.join(root, fn)
                    fnStat = os.stat(abspath2longabspath(fnComp))
                    yield fn, fnStat.st_size

    def __iter__(self):
        """Iterator over pairs (hash, size) for the present volume in the DDBB"""
        for doc in self.container.find(dict(volume=self.volId)):
            yield (doc['hash'], doc['size'])

