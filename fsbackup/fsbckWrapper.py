#!/usr/bin/python3.6


"""
.. module:: fsbck_wrapper
    :platform: Windows
    :synopsis: the entrance point script to the backup system

.. moduleauthor:: Miguel Garcia <zeycus@gmail.com>
"""

import sys
import os
import re
import argparse
import json
import pymongo
import logging

from fsbackup.fileDB import FileDB
from fsbackup.hashVolume import HashVolume
from fsbackup.funcsLogger import loggingStdout
from mongo_shelve import Mongo_shelve

import fsbackup.commands as comms


def fsbck_wrapper(arg_list):
    """Given the arguments passed, runs the appropiate task.

    :param arg_list: arguments after the script name
    :type arg_list: list of str
    :rtype: dict

    Returns info generated that is useful for tests.

    """
    # ***** Parser *****
    parser = argparse.ArgumentParser(
        prog="fsbck",
        description="Filesystem multi-volume backup manager",
    )
    parser.add_argument('command', help="task to perform", type=lambda s:s.lower(),
                        choices=("backupstatus", "extractvolumeinfo", "cleanvolume", "updatevolume", "refreshhashes", "processdrive",
                                 "createdatabase", "checkout", "integritycheck", ))
    parser.add_argument('-db', '--dbfile', help="jsonfile whose filesystem/database is to be managed")
    parser.add_argument('-dr', '--drive', help="Windows drive (letter) where the volume is mounted")
    parser.add_argument('--force', '-f', help="Confirmation flag for sensitive operations", action='store_true')
    parser.add_argument('--sourcepath', help="Path in the filesystem that is to be restored")
    parser.add_argument('--destpath', help="Path where the checkout should be created")
    parser.add_argument('--loglevel', help="logging level.", choices=("CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"), default="DEBUG")
    args = parser.parse_args(arg_list)

    # ***** Logger *****
    logger = loggingStdout(lev=getattr(logging, args.loglevel))

    # ***** Building custom objects *****
    with open(args.dbfile) as f:
        dbConf = json.load(f)
    client = pymongo.MongoClient(dbConf['connstr'])
    databaseName = re.search("(\w*)$", dbConf['connstr']).group(1)  # The database name is the last part of the connection string.
    db = client[databaseName]
    paths = [os.path.normpath(os.path.join(os.path.dirname(args.dbfile), path)) for path in dbConf['paths']]  # If relative paths are found, make them absolute w.r.t the location of the json file.
    fDB = FileDB(
        logger=logger,
        fsPaths=paths,
        container=Mongo_shelve(db['files'], "filename"),
    )
    volDB = Mongo_shelve(db['volumes'], 'hash')
    if args.drive is not None:
        hashVol = HashVolume(
            logger=logger,
            locationPath=r"%s:\\" % args.drive,
            container=volDB,
        )

    # ***** Invoke the function that performs the given command *****
    infoReturned = dict(db=db)
    if args.command.lower() == 'backupstatus':
        comms.backupStatus(fDB=fDB, volDB=volDB, reportPref=dbConf['reportpref'])
    elif args.command.lower() == 'extractvolumeinfo':
        comms.extractVolumeInfo(hashVol=hashVol)
    elif args.command.lower() == 'cleanvolume':
        nDeleted = comms.cleanVolume(fDB=fDB, hashVol=hashVol)
        infoReturned['nDeleted'] = nDeleted
    elif args.command.lower() == 'updatevolume':
        comms.updateVolume(fDB=fDB, hashVol=hashVol)
    elif args.command.lower() == 'integritycheck':
        comms.integrityCheck(fDB=fDB, hashVol=hashVol)
    elif args.command.lower() == 'refreshhashes':
        comms.refreshFileInfo(fDB=fDB, forceRecalc=args.force)
    elif args.command.lower() == 'createdatabase':
        comms.createDatabase(database=db, forceFlag=args.force, logger=logger)
    elif args.command.lower() == 'checkout':
        comms.checkout(fDB=fDB, hashVol=hashVol,
                       sourcePath=args.sourcepath, destPath=args.destpath)
    elif args.command.lower() == 'processdrive':  # Clean + update + backupStatus
        comms.cleanVolume(fDB=fDB, hashVol=hashVol)
        comms.updateVolume(fDB=fDB, hashVol=hashVol)
        comms.backupStatus(fDB=fDB, volDB=volDB, reportPref=dbConf['reportpref'])
    else:
        raise Exception("Command '%s' not supported" % args.command)

    # Return information, useful for now only for testing.
    return infoReturned
