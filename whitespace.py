"""Module to handle whitespace in text files."""

# STDLIB
import os
import re
import sys


__author__ = 'Pey Lian Lim'
__organization__ = 'Space Telescope Science Institute'


def find_trailing_ws(infile, verbose=True):
    """Find occurences of trailing whitespace.

    Parameters
    ----------
    infile: str
        Input text file.

    verbose: bool
        Print extra info to screen.

    Returns
    -------
    found: bool
        True if any line has trailing whitespace.

    """
    assert os.path.exists(infile), 'Input not found.'

    n_match = 0

    with open(infile,'r') as fin:
        for i, line in enumerate(fin, 1):
            s = line.rstrip(os.linesep)
            if len(s) > 0 and re.search('\s', s[-1]):
                n_match += 1

                if verbose:
                    print '{}. Line {}: "{}\\n"'.format(n_match, i, s)
                else:
                    break  # Stop at first occurence if not verbose

    if verbose:
        print
        print 'TOTAL:', n_match, 'lines'
        print

    if n_match == 0:
        return False
    else:
        return True


def del_trailing_ws(infile, outfile):
    """Delete trailing whitespace.

    Parameters
    ----------
    infile: str
        Input text file.

    outfile: str
        Output text file.

    """
    assert infile != outfile, 'Input and output are the same.'
    assert os.path.exists(infile), 'Input not found.'

    if os.path.exists(outfile):
        do_overwrite = True
    else:
        do_overwrite = False

    fout = open(outfile,'w')

    with open(infile,'r') as fin:
        for line in fin:
            fout.write(line.rstrip() + os.linesep)

    fout.close()

    if do_overwrite:
        print outfile, 'overwritten.'
    else:
        print outfile, 'written.'


if __name__ == '__main__':
    assert len(sys.argv) == 3, 'Usage: python whitespace.py infile outfile'
    del_trailing_ws(sys.argv[1], sys.argv[2])
