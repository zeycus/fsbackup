******************************
Filesystem config files 
******************************
The information about filesystems that we want backed-up is gathered in JSON files,
one per filesystem. For instance:

.. code-block:: json

  {
    "connstr": "mongodb://myuser:mypwd@ds21135.mlab.com:34562/fsbackup_tvs761_main",
    "paths": [
      "\\\\ZEYCUS-TVS671\\Multimedia",
      "\\\\ZEYCUS-TVS671\\Resources"
    ],
    "reportpref": "F:\\Dropbox\\fsbackup\\reports\\main_"
  }


The information is as follows:

``connstr``
  The connection string to the mongoDB database.

``paths``
  The list of paths in the filesystem that we want backed-up. So far I've been using absolute paths myself,
  but I think that paths relative to the location of the config file work as well. But I have not tested
  it that heavily.

``reportpref``
  Prefix for reports. All files created by the ``backupStatus`` command are created with that prefix.
  