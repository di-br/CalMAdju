#!/usr/bin/env python
"""Interface to CalMAdju"""

import sys
import calmadju.core as cal


def run(argv = sys.argv):
    """Command line interface to CalMAdju

    This will read all options from the command line
    """

    # parse command line options

    # run main script
    cal.main()


if __name__ == '__main__':
    """Non-interactive interface for CalMAdju

    All options are pre-set and no command line options need be given.
    This will run the script and not require a camera or user interaction,
    solely relying on existing images to test sharpness.
    """

    # set all options

    # run main script
    cal.main()
