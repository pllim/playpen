"""Multiprocessing.

References
----------
http://docs.python.org/library/multiprocessing.html
http://blog.doughellmann.com/2009/04/pymotw-multiprocessing-part-1.html
http://broadcast.oreilly.com/2009/04/pymotw-multiprocessing-part-2.html

"""
# STDLIB
import multiprocessing
import os

# THIRD-PARTY
import numpy as np

# STSCI
from stsci.tools import mputil


def info(title):
    out_str = '\n'.join([title, 'module name: ' + __name__])
    if hasattr(os, 'getppid'):  # only available on Unix
        out_str += '\nparent process: {}'.format(os.getppid())
    out_str += '\nprocess id: {}'.format(os.getpid())
    return out_str


def greet(name):
    print info('function greet')
    print 'hello', name


def example_1():
    print info('main line')
    p1 = multiprocessing.Process(target=greet, args=('bob', ))
    p2 = multiprocessing.Process(target=greet, args=('jane', ))
    p1.start()
    p2.start()
    p1.join()
    p2.join()


def example_2():
    print info('main line')
    pool_size = multiprocessing.cpu_count()
    jobs = [multiprocessing.Process(target=greet, args=(n,))
                                    for n in ('bob', 'jane')]
    mputil.launch_and_wait(jobs, pool_size)


def fill_arr(d, i, val):
    d[i] = val


def example_3():
    pool_size = multiprocessing.cpu_count()
    mgr = multiprocessing.Manager()
    d = mgr.dict()
    jobs = [multiprocessing.Process(target=fill_arr, args=(d, i, i), name=i)
            for i in xrange(10)]
    mputil.launch_and_wait(jobs, pool_size)

    a = np.zeros((20, 10))
    for key, val in d.items():
        a[:, key] = val

    print a


if __name__ == '__main__':
    print '****** EXAMPLE 1'
    example_1()

    print '****** EXAMPLE 2'
    example_2()

    print '****** EXAMPLE 3'
    example_3()
