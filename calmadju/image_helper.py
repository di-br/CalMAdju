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

# Have new print 'statements' (Python 3.0)
from __future__ import print_function
# We use some of OpenCV's magic (barely)
import cv2
# import os to wait for keys pressed
import os


class Image(object):
    """ A class to keep all image data and take care of loading and manipulating
    the images.
    """


    def __init__(self, base_dir=None, filename=None):
        """ Instantiate an image object, optionally loading data in the process.

        May take base directory (defaults to .) and filename to load image data from.
        """

        # Keep image filename (for whatever reason)
        self.filename = filename
        # Clear reduced image data
        self.cropped_img = None
        if base_dir == None:
            base_dir = "."
        # Either clear image data or load file
        if filename == None:
            self.img = None
        else:
            self.filename = filename
            self.load(base_dir, filename)


    def load(self, base_dir, filename):
        """ Try loading the given file.

        Requires base directory and filename to load image data from.
        """

        # This will read the file in greyscale (argument 0)
        self.filename = os.path.join(base_dir, filename)
        self.img = cv2.imread(self.filename, 0)
        # Now, instead of the above we could load the image w/
        # matplotlib and convert the resulting RGB data into
        # grayscale, thus reducing dependencies
        # https://stackoverflow.com/questions/12201577/how-can-i-convert-an-rgb-image-into-grayscale-in-python

        # Check if we really managed to load an image
        if self.img == None:
            print("\nFailed reading the last image.\nExiting\n")
            exit(1)


    def crop(self, x_window, y_window):
        """ Crop image to the given size.

        Takes 2 parameters: symmetric extent in x&y starting from center position.
        """

        height, width = self.img.shape[:2]
        x_center = width / 2
        y_center = height / 2

        self.cropped_img = self.img[y_center - y_window:y_center + y_window,
                                    x_center - x_window:x_center + x_window]
