from __future__ import print_function

# STDLIB
import os
import random


def scramble_codes(code, print_to_screen=True, seed=None):
    """
    Scramble code for Software Carpentry instructors to give
    to students for exercise.

    This function can also print the scrambled code directly on screen
    for copy-and-paste into teaching material (e.g., Jupyter notebook).

    Parameters
    ----------
    code : str
        A string literal of the code snippet.

    seed : int, optional
        Give a random seed if you want reproducible result.

    Returns
    -------
    scrambled_code : str
        Scrambled code snippet with indentation removed.

    """
    s_list = []
    for s in code.split(os.linesep):
        s2 = s.lstrip()  # Remove indentation
        if len(s2) > 0:  # Exclude blank lines
            s_list.append(s2)

    # Shuffle and rejoin the lines
    rng = random.Random(seed)
    rng.shuffle(s_list)
    scrambled_code = os.linesep.join(s_list)

    if print_to_screen:
        print(scrambled_code)

    return scrambled_code


def test_scramble_codes():
    """
    Test for :func:`scramble_codes`.
    """
    code = """
    i = 0
    while i < 10:
        print(i)
        i += 1
    """
    answer = 'while i < 10:\nprint(i)\ni = 0\ni += 1'
    scrambled_code = scramble_codes(code, print_to_screen=False, seed=1234)
    assert scrambled_code == answer
