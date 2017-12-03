*****
TODO
*****
1. Currently, under different SOs, different volume ids are built. It would be better to use the disk serial number always.
   That way, with little effort the backup could be made SO-independent.

2. For now, the only way to retrieve information from the volumes is the ``checkout`` command, which rebuilds a folder/subfolder recursively. However, it would be
   easy to add filters to recover only files that match a given regular expression, or filter them for timestamp or other features, etc.

   Truth be told, this kind of operation is what I implemented for the case in which something *goes wrong*: content was deleted unwantingly, or the disk just crashed.
   Fortunately those events happen pretty rarely, so little effort was dedicated to the recovery of information.
