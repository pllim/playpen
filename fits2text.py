"""Convert FITS to text.

Examples
--------
>>> import fits2text

Convert IMP FITS to text:

>>> fits2txt.imp2txt('w3m17171j_imp.fits', 'w3m17171j_imp.txt')

Convert SYN FITS to text:

>>> fits2txt.syn2txt('acs_f814w_005_syn.fits', 'acs_f814w_005_syn.txt')

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


def syn2txt(inputFile, outFile, ext=1):
    """Convert SYNPHOT throughput table to text.

    Parameters
    ----------
    inputFile : string
        SYNPHOT throughput table with WAVELENGTH and THROUGHPUT.

    outFile : string
        Output text table.

    ext : int, optional
        Table extension to convert.

    """
    tabdata = pyfits.getdata(inputFile, ext)

    with open(outFile, 'w') as fout:
        for w, t in zip(tabdata['WAVELENGTH'], tabdata['THROUGHPUT']):
            fout.write('{:10.3f} {:15.7E}\n'.format(w, t))
