#!/usr/bin/python
"""Utility functions commom to all modules."""

# have new print 'statements' (Python 3.0)
from __future__ import print_function
# import sys and os to wait for keys pressed
import sys
import os

# Base directory for images taken/assessed
base_dir = ''


def wait_key(print_msg="press a key when ready\n"):
    ''' Wait for a key press on the console. '''
    result = None
    return result
    if print_msg:
        print(print_msg)
    if os.name == 'nt':
        import msvcrt
        result = msvcrt.getch()
    else:
        import termios
        fileno = sys.stdin.fileno()

        oldterm = termios.tcgetattr(fileno)
        newattr = termios.tcgetattr(fileno)
        newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
        termios.tcsetattr(fileno, termios.TCSANOW, newattr)

        try:
            result = sys.stdin.read(1)
        except IOError:
            pass
        finally:
            termios.tcsetattr(fileno, termios.TCSAFLUSH, oldterm)

    return result
