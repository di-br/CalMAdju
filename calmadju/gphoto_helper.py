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
    """ Class to interact with gphoto2 via the command line.

    This module deals with the camera interaction.
    """


    def __init__(self, base_dir, batch_mode, cameraless_mode, camerasafe_mode):
        # Base directory for images taken/assessed
        self._base_dir = base_dir
        # Do we run in batch mode and don't ask the user to interact
        self._batch = batch_mode
        # Do we use gphoto2 to interact with the camera or do we stay 'safe'
        self._dry = cameraless_mode
        # Manual adjustment of camera settings
        self._manual = camerasafe_mode
        # Set initial values for detected camera
        self._auto_cam = False
        self._cameras = []
        self._n_cameras_found = 0

        if self._manual:
            # This line will force the AF auto-set to always fail
            self._cameras.append("Test mode")
            self._auto_cam = False


    def check_version(self):
        ''' Check if we have a sufficient libgphoto2 version. '''
        if self._dry:
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

        print("Found gphoto2 version {0}.{1}.{2}".\
               format(version_major, version_minor, version_revision))

        # We know v2.5.11 to work, so check for it
        from pkg_resources import parse_version
        if parse_version(version) < parse_version("2.5.11"):
            print("\nSorry, the gphoto2 version found is probably too old.\nExiting\n")
            exit(1)


    def find_camera(self):
        ''' Identify the attached camera and switch between manual and
        automatic microadjustment.
        '''
        if self._dry:
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
                self._n_cameras_found = self._n_cameras_found + 1
                self._cameras.append(line.split()[0])

        # Do we _have_ a camera?
        if self._n_cameras_found < 1:
            print("\nNo camera found!\n")
            exit(1)
        # Or more than one we don't want to deal with?
        if self._n_cameras_found >= 1:
            print("Camera(s) found:")
            for cam in self._cameras:
                print("\t{0}".format(cam))
            if self._n_cameras_found > 1:
                print("\nPlease attach only one camera!\n")
                exit(1)

        # Do we know the camera's custom function string?
        # AND, do we want to change them automagically?
        if self._cameras[0] in CUSTOMFUNCEX and self._auto_cam:
            print("We match settings for the custom functions ex call\n")
            self._auto_cam = True
        else:
            print("No known settings for this camera, you will have to adjust the "
                  "settings manually\n")
            self._auto_cam = False


    def prepare_camera(self):
        ''' Advise the user on how to set up the camera. '''
        if self._dry:
            return

        print(CAMERA_BANNER)
        self.wait_key()


    def set_af_microadjustment(self, value):
        ''' Change the AF microadjustment, either manually (by the user) or
        automagically (for certain cameras).
        '''
        if self._dry:
            return

        if self._auto_cam:
            # Change the adjustment value ourselves
            pre, post = CUSTOMFUNCEX[self._cameras[0]].split('VALUE')[:2]
            if value >= 0:
                hexvalue = "%02x" % value
            else:
                hexvalue = "%02x" % (256 + value)

            command = ["--set-config=customfuncex={0}{1}{2}".format(pre, hexvalue,
                                                                    post)]
            gp(command, _out='gp_output.log', _err='gp_error.log')
        else:
            print("Please change the microadjustment level to {0} and press "
                  "return when ready".format(value))
            self.wait_key("")


    def get_image(self, filename):
        ''' Capture an image and download said image. '''
        if self._dry:
            return

        filename = os.path.join(self._base_dir, filename)
        command = ["--filename={0}".format(filename), "--force-overwrite",
                   "--capture-image-and-download"]
        try:
            gp(command, _out='gp_output.log', _err='gp_error.log')
        except:
            print("\nError capturing an image!\nExiting\n")
            exit(1)


    def wait_key(self, print_msg="Press return to continue\n", override=False):
        '''Wait for a key press on the console.

        If batch is set to True, we return and do not wait for a key press.
        Set override to True if you want to insist on a key pressed no matter what.
        '''
        result = None

        if self._batch and not override:
            return result

        if print_msg:
            print(print_msg)

        raw_input()

        return result
