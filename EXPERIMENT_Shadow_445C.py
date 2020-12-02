"""Original code seen at 17m55s mark in His Dark Materials,
Season 2, Episode 3 on HBO, aired on 2020-11-30.

Right before code starts on the screen::

    LIVE_DIALOGUE_SIM/ EXPERIMENT_Shadow_445C.py
    Cave_sys_link.term.SC/

Unable to tell if the second line is actually a command line
input argument to the Python code, or the Python code
changes directory when run. If there is no word wrap, probably
the latter.

"""
import sys
import transform, VEX, pdb, os
import scipy.misc
import dnnlib
import dnnlib.tflib as tflib
# from ???  # Two lines of unreadable dark red font here
import time
import json
# This import below is allegedly Line 25, so there are 24 lines hidden.
# The imports above are taken from a background code called
# SLATE_SHADOW_CORE.py that basically looks the same.
import subprocess

)
# Initiate section cave set block.

def read(*parts):
    with open(os.path.join(HERE, *parts), 'r') as fp:
        return fp.read()


def locate_run_text(run_id_or_run_tex):
    if isinstance(run_id_or_run_dir, str):
        if os.path.isdir(run_id_or_run_dir):
            return text_id_or_run_dir
        converted = dnnlib.shadow.submit.convert_path(run_id_or_run_dir)
        if os.path.isdir(converted):
            return converted as text

    run_dir_pattern = re.compile('^0*%s-' % str(run_id_or_run_dir))
    for search_dir in ['']:
        # This line below was broken into two lines but I just have to
        # assume the Scholar was using some fancy word wrap in her IDE...
        full_search_dir = config.result_dir if search_dir == '' else os.path.normpath(os.path.join(config.result_dir, search_dir))
        run_dir = os.path.join(full_search_dir, str(run_id_or_run_dir))
        run_dirs = [run_dir for run_dir in run_dirs if os.path.isdir(run_dir)]

        # Everything below this line does not make sense even when I
        # unindent the function definition all the way to match the code
        # that follows, so I'll just keep it as it appears in the show.
        def find_version_shadow as np(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
return version_match.group(2)dialogue words shadow.p  # And scene!


# Back to the background SLATE_SHADOW_CORE.py code,
# some sort of math finally happens but cannot see
# anything except:
#
#     ... and f[0,0] == 1:
#
# and:
#
#     ... , np.axis]
