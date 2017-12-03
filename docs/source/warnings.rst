***********************
Please, **be aware**!
***********************


.. warning:: To be able to use mongoDB, we must have a connection to a mongoDB server. It could be our own machine, a hosting service, etc.

If you are new to mongoDB, several tutorials are available, `this <https://www.hongkiat.com/blog/webdev-with-mongodb-part1/>`_ is one of them. There are also many mongoDB-hosting services that provide free sandboxes with a decent size, no need to spend a dime just to experiment.

If you have mongoDB installed, to serve it locally in Windows just run:

.. code:: bash

    mongod.exe --dbpath=<database_path>

Very similarly, in Linux after installing mongoDB support run

.. code:: bash

    mongod --dbpath=<database_path>



Regarding tests
=======================

.. warning:: To be able to run tests, we need a mongoDB server to connect to (I know of no better way. If there is, please let me know). The tests are written assuming that a local server is running.

Then, a client is created that connects to it, creates testing databases/collections, fills them, accesses information stored, and wipes them all in the end.

Information safety
====================
The mongoDBs created are essential to be able to recover contents from the backup.

.. warning:: If they were lost, in the volumes you won't see proper filenames or extensions. Therefore although the content is indeed there, finding what you need would be, at the very least, awfully painful, if not utterly infeasable.

For that reason it is reasonable to make sure the mongoDB databases are safe,
and backed-up as frequently and redundantly as possible. I am using mongoDB hosting, and keep a local copy as well. Even periodically storing a copy with its
timestamp might be interesting, if you want to play it safe.


License
=========
This software is released under MIT license, with no warranty implied or otherwise. That said, on the sunny side a unittest is included that performs the complete backup cycle and
makes sure that the checkout is identical to the original filesystem. And ``integrityCheck`` command is available, which actually compares each backed-up file with its
counterpart in the filesystem.

