#!/usr/bin/python3.5

"""
.. module:: fileDB
    :platform: Windows, linux
    :synopsis: module for class :class:`FileDB <fileDB.FileDB>`.

.. moduleauthor:: Miguel Garcia <zeycus@gmail.com>
"""

import re
import os
import filecmp
from collections import defaultdict

from fsbackup.shaTools import sha256
from fsbackup.fileTools import abspath2longabspath, sizeof_fmt


class FileDB(object):
    """Class that handles the DDBB filesystem information.

    Specifically, which files need to be backed-up, their location, size and hash.

    """

    def __init__(self, logger, mountPoint, fsPaths, container):
        """Constructor.

        :param logger: internally stored logger, for feedback.
        :param mountPoint: point where the filesystem is mounted
        :type mountPoint: str
        :param fsPaths: list of paths that we intend to be backed-up. Relative to the mountPoint.
        :type fsPaths: list of str
        :param container: database information regarding the files in the filesystem, its location, size and hash.
        :type container: Mongo_shelve

        """
        self.logger = logger
        self.mountPoint = mountPoint
        self.fsPaths = []
        for path in fsPaths:  # Paths are gathered removing any '\\' at the end
            while path[-1] == '\\':
                path = path[:-1]
            self.fsPaths.append(path)
        self.container = container

    def compFn(self, fn):
        """Returns the absolute filename associated to a relative-to-mountPoint filename."""
        return abspath2longabspath(os.path.join(self.mountPoint, fn))

    @property
    def fsPathsComplete(self):
        """Returns list of fsPaths, in absolute form."""
        return [os.path.join(self.mountPoint, path) for path in self.fsPaths]


    def hashesSet(self):
        """Returns the set of hashes in the DDBB.

        :rtype: set
        """
        return set(info['hash'] for _, info in self)

    def calcDuplicates(self):
        """Return dict hash: [files] for which there are at least two files."""
        hashInfo = defaultdict(list)
        for fn, info in self:
            hashInfo[info['hash']].append(fn)
        return {sha: fns for (sha, fns) in hashInfo.items() if len(fns) >= 2}

    def removeDuplicates(self, regexp):
        """Removes entries matching the regexp"""
        nDeleted = 0
        dups = self.calcDuplicates()
        for fns in dups.values():
            # Check whether at least one file does match the regexp and another does not
            deletables = [fn for fn in fns if re.search(regexp, fn) is not None]
            if deletables and any(fn for fn in fns if re.search(regexp, fn) is None):
                for fn in deletables:
                    self.removeEntry(fn, delete=True)
                    nDeleted += 1
        return nDeleted

    def sievePath(self, path):
        """Recursively removes all files in path that are already present in the FileDB.
        
        The comparison is performed via SHA.
        """
        nDeleted = 0
        hashes = self.hashesSet()
        for root, _, fns in os.walk(path):
            for fn in fns:
                fnComp = os.path.join(root, fn)
                if sha256(self.compFn(fn)) in hashes:
                    self.logger.info("Removing file %s from filesystem." % fnComp)
                    os.remove(fnComp)
                    nDeleted += 1
        return nDeleted

    def removeEntry(self, fn, delete=False):
        """Removes entry for a file.
        
        :param fn: file for which we want the entry deleted
        :type fn: str
        :param delete: flag that tells whether the file should be physically deleted
        :type delete: bool
        """
        self.logger.debug('Removing %s' % fn)
        del self.container[fn]
        if delete:
            os.remove(self.compFn(fn))


    def update(self, forceRecalc=False):
        """Updates the DDBB info traversing the actual filesystem.

        After execution, the DDBB reflects exactly the files currently in the filesystem,
        with their correct hash and size.

        :param forceRecalc: flag that tells if hashes & timestamps should be recalculated from the file always.
               If ``False`` (the default), recalculation happens only when the timestamp of the file is more recent than that
               in the database, or for new files. If ``True``, recalculation takes place for every file.
        :type forceRecalc: bool

        """
        # Traverse actual files
        self.logger.debug("Traversing the filesystem.")
        currentFiles = []
        for sourcePath in self.fsPathsComplete:
            for root, _, fns in os.walk(sourcePath):
                for fn in fns:
                    fnComp = os.path.join(root, fn)
                    ## currentFiles.append(os.path.relpath(fnComp.self.mountPoint))  # Relative paths do not work as expected for start like '\\ZEYCUS'.
                    # See https://stackoverflow.com/questions/47364579/unexpected-behaviour-of-pythons-os-path-relpath/47364931#47364931
                    # Instead, I do it manually:
                    fnAux = fnComp[len(self.mountPoint):]
                    while fnAux[0] == '\\':
                        fnAux = fnAux[1:]
                    currentFiles.append(fnAux)
        currentFiles = set(currentFiles)

        # Obtain files stored in the DDBB
        storedFiles = dict(self)  # We need to access so many times that it is convenient to build a dict with all the info
        storedFilesSet = set(self.container)

        # Delete DDBB entries for files that longer exist.
        self.logger.debug("Removing outdated entries.")
        for fn in sorted(storedFilesSet - currentFiles):
            self.removeEntry(fn)

        # Update information for files with a newer timestamp, or a modified size.
        if forceRecalc:
            self.logger.debug("Updating entries with --force. All %s of them will be recalculated." % len(storedFilesSet & currentFiles))
        else:
            self.logger.debug("Updating entries. Files to check: %s." % len(storedFilesSet & currentFiles))
        for fn in sorted(storedFilesSet & currentFiles):
            fnStat = os.stat(self.compFn(fn))
            timestamp = fnStat.st_mtime
            size = fnStat.st_size
            if forceRecalc or (timestamp > storedFiles[fn]['timestamp']) or (size != storedFiles[fn]['size']):
                self.logger.debug('Modifying %s' % fn)
                self.container[fn] = dict(
                   timestamp=timestamp,
                   size=size,
                   hash=sha256(self.compFn(fn)),
                )

        # Include information for new files
        self.logger.debug("Inserting new entries.")
        for fn in sorted(currentFiles - storedFilesSet):
            self.logger.debug('Adding %s' % fn)
            fnStat = os.stat(self.compFn(fn))
            self.container[fn] = dict(
                timestamp=fnStat.st_mtime,
                size=fnStat.st_size,
                hash=sha256(self.compFn(fn)),
            )


    def checkout(self, vol, sourcePath, destPath):
        """Rebuilds the filesystem, or a subfolder, from the backup content.

        We just invoke the chekout method of the volume.

        :param vol: the volume from which information is to be restored.
        :type vol: HashVolume
        :param sourcePath: path in the filesystem that you want restored
        :type sourcePath: str
        :param destPath: location where you want the files created
        :type destPath: str
        :rtype: list of str

        """
        return vol.checkout(self, sourcePath, destPath)


    def reportStatusToFile(self, volHashesInfo, fnBase):
        """Creates backup-status report files.

        :param volHashesInfo: for each volume, associates the hash of each file with its size.
        :type volHashesInfo: dict {vol: {hash: size}}
        :param fnBase: prefix of the report files to be created
        :type fnBase: str
        """
        volumes = [vol for vol, _ in volHashesInfo]

        # Set of hashes for each volume
        hashesVols = {vol: set(shaSizes) for vol, shaSizes in volHashesInfo}

        # For each sha, its size
        volShaSizes = dict()
        for _, shaSizes in volHashesInfo:
            volShaSizes.update(shaSizes)

        # Set of hashes needed
        hashesNeeded = set()
        for path, info in self:
            hashesNeeded.add(info['hash'])

        notBacked = dict()
        # Detailed information per volume
        volsInfo = {vol: dict() for vol in volumes}
        for path, info in self:
            sha = info['hash']
            found = False
            for vol, hashesInfo in volHashesInfo:
                if sha in hashesInfo:
                    volsInfo[vol][path] = info['size']
                    found = True
            if not found:
                notBacked[path] = info['size']

        with open(fnBase + "missing.txt", 'w', encoding="utf-8") as f:
            for fn, size in sorted(notBacked.items()):
                print("%s (%s)" % (fn, sizeof_fmt(size)), file=f)

        # Content of each volume
        for vol, fnSizes in sorted(volsInfo.items()):
            self.logger.debug("Creating file contents for volume '%s'" % vol)
            with open(fnBase + "content_%s.txt" % vol, 'w', encoding="utf-8") as f:
                for fn, size in sorted(fnSizes.items()):
                    print("%s (%s)" % (fn, sizeof_fmt(size)), file=f)

        # Summary
        with open(fnBase + "summary.txt", 'w') as f:
            print("Missing files: %s (%s)\n" % (len(notBacked), sizeof_fmt(sum(notBacked.values()))), file=f)

            for vol, fnSizes in sorted(volsInfo.items()):
                print("Information volume '%s':" % vol, file=f)
                print("\tBackup up %s files (%s)" % (len(fnSizes), sizeof_fmt(sum(fnSizes.values()))), file=f)

                shaDelet = hashesVols[vol] - hashesNeeded
                sizeDelet = sum(volShaSizes[sha] for sha in shaDelet)
                print("\tDeletable %s files (%s)" % (len(shaDelet), sizeof_fmt(sizeDelet)), file=f)
                print("", file=f)


    def volumeIntegrityCheck(self, vol):
        """Performs a volume integrity check.

        For each file that according to the DDBB is in this volume, a full comparison
        is performed between the file in the filesystem and the file in the backup volume.
        Of course, only when the file exists yet in the filesystem.

        A final report with errors is generated, a list of errors returned.

        :param vol: the volume from which information is to be restored.
        :type vol: HashVolume
        :rtype: list of str

        """
        shaSizes = {sha: size for (sha, size) in vol}
        shaNeededSet = set(shaSizes)
        problems = []
        for fn, info in sorted(self):
            sha = info['hash']
            if sha in shaNeededSet:
                fnComp = self.compFn(fn)
                # Check file sizes
                size_fs_db = info['size']
                size_fs_real = os.stat(fnComp).st_size
                if size_fs_db != size_fs_real:
                    msg = "In filesystem, file sizes disagree for '%s': %s in ddbb and %s actual file size." % (
                    fn, size_fs_db, size_fs_real)
                    self.logger.warning(msg)
                    problems.append(msg)
                fnVol = vol.fnForHash(sha)
                size_vol_db = shaSizes[sha]
                size_vol_real = os.stat(fnVol).st_size
                if size_vol_db != size_vol_real:
                    msg = "In volume, file sizes disagree for '%s': %s in ddbb and %s actual file size." % (
                    fn, size_vol_db, size_vol_real)
                    self.logger.warning(msg)
                    problems.append(msg)

                # Check file content is equal
                self.logger.debug("Errors so far: %s. Comparing '%s' and '%s'." % (len(problems), fn, fnVol))
                try:
                    areEqual = filecmp.cmp(fnComp, fnVol, shallow=False)  # This might fail there are I/O reading problems.
                    if not areEqual:
                        msg = "File '%s' in filesystem is not equal to file '%s' in volume." % (fn, fnVol)
                        self.logger.warning(msg)
                        problems.append(msg)
                except:
                    msg = "Files '%s' in filesystem and '%s' in volume could not be compared. I/O error?." % (fn, fnVol)
                    self.logger.warning(msg)
                    problems.append(msg)
        if problems:
            self.logger.warning("Unfortunately, some problems were found:")
            for msg in problems:
                self.logger.warning(msg)
        else:
            self.logger.info("No single problem was detected.")


    def __iter__(self):
        """Iterator for pairs (fn, Info). For each file, its size and hash."""
        yield from self.container.items()


    def __len__(self):
        """Returns the number of files in the database"""
        return len(self.container)

