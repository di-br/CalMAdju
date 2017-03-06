#!/usr/bin/env python
"""
This file is part of CalMAdju.

Copyright (C) 2016-2017 di-br@users.noreply.github.com
                        https://github.com/di-br/CalMAdju

CalMAdju is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

import sys
from calmadju.core import Core

def run(argv=sys.argv):
    """Wrapper script to run CalMAdju, adds command line interface.

    This will read all options from the command line.
    """
    import argparse

    # Parse command line options
    parser = argparse.ArgumentParser(prog=argv[0],
                                     description="Helps calibrate the micro-adjustments for your auto-focus system.",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-m", "--metric", dest="metric", type=str, default=["variance", "fft"],
                        help="sharpness metrics used for evaluation, possible values are"
                        "variance, gradient, and fft", nargs="+")
    parser.add_argument("--no-camera", dest="nocamera", action="store_true",
                        help="do not use gphoto2 to interact with camera (simply process previously "
                        "taken images)")
    parser.add_argument("--manual-setting", dest="manual", action="store_true",
                        help="change the camera's settings manually instead of trying to script it")
    parser.add_argument("-b", "--batch-mode", dest="batch", action="store_true",
                        help="run in batch mode without user interaction")
    parser.add_argument("-i", "--image_path", metavar="PATH", type=str, default="images",
                        help="path to store/read images to/from")
    parser.add_argument("-v", "--version", action="version", version="%(prog)s version: BETA",
                        help="show version")

    parser.set_defaults(path="images")
    parser.set_defaults(nocamera=False)
    parser.set_defaults(batch=False)
    parser.set_defaults(manual=False)

    args = parser.parse_args()

    # convert argument list in something Core understands
    metric_list = []
    for metric in args.metric:
        if metric.lower() == "variance":
            metric_list.append(Core.VARIANCE)
        if metric.lower() == "fft":
            metric_list.append(Core.FFT)
        if metric.lower() == "gradient":
            metric_list.append(Core.GRADIENT)

    # Run main script
    runner = Core(base_dir=args.image_path, batch_mode=args.batch, metrics=metric_list,
                  gp_cameraless_mode=args.nocamera, gp_camerasafe_mode=args.manual)
    runner.main()


if __name__ == "__main__":
    run()
