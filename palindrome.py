def is_palindrome(word):
    """Check if a given word is a palindrome."""

    if not isinstance(word, str):
        raise ValueError('Word must be a string')

    n = len(word)

    # Edge cases
    if n == 0:
        raise ValueError('I still need convincing that empty string '
                         'is a palindrome, Dan')
    elif n == 1:
        return True

    word = word.lower()
    i_mid = n // 2

    # Skip middle letter if odd.
    if n % 2 == 1:
        i_mid2 = i_mid + 1
    else:
        i_mid2 = i_mid

    first_half = word[:i_mid]
    second_half = word[i_mid2:][::-1]

    return first_half == second_half


# NOTE: Could use pytest here but I don't want that dependency.
def test_palindrome():
    words1 = ['a', 'GG', 'gig', 'tacocat', 'abbA']
    words2 = ['go', 'goo', 'kebab', 'babB']

    for w in words1:
        assert is_palindrome(w)

    for w in words2:
        assert not is_palindrome(w)

    try:
        is_palindrome('')
    except ValueError:
        pass
    else:
        raise AssertionError('Empty string did not raise ValueError')

    try:
        is_palindrome(1.0)
    except ValueError:
        pass
    else:
        raise AssertionError('Non-string did not raise ValueError')
