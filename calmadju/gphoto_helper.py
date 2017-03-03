#!/usr/bin/env python
"""This module deals with the camera interaction."""

# Have new print 'statements' (Python 3.0)
from __future__ import print_function
# Use regex to do some filtering and splitting
import re
# to fiddle with file paths
import os

# Check if we find the gphoto2 cdl utility
try:
    from sh import gphoto2 as gp
except ImportError:
    print("\ngphoto2 not found\n")
    exit(1)

# Set up custom parameter strings for known cameras
# NOTE: currently only a Canon EOS 7D is known
CUSTOMFUNCEX = {}
CUSTOMFUNCEX['Canon EOS 7D'] = \
'c4,1,3,b8,d,502,1,0,504,1,0,503,1,0,505,1,0,507,5,2,2,' \
'VALUE,' \
'2,0,512,2,0,17,513,1,1,510,1,0,514,1,0,515,1,0,50e,1,0,516,1,1,60f,1,0,'

CAMERA_BANNER = """
+------------------------------------------------------------------+
| NOW YOU NEED TO SET UP YOUR CAMERA                               |
|                                                                  |
| * put camera on a tripod with suitable distance to target        |
| * align focal plane parallel to target, central to target        |
| * make sure the shutter/release button does autofocus and meter  |
| * reduce ISO value to a minimum to reduce noise                  |
| * set image format to JPG to download suitable files             |
| * reduce DOF to a minimum, i.e. open aperture as far as possible |
|   to have biggest impact of front/back focussing                 |
| * ensure constant and even lighting of target                    |
+------------------------------------------------------------------+

"""


class Gphoto(object):
    """ Class to interact with gphoto2 via the command line. """

    # Base directory for images taken/assessed
    base_dir = ''
    # Do we run in batch mode and don't ask the user to interact
    batch = False
    # Set initial values for detected camera
    dry = False
    manual = False
    auto_cam = False
    cameras = []
    n_cameras_found = 0


    def __init__(self, base_dir, batch_mode, cameraless_mode, camerasafe_mode):
        self.base_dir = base_dir
        self.batch = batch_mode
        self.dry = cameraless_mode
        self.manual = camerasafe_mode
        self.n_cameras_found = 0
        if self.manual:
            # This line will force the AF auto-set to always fail
            self.cameras.append("Test mode")
            self.auto_cam = False


    def check_version(self):
        ''' Check if we have a sufficient libgphoto2 version. '''
        if self.dry:
            return

        # Enquire gphoto2 version
        try:
            gp_version = gp("--version", _err='gp_error.log')
        except:
            print("\ngphoto2 cannot be called?\nExiting\n")
            exit(1)

        for line in gp_version:
            if re.match(r"libgphoto2\s+", line, re.IGNORECASE):
                version = line.split()[1]
                version_major, \
                version_minor, \
                version_revision = (version.split(".")[:3])

        print("Found gphoto2 version {0}.{1}.{2}".format(
              version_major, version_minor, version_revision))

        # We know v2.5.11 to work, so check for it
        from pkg_resources import parse_version
        if parse_version(version) < parse_version("2.5.11"):
            print("\nSorry, the gphoto2 version found is probably too old.\nExiting\n")
            exit(1)

        return


    def find_camera(self):
        ''' Identify the attached camera and switch between manual and
        automatic microadjustment.
        '''
        if self.dry:
            return

        self.wait_key("Please attach your camera, switch it on, and press return.")

        try:
            gp_detect = gp("--auto-detect", _err='gp_error.log')
        except:
            print("\nCannot auto-detect any cameras.\nExiting\n")
            exit(1)

        for line in gp_detect:
            # Why is there a 'Loading sth usb something' message...?
            if not re.match(r"(Loadin|Model|(-)+)", line, re.IGNORECASE):
                self.n_cameras_found = self.n_cameras_found + 1
                self.cameras.append(line.split()[0])

        # Do we _have_ a camera?
        if self.n_cameras_found < 1:
            print("\nNo camera found!\n")
            exit(1)
        # Or more than one we don't want to deal with?
        if self.n_cameras_found >= 1:
            print("Camera(s) found:")
            for cam in self.cameras:
                print("\t{0}".format(cam))
            if self.n_cameras_found > 1:
                print("\nPlease attach only one camera!\n")
                exit(1)

        # Do we know the camera's custom function string?
        # AND, do we want to change them automagically?
        if self.cameras[0] in CUSTOMFUNCEX and self.auto_cam:
            print("We match settings for the custom functions ex call\n")
            self.auto_cam = True
        else:
            print("No known settings for this camera, you will have to adjust the "
                  "settings manually\n")
            self.auto_cam = False


    def prepare_camera(self):
        ''' Advise the user on how to set up the camera. '''
        if self.dry:
            return

        print(CAMERA_BANNER)
        self.wait_key()


    def set_af_microadjustment(self, value):
        ''' Change the AF microadjustment, either manually (by the user) or
        automagically (for certain cameras).
        '''
        if self.dry:
            return

        if self.auto_cam:
            # Change the adjustment value ourselves
            pre, post = CUSTOMFUNCEX[self.cameras[0]].split('VALUE')[:2]
            if value >= 0:
                hexvalue = "%02x" % value
            else:
                hexvalue = "%02x" % (256 + value)

            command = ["--set-config=customfuncex={0}{1}{2}".format(pre, hexvalue,
                                                                    post)]
            gp_madj = gp(command, _out='gp_output.log', _err='gp_error.log')
        else:
            print("Please change the microadjustment level to {0} and press "
                  "return when ready".format(value))
            self.wait_key("")


    def get_image(self, filename):
        ''' Capture an image and download said image. '''
        if self.dry:
            return

        filename = os.path.join(self.base_dir, filename)
        command = ["--filename={0}".format(filename), "--force-overwrite",
                   "--capture-image-and-download"]
        try:
            gp_capture = gp(command, _out='gp_output.log', _err='gp_error.log')
        except:
            print("\nError capturing an image!\nExiting\n")
            exit(1)


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
