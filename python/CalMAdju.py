#!/usr/bin/env python
"""This module helps calibrating your camera's AF system."""

# Have new print 'statements' (Python 3.0)
from __future__ import print_function
# Use regex to do some filtering and splitting
import re
# Some maths bits and bobs we require...
import numpy as np
# ...and plotting data and images
import matplotlib.pyplot as plt
import matplotlib as mpl
# We use some of OpenCV's magic (barely)
import cv2
# Import sys and os to wait for keys pressed
import sys
import os

# Check if we find the gphoto2 cdl utility
try:
    from sh import gphoto2 as gp
except ImportError:
    print("\ngphoto2 not found\n")
    exit(1)

# Turn off toolbar for matplotlib windows
mpl.rcParams['toolbar'] = 'None'

BASE_DIR = "images"

CAMERA_BANNER = """
+------------------------------------------------------------------+
| NOW YOU NEED TO SET UP YOUR CAMERA                               |
|                                                                  |
| * Put camera on a tripod with suitable distance to target        |
| * Align focal plane parallel to target, central to target        |
| * Make sure the shutter/release button does autofocus and meter  |
| * Reduce ISO value to a minimum to reduce noise                  |
| * Set image format to JPG to download suitable files             |
| * Reduce DOF to a minimum, i.e. open aperture as far as possible |
|   to have biggest impact of front/back focussing                 |
| * Ensure constant and even lighting of target                    |
+------------------------------------------------------------------+

"""

GREETING = """
This will try to calibrate your autofocus (AF) micro-adjustments (MADJ)
(or at least help in finding a good value).

Please attach your camera, switch it on, and press a key.
"""

# Set up custom parameter strings for known cameras.
# NOTE: currently only a Canon EOS 7D is known
#
# This MAY only work for one lens. Using another lens with this command only
# repeatedly crashed the camera...
CUSTOMFUNCEX = {}
CUSTOMFUNCEX['Canon EOS 7D'] = 'c4,1,3,b8,d,502,1,0,504,1,0,503,1,0,505,1,' \
'0,507,5,2,2,VALUE,2,0,512,2,0,17,513,1,1,510,1,0,514,1,0,515,1,0,50e,1,0,' \
'516,1,1,60f,1,0,'


def greeting():
    ''' Print hello world and 'version'. '''
    print(GREETING)
    wait_key("")

    return


def check_version():
    ''' Check if we have a sufficient libgphoto2 version. '''
    # Enquire gphoto2 version
    try:
        gp_version = gp("--version", _err='gp_error.log')
    except:
        print("\ngphoto2 cannot be called?\n")
        exit(1)

    for line in gp_version:
        if re.match(r"libgphoto2\s+", line, re.IGNORECASE):
            version = line.split()[1]
            version_major, version_minor, version_revision = (
                version.split(".")[:3])

    print("found gphoto2 version {0}.{1}.{2}".format(
        version_major, version_minor, version_revision))

    # We know v2.5.11 to work, so check for it
    from pkg_resources import parse_version
    if parse_version(version) < parse_version("2.5.11"):
        print("\nsorry, gphoto2 version probably too old\nexiting\n")
        exit(1)

    return


def find_camera():
    ''' Identify the attached camera and switch between manual and
    automatic microadjustment.
    '''
    try:
        gp_detect = gp("--auto-detect", _err='gp_error.log')
    except:
        print("\ncannot auto-detect cameras\n")
        exit(1)

    n_cameras = 0
    cameras = []
    for line in gp_detect:
        # Why is there a 'Loading sth usb something' message...?
        if not re.match(r"(Loadin|Model|(-)+)", line, re.IGNORECASE):
            n_cameras = n_cameras + 1
            cameras.append(line.split()[0])

    # Do we _have_ a camera?
    if n_cameras < 1:
        print("\nNo camera found!\n")
        exit(1)
    # Or more than one we don't want to deal with?
    if n_cameras >= 1:
        print("Camera(s) found:")
        for cam in cameras:
            print("\t{0}".format(cam))
        if n_cameras > 1:
            print("\nPlease attach only one camera!\n")
            exit(1)

    # Do we know the camera's custom function string?
    if cameras[0] in CUSTOMFUNCEX:
        print("We match settings for the custom functions ex call.\n")
        auto_cam = True
    else:
        print("No known settings for this camera, you will have to adjust the "
              "settings manually.\n")
        auto_cam = False

    return auto_cam, cameras


def wait_key(print_msg="Press a key when ready.\n"):
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


def prepare_camera():
    ''' Advise the user on how to set up the camera. '''
    print(CAMERA_BANNER)
    wait_key()

    return


def set_af_microadjustment(value, auto_cam, cameras):
    ''' Change the AF microadjustment, either manually (by the user) or
    automagically (for certain cameras).
    '''
    if auto_cam:
        # Change the adjustment value ourselves
        pre, post = CUSTOMFUNCEX[cameras[0]].split('VALUE')[:2]
        if value >= 0:
            hexvalue = "%02x" % value
        else:
            hexvalue = "%02x" % (256 + value)

        command = ["--set-config=customfuncex={0}{1}{2}".format(pre, hexvalue,
                                                                post)]
        gp_madj = gp(command, _out='gp_output.log', _err='gp_error.log')
    else:
        print("Please change the microadjustment level to {0} and press a "
              "key when ready".format(value))
        wait_key(None)

    return


def get_image(filename):
    ''' Capture an image and download said image. '''
    filename = os.path.join(BASE_DIR, filename)
    command = ["--filename={0}".format(filename), "--force-overwrite",
               "--capture-image-and-download"]
    try:
        gp_capture = gp(command, _out='gp_output.log', _err='gp_error.log')
    except:
        print("\nError capturing an image!\n")
        exit(1)

    return


def safe_load_image(filename):
    """Try loading the given file."""
    try:
        # This will read the file in greyscale (argument 0)
        filename = os.path.join(BASE_DIR, filename)
        img = cv2.imread(filename, 0)
        # Now, instead of the above we could load the image w/
        # matplotlib and convert the resulting RGB data into
        # grayscale, thus reducing dependencies
        # https://stackoverflow.com/questions/12201577/how-can-i-convert-an-rgb-image-into-grayscale-in-python
    except:
        print("\nfailed reading the last image\n")
        exit(1)
    return img


def crop_image(img, x_window, y_window):
    """Crop image to the given size."""
    height, width = img.shape[:2]
    x_center = width / 2
    y_center = height / 2

    reduced_img = img[y_center - y_window:y_center + y_window,
                      x_center - x_window:x_center + x_window]
    return reduced_img


def estimate_sharpness(filename, x_window, y_window):
    ''' Estimate sharpness of the image by looking at a contrast value
    and image gradients.
    '''
    # Read file
    img = safe_load_image(filename)
    reduced_img = crop_image(img, x_window, y_window)

    # Compute a variance measure that should prefer a contrasty result,
    # thus a sharper one
    score1 = np.mean(np.var(reduced_img))

    # Compute gradients in x and y that should prefer more edges,
    # so a sharper image
    gy, gx = np.gradient(reduced_img, 2)
    gnorm = np.sqrt(gx**2 + gy**2)
    # Normalise to max value, in the hope of compensating lighting variations?
    gnorm = gnorm / np.max(gnorm)
    score2 = np.mean(gnorm)

    score3 = 0.
    fraction = 0.3
    # compute fft measure
    fft = np.fft.fft2(reduced_img)  # It may be better to compute FFT on larger
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


def find_center(filename):
    ''' Display image w/ matplotlib and have the user restrict the interesting
    area.
    '''
    # Read file
    img = safe_load_image(filename)

    # Start with some extent
    x_window = 900
    y_window = 600

    # TODO: add a loop to query the user for input on the interesting area
    # we have a fixed window bang in the middle right now...
    cropped_image = crop_image(img, x_window, y_window)

    # Display
    plt.ion()
    # Show original image
    plt.subplot(1, 2, 1)
    plt.imshow(img, cmap='gray')
    plt.title('original image')
    # Show 'relevant' region
    plt.subplot(1, 2, 2)
    plt.imshow(cropped_image, cmap='gray')
    plt.title('selected region')
    plt.draw()

    wait_key()
    plt.show()
    plt.close()

    return x_window, y_window


def display_reference(filename, x_window, y_window):
    ''' Display two images side by side, also show the sharpness values we got
    so far.
    '''
    # Read reference file
    img = safe_load_image(filename)
    default_img = crop_image(img, x_window, y_window)

    # Clear 'adjusted' file
    current_img = 0. * default_img

    plt.subplot(2, 2, 1)
    plt.imshow(default_img, cmap='gray')
    plt.title('original image')
    plt.xticks([])
    plt.yticks([])
    plt.subplot(2, 2, 2)
    plt.imshow(current_img, cmap='gray')
    plt.title('microadjusted image')
    plt.xticks([])
    plt.yticks([])
    plt.draw()


def display_current(current_filename, x_window, y_window, data):
    ''' Display two images side by side, also show the sharpness values we got
    so far.
    '''
    # Read 'adjusted' file
    img = safe_load_image(current_filename)
    current_img = crop_image(img, x_window, y_window)

    # Extract sharpness data
    x_data = np.array(range(-20, 21, 1))
    y_data = x_data * 1.0
    minval = 1e6
    maxval = -1e6
    for val in x_data:
        if data[val + 20] != 0:
            y_data[val + 20] = data[val + 20]
            if data[val + 20] < minval:
                minval = data[val + 20]
            if data[val + 20] > maxval:
                maxval = data[val + 20]
        else:
            y_data[val + 20] = 0

    plt.subplot(2, 2, 2)
    plt.imshow(current_img, cmap='gray')
    plt.title('microadjusted image')
    plt.xticks([])
    plt.yticks([])
    plt.subplot(2, 2, 4)
    plt.title('sharpness values')
    plt.ylabel('sharpness')
    plt.xlabel('microadjustment')
    plt.scatter(x_data, y_data)
    plt.ylim([minval * .9, maxval * 1.1])
    plt.draw()


def find_best_madj(data):
    """Find best value by fitting a Gaussian."""
    from scipy.optimize import curve_fit

    def func(x, a, b, c):
        """Fit function."""
        return a * np.exp(-1/c * (x-b)**2)

    print("Trying to fit the measured points w/ a Gaussian to determine best "
          "'region'\n")

    # Extract sharpness data
    x_data = []
    y_data = []
    minval = 1e6
    maxval = -1.e6
    for val in range(-20, 21, 1):
        if data[val + 20] != 0:
            x_data.append(val)
            y_data.append(data[val + 20])
            if data[val + 20] < minval:
                minval = data[val + 20]
            if data[val + 20] > maxval:
                maxval = data[val + 20]

    popt, pcov = curve_fit(func, x_data, y_data, p0=[maxval, 0, 1])
    print('Parameters to the Gaussian function are: {0}'.format(popt))
    print('The best microadjustment could thus be around {0}'.
          format(int(popt[1])))

    # Now plot data and fit
    x_data2 = np.arange(-20.0, 20.0, 0.5)
    plt.subplot(2, 2, 4)
    plt.title('sharpness values')
    plt.ylabel('sharpness')
    plt.xlabel('microadjustment')
    plt.plot(x_data, y_data, 'bo',
             x_data2, func(x_data2, popt[0], popt[1], popt[2]), 'k',
             int(popt[1]), func(int(popt[1]), popt[0], popt[1], popt[2]), 'ro')
    plt.ylim([minval * .9, maxval * 1.1])
    plt.draw()

    return int(popt[1])


################################################
def main():
    """Main function running the micro adjustment testing."""
    greeting()
    check_version()
    ## UNCOMMENT FOR NON-DRY-RUN
    #auto_cam, cameras = find_camera()
    ## COMMENT FOR NON-DRY-RUN
    auto_cam = False
    ## COMMENT FOR NON-DRY-RUN
    cameras = ["test"]

    prepare_camera()

    # Take a reference image
    print("taking a reference image")
    ## UNCOMMENT FOR NON-DRY-RUN
    reference_image = 'reference.jpg'
    #get_image(reference_image)

    # Show reference image and get user to adjust relevant area
    x_window, y_window = find_center(reference_image)

    # Have empty results array
    data = np.zeros(41)

    # Now loop over a couple of values and evaluate image sharpness,
    # start with 0 to have a default image first
    # NOTE: we allow for several 'runs' to revisit some values around the
    # approximate ideal point more often, this is a TODO atm
    run = 0
    plt.ion()
    display_reference(reference_image, x_window, y_window)

    # Normalising variables
    found_norm = False
    norm = [1.0, 1.0]

    for value in [-20, -15, -12, -10, -8, -6, -4, -2, 0, 2, 4, 6, 8, 10, 12, 15, 20]:
        set_af_microadjustment(value, auto_cam, cameras)
        current_image_name = "AFtest_iter_{r}_adj_{v}.jpg".format(r=run, v=value)
        ## UNCOMMENT FOR NON-DRY-RUN
        #get_image(current_image_name)
        sharpness = estimate_sharpness(current_image_name, x_window, y_window)
        if not found_norm:
            found_norm = True
            norm = sharpness
        sharpness = [sharpness[0] / norm[0], sharpness[2] / norm[2]]
        # Keep the result, assuming both parameters are ok, so average the
        # normalised values
        data[value + 20] = np.mean(sharpness)
        # At a later stage, we should really fit both (or also the FFT one)
        # independently and compare the results...
        display_current(current_image_name, x_window, y_window, data)
        print("Sharpness {0} for adjustment {1}".format(sharpness, value))

    wait_key()

    # Fit and find max
    madj = find_best_madj(data)
    raw_input()

    wait_key()

    ##data2 = np.zeros(41)
    ### iterate 7 points around max
    ##run = 1
    ##for value in range(madj-3,madj+4,1):
    ##    set_af_microadjustment(value, auto_cam, cameras)
    ##    current_image_name = "AFtest_iter_"+str(run)+"_adj_"+str(value)+".jpg"
    ##    get_image(current_image_name)
    ##    sharpness = estimate_sharpness(current_image_name, x_window, y_window)[0]
    ##    data2[value+20] = sharpness
    ##    display_current('reference.jpg', current_image_name, x_window, y_window, data2)
    ##    print "sharpness ",sharpness," for adjustment", value
    ##
    ##wait_key()
    ##
    ### fit and find max
    ##madj = find_best_madj(data2)
    ##
    ##wait_key()
    plt.show()
    plt.close()


if __name__ == "__main__":
    main()
