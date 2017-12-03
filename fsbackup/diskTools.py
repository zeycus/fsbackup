#!/usr/bin/python3.6

"""
.. module:: diskTools
    :platform: Windows, linux
    :synopsis: module with functions that provide drive and volume information

.. moduleauthor:: Miguel Garcia <zeycus@gmail.com>

"""


import os
import re
import subprocess

def genDrivesInfo():
    """Generator for drives information."""
    fields = dict(
        Index=int,
        Model=lambda x: x.replace(' ', '_'),
        Name=lambda x: x.replace(' ', '_'),
        SerialNumber=lambda x: x.replace('.', ''),  # Quitamos el punto final
        # Size=int,  # Sometimes it is empty
    )
    fieldsList = sorted(fields)  # Importante el orden alfabetico, porque wmic reordena si no.
    command = "wmic diskdrive get " + (','.join(f.lower() for f in fieldsList))
    try:
        lines = subprocess.check_output(command).decode("utf-8").split('\n')
    except FileNotFoundError:
        raise OSError("In Windows, the volume extraction is performed with 'wmic'. It could not be found.")

    headers = lines.pop(0)
    positions = [headers.index(field) for field in fieldsList] + [10**5]
    for line in lines:
        line = line.strip()
        if line:
            data = dict()
            for lft, rgt, field in zip(positions, positions[1:], fieldsList):
                transf = fields[field]
                data[field] = transf(line[lft:rgt].strip())
            yield data


def genVolumesInfo():
    """Generator for volumes information."""
    fields = dict(
        DeviceID=lambda x: x,
        VolumeSerialNumber=lambda x: x.replace(' ', '_'),
        ProviderName=lambda x: x,
    )
    fieldsList = sorted(fields)  # Importante el orden alfabetico, porque wmic reordena si no.
    command = "wmic logicaldisk get " + (','.join(f.lower() for f in fieldsList))
    lines = subprocess.check_output(command).decode("utf-8").split('\n')
    headers = lines.pop(0)
    positions = [headers.index(field) for field in fieldsList] + [10**5]
    for line in lines:
        line = line.strip()
        if line:
            data = dict()
            for lft, rgt, field in zip(positions, positions[1:], fieldsList):
                transf = fields[field]
                data[field] = transf(line[lft:rgt].strip())
            yield data


def getVolumeInfo(driveLetter):
    """Returns volume info for the given driveLetter.

    :param driveLetter: the drive letter, for instance 'C'
    :type driveLetter: str
    :rtype: dict
    """
    for info in genVolumesInfo():
        if info['DeviceID'] == driveLetter.upper() + ":":
            return info
    raise Exception("Drive %s: not mounted." % driveLetter)


def getAvailableLetter():
    """Returns the first drive letter available, for Windows."""
    for let in "HIJKLMNOPQRSTUVXYZ":
        if not(os.path.isdir("%s:\\" % let)):
            return let
    raise Exception("No drive letter seems available")


def getMountPointSerialNumberLinux(mp):
    """For the mount point of an external drive in Linux, returns the SerialNumber of the disk.

    :param mp: mount point
    :type mp: str
    :rtype: str

    For instance, if /dev/sdb is mounted on /mnt/zeycus/E321-ABCD,
    using getMountPointSerialNumberLinux('E321-ABCD') should return the disk's serialnumber.

    """
    lines = subprocess.check_output(["df" , "-h", mp]).decode("utf-8").split('\n')
    if not (lines[0].startswith("Filesystem")):
        raise OSError("Command df failed.")
    device = re.search("^(.*?)\s", lines[1]).group(1)
    udev = subprocess.Popen(["udevadm", "info", "--query=all", "--name=%s" % device],  stdout=subprocess.PIPE)
    lines = subprocess.check_output(["grep", "ID_SERIAL_SHORT"], stdin=udev.stdout).decode("utf-8").split('\n')
    udev.wait()
    return re.search("ID_SERIAL_SHORT=(\w*)$", lines[0]).group(1)


if __name__ == "__main__":
    print("Drives")
    for data in genDrivesInfo():
        print(data)
    print("Volumes")
    for data in genVolumesInfo():
        print(data)
    print("buscado:", getVolumeInfo('c'))

    avLetter = getAvailableLetter()
    print("Available: %s:" % avLetter)
