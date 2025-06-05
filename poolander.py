"""Find matching JWST associations pool file.

Examples
--------

>>> from poolander import do_match
>>> filename_1 = '/path/to/pool_002_image_miri.csv'
>>> patt = '/another/path/to/jw*.csv'
>>> score, details = do_match(filename_1, candidates_patt=patt)
This took 9.4 seconds.

>>> score.most_common(5)
[('/path/to/jw02304_20250316t004555_pool.csv', 1620),
 ('/path/to/jw05204_20250308t202944_pool.csv', 1618),
 ('/path/to/jw06123_20250316t014216_pool.csv', 1612),
 ('/path/to/jw05842_20250316t011943_pool.csv', 1610),
 ('/path/to/jw01279_20250316t060526_pool.csv', 1607)]

>>> len(score)
771

>>> details['/path/to/jw04496_20250412t204115_pool.csv']
{'nrows': (8, 32),
 'ACT_ID': ([1, 2, 3, 4, 6], [1]),
 'APERNAME': (['MIRIM_FULL_ILLCNTR'], ['MIRIM_FULL']),
 'ASN_CANDIDATE': (["@!fmt_cand([(obsnum.value, 'OBSERVATION')])"],
  ["[('o001', 'OBSERVATION')]",
   "[('o002', 'OBSERVATION')]",
   "[('o003', 'OBSERVATION')]",
   "[('o004', 'OBSERVATION')]"]),
 'BAND': (['NULL'], ['NULL']),
 'CHANNEL': (['NULL'], ['NULL']),
 'DETECTOR': (['MIRIMAGE'], ['MIRIMAGE']),
 'DITHERID': (['NULL'], ['NULL']), ...,
}

"""
import time
from collections import Counter
from glob import iglob

from astropy.table import Table


def do_match(fn_old, candidates_patt="jw*.csv", match_type="exact",
             verbose=True):
    """Given pool file to replace from candidates, find best match.
    Match type can be exact or subset.

    """
    t_old = Table.read(fn_old, delimiter="|", format="ascii")
    d_scores = Counter()
    d_details = {}

    if verbose:
        t_start = time.time()

    for fn_cur in iglob(candidates_patt):
        if "jw02741" in fn_cur:  # Known irrelevant pools
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
        "INSTRUME": 1000,
        "DETECTOR": 500,
        "CHANNEL": 50,
        "FILTER": 10,
        "SUBARRAY": 100,
        "TSOVISIT": 5,
    }
    no_match_penalty = {
        "TEMPLATE": 1000,
    }

    for colname in common_colnames:
        s1 = set(t_old[colname].tolist())
        s2 = set(t_candidate[colname].tolist())
        if ((match_type == "exact" and s1 == s2) or
                (match_type == "subset" and s1 <= s2)):
            score += scoreboard.get(colname, 1)
        else:
            score -= no_match_penalty.get(colname, 1)
        details[colname] = (sorted(s1), sorted(s2))

    return score, details
