"""
Disk usage analysis.

:Author: Pey Lian Lim

:Organization: Space Telescope Science Institute

TODO
----
From Matt Davis (2012-03-07):

#. For dictionaries 'key in dict' is the same as 'key in dict.keys()'
   and the former doesn't involve constructing a new list.

   Response from Erik Bray (2012-03-19):

   Caveat! If you're looping over a dictionary and *deleting* keys
   within that loop, for example something like:

   >>> for key in mydict:
   >>>     if mydict[key] == 1:
   >>>         del mydict[key]

   This will not end well for you. This is because you're modifying
   the dictionary's internal list of keys while in the middle of
   looping over it, which can lead to unpredictable behavior. In
   this case you really do want a new list containing a copy of all
   the keywords. But even in that case, don't use dict.keys() -- in
   Python 3 the behavior of dict.keys() is such that it no longer
   returns a *copy* of the keys. Instead use:

   >>> for key in list(mydict):
   >>>     ...

   Calling the list() builtin with an iterable will create a new
   list from that iterable. In the case of dictionaries, iterating
   over them returns all their keys, so list(mydict) creates a new
   list containing all the keys.

   Response from Matt Davis (2012-03-19):

   I ran across dictionary views recently while browsing the
   Python docs:

   http://docs.python.org/library/stdtypes.html#dictionary-view-objects

   They are a way to have a dynamic iterator over the dictionary
   that is updated when the dictionary changes.

#. You are not really using opt parse, you might as well use sys.argv.
   Anyway, I vastly prefer argparse to optparse.

#. It looks like the pwd.getpwuid returns a namedtuple like object so
   you could say user = pwd.getpwuid(uid).pw_name instead of [0].
   Makes it a little more clear.

#. It would be nice to find a more intuitive container structure for
   the path/size info instead of the nested dictionaries, but this
   certainly works!

"""
import os, pwd, glob
from optparse import OptionParser
from collections import Counter

_VERSION = '$Id: disk_usage.py 1810 2012-03-21 15:44:03Z lim $'

def UsageByUser(parentPath, displayDirOnly=True):
    """
    Grouped by owner in descending usage.
    Also prints all directoried owned.
    Search one level down only.
    
    """   
    oneLevelDown = os.sep + '*'
    paths = glob.glob(parentPath + oneLevelDown)

    tally = Counter()
    pathByUser = {}

    for path in paths:      
        userID   = os.stat(path).st_uid
        usedByte = FindUsedByte(path)
        
        tally[userID] += usedByte

        if userID in pathByUser.keys():
            if usedByte in pathByUser[userID].keys():
                pathByUser[userID][usedByte].append(path)
            else:
                pathByUser[userID][usedByte] = [path]
        else:
            pathByUser[userID] = {usedByte:[path]}

    sortedTally = tally.most_common()

    for key,val in sortedTally:
        sortedPathSize = pathByUser[key].keys()
        sortedPathSize.sort(reverse=True)

        print FindUserName(key), '\t', MakeHumanReadable(val)
        print
        for sz in sortedPathSize:
            curPath = pathByUser[key][sz][0]
            if not displayDirOnly or os.path.isdir(curPath):
                print '\t', curPath, '\t', MakeHumanReadable(sz)
        print

def FindUserName(uid):   
    try:
        user = pwd.getpwuid(uid)[0]
    except KeyError:
        user = str(uid)
    return user

def FindUsedByte(path):
    """ http://stackoverflow.com/questions/1392413/calculating-a-directory-size-using-python """
    used_byte = 0

    if os.path.islink(path):
        return used_byte

    if os.path.isdir(path):
        for dirpath, dirnames, filenames in os.walk(path):
            for f in filenames:
                fp = os.path.join(dirpath, f)

                if os.path.islink(fp): continue
                
                used_byte += os.path.getsize(fp)
    else:
        used_byte = os.path.getsize(path)
        
    return used_byte

def MakeHumanReadable(totalByte):
    """ Disk usage human-readable string. """
    
    # Convert to nearest thousand while still >1
    numDigits = len( str(totalByte) )
    numExp    = (numDigits - 1) / 3
    divByThou = 1000 ** numExp

    # Find unit name
    if   numExp == 0:
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

    return '{:.1f} {}'.format(totalByte/divByThou, unitName)

if __name__ == '__main__':
    usageStr = 'USAGE: python disk_usage.py [options] path'
    parser = OptionParser(usageStr)   
    (opts, args) = parser.parse_args()

    assert len(args) == 1, usageStr

    dir2search = args[0]

    assert os.path.isdir(dir2search), 'ERROR: Invalid path'
    
    UsageByUser( dir2search )
