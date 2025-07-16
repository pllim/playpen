import re

__all__ = ["generate_all"]


def generate_all(filename, is_init=False):
    """Return string with ``__all__`` to add to top of given file.
    The input file is not modified by this function.
    Set ``is_init=True`` for file that is like ``__init__.py``.

    """
    if is_init:
        patt = r".*import\s([^_]\w*).*"  # FIXME: CSV
    else:
        patt = r"(def|class)\s([^_]\w*).*"
    all_list = []
    with open(filename) as fin:
        for line in fin:
            m = re.findall(patt, line)
            if m:
                if is_init:
                    all_list.append(m[0])
                else:
                    for s in m:
                        all_list.append(s[1])

    return f"__all__ = {repr(all_list).replace("'", "\"")}"
