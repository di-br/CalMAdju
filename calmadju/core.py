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
# Some maths bits and bobs we require...
import numpy as np
# ...and plotting data and images
import matplotlib.pyplot as plt
import matplotlib as mpl

from calmadju.gphoto_helper import Gphoto
from calmadju.image_helper import Image

# Turn off toolbar for matplotlib windows
mpl.rcParams["toolbar"] = "None"

GREETING = """
This will try to calibrate your autofocus (AF) micro-adjustments (MADJ)
(or at least help in finding a good value).

"""


class Core(object):
    """ Core components of CalMAdju that controls camera usage and evaluates
    pictures for sharpenss.

    We're aiming to help calibrating your camera's AF system.
    """

    # Base directory for images taken/assessed
    base_dir = ''
    # Default filename for reference image
    reference_image_filename = ""
    # Filename for currently taken and estimated image
    current_image_filename = ""
    # Start with some extent
    x_window = 0
    y_window = 0
    # Do we run in batch mode and don't ask the user to interact
    batch = False
    # Do we use gphoto2 to interact with the camera or do we stay 'safe'
    dry = True
    # Manual adjustment of camera settings
    manual = True
    # Lists for adjustments and sharpness estimates
    adjustment = []
    sharpness = []
    # Fraction of 'frequency range' (kind of, but not really) for FFT sharpness
    fraction = 0.
    # Value of best estimate for the microadjustment
    madj = 0.


    def __init__(self, base_dir="images", batch_mode=False, cameraless_mode=True,
                 camerasafe_mode=True):
        self.base_dir = base_dir
        self.reference_image_filename = "reference.jpg"
        self.current_image_filename = ""
        self.x_window = 900
        self.y_window = 600
        self.batch = batch_mode
        self.dry = cameraless_mode
        self.manual = camerasafe_mode
        self.adjustment = []
        self.sharpness = []
        self.fraction = 0.3
        self.madj = 0.
        # Now get an instance of our gphoto helper...
        self.gphoto = Gphoto(base_dir=self.base_dir, batch_mode=self.batch,
                             cameraless_mode=self.dry, camerasafe_mode=self.manual)


    @staticmethod
    def greeting():
        """ Print hello world and 'version'. """

        print(GREETING)


    def estimate_sharpness(self):
        """ Estimate sharpness of the image by looking at a contrast value
        and image gradients.
        """

        # List our score values
        score = []

        # Read file
        image = Image(self.base_dir, self.current_image_filename)
        image.crop(self.x_window, self.y_window)

        # Compute a variance measure that should prefer a contrasty result,
        # thus a sharper one
        score.append(np.mean(np.var(image.cropped_img)))

        # Compute gradients in x and y that should prefer more edges,
        # so a sharper image
        grad_y, grad_x = np.gradient(image.cropped_img, 2)
        gnorm = np.sqrt(grad_x**2 + grad_y**2)
        # Normalise to max value, in the hope of compensating lighting variations?
        gnorm = gnorm / np.max(gnorm)
        score.append(np.mean(gnorm))

        # compute fft measure
        fft = np.fft.fft2(image.cropped_img)  # It may be better to compute FFT on larger
                                            # section (to get more frequencies...)
        # Look at real part, normalise, and shift zeroth component to center
        fft_usable = np.abs(np.real(np.fft.fftshift(fft)))
        fft_usable /= np.max(fft_usable)

        # Find center of frequencies and the extent
        center_x = np.shape(fft)[0] / 2
        center_y = np.shape(fft)[1] / 2
        region_x_min = np.int(center_x - self.fraction*center_x)
        region_x_max = np.int(center_x + self.fraction*center_x)
        region_y_min = np.int(center_y - self.fraction*center_y)
        region_y_max = np.int(center_y + self.fraction*center_y)
        # Take region from center outwards, a fraction of frequencies
        score.append(np.sum(np.sqrt(fft_usable[region_x_min:region_x_max,
                                               region_y_min:region_y_max])))
        return score


    def find_center(self):
        """ Display image w/ matplotlib and have the user restrict the interesting
        area.
        """
        # TODO: add a loop to query the user for input on the interesting area
        # we have a fixed window bang in the middle right now...

        # Read file
        image = Image(self.base_dir, self.reference_image_filename)
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

        self.wait_key(override=True)
        # Here is where we prompt for alternative dimensions for the window...
        self.x_window *= 1
        self.y_window *= 1

        plt.close()


    def display_reference(self):
        """ Display reference image on lhs of a grid. """

        # Read reference file
        reference_image = Image(self.base_dir, self.reference_image_filename)
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
        current_image = Image(self.base_dir, self.current_image_filename)
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

        # TODO: make sharpness metric user-selectable
        import scipy
        from scipy.optimize import curve_fit
        from pkg_resources import parse_version

        def fit_function(x_var, amplitude, shift, width):
            """Fit function."""
            return amplitude * np.exp(-1/width * (x_var - shift)**2)

        print("Trying to fit the measured points w/ a Gaussian to determine best "
              "'region'\n")

        # Extract sharpness data
        data = np.array([self.adjustment, self.sharpness])
        minval = np.min(data[1, :])
        maxval = np.max(data[1, :])

        try:
            if parse_version(scipy.version.version) == parse_version("0.18.0"):
                # yet to be tested
                popt, pcov = curve_fit(fit_function,
                                       data[0, :], data[1, :],
                                       p0=[maxval, 0, 1],
                                       bounds=([0, np.min(data[0, :]), 1e-6],
                                               [2*maxval, np.max(data[0, :]), 1.]))
            else:
                popt, pcov = curve_fit(fit_function,
                                       data[0, :], data[1, :],
                                       p0=[maxval, 0, 1])
        except ValueError:
            print("Something went wrong with the measured values, fit not possible")
            return 0
        except RuntimeError:
            print("The fit did not converge.\n\nAre the images usable? Does the sharpness"
                  "estimate indicate no real change in sharpness? In any case,"
                  "the fit is not possible")
            return 0
        #except OptimizeWarning:
        #    print("The fit did not return proper covariance values, so results may"
        #          "be fishy. Check the plot")

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
                 x_data2, fit_function(x_data2, popt[0], popt[1], popt[2]), "k",
                 int(popt[1]), fit_function(int(popt[1]), popt[0], popt[1], popt[2]), "ro")
        plt.ylim([minval * .9, maxval * 1.1])
        plt.draw()

        return int(popt[1])


    def wait_key(self, print_msg="Press return to continue\n", override=False):
        '''Wait for a key press on the console.

        If batch is set to True, we return and do not wait for a key press.
        Set override to True if you want to insist on a key pressed no matter what.
        '''
        result = None

        if self.batch and not override:
            return result

        if print_msg:
            print(print_msg)

        raw_input()

        return result


    ################################################
    def main(self):
        """ Main function running the micro adjustment testing. """

        self.greeting()

        self.gphoto.check_version()
        self.gphoto.find_camera()
        self.gphoto.prepare_camera()

        # Take a reference image
        print("Taking a reference image")
        self.gphoto.get_image(self.reference_image_filename)

        # Show reference image and get user to adjust relevant area
        self.find_center()

        # Now loop over a couple of values and evaluate image sharpness,
        # start with 0 to have a default image first
        # NOTE: we want to allow for several 'runs' to revisit some values around the
        # approximate ideal point more often, this is a TODO atm
        run = 0
        plt.ion()
        self.display_reference()

        # TODO: make values user-selectable
        for value in [-20, -15, -12, -10, -8, -6, -4, -2, 0, 2, 4, 6, 8, 10, 12, 15, 20]:
            self.gphoto.set_af_microadjustment(value)
            self.current_image_filename = "AFtest_iter_{r}_adj_{v}.jpg".format(r=run, v=value)
            self.gphoto.get_image(self.current_image_filename)
            sharpness = self.estimate_sharpness()
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

        self.wait_key()

        # Fit and find max
        self.madj = self.find_best_madj()

        self.wait_key(override=True)

        plt.show()
        plt.close()
