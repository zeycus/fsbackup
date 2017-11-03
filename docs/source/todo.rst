*****
TODO
*****
1. There are several aspects in this process than are very OS-dependent. For instance:
    * Copying files
    * The systax for absolute paths
    * Extraction of volume id

    For now, I've been working on Windows, and I even had to implement at least an ugly hack (to handle +260 chars absolute paths, which
    surprisingly causes problems in Windows). I wish it worked for Linux as well, at least, that is the very first thing I'd like to do.

2. It seems not all filesystems have volume serialNumber. For that reason it seems that using disk serial numbers instead might be an improvement.
   I chose volume serialnumbers because it was easy to extract, while the drive serial number containing a volume seemed hard to get (Googled for a while,
   found no easy path). 

3. For now, the only way to retrieve information from the volumes is the ``checkout`` command, which rebuilds a folder/subfolder recursively. However, it would be
   easy to add filters to recover only files that match a given regular expression, or filter them for timestamp or other features, etc.

   Truth be told, this kind of operation is what I implemented for the case in which something *goes wrong*: content was deleted unwantingly, or the disk just crashed.
   Fortunately those events happen pretty rarely, so little effort was dedicated to the recovery of information.

4. If the ``updateVolume`` is aborted, I am not sure whether it is possible that a file could be partially written in the volume. I wonder if it could happen that, after
   such event, the system thinks that file is correctly backed-up, when it is not. I should try to provoke this event and see what happens. In that case, maybe same kind
   of *write-and-check-size* or something like that might be in order.