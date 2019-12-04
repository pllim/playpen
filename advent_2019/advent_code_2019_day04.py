import numpy as np


def is_possible_password(pw, min_pw=None, max_pw=None):
    if min_pw is not None and pw <= min_pw:  # Must be in range
        return False
    if max_pw is not None and pw >= max_pw:
        return False

    pw_chars = np.array([c for c in str(pw)])

    if len(pw_chars) != 6:  # Also must be 6-digit
        return False

    repeat_loc = pw_chars[1:] == pw_chars[:-1]
    if ~np.any(repeat_loc):  # Must repeat
        return False

    if np.all(repeat_loc):  # Repeating pair not unique
        return False
    idx = np.append(repeat_loc, False)
    rpt_chars = set(pw_chars[idx])
    x = np.array([np.count_nonzero(pw_chars == c) for c in rpt_chars])
    if np.all(x > 2):
        return False

    if np.any(pw_chars[1:] < pw_chars[:-1]):  # Cannot decrease
        return False

    return True


def n_possible_passwords():
    min_pw = 353096
    max_pw = 843212
    n = 0

    for pw in range(min_pw, max_pw + 1):
        if is_possible_password(pw):
            n += 1

    return n


if __name__ == '__main__':
    print(n_possible_passwords())
