#!/usr/bin/env python
""" Image class to load and cut the images. """

# Have new print 'statements' (Python 3.0)
from __future__ import print_function
# We use some of OpenCV's magic (barely)
import cv2
# import os to wait for keys pressed
import os
import utils


class Image(object):
    """ A class to keep all image data and take care of loading and manipulating
    the images
    """


    def __init__(self, filename=None):
        """ Instanciate an image object, optionally loading data in the process. """

        # Keep image filename (for whatever reason)
        self.filename = filename
        # Clear reduced image data
        self.cropped_img = None
        # Either clear image data or load file
        if filename == None:
            self.img = None
        else:
            self.filename = filename
            self.safe_load_image(filename)


    def safe_load_image(self, filename):
        """ Try loading the given file. """

        # This will read the file in greyscale (argument 0)
        self.filename = os.path.join(utils.base_dir, filename)
        self.img = cv2.imread(self.filename, 0)
        # Now, instead of the above we could load the image w/
        # matplotlib and convert the resulting RGB data into
        # grayscale, thus reducing dependencies
        # https://stackoverflow.com/questions/12201577/how-can-i-convert-an-rgb-image-into-grayscale-in-python

        # Check if we really managed to load an image
        if self.img == None:
            print("\nFailed reading the last image.\nExiting\n")
            exit(1)


    def crop_image(self, x_window, y_window):
        """ Crop image to the given size. """

        height, width = self.img.shape[:2]
        x_center = width / 2
        y_center = height / 2

        self.cropped_img = self.img[y_center - y_window:y_center + y_window,
                                    x_center - x_window:x_center + x_window]
