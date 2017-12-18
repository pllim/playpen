"""This is module doc."""
from __future__ import print_function
import inspect

# Define this in local namespace.
locals()['_d'] = 'ddd'

# This is not supposed to be defined yet.
# reload does not reset locals, hence this check.
try:
    print(locals()['_c'])
except KeyError:
    pass
else:
    print('_c is defined before it is defined!')


def fake_func():
    print('beg')

    cur_frame = inspect.currentframe()  # This function
    parent_module = inspect.getmodule(cur_frame)  # This module

    # Same as if '_d' in locals() at module level.
    if '_d' in parent_module.__dict__:
        print(getattr(parent_module, '_d'))

    # locals()['pllim']
    print(getattr(parent_module, 'pllim', None))

    # locals()['_c'] = [...]
    setattr(parent_module, '_c', ['a', 'b', 'c'])

    print('end')


# Append to module level docstring.
def fake_doc():
    global __doc__
    if __doc__ is not None:
        __doc__ += '\n'.join(['hello', 'world'])


fake_doc()
fake_func()
print(locals()['_c'])
print(__doc__)
