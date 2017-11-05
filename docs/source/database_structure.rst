******************
Database Structure
******************

Information regarding the filesystem to be backed-up, and the current content
of volumes, is stored in a `mongoDB <https://www.mongodb.com/>`_ database. 


Filesystem
==========
The collection that stores the information about the files currently in the filesystem is (uninspiredly!) named ``files``.
The entries/documents in it have the form:

.. code-block:: python

	{
        '_id': ObjectId("59e0a71c2afc32cfc4e7fa48"),
        'filename': r"\\ZEYCUS-TVS671\Multimedia\video\animePlex\Shin Chan\Season 01\Shin Chan - S01E613.mp4",
        'hash': "4a7facfe42e8ff8812f9cab058bf79981974d9e2e300d56217d675ec5987cf05",
        'timestamp': 1197773340,
        'size': 68097104
	}

where:

    * The ``filename`` field is the absolute path of the file.
    * The ``hash`` field is the SHA-256 hash of the file.
    * ``timestamp`` is the file's last-modified timestamp.
    * ``size`` is the size of the file in bytes, obtained with ``os.stat(fn).st_mtime``\ .

The fields used for look-up are ``filename`` and ``hash``, so the collection should have an index on each of them.
The one on ``filename`` should have ``unique=True``, to ensure no filename is added twice [#fInd]_ .



The class that manages this collection is :class:`FileDB <fsbackup.fileDB.FileDB>`.



Volumes
=======

On the other hand, the present state of backup volumes is stored in the collection ``volumes``,
with entries like

.. code-block:: python

	{
        '_id': ObjectId("59e484603e12972bd4209fbe"),
        'volume': "3EC0BECC",
        'hash': "0017eef276f4247807fa3f4e565b8c925a2db0f8bfbb020248ad6c3df6a6ea77",
        'size': 97092
	}

where:

    * The ``volume`` is the volume SerialNumber.
    * The ``hash`` field is the SHA-256 hash of the file.
    * ``size`` is the size of the file in bytes.
	
This entry is saying that volume 3EC0BECC contains a file with the given hash, and filesize 97,092 bytes.

There should be a a unique index on field ``hash`` [#f1]_ .



The methods that add/remove files from a volume (see class :class:`HashVolume <fsbackup.hashVolume.HashVolume>`)
also update this collection, so that it remains up-to-date.


.. rubric:: Footnotes

.. [#f1] In fact, this enforces that only one volume may contain a file with a specific hash. If the backup
   methods are working correctly this should be the case. If the same file is found in different
   folders in the filesystem, or with different names, no space is wasted and just one copy will 
   be present in backup volumes.

.. [#fInd] This is not true for ``hash``, because we need to be able to backup systems that contain the same file in different locations.
   I was surprised to find that I had about a 5% of file redundancy in number of files, it turned out that some tiny files were necessary in many locations.