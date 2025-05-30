"""Find matching JWST associations pool file.

Examples
--------

>>> from poolander import do_match
>>> filename_1 = '/path/to/pool_002_image_miri.csv'
>>> patt = '/another/path/to/jw*.csv'
>>> score, details = do_match(filename_1, candidates_patt=patt)
This took 9.4 seconds.

>>> score.most_common(5)
[('/path/to/jw04496_20250412t204115_pool.csv', 1687),
 ('/path/to/jw04762_20250311t142127_pool.csv', 1687),
 ('/path/to/jw06809_20250316t040349_pool.csv', 1687),
 ('/path/to/jw01293_20250321t150225_pool.csv', 1686),
 ('/path/to/jw01349_20250319t131303_pool.csv', 1686)]

>>> len(score)
772

>>> details['/path/to/jw04496_20250412t204115_pool.csv']
{'nrows': (8, 433),
 'BAND': (['NULL'], ['LONG', 'MEDIUM', 'NULL', 'SHORT']),
 'CHANNEL': (['NULL'], ['12', '34', 'LONG', 'NULL', 'SHORT']),
 'DETECTOR': (['MIRIMAGE'],
  ['MIRIFULONG',
   'MIRIFUSHORT',
   'MIRIMAGE',
   'NIS',
   'NRCA2',
   'NRCA3',
   'NRCA4',
   'NRCALONG',
   'NRCB1',
   'NRCBLONG',
   'NRS1',
   'NRS2']),
 'DITHERID': (['NULL'], ['1', 'NULL']),
 'DITHPTIN': ([1], [0, 1, 2, 3, 4, 5]),
 'EXPOSURE': ([1], [1, 2, 3, 4, 5]),
 'EXPSPCIN': ([1], [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]),
 'EXP_TYPE': (['MIR_IMAGE'],
  ['MIR_CORONCAL',
   'MIR_IMAGE',
   'MIR_LRS-FIXEDSLIT',
   'MIR_LRS-SLITLESS',
   'MIR_MRS',
   'MIR_TACONFIRM',
   'MIR_TACQ',
   'NIS_IMAGE',
   'NRC_CORON',
   'NRC_IMAGE',
   'NRC_TACQ',
   'NRS_FIXEDSLIT',
   'NRS_TACONFIRM',
   'NRS_WATA']),
 'FILTER': (['F560W'],
  ['CLEAR',
   'F070W',
   'F090W',
   'F1000W',
   'F110W',
   'F1130W',
   'F115W',
   'F1280W',
   'F1500W',
   'F150W',
   'F1550C',
   'F1800W',
   'F182M',
   'F200W',
   'F2100W',
   'F210M',
   'F212N',
   'F2300C',
   'F2550W',
   'F277W',
   'F335M',
   'F356W',
   'F410M',
   'F430M',
   'F444W',
   'F460M',
   'F480M',
   'F560W',
   'F770W',
   'FND',
   'NULL',
   'P750L']),
 'FXD_SLIT': (['NULL'], ['NULL', 'S1600A1']),
 'GRATING': (['NULL'], ['MIRROR', 'NULL', 'PRISM']),
 'INSTRUME': (['MIRI'], ['MIRI', 'NIRCAM', 'NIRISS', 'NIRSPEC']),
 'MODULE': (['NULL'], ['A', 'B', 'NULL']),
 'MOSTILNO': ([1, 2], [0, 1, 2, 3, 4]),
 'PATTSIZE': (['NULL'], ['LARGE', 'NULL']),
 'PATTTYPE': (['NULL'],
  ['2-POINT',
   '4-POINT',
   '4-POINT-SETS',
   '5-POINT-NOD',
   'ALONG-SLIT-NOD',
   'CYCLING',
   'IMAGING',
   'NONE',
   'NULL',
   'SUBARRAY_DITHER']),
 'PATT_NUM': ([0], [0, 1, 2, 3, 4, 5]),
 'PNTGTYPE': (['SCIENCE'], ['SCIENCE', 'TARGET_ACQUISITION']),
 'PNTG_SEQ': ([1],
  [1,
   2, ...,
   36]),
 'PUPIL': (['NULL'],
  ['CLEAR', 'F090W', 'F115W', 'F150W', 'F200W', 'MASKBAR', 'MASKRND', 'NULL']),
 'SEQ_ID': ([1], [1]),
 'SUBARRAY': (['FULL'],
  ['BRIGHTSKY',
   'FULL',
   'MASK1550',
   'MASKLYOT',
   'SLITLESSPRISM',
   'SUB2048',
   'SUB256',
   'SUB32',
   'SUB320A335R',
   'SUB320A430R',
   'SUB400X256ALWB',
   'SUB512',
   'SUB64',
   'SUB640A210R',
   'SUB640ASWB',
   'SUB64P',
   'SUBNDA210R',
   'SUBNDA335R',
   'SUBNDA430R',
   'SUBNDALWBL',
   'SUBNDALWBS',
   'SUBNDASWBL',
   'SUBNDASWBS']),
 'TARGETID': ([1], [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]),
 'TARGORDN': ([1], [0, 1]),
 'TARGTYPE': (['FIXED'], ['FIXED']),
 'TEMPLATE': (['MIRI Imaging'],
  ['MIRI Coronagraphic Photometric Calibration',
   'MIRI Imaging',
   'MIRI Low Resolution Spectroscopy',
   'MIRI Medium Resolution Spectroscopy',
   'NIRCam Coronagraphic Imaging',
   'NIRCam Engineering Imaging',
   'NIRCam Imaging',
   'NIRISS External Calibration',
   'NIRSpec Fixed Slit Spectroscopy']),
 'TSOVISIT': (['F'], ['F', 'T']),
 'VISITGRP': ([2], [2, 3, 4, 5, 6, 8, 10])}

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
        nrows = len(t_cur)
        if nrows == 0 or nrows > 500:
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
    details = {"nrows": (len(t_old), len(t_candidate))}
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
