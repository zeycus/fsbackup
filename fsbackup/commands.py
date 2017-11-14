#!/usr/bin/python3.6

"""
.. module:: commands
    :platform: Windows
    :synopsis: module with the function to be executed for each fsbackup command

.. moduleauthor:: Miguel Garcia <zeycus@gmail.com>
"""


from fsbackup.miscTools import buildVolumeInfoList
import pymongo


def backupStatus(fDB, volDB, reportPref):
    """Generates the status report.
    
    Several files are created:
        * summary.txt: global summary.
        * missing.txt: list of files not yet backed-up.
        * content_<vol>.txt: the list of files backed-up in each volume.
     
    :param fDB: the information regarding files
    :type fDB: FileDB
    :param volDB: the informating regarading volumes
    :type volDB: permanent-dict class
    :param reportPref: prefix that tells where to create reporting 
    :type reportPref: str

    """
    volHashesInfo = buildVolumeInfoList(volDB)
    fDB.reportStatusToFile(volHashesInfo, reportPref)


def extractVolumeInfo(hashVol):
    """Regenerates the DDBB information regarding the files contained in the present volume.

    :param hashVol: the information regarding volumes
    :type hashVol: HashVolume

    """
    hashVol.recalculateContainer()

def showVolumeId(hashVol):
    """Shows the volume id.

    :param hashVol: the information regarding volumes
    :type hashVol: HashVolume

    """
    hashVol.logger.info("The volume has id '%s'." % hashVol.volId)

def cleanVolume(fDB, hashVol):
    """Removes files from the volume that are not necessary anymore.

    Returns the number of deleted files.

    :param fDB: the information regarding files
    :type fDB: FileDB
    :param hashVol: the information regarding volumes
    :type hashVol: HashVolume
    :rtype: int

    """
    hashesNeeded = fDB.hashesSet()
    nDeleted = hashVol.cleanOldHashes(totalHashesNeeded=hashesNeeded)
    fDB.logger.debug("Deleted %s files from the volume." % nDeleted)
    return nDeleted


def checkout(fDB, hashVol, sourcePath, destPath):
    """Restores a given path from the volume, recursively.

    If sourcePath is the root of the backed-up filesystem, all the content would be restored.

    :param fDB: the information regarding files
    :type fDB: FileDB
    :param hashVol: the information regarding volumes
    :type hashVol: HashVolume
    :param sourcepath: path in the backed-up filesystem that needs to be restored
    :type sourcepath: str
    :param checkoutpath: path where we want the files to be created
    :type checkoutpath: str

    """
    fDB.checkout(hashVol, sourcePath, destPath)


def updateVolume(fDB, hashVol):
    """Deletes useless files in the volume, and copies new files that need to be backed-up.

    :param fDB: the information regarding files
    :type fDB: FileDB
    :param hashVol: the information regarding volumes
    :type hashVol: HashVolume

    """
    logger = fDB.logger
    hashesNew, finished = hashVol.augmentWithFiles(fDB=fDB)
    if finished:
        logger.info("With the present (%s) volume, the backup is complete." % hashVol.volId)
    else:
        logger.warning("Some files could *not* be backed-up due to lack of space in the volume. Update another volume.")


def refreshFileInfo(fDB, forceRecalc):
    """Updates the filename collection in the database, reflecting changes in the filesystem.

    :param fDB: the information regarding files
    :type fDB: FileDB
    :param forceRecalc: flag that tells if hashes & timestamps should be recalculated from the file always.
           If False (the default), recalculation happens always when the timestamp of the file is more recent than that
           in the database, or for new files. If True, we recalculate for every file.
    :type forceRecalc: bool

    """
    return fDB.update(forceRecalc=forceRecalc)


def createDatabase(database, forceFlag, logger):
    """Creates database collections from scratch.

    :param fDB: the information regarding files
    :type fDB: FileDB
    :param forceFlag: tells whether to remove info, if collections already exist
    :type forceFlag: bool

    """
    if (not forceFlag) and ((database['files'].count() > 0) or (database['volumes'].count() > 0)):
        raise Exception("Found collections with content, aborted creation. Use --force to destroy current information.")
    logger.debug("Remove content of collection 'hashes', and create indexes.")
    database['files'].delete_many({})
    database['files'].create_index([('filename', pymongo.ASCENDING)], unique=True)
    database['files'].create_index([('hash', pymongo.ASCENDING)])
    logger.debug("Remove content of collection 'volumes', and create indexes.")
    database['volumes'].delete_many({})
    database['volumes'].create_index([('hash', pymongo.ASCENDING)], unique=True)


def integrityCheck(fDB, hashVol):
    """Performs an integrity check for the volume.

    :param fDB: the information regarding files
    :type fDB: FileDB
    :param hashVol: the information regarding volumes
    :type hashVol: HashVolume

    """
    return fDB.volumeIntegrityCheck(hashVol)
