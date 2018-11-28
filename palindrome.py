def is_palindrome(word):
    """Check if a given word is a palindrome."""
    n = len(word)
    i_mid = n // 2

    # Skip middle letter if odd.
    if n % 2 == 1:
        i_mid2 = i_mid + 1
    else:
        i_mid2 = i_mid

    first_half = word[:i_mid]
    second_half = word[i_mid2:][::-1]

    return first_half == second_half


# NOTE: Could use pytest.mark.parametrize here but I don't want
#       that dependency.
def test_palindrome():
    words1 = ['tacocat', 'abba']
    words2 = ['kebab', 'babb']

    for w in words1:
        assert is_palindrome(w)

    for w in words2:
        assert not is_palindrome(w)
