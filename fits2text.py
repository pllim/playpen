"""Convert FITS to text.

Examples
--------
>>> import fits2text

Convert IMP FITS to text:

>>> fits2txt.imp2txt('acs_wfc1_dev_imp.fits', 'acs_wfc1_dev_imp.txt')

"""
# THIRD-PARTY
import pyfits


__author__ = 'Pey Lian Lim'
__organization__ = 'Space Telescope Science Institute'


def imp2txt(inputFile, outFile, ext=1):
    """Convert IMP FITS table to text.

    Parameters
    ----------
    inputFile : string
        IMP FITS table.

    outFile : string
        Output text table.

    ext : int, optional
        Table extension to convert.

    """
    with pyfits.open(inputFile) as pf:
        tabdata = pf[ext].data

        # Write to text file (overwrite)
        with open(outFile, 'w') as fout:
            for row in tabdata:
                cols = [str(col).replace('\n', '   ') for col in row]
                fout.write('\t'.join(cols) + '\n')
