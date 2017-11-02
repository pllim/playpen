"""Disk usage analysis."""
from __future__ import division, print_function

import glob
import os
import pwd
import sys
from collections import Counter


__author__ = 'Pey Lian Lim'
__organization__ = 'Space Telescope Science Institute'


def usage_by_user(parentPath, displayDirOnly=True):
    """
    Grouped by owner in descending usage.
    Also prints all directoried owned.
    Search one level down only.

    .. todo::

        It would be nice to find a more intuitive container structure for
        the path/size info instead of the nested dictionaries, but this
        certainly works! -- Erik Bray

    """
    oneLevelDown = os.sep + '*'
    paths = glob.glob(parentPath + oneLevelDown)

    tally = Counter()
    pathByUser = {}

    for path in paths:
        userID = os.stat(path).st_uid
        usedByte = calc_dir_size(path)

        tally[userID] += usedByte

        if userID in pathByUser:
            if usedByte in pathByUser[userID]:
                pathByUser[userID][usedByte].append(path)
            else:
                pathByUser[userID][usedByte] = [path]
        else:
            pathByUser[userID] = {usedByte: [path]}

    sortedTally = tally.most_common()

    for key, val in sortedTally:
        sortedPathSize = sorted(pathByUser[key].keys(), reverse=True)

        print(username_by_uid(key), '\t', human_readable_bytes(val))
        print()
        for sz in sortedPathSize:
            curPath = pathByUser[key][sz][0]
            if not displayDirOnly or os.path.isdir(curPath):
                print('\t', curPath, '\t', human_readable_bytes(sz))
        print()


def username_by_uid(uid):
    try:
        user = pwd.getpwuid(uid).pw_name
    except KeyError:
        user = str(uid)
    return user


# http://stackoverflow.com/questions/1392413/calculating-a-directory-size-using-python
def calc_dir_size(path):
    used_byte = 0

    if os.path.islink(path):
        return used_byte

    if os.path.isdir(path):
        for dirpath, dirnames, filenames in os.walk(path):
            for f in filenames:
                fp = os.path.join(dirpath, f)

                if os.path.islink(fp):
                    continue

                used_byte += os.path.getsize(fp)
    else:
        used_byte = os.path.getsize(path)

    return used_byte


def human_readable_bytes(totalByte):
    """ Disk usage human-readable string. """

    # Convert to nearest thousand while still >1
    numDigits = len(str(totalByte))
    numExp = (numDigits - 1) // 3
    divByThou = 1000 ** numExp

    # Find unit name
    if numExp == 0:
        unitName = 'B'
    elif numExp == 1:
        unitName = 'KB'
    elif numExp == 2:
        unitName = 'MB'
    elif numExp == 3:
        unitName = 'GB'
    elif numExp == 4:
        unitName = 'TB'
    else:
        unitName = '>TB'

    return '{:.1f} {}'.format(totalByte / divByThou, unitName)


if __name__ == '__main__':
    assert len(sys.argv) == 2, 'USAGE: python disk_usage.py path'

    dir2search = sys.argv[-1]

    if not os.path.isdir(dir2search):
        raise IOError('Invalid path')

    usage_by_user(dir2search)
