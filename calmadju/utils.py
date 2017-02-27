#!/usr/bin/python
"""Utility functions commom to all modules."""

# have new print 'statements' (Python 3.0)
from __future__ import print_function

# Base directory for images taken/assessed
base_dir = ''
# Wait for user or don't
batch = False


def wait_key(print_msg="Press return to continue\n", override=False):
    '''Wait for a key press on the console.

    If batch is set to True, we return and do not wait for a key press.
    Set override to True if you want to insist on a key pressed no matter what.
    '''
    result = None

    if batch and not override:
        return result

    if print_msg:
        print(print_msg)

    raw_input()

    return result
