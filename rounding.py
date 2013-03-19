"""Unconventional rounding of number."""

def round_odd(x):
    """Round X to nearest odd integer."""
    return int(round(x) + 1 - round(x % 2))
