#!/usr/bin/env python
"""The core module to help calibrating your camera's AF system."""

# Have new print 'statements' (Python 3.0)
from __future__ import print_function
# Some maths bits and bobs we require...
import numpy as np
# ...and plotting data and images
import matplotlib.pyplot as plt
import matplotlib as mpl

import utils
import gphoto
from image_helper import *

# Turn off toolbar for matplotlib windows
mpl.rcParams["toolbar"] = "None"

GREETING = """
This will try to calibrate your autofocus (AF) micro-adjustments (MADJ)
(or at least help in finding a good value).

"""


class Core(object):
    """ Core components of CalMAdju that controls camera usage and evaluates
    pictures for sharpenss
    """

    def __init__(self):
        # Default filename for reference image
        self.reference_image_filename = "reference.jpg"
        # Filename for currently taken and estimated image
        self.current_image_filename = ""
        # Start with some extent
        self.x_window = 900
        self.y_window = 600
        # Lists for adjustments and sharpness estimates
        self.adjustment = []
        self.sharpness = []


    @staticmethod
    def greeting():
        """ Print hello world and 'version'. """

        print(GREETING)
        return


    @staticmethod
    def estimate_sharpness(filename, x_window, y_window):
        """ Estimate sharpness of the image by looking at a contrast value
        and image gradients.
        """

        # Read file
        image = Image(filename)
        image.crop(x_window, y_window)

        # Compute a variance measure that should prefer a contrasty result,
        # thus a sharper one
        score1 = np.mean(np.var(image.cropped_img))

        # Compute gradients in x and y that should prefer more edges,
        # so a sharper image
        gy, gx = np.gradient(image.cropped_img, 2)
        gnorm = np.sqrt(gx**2 + gy**2)
        # Normalise to max value, in the hope of compensating lighting variations?
        gnorm = gnorm / np.max(gnorm)
        score2 = np.mean(gnorm)

        score3 = 0.
        fraction = 0.3
        # compute fft measure
        fft = np.fft.fft2(image.cropped_img)  # It may be better to compute FFT on larger
                                            # section (to get more frequencies...)
        # Look at real part, normalise, and shift zeroth component to center
        fft_usable = np.abs(np.real(np.fft.fftshift(fft)))
        fft_usable /= np.max(fft_usable)

        # Find center of frequencies and the extent
        center_x = np.shape(fft)[0] / 2
        center_y = np.shape(fft)[1] / 2
        region_x_min = np.int(center_x - fraction*center_x)
        region_x_max = np.int(center_x + fraction*center_x)
        region_y_min = np.int(center_y - fraction*center_y)
        region_y_max = np.int(center_y + fraction*center_y)
        # Loop from center outwards, a fraction of frequencies
        for value in np.nditer(fft_usable[region_x_min:region_x_max,
                                          region_y_min:region_y_max]):
            score3 += np.sqrt(value)

        return [score1, score2, score3]


    def find_center(self, filename):
        """ Display image w/ matplotlib and have the user restrict the interesting
        area.
        """
        # TODO: add a loop to query the user for input on the interesting area
        # we have a fixed window bang in the middle right now...

        # Read file
        image = Image(filename)
        # And crop to standard size
        image.crop(self.x_window, self.y_window)

        # Display both images
        plt.ion()

        # Show original image
        plt.subplot(1, 2, 1)
        plt.imshow(image.img, cmap="gray")
        plt.title("original image")
        # Show 'relevant' region
        plt.subplot(1, 2, 2)
        plt.imshow(image.cropped_img, cmap="gray")
        plt.title("selected region")
        plt.draw()

        plt.show()

        utils.wait_key(override=True)
        # Here is where we prompt for alternative dimensions for the window...
        self.x_window *= 1
        self.y_window *= 1

        plt.close()


    def display_reference(self):
        """ Display reference image on lhs of a grid. """

        # Read reference file
        reference_image = Image(self.reference_image_filename)
        reference_image.crop(self.x_window, self.y_window)

        plt.subplot(2, 2, 1)
        plt.imshow(reference_image.cropped_img, cmap="gray")
        plt.title("original image")
        plt.xticks([])
        plt.yticks([])
        plt.draw()


    def display_current(self):
        """ Display two images side by side, also show the sharpness values we got
        so far.
        """

        # Read 'adjusted' file
        current_image = Image(self.current_image_filename)
        current_image.crop(self.x_window, self.y_window)

        # Extract sharpness data
        data = np.array([self.adjustment, self.sharpness])
        minval = np.min(data[1, :])
        maxval = np.max(data[1, :])

        plt.subplot(2, 2, 2)
        plt.imshow(current_image.cropped_img, cmap="gray")
        plt.title("microadjusted image")
        plt.xticks([])
        plt.yticks([])
        plt.subplot(2, 2, 4)
        plt.title("sharpness values")
        plt.ylabel("estimator")
        plt.xlabel("microadjustment")
        plt.scatter(data[0, :], data[1, :])
        plt.ylim([minval * .9, maxval * 1.1])
        plt.draw()


    def find_best_madj(self):
        """ Find best value by fitting a Gaussian. """

        from scipy.optimize import curve_fit

        def func(x, a, b, c):
            """Fit function."""
            return a * np.exp(-1/c * (x-b)**2)

        print("Trying to fit the measured points w/ a Gaussian to determine best "
              "'region'\n")

        # Extract sharpness data
        data = np.array([self.adjustment, self.sharpness])
        minval = np.min(data[1, :])
        maxval = np.max(data[1, :])

        popt, pcov = curve_fit(func, data[0, :], data[1, :], p0=[maxval, 0, 1])
        print("Parameters to the Gaussian function are: {0}".format(popt))
        print("The best microadjustment could thus be around {0}".
              format(int(popt[1])))

        # Now plot data and fit
        x_data2 = np.arange(-20.0, 20.0, 0.5)
        plt.subplot(2, 2, 4)
        plt.title("sharpness values")
        plt.ylabel("estimator")
        plt.xlabel("microadjustment")
        plt.plot(data[0, :], data[1, :], "bo",
                 x_data2, func(x_data2, popt[0], popt[1], popt[2]), "k",
                 int(popt[1]), func(int(popt[1]), popt[0], popt[1], popt[2]), "ro")
        plt.ylim([minval * .9, maxval * 1.1])
        plt.draw()

        return int(popt[1])


    ################################################
    def main(self):
        """ Main function running the micro adjustment testing. """

        self.greeting()

        gphoto.check_version()
        gphoto.find_camera()
        gphoto.prepare_camera()

        # Take a reference image
        print("Taking a reference image")
        gphoto.get_image(self.reference_image_filename)

        # Show reference image and get user to adjust relevant area
        self.find_center(self.reference_image_filename)

        # Now loop over a couple of values and evaluate image sharpness,
        # start with 0 to have a default image first
        # NOTE: we want to allow for several 'runs' to revisit some values around the
        # approximate ideal point more often, this is a TODO atm
        run = 0
        plt.ion()
        self.display_reference()

        for value in [-20, -15, -12, -10, -8, -6, -4, -2, 0, 2, 4, 6, 8, 10, 12, 15, 20]:
            gphoto.set_af_microadjustment(value)
            self.current_image_filename = "AFtest_iter_{r}_adj_{v}.jpg".format(r=run, v=value)
            gphoto.get_image(self.current_image_filename)
            sharpness = self.estimate_sharpness(self.current_image_filename, self.x_window, self.y_window)
            try:
                norm
            except NameError:
                norm = sharpness

            combined_sharpness = [sharpness[0] / norm[0], sharpness[2] / norm[2]]
            # Keep the result, assuming both parameters are ok, so average the
            # normalised values
            self.adjustment.append(value)
            self.sharpness.append(np.mean(combined_sharpness))

            # At a later stage, we should really fit both (or also the FFT one)
            # independently and compare the results...
            self.display_current()
            print("Sharpness {0} for adjustment {1}".format(combined_sharpness, value))

        utils.wait_key()

        # Fit and find max
        madj = self.find_best_madj()

        utils.wait_key(override=True)

        plt.show()
        plt.close()
