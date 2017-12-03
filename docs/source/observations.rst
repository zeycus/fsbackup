*************
Observations
*************

Volume identification
=======================
Volumes are not numbered, instead they are identified by a unique identifier (see :ref:`sec_SO_differences`).
This means you never need to process the volumes in any order, nor when you update them.

For instance, suppose you remove some huge files from your filesystem (who would want to watch **THAT** tv-show again!?). As a consequence the ``backupstatus`` report
shows that a volume contains now 300GB of removable files. You could choose this volume for your next ``processDrive`` and useless content will be dropped, making room and using it for fresh file backups.



Volume content
=================
Files are not backed-up in any order. The system just aims to have each file backed-up in a (single) volume. This means content is more or less randomly
divided among volumes.


