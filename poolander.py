"""Find matching JWST associations pool file.

Examples
--------

>>> from poolander import do_match, sneakpeek
>>> filename_1 = '/path/to/pool_002_image_miri.csv'
>>> patt = '/another/path/to/jw*.csv'
>>> score, details = do_match(filename_1, candidates_patt=patt)
This took 10.0 seconds.

>>> score.most_common(5)
[('/another/path/to/jw05204_20250308t202944_pool.csv', 6560),
 ('/another/path/to/jw06123_20250316t014216_pool.csv', 6554),
 ('/another/path/to/jw05842_20250316t011943_pool.csv', 6552),
 ('/another/path/to/jw04093_20250316t063820_pool.csv', 6540),
 ('/another/path/to/jw01052_20250316t101635_pool.csv', 6533)]

>>> len(score)
771

>>> details['/another/path/to/jw05204_20250308t202944_pool.csv']
{nrows': (8, 28),
 'ACT_ID': ([1, 2, 3, 4, 6], ['01', '03', '05', '07', '09', '0B', '0D']),
 'APERNAME': (['MIRIM_FULL_ILLCNTR'], ['MIRIM_FULL']),
 'ASN_CANDIDATE': (["@!FMT_CAND([(OBSNUM.VALUE, 'OBSERVATION')])"],
  ["[('O001', 'OBSERVATION'), ('C1000', 'GROUP'), ('C1001', 'GROUP')]"]),
 'BAND': (['NULL'], ['NULL']),
 'CHANNEL': (['NULL'], ['NULL']),
 'DETECTOR': (['MIRIMAGE'], ['MIRIMAGE']),
 'DITHERID': (['NULL'], [1]), ...,
}

>>> sneakpeek(score, details, 'nrows', most_common=5)
{'original': 8,
 'jw05204_20250308t202944_pool.csv': 28,
 'jw06123_20250316t014216_pool.csv': 36,
 'jw05842_20250316t011943_pool.csv': 36,
 'jw04093_20250316t063820_pool.csv': 48,
 'jw01052_20250316t101635_pool.csv': 57}

"""
import os
import time
from collections import Counter
from glob import iglob

import numpy as np
from astropy.table import Table

__all__ = ["do_match", "match_criteria", "sneakpeek"]


def do_match(fn_old, candidates_patt="jw*.csv", match_type="exact",
             verbose=True):
    """Given pool file to replace from candidates, find best match.
    Match type can be exact or subset.

    """
    t_old = Table.read(fn_old, delimiter="|", format="ascii")
    d_scores = Counter()
    d_details = {}

    # Known irrelevant pools or calibration programs to ignore.
    progs_to_ignore = ["jw0153", "jw02741", "jw04492", "jw06620"]

    # Force uppercase column names to ensure match with inflight data.
    t_old.rename_columns(
        t_old.colnames, list(map(str.upper, t_old.colnames)))

    if verbose:
        t_start = time.time()

    for fn_cur in iglob(candidates_patt):
        ignore_this = False
        for bad_prog in progs_to_ignore:
            if bad_prog in fn_cur:
                ignore_this = True
                break
        if ignore_this:
            continue

        t_cur = Table.read(fn_cur, delimiter="|", format="ascii")
        nrows = len(t_cur)
        if nrows == 0 or nrows > 500:
            continue
        score, details = match_criteria(t_old, t_cur, match_type=match_type)
        d_scores[fn_cur] = score
        d_details[fn_cur] = details

    if verbose:
        t_end = time.time()
        print(f"This took {t_end - t_start:.1f} seconds.")

    return d_scores, d_details


def match_criteria(t_old, t_candidate, match_type="exact"):
    """Higher number is better."""
    score = len(t_old) - len(t_candidate)
    details = {"nrows": (len(t_old), len(t_candidate))}
    common_colnames = sorted(set(t_old.colnames) & set(t_candidate.colnames))
    scoreboard = {
        "BAND": 500,
        "CHANNEL": 500,
        "DETECTOR": 1000,
        "FILTER": 500,
        "FXD_SLIT": 500,
        "GRATING": 500,
        "INSTRUME": 1000,
        "PUPIL": 500,
        "SUBARRAY": 100,
        "TEMPLATE": 1000,
        "TSOVISIT": 1000,
    }
    no_match_penalty = {
        "DETECTOR": 1000,
        "INSTRUME": 1000,
        "TEMPLATE": 1000,
        "TSOVISIT": 1000,
    }

    for colname in common_colnames:
        if t_old[colname].dtype.type is np.str_:
            c_old = list(map(str.upper, t_old[colname]))
        else:
            c_old = t_old[colname].tolist()

        if t_candidate[colname].dtype.type is np.str_:
            c_cur = list(map(str.upper, t_candidate[colname]))
        else:
            c_cur = t_candidate[colname].tolist()

        s1 = set(c_old)
        s2 = set(c_cur)
        if ((match_type == "exact" and s1 == s2) or
                (match_type == "subset" and s1 <= s2)):
            score += scoreboard.get(colname, 1)
        else:
            score -= no_match_penalty.get(colname, 1)
        details[colname] = (sorted(s1), sorted(s2))

    return score, details


def sneakpeek(score, details, key, most_common=5):
    """Quick details inspection of given key."""
    d = {}

    for match_tuple in score.most_common(most_common):
        fn = match_tuple[0]
        detail = details[fn][key]
        if "original" not in d:
            d["original"] = detail[0]
        d[os.path.basename(fn)] = detail[1]

    return d
