"""Files related functions.

Examples
--------
>>> import fileinfo

Find total file size for all '*py':

>>> total_size = fileinfo.get_filesize('*py')
0.073599 MB for 24 files

Find last modified '*py' in the directory:

>>> myfile = fileinfo.get_latest_file('*py')

"""
from __future__ import print_function

# STDLIB
import glob
import os


__authors__ = 'Erik Bray, Pey Lian Lim'
__organization__ = 'Space Telescope Science Institute'


def get_filesize(fileStr, verbose=True):
    """Find total file size.

    Parameters
    ----------
    fileStr : string
        Filename(s). Can have wildcard.

    verbose : bool, optional
        Print info to screen.

    Returns
    -------
    sz : float
        Total file size in MB.

    """
    sz = 0.0
    fileList = glob.glob(fileStr)
    for f in fileList:
        sz += os.path.getsize(f) * 1E-6
    if verbose:
        print('{} MB for {} files'.format(sz, len(fileList)))
    return sz


# Erik on performance of the new version:
#
# I did little bit of testing, and on an 'average' directory
# (containing a couple hundred entries) this version was about
# 2.5 times faster. Though as the directory size grows (to
# about 10000 entries) the time os.stat() takes on each file
# completely dominates the run time, and so the times for both
# versions converge.
#
# And it should be noted that in the 'average' case, although
# there was a speed-up, we are still talking on the order of
# nano-seconds, so this does not matter unless you are calling
# on thousands of directories.
#
# One side-effect, which may or may not be desired, is that if
# two files have the same mod time, it will return the one with
# the lexicographically higher filename, though this could be
# mitigated by calling it with max(..., key=lambda x: x[0]) to
# compare only the mod times and not the filenames.
#
# The reason using max() is generally faster in this case is
# because it calls into C code instead of doing a Python loop.
# Of course, in the C code it is doing pretty much the same
# thing as your Python version. So it does not make an enormous
# difference.
#
def get_latest_file(searchString):
    """Find the last modified file.

    Parameters
    ----------
    searchString : string
        Search string for the file(s) to compare.

    Returns
    -------
    fileLatest : string
        Absolute path to last modified file.

    """
    return os.path.abspath(
        max((os.stat(f).st_mtime,f) for f in glob.iglob(searchString))[1])


def get_first_found(file_list):
    """Find a list of files, given in the order of descending
    priorities, until one is found.

    Parameters
    ----------
    file_list : list of str
        List of files given in descending order.

    Returns
    -------
    f : str or `None`
        First file found in the given list.
        Returns `None` if none found.

    """
    for f in file_list:
        if os.path.exists(f):
            return f
        else:
            return find_file(file_list[1:])
