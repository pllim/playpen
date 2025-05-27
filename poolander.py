"""Find matching JWST associations pool file.

Examples
--------

>>> from poolander import do_match
>>> filename_1 = '/path/to/pool_002_image_miri.csv'
>>> x = do_match(filename_1)
This took 7.1 seconds.
>>> x.most_common(5)
[('jw02741_20250308t165426_pool.csv', 1681),
 ('jw06615_20250318t232341_pool.csv', 1671),
 ('jw02526_20250316t163812_pool.csv', 1669),
 ('jw04256_20250317t195600_pool.csv', 1669),
 ('jw01052_20250316t101635_pool.csv', 1668)]
>>> len(x)
967

"""
import time
from collections import Counter
from glob import iglob

from astropy.table import Table


def do_match(fn_old, candidates_patt="jw*.csv", verbose=True):
    """Given pool file to replace from candidates, find best match."""
    t_old = Table.read(fn_old, delimiter="|", format="ascii")
    d_scores = Counter()

    if verbose:
        t_start = time.time()

    for fn_cur in iglob(candidates_patt):
        t_cur = Table.read(fn_cur, delimiter="|", format="ascii")
        if len(t_cur) == 0:
            continue
        score = match_criteria(t_old, t_cur)
        d_scores[fn_cur] = score

    if verbose:
        t_end = time.time()
        print(f"This took {t_end - t_start:.1f} seconds.")

    return d_scores


def match_criteria(t_old, t_candidate):
    """Higher number is better."""
    score = 0
    common_colnames = set(t_old.colnames) & set(t_candidate.colnames)
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
        if s1 == s2:
            score += scoreboard.get(colname, 1)

    return score
