"""Find matching JWST associations pool file.

Examples
--------

>>> from poolander import do_match
>>> filename_1 = '/path/to/pool_002_image_miri.csv'
>>> patt = '/another/path/to/jw*.csv'
>>> score, details = do_match(filename_1, candidates_patt=patt)
This took 9.8 seconds.

>>> score.most_common(5)
[('jw01207_20250329t220818_pool.csv', 1688),
 ('jw01309_20250329t054743_pool.csv', 1688),
 ('jw01538_20250323t143736_pool.csv', 1688),
 ('jw01227_20250329t195159_pool.csv', 1687),
 ('jw01536_20250323t233438_pool.csv', 1687)]

>>> len(score)
967

>>> details['jw01207_20250329t220818_pool.csv']
{'BAND': (['NULL'], ['NULL']),
 'CHANNEL': (['NULL'], ['NULL']),
 'DETECTOR': (['MIRIMAGE'], ['MIRIMAGE', 'NRS1', 'NRS2']),
 'DITHERID': (['NULL'], ['1', '2', 'NULL']),
 'DITHPTIN': ([1], [0, 1, 2, 3, 4]),
 'EXPOSURE': ([1], [1, 2, 3, 4]),
 'EXPSPCIN': ([1], [0, 1, 2, 3, 4, 5, 6, 7, 8]),
 'EXP_TYPE': (['MIR_IMAGE'],
  ['MIR_IMAGE', 'NRS_MSASPEC', 'NRS_MSATA', 'NRS_TACONFIRM']),
 'FILTER': (['F560W'],
  ['CLEAR',
   'F1000W',
   'F100LP',
   'F1280W',
   'F1500W',
   'F170LP',
   'F1800W',
   'F2100W',
   'F2550W',
   'F560W',
   'F770W']),
 'FXD_SLIT': (['NULL'], ['NULL']),
 'GRATING': (['NULL'], ['G140M', 'G235M', 'MIRROR', 'NULL']),
 'INSTRUME': (['MIRI'], ['MIRI', 'NIRSPEC']),
 'MODULE': (['NULL'], ['NULL']),
 'MOSTILNO': ([1, 2], [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]),
 'PATTSIZE': (['NULL'], ['NULL']),
 'PATTTYPE': (['NULL'], ['4-POINT-SETS', 'NONE', 'NULL']),
 'PATT_NUM': ([0], [0, 1, 2, 3, 4]),
 'PNTGTYPE': (['SCIENCE'], ['SCIENCE', 'TARGET_ACQUISITION']),
 'PNTG_SEQ': ([1],
  [1, ...
   32]),
 'PUPIL': (['NULL'], ['NULL']),
 'SEQ_ID': ([1], [1]),
 'SUBARRAY': (['FULL'], ['FULL']),
 'TARGETID': ([1], [1, 10, 11, 15]),
 'TARGORDN': ([1], [0, 1]),
 'TARGTYPE': (['FIXED'], ['FIXED']),
 'TEMPLATE': (['MIRI Imaging'],
  ['MIRI Imaging', 'NIRSpec MultiObject Spectroscopy']),
 'TSOVISIT': (['F'], ['F']),
 'VISIT': ([1, 2], [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]),
 'VISITGRP': ([2], [2, 3, 4, 5, 6, 7, 9, 11, 13, 15, 17])}
"""
import time
from collections import Counter
from glob import iglob

from astropy.table import Table


def do_match(fn_old, candidates_patt="jw*.csv", verbose=True):
    """Given pool file to replace from candidates, find best match."""
    t_old = Table.read(fn_old, delimiter="|", format="ascii")
    d_scores = Counter()
    d_details = {}

    if verbose:
        t_start = time.time()

    for fn_cur in iglob(candidates_patt):
        t_cur = Table.read(fn_cur, delimiter="|", format="ascii")
        if len(t_cur) == 0:
            continue
        score, details = match_criteria(t_old, t_cur)
        d_scores[fn_cur] = score
        d_details[fn_cur] = details

    if verbose:
        t_end = time.time()
        print(f"This took {t_end - t_start:.1f} seconds.")

    return d_scores, d_details


def match_criteria(t_old, t_candidate):
    """Higher number is better."""
    score = 0
    details = {}
    common_colnames = sorted(set(t_old.colnames) & set(t_candidate.colnames))
    scoreboard = {
        "INSTRUME": 1000,
        "DETECTOR": 500,
        "CHANNEL": 50,
        "FILTER": 10,
        "SUBARRAY": 100,
        "TSOVISIT": 5,
    }

    for colname in common_colnames:
        s1 = set(t_old[colname].tolist())
        s2 = set(t_candidate[colname].tolist())
        if s1 <= s2:
            score += scoreboard.get(colname, 1)
            details[colname] = (sorted(s1), sorted(s2))

    return score, details
