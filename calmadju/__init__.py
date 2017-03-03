#!/usr/bin/env python
"""Interface to CalMAdju"""

import sys
from calmadju.core import Core


def run(argv = sys.argv):
    """Command line interface to CalMAdju

    This will read all options from the command line
    """
    import argparse

    # Parse command line options
    parser = argparse.ArgumentParser(prog=argv[0],
                                     description="Helps calibrate the micro-adjustments for your auto-focus system.",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--no-camera", dest="nocamera", action="store_true",
                        help="do not use gphoto2 to interact with camera (simply process previously "
                        "taken images)")
    parser.add_argument("--manual-setting", dest="manual", action="store_true",
                        help="change the camera's settings manually instead of trying to script it")
    parser.add_argument("--batch-mode", dest="batch", action="store_true",
                        help="run in batch mode without user interaction")
    parser.add_argument("-i", "--image_path", metavar="path", type=str, default="images",
                        help="path to store/read images to/from")
    parser.add_argument("-v", "--version", action="version", version="%(prog)s version: ALPHA",
                        help="show version")

    parser.set_defaults(path="images")
    parser.set_defaults(nocamera=False)
    parser.set_defaults(batch=False)
    parser.set_defaults(manual=False)

    args = parser.parse_args(argv[1:])

    # Run main script
    runner = Core(base_dir=args.image_path, batch_mode=args.batch,
                  cameraless_mode=args.nocamera, camerasafe_mode=args.manual)
    runner.main()


if __name__ == "__main__":
    """Non-interactive interface for CalMAdju

    All options are pre-set and no command line options need be given.
    This will run the script and not require a camera or user interaction,
    solely relying on existing images to test sharpness.
    """

    # Set all options

    # Set path to 'images'
    # Do not wait for user interaction, batch = True
    # Disable camera detection and disable automatic adjustment setting
    #   This will have no real effect, since no gphoto calls should be made
    #   anyway, remember, we want a dry-run
    # cameraless_mode = True
    # camerasafe_mode = True

    # Run main script
    runner = Core(base_dir="images", batch_mode=True, cameraless_mode=True,
                  camerasafe_mode=True)
    runner.main()
