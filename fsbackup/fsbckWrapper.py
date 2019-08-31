#!/usr/bin/python3.6


"""
.. module:: fsbck_wrapper
    :platform: Windows, linux
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
                                 "createdatabase", "checkout", "integritycheck", "showvolumeid", "removeduplicates", "sievepath", ))
    parser.add_argument('-db', '--dbfile', required=True, help="jsonfile whose filesystem/database is to be managed")
    if os.name == 'nt':
        parser.add_argument('-dr', '--drive', help="Windows drive (letter) where the volume is mounted")
    elif os.name == 'posix':
        parser.add_argument('-dmp', '--drivemountpoint', help="Mounting point for external drive")
    else:
        raise OSError("OS '%s' not supported" % os.name)
    parser.add_argument('--force', '-f', help="Confirmation flag for sensitive operations", action='store_true')
    parser.add_argument('--sourcepath', help="Path in the filesystem that is to be restored")
    parser.add_argument('--destpath', help="Path where the checkout should be created")
    parser.add_argument('--loglevel', help="logging level.", choices=("CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"), default="DEBUG")
    parser.add_argument('--volumeid', help="Volume id to be used, if forcing it is needed", default=None)
    parser.add_argument('--regexp', help="Regular Expression to be used")

    args = parser.parse_args(arg_list)

    # ***** Logger *****
    logger = loggingStdout(lev=getattr(logging, args.loglevel))

    # ***** Building custom objects *****
    with open(args.dbfile) as f:
        dbConf = json.load(f)
    client = pymongo.MongoClient(dbConf['connstr'])
    databaseName = re.search("(\w*)$", dbConf['connstr']).group(1)  # The database name is the last part of the connection string.
    db = client[databaseName]
    if dbConf['mountPoint'][0] == '.':  # Relative path to the json location are allowed, if they start with '.'
        mountPoint = os.path.normpath(os.path.join(os.path.dirname(args.dbfile), dbConf['mountPoint']))
    else:
        mountPoint = dbConf['mountPoint']
    fDB = FileDB(
        logger=logger,
        mountPoint=mountPoint,
        fsPaths=dbConf['paths'],
        container=Mongo_shelve(db['files'], "filename"),
    )
    volDB = Mongo_shelve(db['volumes'], 'hash')
    if ('drive' in args) and (args.drive is not None):  # Drive for Windows
        hashVol = HashVolume(
            logger=logger,
            locationPath="%s:\\" % args.drive,
            container=volDB,
            volId=args.volumeid,
        )
    elif ('drivemountpoint' in args) and (args.drivemountpoint is not None):  # Drive for Linux
        hashVol = HashVolume(
            logger=logger,
            locationPath=args.drivemountpoint,
            container=volDB,
            volId=args.volumeid,
        )

    # ***** Invoke the function that performs the given command *****
    infoReturned = dict(db=db)
    if args.command.lower() == 'backupstatus':
        comms.backupStatus(fDB=fDB, volDB=volDB, reportPref=dbConf['reportpref'])
    elif args.command.lower() == 'removeduplicates':
        nDeleted = comms.removeDuplicates(fDB=fDB, regexp=args.regexp)
        infoReturned['nDeleted'] = nDeleted
    elif args.command.lower() == 'sievepath':
        nDeleted = comms.removeDuplicates(fDB=fDB, path=args.sourcepath)
        infoReturned['nDeleted'] = nDeleted
    elif args.command.lower() == 'extractvolumeinfo':
        comms.extractVolumeInfo(hashVol=hashVol)
    elif args.command.lower() == 'showvolumeid':
        comms.showVolumeId(hashVol=hashVol)
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
