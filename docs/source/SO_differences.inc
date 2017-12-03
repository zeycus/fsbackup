.. _sec_SO_differences:

**************
SO Differences
**************

Currently, there is support for Linux and Windows. However, there are some differences that need to be taken into account.


Volume identification
=======================
Volumes are not numbered, instead they are identified by a unique identifier.
In Windows, `volume serial numbers <https://en.wikipedia.org/wiki/Volume_serial_number>`_ are used.
In Linux, disk serial numbers are used instead.

This is because in Windows I found no easy way to retrieve the disk serial number of the disk where
a specific path is located, while the volume serial number was easy. On the other hand, typical Linux
filesystems like ext* do not even have a volume serial number, and the disk serial number is straightforward to get.


Path format
===========
In Windows, paths are typically written with backslashes, while for Linux it is done with forward slashes.


.. warning:: In its current state, if a backup is created for a filesystem with a SO, it should always be handled with that SO.

The main reason is the difference in volume ids: the same disk gets different id if the script is run in Windows or Linux.
There are also minor differences, like the path separator, but that would be easy to overcome.

For now, this does not seem a big issue. Suppose you have created a backup with Windows and one day you decide to dump
it forever (nobody would blame you!) and use Linux. In that case you basically would need to update de collections in the database as follows:

    * Replace volume serial numbers with disk serial numbers. You can get them in both SOs with the ``showVolumeId`` command.
    * Replace backslashes with forward slashes.
    * Redefine ``mountpoint`` in the config file, with the Linux mount point of the filesystem that needs backup.
      
Before doing that, it would not hurt to backup the database. Just in case.



