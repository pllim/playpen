import re

__all__ = ["generate_all"]


def generate_all(filename, is_init=False):
    """Return string with ``__all__`` to add to top of given file.
    The input file is not modified by this function.
    Set ``is_init=True`` for file that is like ``__init__.py``.

    """
    if is_init:
        patt = r".*import\s(.*)"
    else:
        patt = r"(def|class)\s([^_]\w*).*"
    all_list = []
    with open(filename) as fin:
        for row in fin:
            if row.startswith(" "):
                continue
            line = row.strip()
            m = re.findall(patt, line)
            if m:
                if is_init:
                    for s in m[0].split(", "):
                        if s.startswith("_"):
                            continue
                        all_list.append(s.split(" ")[0])  # Ditch comment
                else:
                    for s in m:
                        all_list.append(s[1])

    return f"__all__ = {repr(all_list).replace("'", "\"")}"
