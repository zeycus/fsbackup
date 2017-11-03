#!/usr/bin/python 3.5

import os
import unittest
import shutil

from fsbackup.auxiliarForTests import createTree, checkFiletreesIdentical
from fsbackup.mountPathInDrive import MountPathInDrive
from fsbackup.diskTools import getAvailableLetter
from fsbackup.fsbckWrapper import fsbck_wrapper


class TestFsbackup(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pathbase = os.path.join(os.path.dirname(__file__), 'temp')
        cls.conn_testing = os.path.join(os.path.dirname(__file__), 'conn_testing.json')
        cls.nFiles = 319

        # Create the database, or make it empty if it existed.
        infoReturned = fsbck_wrapper([
            'createDatabase',
            '-db=%s' % cls.conn_testing,
            '--loglevel=CRITICAL',
            '--force',
        ])
        cls.db = infoReturned['db']


    @classmethod
    def tearDownClass(cls):
        cls.db.client.drop_database(cls.db.name)
        shutil.rmtree(cls.pathbase)


    def testBasicBackup(self):
        """Backup & checkout in a simple scenario works. Modifying the filesystem and updating, too.

        1. A filesystem with dumb files is created on the fly, the file content in the DB is filled.
           A volume is created to backup the fs, then a checkout is performed and both folders compared.

        2. After that, a few files are removed, the volume is cleaned and updated. Then a new checkout
           is built, and folders compared.

        """
        shutil.rmtree(self.pathbase, ignore_errors=True)
        fs_path = os.path.join(self.pathbase, 'filesystem')
        vol_path = os.path.join(self.pathbase, 'volume')
        checkout_path = os.path.join(self.pathbase, 'checkout')
        createTree(pathbase=fs_path, nFiles=self.nFiles)
        avLetter = getAvailableLetter()
        os.makedirs(vol_path, exist_ok=True)

        self.assertEqual(self.db['files'].count(), 0)  # Make sure collections are empty
        self.assertEqual(self.db['volumes'].count(), 0)  # Make sure collections are empty

        # Fill the 'files' collection with the filesystems' information
        fsbck_wrapper([
            'refreshHashes',
            '-db=%s' % self.conn_testing,
            '--loglevel=CRITICAL',
        ])
        self.assertEqual(self.db['files'].count(), self.nFiles)  # Make sure each file has an entry

        with MountPathInDrive(path=vol_path, driveLetter=avLetter):
            # Update a volume in a mocked windows drive
            fsbck_wrapper([
                'updateVolume',
                '-db=%s' % self.conn_testing,
                '--drive=%s' % avLetter,
                '--loglevel=CRITICAL',
            ])
            # Make sure each file has an entry, and identical files are backed-up only once.
            # There are 100 or less because of the special way in which createTree fills files content.
            self.assertEqual(self.db['volumes'].count(), min(self.nFiles, 100))

            # Restore info from the volume
            fsbck_wrapper([
                'checkout',
                '-db=%s' % self.conn_testing,
                '--drive=%s' % avLetter,
                '--sourcepath=%s' % fs_path,
                '--destpath=%s' % checkout_path,
                '--loglevel=CRITICAL',
            ])

            # Make sure that the checkout is exact to the original filesystem.
            self.assertTrue(checkFiletreesIdentical(fs_path, checkout_path),
                            msg="The checkout tree is not exactly equal to the original filesystem.")

            # Delete a few files from the original filesystem: those ending in 5 and 6
            nDeleted = 0
            for root, _, files in os.walk(fs_path):
                for fn in files:
                    fnComp = os.path.join(root, fn)
                    if (fn[-5] == '5') or (fn[-5] == '6'):
                        os.remove(fnComp)
                        nDeleted += 1

            # Refresh file content in DB
            fsbck_wrapper([
                'refreshHashes',
                '-db=%s' % self.conn_testing,
                '--loglevel=CRITICAL',
            ])

            # Make sure entries were deleted
            self.assertEqual(self.db['files'].count(), self.nFiles - nDeleted)

            # Clean the volume
            infoAux = fsbck_wrapper([
                'cleanVolume',
                '-db=%s' % self.conn_testing,
                '--drive=%s' % avLetter,
                '--loglevel=CRITICAL',
            ])
            self.assertEqual(infoAux['nDeleted'], 20)  # Exactly 20 hashes, 10 for files ending in 6 and 10 ending in 5

            # Perform another checkout
            shutil.rmtree(checkout_path)
            fsbck_wrapper([
                'checkout',
                '-db=%s' % self.conn_testing,
                '--drive=%s' % avLetter,
                '--sourcepath=%s' % fs_path,
                '--destpath=%s' % checkout_path,
                '--loglevel=CRITICAL',
            ])

            # Make sure that the checkout is exact to the current filesystem.
            self.assertTrue(checkFiletreesIdentical(fs_path, checkout_path),
                            msg="The checkout tree is not exactly equal to the original filesystem.")



if __name__ == '__main__':
    unittest.main()
