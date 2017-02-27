#!/usr/bin/env python
"""Interface to CalMAdju"""

import sys
import calmadju.core as cal


def run(argv = sys.argv):
    """Command line interface to CalMAdju

    This will read all options from the command line
    """
    import utils
    import gphoto

    # Set path to images
    utils.base_dir = 'images'
    # Disable automatic camera changes
    gphoto.auto_cam = False

    # Parse command line options

    # Run main script
    cal.main()


if __name__ == '__main__':
    """Non-interactive interface for CalMAdju

    All options are pre-set and no command line options need be given.
    This will run the script and not require a camera or user interaction,
    solely relying on existing images to test sharpness.
    """
    import utils
    import gphoto

    # Set all options

    # Set path to images
    utils.base_dir = 'images'

    # Disable camera detection and disable automatic adjustment setting
    #   This will have no real effect, since no gphoto calls should be made
    #   anyway, remember, we want a dry-run
    gphoto.auto_cam = False

    # Run main script
    cal.main()
