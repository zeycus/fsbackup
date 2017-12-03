******************************
Filesystem config files 
******************************
The information about filesystems that we want backed-up is gathered in JSON files,
one per filesystem. For instance:

.. code-block:: json

  {
    "connstr": "mongodb://myuser:mypwd@ds21135.mlab.com:34562/fsbackup_tvs761_main",
    "mountpoint": "\\\\ZEYCUS-TVS671",
    "paths": [
      "Multimedia",
      "Resources"
    ],
    "reportpref": "F:\\Dropbox\\fsbackup\\reports\\main_"
  }


The information is as follows:

``connstr``
  The connection string to the mongoDB database.

``mountpoint``
  The location where the filesystem is mounted. It is used as a basepath for ``paths``.
  
``paths``
  The list of paths in the filesystem that we want backed-up, relative to the ``mountpoint``.

``reportpref``
  Prefix for reports. All files created by the ``backupStatus`` command are created with that prefix.
  
