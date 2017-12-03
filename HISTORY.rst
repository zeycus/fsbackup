.. :changelog:

***************
Release History
***************


0.2.1 (2017-12-04)
====================

**Improvements**

- Linux support.
- New attribute ``mountPoint`` for **FileDB**.
- New command ``showVolumeId``.


**Bugfixes**

- I had forgotten to use FileDB.fnComp() in a point of code.
  


0.1.3 (2017-11-12)
====================

**Improvements**

- Make filename paths stored in the database relative to its mount point.


0.1.2 (2017-11-09)
====================

**Improvements**

- New safe file copy: deletes target file if the writting process failed.
- New "How do I start?" section in README.
- New "Release History".
- Replace deprecated pymongo collections ``remove`` with ``delete_many``.


**Bugfixes**

- Fixed typo in setup ``tests_require`` argument.


0.1.1 (2017-11-05)
=====================

* First version made available
