# -*- coding: utf-8 -*-
#
# File: decorators.py

__author__ = 'Ramon Bartl <ramon.bartl@googlemail.com>'
__docformat__ = 'plaintext'

import time


def runtime(func):
    """ simple runtime measurement of the called function
    """

    def decorator(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        result.update(dict(runtime=end-start))
        return result

    return decorator

# vim: set ft=python ts=4 sw=4 expandtab :
