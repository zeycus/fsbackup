********
Overview
********

A command-line script in Python is provided, to manage backups for large filesystems in multiple external disks.

It is intended as a minimalist system, to get the job done but with no GUI or other niceties. At least not yet!
I just wanted to sleep well at night.



Motivation
==========


The Problem
-----------
For more than a decade I had being gathering content and
storing it in external drives.
For backup purposes I used to buy them in pairs, so that one would work as the other's mirror.
Of course the solution was far from ideal, there were tv-series, movies, and documentaries in most disks,
sparsed pretty much randomly, and when the number of disks reached 15 (plus backups) even finding content was a pain.
I had simple text files with the file contents of each disk, which needed to be updated, etc.


An Improvement
------------------
A friend talked to me about a NAS he had recently acquired. After little consideration I realized I had been needing
one myself for a long time, just did not know such a thing existed. Taking into account the size of the files I already had,
plus reasonable mid-term foreseable needs, I bought a 6-slots NAS and put 8GB disks in it (5 of them currently).

Now the content was neatly organised, easy to find and maintain.

I was using RAID5, which is nice, but in several forums I found the clear warning
that `RAID does not work as backup <https://serverfault.com/questions/2888/why-is-raid-not-a-backup>`_\ , so I started worring.
I had the need of a real backup, and a bunch of external drives which content was already in the NAS.
Obviously they might be used to backup content, but I could not bring myself to even try to micro-manage it.
It would be particularly hard because some folders are way bigger that the external drives, so they would have to be split manually.



Backup System Overview
======================
The idea behind the implementation of **fsbackup** is pretty simple, and everything gets done by the ``fsbck`` command.
Given a list of one or more paths that we want backed-up, the backup system works in three stages.


Stage 1
-------

A command (intended to be scheduled nightly) keeps a collection in a `mongoDB <https://www.mongodb.com/>`_ database updated with
the absolute path, size, last modification timestamp and a hash function (currently SHA-256) of each file in that list of paths.
They are interpreted as file-trees, so all the content buried in those paths is included.
It can be done with something like::

    fsbck.py refreshHashes -db=conn_multimedia.json

Only new files, or files with a more recent modification timestamp than the one in the database have their hash function recalculated
(since it is really time-consuming). As you might have guessed, the ``db`` argument refers
to a `json <https://en.wikipedia.org/wiki/JSON>`_ file with information regarding the location
of the filesystem, as well as mongoDB collections where the information is stored.


Stage 2
--------
External hard disks work as backup volumes, containing files renamed with their hash function. The folder structure in the original filesystem
is not replicated, all files are at root level. Except that, using git-style, they are divided in folders according to the first
letters in the hash, to avoid having thousands of files in the same directory.

In order to update the backup, we can mount a disk that works as backup volume (say, it is in G:), and run::

    fsbck.py processDrive -db=conn_multimedia.json --drive=G

This action:

* Removes from the volume files that are not necessary anymore.
* Copies new files that were not backed-up yet.
* Provides a backup status report, with:

    * the number of files/size pending backup (if there was not enough room in that volume).
    * a summary of the number of files/size in each volume.
    * a file per volume is created with the detailed absolute paths of each file backed-up in it.

For this to work properly, another collection in the database stores the hashes backed in each volume.


Stage 3
--------
If/when the time comes information needs to be retrieved from the volumes, the script handles that as well. For instance, the command::

  fsbck.py checkout -db=conn_multimedia.json --drive=G --sourcepath=//Zeycus/multimedia/movies --destpath=F:\chekouts\movies

recovers the relevant information in the actual (G:) volume for a particular folder. In a worst-case scenario, to recover all the files
you'd have to do this for every volume.


So, how do I start?
===================
In a nutshell:

1. Get a mongoDB server connection and create a database there. It could be local, mongoDB hosting (like `mlab <https://mlab.com/>`_ , just to name one), etc.

2. Build a JSON config_file for the filesystem you want backed-up. For instance:

.. code-block:: json

  {
    "connstr": "mongodb://myuser:mypwd@ds21135.mlab.com:34562/fsbackup_tvs761_main",
    "paths": [
      "\\\\ZEYCUS-TVS671\\Multimedia",
      "\\\\ZEYCUS-TVS671\\Resources"
    ],
    "reportpref": "F:\\Dropbox\\fsbackup\\reports\\main_"
  }

where ``connstr`` is the conection string to your mongoDB database (in this case, ``fsbackup_tvs761_main``). More details in the documentation.
Make sure the path in ``reportpref`` actually exists, reporting files are created there. In this case,
``F:\\Dropbox\\fsbackup\\reports``.


3. Create the actual collections in the database with::

    fsbck.py createDatabase -db=<config_file> --force
   

4. Gather the current filesystem information with::

    fsbck.py refreshHashes -db=<config_file>
	
The first time hashes are calculated for all files, so this may take **long**.

5. Connect a formated external drive. Assuming it gets mounted in ``driveLetter``, execute::

    fsbck.py processDrive -db=<config_file> --drive=<driveLetter>

This fills the volume with backup data. When finished, a message will clarify whether more volumes are needed to go on
with the backup.
     



Collaboration
=============

You may wish to improve or add features, in that case you are more than welcome, feel free to contact me at zeycus@gmail.com.

