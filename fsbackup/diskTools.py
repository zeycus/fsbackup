#!/usr/bin/python3.6

"""
.. module:: diskTools
    :platform: Windows
    :synopsis: module with functions that provide drive and volume information

.. moduleauthor:: Miguel Garcia <zeycus@gmail.com>

"""


import os
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
    """Returns the first drive letter available."""
    for let in "HIJKLMNOPQRSTUVXYZ":
        if not(os.path.isdir("%s:\\" % let)):
            return let
    raise Exception("No drive letter seems available")



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
