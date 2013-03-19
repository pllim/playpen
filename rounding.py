"""Unconventional rounding of number."""

def round_odd(x):
    """Round X to nearest odd integer."""
    return int(x + 1 - x % 2)
