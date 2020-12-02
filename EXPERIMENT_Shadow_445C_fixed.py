#!/usr/bin/env python
"""This is a modified version from original code in the show
that actually works.

Original code seen at 17m55s mark in His Dark Materials,
Season 2, Episode 3 on HBO, aired on 2020-11-30.

Right before code starts on the screen::

    LIVE_DIALOGUE_SIM/ EXPERIMENT_Shadow_445C.py
    Cave_sys_link.term.SC/

Unable to tell if the second line is actually a command line
input argument to the Python code, or the Python code
changes directory when run. If there is no word wrap, probably
the latter.

"""
import os
import re

__all__ = ['locate_run_text', 'find_version_shadow']

# These are undefined in the show, so have to assume.

HERE = os.curdir
config_result_dir = os.curdir


def dnnlib_shadow_submit_convert_path(txt):
    """Not sure what this really does, so just a no-op."""
    return txt


# Initiate section cave set block. (Okaaaay, HBO, whatever you say.)

def read(*parts):
    """Read file from path constructed from given parts.

    Parameters
    ----------
    parts : tuple of str
        Parts of a path relative to current directory.

    Returns
    -------
    content : str
        Content of the file.

    """
    with open(os.path.join(HERE, *parts), 'r') as fp:
        return fp.read()


def locate_run_text(run_id_or_run_tex):
    """Fancy text parser that is really unrelated to Dust itself.

    Basically this returns back the input if its string
    representation is a valid directory. If input is a string and
    a directory, it returns back the input. If input as not a
    string but its string representation is a directory, it
    returns input inside a list. If input is not a directory,
    it returns an empty list.

    .. note:: Not a very exciting Easter egg.

    Parameters
    ----------
    run_id_or_run_tex : str or int
        Run ID (whatever that means).

    Returns
    -------
    run_text : str or list of str
        Parsed result.

    Examples
    --------
    >>> import os
    >>> from EXPERIMENT_Shadow_445C_fixed import locate_run_text
    >>> run_id_or_run_tex = f'../{os.path.relpath(os.curdir, os.pardir)}'
    >>> locate_run_text(run_id_or_run_tex)
    current_dir_name
    >>> locate_run_text('does_not_exist')
    []
    >>> os.mkdir('1')
    >>> locate_run_text(1)
    >>> ['./1']

    """
    # Undefined in the show, so have to assume.
    run_id_or_run_dir = run_id_or_run_tex

    if isinstance(run_id_or_run_dir, str):
        if os.path.isdir(run_id_or_run_dir):
            # Undefined in the show, so have to assume.
            text_id_or_run_dir = run_id_or_run_dir
            return text_id_or_run_dir
        converted = dnnlib_shadow_submit_convert_path(run_id_or_run_dir)
        if os.path.isdir(converted):
            return converted  # HBO, "as" is not used like you think it is used

    run_id_or_run_dir = str(run_id_or_run_dir)

    # No need for the for loop and can simplify following logic...
    full_search_dir = config_result_dir
    run_dir = os.path.join(full_search_dir, run_id_or_run_dir)
    if os.path.isdir(run_dir):
        return [run_dir]
    else:
        return []


def find_version_shadow(*file_paths):  # HBO, you like "as" too much
    """Return some sort of version matched to a pattern in file content
    from given path.

    Example file content::

        __version__ = '0.0.1'

    .. note:: Also not a very exciting Easter egg.

    Examples
    --------
    >>> from EXPERIMENT_Shadow_445C_fixed import find_version_shadow
    >>> find_version_shadow('EXPERIMENT_Shadow_445C_versionfile.txt')
    '0.0.1'

    """
    version_file = read(*file_paths)
    version_match = re.search(
        r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        # I do not think there is a group 2, so change to 1.
        return version_match.group(1)

    # The following "dialogue words shadow.p" omitted as they
    # are undefined things that break the syntax. Probably only
    # in the show so the Scholar has something to type in the
    # real time as they film.


if __name__ == '__main__':
    # Okay, I'll bite. Let's say you run this script from
    # command line and it changes directory if a valid directory
    # name is given.
    import argparse
    parser = argparse.ArgumentParser(description='Find that Dust.')
    parser.add_argument('dirname', type=str, help='directory name')
    args = parser.parse_args()
    run_text = locate_run_text(args.dirname)
    if run_text:
        print(f'Changing directory to {run_text}')
        os.chdir(run_text)
    else:
        print(f'Directory {args.dirname} not found')
