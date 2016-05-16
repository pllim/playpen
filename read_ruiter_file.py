"""Read multi-line ASCII data block.

.. note:: For Dr. Ashley Ruiter.

Example data::

  1 2
  99 98 98
  0 0 0 1
  5

  3 4
  98 87 73
  1 2 2 3
  8

  7 3
  90 33 87
  3 5 1.000 7
  7

Desired output::

  1 2 99 98 98 0 0 0 1 5
  3 4 98 87 73 1 2 2 3 8
  7 3 90 33 87 3 5 1.000 7 7

Examples
--------
>>> import read_ruiter_file
>>> tab = read_ruiter_file.read('ruiter_input_yikes.txt')
>>> tab
<Table length=3>
 col_01  col_02  col_03  col_04  col_05  col_06  col_07  col_08  col_09  col_10
float64 float64 float64 float64 float64 float64 float64 float64 float64 float64
------- ------- ------- ------- ------- ------- ------- ------- ------- -------
    1.0     2.0    99.0    98.0    98.0     0.0     0.0     0.0     1.0     5.0
    3.0     4.0    98.0    87.0    73.0     1.0     2.0     2.0     3.0     8.0
    7.0     3.0    90.0    33.0    87.0     3.0     5.0     1.0     7.0     7.0
>>> tab.write('ruiter_input_yay.txt', format='ascii')

See Also
--------
http://docs.astropy.org/en/stable/io/ascii/
http://docs.astropy.org/en/stable/table/
http://docs.astropy.org/en/stable/io/unified.html#built-in-table-readers-writers

"""
# Python 2/3 compatibility
from __future__ import absolute_import, division, print_function

# Third-party software
import numpy as np
from astropy.io import ascii
from astropy.io.ascii.core import BaseInputter


class RuiterInputter(BaseInputter):
    """Turn multi-line data block into single-line columns."""

    def process_lines(self, lines):
        """Process the lines in given input file."""
        outlines = []  # Stores parsed output to be returned
        outstr = ''  # Stores temporarily parsed current line

        # NOTE: This does not work properly if FIRST ROW is empty row.
        for line in lines:
            cols = line.split()

            if len(cols) == 0:  # Empty row = start of new data block
                outlines.append(outstr)  # Store old block for output
                outstr = ''  # Reset temporary variable
            else:
                if outstr:  # Append = add extra whitespace in front
                    outstr += ' '
                outstr += ' '.join(cols)

        # NOTE: This does not work properly if there are extra empty rows
        #       at the end of file.
        # Append the last data block.
        outlines.append(outstr)

        return outlines


def read(inputfile):
    """Read the given input file and return parsed Astropy Table."""

    # NOTE: You can replace this with meaningful column names if you want.
    colnames = ['col_01', 'col_02', 'col_03', 'col_04', 'col_05',
                'col_06', 'col_07', 'col_08', 'col_09', 'col_10']

    # NOTE: You can change the data types here for each col as you see fit.
    # ps. Tried using defaultdict magic but didn't work, not sure why.
    #     So, we have to define the dictionary explicitly here.
    # This converts everything to float. It uses INTERNAL column names.
    converters = {'col1': [ascii.convert_numpy(np.float)],
                  'col2': [ascii.convert_numpy(np.float)],
                  'col3': [ascii.convert_numpy(np.float)],
                  'col4': [ascii.convert_numpy(np.float)],
                  'col5': [ascii.convert_numpy(np.float)],
                  'col6': [ascii.convert_numpy(np.float)],
                  'col7': [ascii.convert_numpy(np.float)],
                  'col8': [ascii.convert_numpy(np.float)],
                  'col9': [ascii.convert_numpy(np.float)],
                  'col10': [ascii.convert_numpy(np.float)]}

    tab = ascii.read(inputfile, format='no_header', guess=False,
                     Inputter=RuiterInputter, data_start=0, names=colnames,
                     converters=converters)

    # Now you can science with this data!
    return tab
