.. filesystem backup documentation master file, created by
   sphinx-quickstart on Mon Oct 30 10:28:36 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

############################################################################
Module :mod:`fsbackup`, Multi-Volume Backup for Large Filesystems
############################################################################


.. toctree::
   :maxdepth: 2


.. include:: README.rst

.. include:: database_structure.rst

.. include:: volume_content.rst

.. include:: config_files.rst

.. include:: command_usage.rst

.. include:: observations.rst

.. include:: warnings.rst

.. include:: todo.rst


######################
Code documentation
######################

******************** 
Main Commands Module
********************
.. automodule:: fsbackup.commands
.. currentmodule:: fsbackup.commands
.. autofunction:: backupStatus
.. autofunction:: extractVolumeInfo
.. autofunction:: cleanVolume
.. autofunction:: updateVolume
.. autofunction:: refreshFileInfo
.. autofunction:: createDatabase
.. autofunction:: integrityCheck

*****************
Auxiliary Modules
*****************

Module :mod:`miscTools <fsbackup.miscTools>`
============================================
.. automodule:: fsbackup.miscTools
.. currentmodule:: fsbackup.miscTools
.. autofunction:: buildVolumeInfoList

Module :mod:`fileTools <fsbackup.fileTools>`
============================================
.. automodule:: fsbackup.fileTools
.. currentmodule:: fsbackup.fileTools
.. autofunction:: sizeof_fmt
.. autofunction:: abspath2longabspath

Module :mod:`diskTools <fsbackup.diskTools>`
============================================
.. automodule:: fsbackup.diskTools
.. currentmodule:: fsbackup.diskTools
.. autofunction:: genDrivesInfo
.. autofunction:: genVolumesInfo
.. autofunction:: getVolumeInfo
.. autofunction:: getAvailableLetter



**********************************************************
Class :class:`HashVolume <fsbackup.hashVolume.HashVolume>`
**********************************************************
.. automodule:: fsbackup.hashVolume
.. autoclass:: fsbackup.hashVolume.HashVolume
    :members: 


**********************************************************
Class :class:`FileDB <fsbackup.fileDB.FileDB>`
**********************************************************
.. automodule:: fsbackup.fileDB
.. autoclass:: fsbackup.fileDB.FileDB
    :members: 


***********************************************************************************
Class :class:`MountPathInDrive <fsbackup.mountPathInDrive.MountPathInDrive>`
***********************************************************************************
.. automodule:: fsbackup.mountPathInDrive
.. autoclass:: fsbackup.mountPathInDrive.MountPathInDrive
    :members: 


####################
Indices and tables
####################

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

