#!/usr/bin/env python
"""Interface to CalMAdju"""

import sys
import core
import utils
import gphoto


def run(argv = sys.argv):
    """Command line interface to CalMAdju

    This will read all options from the command line
    """
    import argparse

    # Set path to images
    utils.base_dir = 'images'
    # Disable automatic camera changes
    gphoto.auto_cam = False
    # This line will force the AF auto-set to always fail
    gphoto.cameras.append('Test mode')

    # Parse command line options
    parser = argparse.ArgumentParser(prog=argv[0],
                                     description='Helps calibrate the micro-adjustments for your auto-focus system.',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--no-camera', dest='camera', action='store_true',
                        help='do not use gphoto2 to interact with camera (simply process previously '
                        'taken images)')
    parser.add_argument('--batch-mode', dest='batch', action='store_true',
                        help='run in batch mode without user interaction')
    parser.add_argument('-i', '--image_path', metavar='path', type=str, default='images',
                        help='path to store/read images to/from')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s version: ALPHA',
                        help='show version')

    parser.set_defaults(camear=True)

    args = parser.parse_args(argv[1:])

    # Wait for user interaction (aka keypress)
    if args.batch:
        utils.batch = True
    else:
        utils.batch = False
    # Use gphoto2 (and take pictures)
    if args.camera:
        gphoto.dry = True
    else:
        gphoto.dry = False

    utils.base_dir = args.image_path

    # Run main script
    runner = core.Core()
    runner.main()


if __name__ == '__main__':
    """Non-interactive interface for CalMAdju

    All options are pre-set and no command line options need be given.
    This will run the script and not require a camera or user interaction,
    solely relying on existing images to test sharpness.
    """

    # Set all options

    # Set path to images
    utils.base_dir = 'images'
    # Do not wait for user interaction
    utils.batch = True
    # Disable camera detection and disable automatic adjustment setting
    #   This will have no real effect, since no gphoto calls should be made
    #   anyway, remember, we want a dry-run
    gphoto.dry = True
    gphoto.auto_cam = False
    # This line will force the AF auto-set to always fail
    gphoto.cameras.append('Test mode')

    # Run main script
    runner = core.Core()
    runner.main()
