#!/usr/bin/python
"""This module deals with the camera interaction."""

# have new print 'statements' (Python 3.0)
from __future__ import print_function
# use regex to do some filtering and splitting
import re

from calmadju.utils import wait_key

# check if we find the gphoto2 cdl utility
try:
    from sh import gphoto2 as gp
except ImportError:
    print("\ngphoto2 not found\n")
    exit(1)

# Set up custom parameter strings for known cameras
# NOTE: currently only a Canon EOS 7D is known
CUSTOMFUNCEX = {}
CUSTOMFUNCEX['Canon EOS 7D'] = 'c4,1,3,b8,d,502,1,0,504,1,0,503,1,0,505,1,'
'0,507,5,2,2,VALUE,2,0,512,2,0,17,513,1,1,510,1,0,514,1,0,515,1,0,50e,1,0,516,1,'
'1,60f,1,0,'

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


def check_version():
    ''' Check if we have a sufficient libgphoto2 version. '''
    # enquire gphoto2 version
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

    # we know v2.5.11 to work, so check for it
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
        # why is there a 'Loading sth usb something' message...?
        if not re.match(r"(Loadin|Model|(-)+)", line, re.IGNORECASE):
            n_cameras = n_cameras + 1
            cameras.append(line.split()[0])

    # do we _have_ a camera?
    if n_cameras < 1:
        print("\nno camera found!\n")
        exit(1)
    # or more than one we don't want to deal with?
    if n_cameras >= 1:
        print("camera(s) found:")
        for cam in cameras:
            print("\t{0}".format(cam))
        if n_cameras > 1:
            print("\nplease attach only one camera!\n")
            exit(1)

    # do we know the camera's custom function string?
    if cameras[0] in CUSTOMFUNCEX:
        print("we match settings for the custom functions ex call\n")
        auto_cam = True
    else:
        print("no known settings for this camera, you will have to adjust the "
              "settings manually\n")
        auto_cam = False

    return auto_cam, cameras


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
        # change the adjustment value ourselves
        pre, post = CUSTOMFUNCEX[cameras[0]].split('VALUE')[:2]
        if value >= 0:
            hexvalue = "%02x" % value
        else:
            hexvalue = "%02x" % (256 + value)

        command = ["--set-config=customfuncex={0}{1}{2}".format(pre, hexvalue,
                                                                post)]
        gp_madj = gp(command, _out='gp_output.log', _err='gp_error.log')
    else:
        print("please change the microadjustment level to {0} and press a "
        "key when ready".format(value))
        wait_key("")

    return


def get_image(filename):
    ''' Capture an image and download said image. '''
    filename = os.path.join(BASE_DIR, filename)
    command = ["--filename={0}".format(filename), "--force-overwrite",
               "--capture-image-and-download"]
    try:
        gp_capture = gp(command, _out='gp_output.log', _err='gp_error.log')
    except:
        print("\nerror capturing an image!\n")
        exit(1)

    return
