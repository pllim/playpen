import re

__all__ = ["generate_all", "compare_all"]


def generate_all(filename, is_init=False, as_string=True):
    """Return string with ``__all__`` to add to top of given file.
    The input file is not modified by this function.

    Parameters
    ----------
    filename : str
        Python module file to inspect.

    is_init : bool
        Set to `True` for file that is like ``__init__.py``.

    as_string : bool
        If `True`, return a dunder all string ready to be copied to file.
        Otherwise, a list of member names that are expected in dunder all.

    Returns
    -------
    all_value : str or list of str
        Depends on ``as_string`` setting above.

    """
    if is_init:
        patt = r".*import\s(.*)"
    else:
        patt = r"(def|class)\s([^_]\w*).*"
    all_list = []
    with open(filename) as fin:
        for row in fin:
            if row.startswith(" ") or row.startswith("#"):
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

    if as_string:
        all_value = f"__all__ = {repr(all_list).replace("'", "\"")}"
    else:
        all_value = all_list

    return all_value


def compare_all(moduleobj):
    """Check if module ``__all__`` has all the non-private members.

    Returns
    -------
    is_same : bool
        True if everything is fine.

    in_attr_only : list
        Found in ``moduleobj.__all__`` but not expected by
        :func:`generate_all`. This list is alphabetically
        sorted, not by order of appearance in the module.

    in_gen_only : list
        Missing from ``moduleobj.__all__`` but  expected by
        :func:`generate_all`. This list is alphabetically
        sorted, not by order of appearance in the module.

    """
    filename = moduleobj.__file__
    builtin_all = set(getattr(moduleobj, "__all__", []))
    generated_all = set(generate_all(filename, as_string=False))
    is_same = builtin_all == generated_all
    in_attr_only = sorted(builtin_all - generated_all)
    in_gen_only = sorted(generated_all - builtin_all)
    return is_same, in_attr_only, in_gen_only
