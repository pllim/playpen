"""Pad DESCRIP in CDBS reference files.

Examples
--------
>>> from cdbs_paddescrip import pad_dscrp
>>> pad_dscrp('BLAH')
'BLAH---------------------------------------------------------------'

"""


__author__ = 'Pey Lian Lim'
__organization__ = 'Space Telescope Science Institute'


def pad_dscrp(in_str, out_len=67, pad_char='-'):
    """Pad DESCRIP with dashes until required length is met.

    Parameters
    ----------
    in_str : string
        String to pad.

    out_len : int, optional
        The required length. CDBS default is 67 char.

    pad_char : char, optional
        Char to pad with. CDBS default is '-'.

    Returns
    -------
    out_str : string
        Padded string.

    """
    sz_str = len(in_str)

    if sz_str > out_len:    # truncate
        out_str = in_str[:out_len]
    elif sz_str < out_len:  # pad
        out_str = in_str + pad_char * (out_len - sz_str)
    else:                   # no change
        out_str = in_str

    return out_str
