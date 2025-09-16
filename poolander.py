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
import re
import time
from collections import Counter
from glob import iglob

import numpy as np
from astropy.table import Table

__all__ = ["do_match", "match_criteria", "sneakpeek", "apply_filters"]


def do_match(fn_old, candidates_patt="jw*.csv", match_type="exact",
             max_nrows=500, verbose=True, debug=False):
    """Given pool file to replace from candidates, find best match.

    Parameters
    ----------
    fn_old : str
        Filename of the CSV to be replaced.
        Provide full path if not in working directory.

    candidates_patt : str
        Search pattern as accepted by :py:func:`glob.iglob`,
        or if a single ``.txt`` file is provided, it is assumed
        to contain a list of CSV files to match against.
        Provide full path is not in working directory.

    match_type : {'exact', 'subset'}
        Type of matching to be done for values found in shared columns:

        * ``'exact'``: Values must be the same exactly.
        * ``'subset'``: Replacement table may contain other stuff
          as long as it also contains all old values.

    max_nrows : int
        Skip candidates with more than this number of rows to avoid
        choosing a large program.

    verbose : bool
        Print informational text.

    debug : bool
        Print debugging text.

    Returns
    -------
    d_scores : :py:class:`~collections.Counter`
        Ranked matches (filenames with scores).

    d_details : dict
        Maps each possible replacement filename to full comparison
        details by common column names.

    """
    t_old = Table.read(fn_old, delimiter="|", format="ascii")
    d_scores = Counter()
    d_details = {}

    # Force uppercase column names to ensure match with inflight data.
    t_old.rename_columns(
        t_old.colnames, list(map(str.upper, t_old.colnames)))

    # Known irrelevant pools or calibration programs to ignore.
    is_cal_old, progs_to_ignore = _get_progs_to_ignore(
        t_old["EXP_TYPE"], verbose=verbose)

    if candidates_patt.endswith(".txt") and os.path.isfile(candidates_patt):
        with open(candidates_patt) as flist_in:
            fn_list = [s.strip() for s in flist_in.readlines()]
    else:
        fn_list = iglob(candidates_patt)

    if verbose:
        t_start = time.time()

    for fn_cur in fn_list:
        if fn_cur == fn_old:
            continue

        prognum = _get_prog(fn_cur)
        if prognum <= 1000 or prognum >= 10000:
            if debug:
                print(f"Skipping non-flight program {prognum}: {fn_cur}")
            continue

        ignore_this = False
        for bad_prog in progs_to_ignore:
            if bad_prog in fn_cur:
                ignore_this = True
                if debug:
                    print(f"Skipping bad program {bad_prog}: {fn_cur}")
                break
        if ignore_this:
            continue

        t_cur = Table.read(fn_cur, delimiter="|", format="ascii")

        nrows = len(t_cur)
        if nrows == 0 or nrows > max_nrows:
            if debug:
                print(f"Skipping nrows={nrows}: {fn_cur}")
            continue

        # Force uppercase column names to ensure match with input data.
        t_cur.rename_columns(
            t_cur.colnames, list(map(str.upper, t_cur.colnames)))

        is_cal_cur = _is_cal(t_cur["EXP_TYPE"])
        if is_cal_cur is not is_cal_old:
            if debug:
                print(f"Skipping {is_cal_cur}!={is_cal_old}: {fn_cur}")
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
    asn_cand_old = _unique_asn_cand_types(t_old["ASN_CANDIDATE"])
    scoreboard = {
        "ASN_CANDIDATE": 1000,
        "BAND": 500,
        "CHANNEL": 500,
        "DETECTOR": 1000,
        "EXP_TYPE": 1500,
        "FILTER": 500,
        "FXD_SLIT": 500,
        "GRATING": 500,
        "INSTRUME": 1000,
        "PATTTYPE": 500,
        "PUPIL": 500,
        "SPAT_NUM": 100,
        "SPEC_NUM": 100,
        "SUBARRAY": 100,
        "TEMPLATE": 1000,
        "TSOVISIT": 1000,
    }
    no_match_penalty = {
        "DETECTOR": 1000,
        "EXP_TYPE": 1000,
        "INSTRUME": 1000,
        "TEMPLATE": 1000,
        "TSOVISIT": 1000,
    }

    for colname in common_colnames:
        # Not useful and clutter output.
        if colname in ("FILENAME", "OBS_ID", "VISIT_ID"):
            continue

        if colname == "ASN_CANDIDATE":
            s1 = asn_cand_old
            s2 = _unique_asn_cand_types(t_candidate[colname])

        else:
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


def apply_filters(score, details, filters):
    """Filters are a list of ``(key, val)``
    where ``val`` is in one of the values.

    Examples
    --------
    >>> apply_filters(score, details, [
    ...     ('ASN_CANDIDATE', 'BACKGROUND'),
    ...     ('APERNAME', 'MIRIM_FULL_SLITCNTR'),
    ...     ('EXP_TYPE', 'MIR_LRS-FIXEDSLIT')])

    """
    matches = []

    for match_tuple in score.most_common():
        scoreboard = []
        fn = match_tuple[0]
        d = details[fn]
        for key, val in filters:
            status = False
            detail = d[key][1]
            if key == 'nrows':
                if val == detail:
                    status = True
            elif val in detail:
                status = True
            scoreboard.append(status)
        if scoreboard and np.all(scoreboard):
            matches.append(fn)

    return matches


def _unique_asn_cand_types(t_col):
    rpatt_asn_cand = r", '(\w*)'"
    output_set = set()
    for cell in t_col:
        m = re.findall(rpatt_asn_cand, cell)
        if m:
            output_set |= set(sorted(m))
    return output_set


def _is_cal(exptype_col):
    # EXP_TYPE for calibration programs.
    cal_exptype_by_ins = [
        # FGS
        "FGS_ACQ1", "FGS_ACQ2", "FGS_FINEGUIDE", "FGS_ID-IMAGE",
        "FGS_ID-STACK", "FGS_TRACK",
        # MIRI
        "MIR_4QPM", "MIR_CORONCAL", "MIR_DARKALL", "MIR_DARKIMG",
        "MIR_DARKMRS", "MIR_FLATIMAGE", "MIR_FLATIMAGE-EXT",
        "MIR_FLATMRS", "MIR_FLATMRS-EXT",
        # NIRCAM
        "NRC_DARK", "NRC_FLAT", "NRC_FOCUS", "NRC_LED", "NRC_WFSC",
        # NIRISS
        "NIS_DARK", "NIS_EXTCAL", "NIS_FOCUS", "NIS_LAMP",
        # NIRSPEC
        "NRS_AUTOFLAT", "NRS_AUTOWAVE", "NRS_CONFIRM", "NRS_DARK",
        "NRS_FOCUS", "NRS_IMAGE", "NRS_LAMP", "NRS_MIMF", "NRS_VERIFY"
    ]

    is_cal = False
    for val in exptype_col:
        if val.upper() in cal_exptype_by_ins:
            is_cal = True
            break

    return is_cal


def _get_progs_to_ignore(exptype_col, verbose=True):
    # Known irrelevant pools or calibration programs to ignore
    # for science pools.
    progs_to_ignore = ["jw0153", "jw02741", "jw04492", "jw06620"]

    is_cal = _is_cal(exptype_col)

    if is_cal:
        if verbose:
            print("Calibration pool; not ignoring any programs."
                  f"\n{sorted(set(exptype_col.tolist()))}")
        return is_cal, []  # Do not ignore any program

    if verbose:
        print(f"Science pool; ignoring {progs_to_ignore}")
    return is_cal, progs_to_ignore  # Science!


def _get_prog(fn):
    # jwNNNNN_blah_blah.csv
    return int(os.path.basename(fn)[2:7])
