#!/usr/bin/python

# use regex to do some filtering and splitting
import re
# some maths bits and bobs we require
import numpy as np
# and plotting data and images
from matplotlib import pyplot as plt
import matplotlib as mpl
mpl.rcParams['toolbar'] = 'None'
# we use some of OpenCV's magic (barely)
import cv2
# check if we find the gphoto2 cdl utility
try:
    from sh import gphoto2 as gp
except:
    print("\ngphoto2 not found\n")
    exit(1)

def greeting():
    ''' Print hello world and 'version'. '''
    print("\nthis will try to calibrate your autofocus (AF) micro-adjustments (MADJ)")
    print("(or at least help in finding a good value)")
    print("version 0.0.1\n")

    print("please attach your camera, switch it on, and press a key\n")
    wait_key()

    return

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
            version = re.split('\s+', line)[1]
            version_major = re.split('\.', version)[0]
            version_minor = re.split('\.', version)[1]
            version_revision = re.split('\.', version)[2]

    print("found gphoto2 version "+version_major+"."+version_minor+"."+version_revision+"\n")

    # we know v2.5.11 to work, so check for it
    from pkg_resources import parse_version
    if (parse_version(version) < parse_version("2.5.11")):
        print("\nsorry, gphoto2 version probably too old\nexiting\n")
        exit(1)

    return

# set up custom parameter strings for known cameras
# NOTE: currently only a Canon EOS 7D is known
customfuncex = {}
customfuncex['Canon EOS 7D'] = 'c4,1,3,b8,d,502,1,0,504,1,0,503,1,0,505,1,0,507,5,2,2,VALUE,2,0,512,2,0,17,513,1,1,510,1,0,514,1,0,515,1,0,50e,1,0,516,1,1,60f,1,0,'

def find_camera():
    ''' Identify the attached camera and switch between manual and automatic microadjustment. '''
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
            cameras.append(re.split('(\s\s)+', line)[0])

    # do we _have_ a camera?
    if (n_cameras < 1):
        print("\nno camera found!\n")
        exit(1)
    # or more than one we don't want to deal with?
    if (n_cameras >= 1):
        print("camera(s) found:")
        for cam in cameras:
            print("\t"+cam)
        if (n_cameras > 1):
            print("\nplease attach only one camera!\n")
            exit(1)

    # do we know the camera's custom function string?
    if cameras[0] in customfuncex:
        print("we match settings for the custom functions ex call\n")
        auto_cam = True
    else:
        print("no known settings for this camera, you will have to adjust the settings manually\n")
        auto_cam = False

    return auto_cam, cameras

import sys, os
def wait_key():
    ''' Wait for a key press on the console. '''
    result = None
    if os.name == 'nt':
        import msvcrt
        result = msvcrt.getch()
    else:
        import termios
        fd = sys.stdin.fileno()

        oldterm = termios.tcgetattr(fd)
        newattr = termios.tcgetattr(fd)
        newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
        termios.tcsetattr(fd, termios.TCSANOW, newattr)

        try:
            result = sys.stdin.read(1)
        except IOError:
            pass
        finally:
            termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)

    return result

def prepare_camera():
    ''' Advise the user on how to set up the camera. '''
    print(" +------------------------------------------------------------------+")
    print(" | NOW YOU NEED TO SET UP YOUR CAMERA                               |")
    print(" |                                                                  |")
    print(" | * put camera on a tripod with suitable distance to target        |")
    print(" | * align focal plane parallel to target, central to target        |")
    print(" | * make sure the shutter/release button does autofocus and meter  |")
    print(" | * reduce ISO value to a minimum to reduce noise                  |")
    print(" | * set image format to JPG to download suitable files             |")
    print(" | * reduce DOF to a minimum, i.e. open aperture as far as possible |")
    print(" |   to have biggest impact of front/back focussing                 |")
    print(" | * ensure constant and even lighting of target                    |")
    print(" +------------------------------------------------------------------+")
    print("\n")
    print("press a key when ready\n")
    wait_key()

    return

def set_AFmicroadjustment(value, auto_cam, cameras):
    ''' Change the AF microadjustment, either manually (by the user) or automagically (for certain cameras). '''
    if auto_cam:
        # change the adjustment value ourselves
        pre = re.split('VALUE', customfuncex[cameras[0]])[0]
        if (value >= 0):
            hexvalue = "%02x" % value
        else:
            hexvalue = "%02x" % (256+value)
        post = re.split('VALUE', customfuncex[cameras[0]])[1]

        command = ["--set-config=customfuncex="+pre+hexvalue+post]
        gp_madj = gp(command, _out='gp_output.log', _err='gp_error.log')
        #print gp_madj
    else:
        print "please change the microadjustment level to ",value," and press a key when ready"
        wait_key()

    return

def get_image(filename):
    ''' Capture an image and download said image. '''
    command = ["--filename=images/"+filename,"--force-overwrite","--capture-image-and-download"]
    try:
        gp_capture = gp(command, _out='gp_output.log', _err='gp_error.log')
        #print gp_capture
    except:
        print("\nerror capturing an image!\n")
        exit(1)

    return

def estimate_sharpness(filename, x_window, y_window, switch):
    ''' Estimate sharpness of the image by looking at a contrast value (optionally image gradients). '''
    # read file
    try:
        # this will read the file in greyscale (argument 0)
        img = cv2.imread('images/'+filename,0)
    except:
        print("\nfailed reading the last image\n")
        exit(1)

    # get image dimensions and center point
    height, width = img.shape[:2]
    x_center = width/2
    y_center = height/2

    reduced_img = img[y_center-y_window:y_center+y_window,x_center-x_window:x_center+x_window]
    # start with some extent
    if not switch:
        # compute a variance measure that should provide a contrasty result
        avg_img = reduced_img.sum()/np.size(reduced_img)
        var = (img-avg_img)**2
        score = var.sum()/np.size(var)
    else:
        # compute gradients in x and y
        gy, gx = np.gradient(reduced_img,2)
        gnorm = np.sqrt(gx**2 + gy**2)
        score = np.average(gnorm)

    return score

def find_center(filename):
    ''' Display image w/ matplotlib and have the user restrict the interesting area. '''
    # read file
    try:
        # this will read the file in greyscale (argument 0)
        img = cv2.imread('images/'+filename,0)
        # now, instead of the above we could load the image w/ matplotlib and convert
        # the resulting RGB data into grayscale, thus reducing dependencies
        # https://stackoverflow.com/questions/12201577/how-can-i-convert-an-rgb-image-into-grayscale-in-python
    except:
        print("\nfailed reading the last image\n")
        exit(1)

    # get image dimensions and center point
    height, width = img.shape[:2]
    x_center = width/2
    y_center = height/2

    # start with some extent
    x_window = 900
    y_window = 600

    # display
    plt.ion()
    # show original image
    plt.subplot(1,2,1)
    plt.imshow(img, cmap = 'gray')
    plt.title('original image')
    # show 'relevant' region
    plt.subplot(1,2,2)
    plt.imshow(img[y_center-y_window:y_center+y_window,x_center-x_window:x_center+x_window], cmap = 'gray')
    plt.title('selected region')
    plt.draw()

    print("press a key when ready\n")
    wait_key()
    plt.show()
    plt.close()

    return x_window, y_window

def display_default_and_current(default_filename, current_filename, x_window, y_window, data):
    ''' Display two images side by side, also show the sharpness values we got so far. '''
    # read reference file
    try:
        # this will read the file in greyscale (argument 0)
        img = cv2.imread('images/'+default_filename,0)
    except:
        print("\nfailed reading the last image\n")
        exit(1)
    height, width = img.shape[:2]
    x_center = width/2
    y_center = height/2
    default_img = img[y_center-y_window:y_center+y_window,x_center-x_window:x_center+x_window]
    # clear 'adjusted' file
    current_img = 0. * default_img

    plt.subplot(2,2,1)
    plt.imshow(default_img, cmap = 'gray')
    plt.title('original image'), plt.xticks([]), plt.yticks([])
    plt.subplot(2,2,2)
    plt.imshow(current_img, cmap = 'gray')
    plt.title('microadjusted image'), plt.xticks([]), plt.yticks([])
    plt.draw()

def display_current(default_filename, current_filename, x_window, y_window, data):
    ''' Display two images side by side, also show the sharpness values we got so far. '''
    # read 'adjusted' file
    try:
        # this will read the file in greyscale (argument 0)
        img = cv2.imread('images/'+current_filename,0)
    except:
        print("\nfailed reading the last image\n")
        exit(1)
    height, width = img.shape[:2]
    x_center = width/2
    y_center = height/2
    current_img = img[y_center-y_window:y_center+y_window,x_center-x_window:x_center+x_window]

    # extract sharpness data
    x_data = np.array(range(-20,21,1))
    y_data = x_data*1.0
    minval = 1e6
    maxval = -1e6
    for val in x_data:
        if (data[val+20] != 0):
            y_data[val+20] = data[val+20]
            if (data[val+20] < minval):
                minval = data[val+20]
            if (data[val+20] > maxval):
                maxval = data[val+20]
        else:
            y_data[val+20] = 0

    plt.subplot(2,2,2)
    plt.imshow(current_img, cmap = 'gray')
    plt.title('microadjusted image'), plt.xticks([]), plt.yticks([])
    plt.subplot(2,2,4)
    plt.title('sharpness values')
    plt.ylabel('sharpness')
    plt.xlabel('microadjustment')
    plt.scatter(x_data, y_data)
    plt.ylim([minval*.9,maxval*1.1])
    plt.draw()

def find_best_madj(data):
    from scipy.optimize import curve_fit

    def func(x, a, b, c):
            return a * np.exp(-1/c * (x-b)**2)

    print "trying to fit the measured points w/ a Gaussian to determine best 'region'\n"

    # extract sharpness data
    x_data = []
    y_data = []
    minval = 1e6
    maxval = -1.e6
    for val in range(-20,21,1):
        if (data[val+20] != 0):
            x_data.append(val)
            y_data.append(data[val+20])
            if (data[val] < minval):
                minval = data[val+20]
            if(data[val] > maxval):
                maxval = data[val+20]

    popt, pcov = curve_fit(func, x_data, y_data, p0=[maxval, 0, 1])
    print 'parameters to the Gaussian function are: ',popt
    print 'the best microadjustment could thus be around ', int(popt[1])

    # now plot data and fit
    x_data2 = np.arange(-20.0, 20.0, 0.5)
    plt.subplot(2,2,4)
    plt.title('sharpness values')
    plt.ylabel('sharpness')
    plt.xlabel('microadjustment')
    plt.plot(x_data, y_data, 'bo', x_data2, func(x_data2, popt[0], popt[1], popt[2]), 'k')
    plt.ylim([minval*.9,maxval*1.1])
    plt.draw()

    return int(popt[1])

################################################
greeting()
check_version()
## UNCOMMENT FOR NON-DRY-RUN
#auto_cam, cameras = find_camera()
## COMMENT FOR NON-DRY-RUN
auto_cam=False
## COMMENT FOR NON-DRY-RUN
cameras = ["test"]

prepare_camera()

# take a reference image
print("taking a reference image")
## UNCOMMENT FOR NON-DRY-RUN
#get_image('reference.jpg')

# show reference image and get user to adjust relevant area
x_window, y_window = find_center('reference.jpg')

# have empty results array
data = np.zeros(41)

# now loop over a couple of values and evaluate image sharpness
# start with 0 to have a default image first
# NOTE: we allow for several 'runs' to revisit some values around the approximate ideal point more often
#       this is a TODO atm
run = 0
plt.ion()
display_default_and_current('reference.jpg', 'reference.jpg', x_window, y_window, data)

for value in [-20, -15, -12, -10, -8, -6, -4, -2, 0, 2, 4, 6, 8, 10, 12, 15, 20]:
    set_AFmicroadjustment(value, auto_cam, cameras)
    current_image_name = "AFtest_iter_"+str(run)+"_adj_"+str(value)+".jpg"
    ## UNCOMMENT FOR NON-DRY-RUN
    #get_image(current_image_name)
    sharpness = estimate_sharpness(current_image_name, x_window, y_window, False)
    # keep the result
    data[value+20] = sharpness
    display_current('reference.jpg', current_image_name, x_window, y_window, data)
    print "sharpness ",sharpness," for adjustment", value

print("press a key when ready\n")
wait_key()

# fit and find max
madj = find_best_madj(data)

print("press a key when ready\n")
wait_key()

##data2 = np.zeros(41)
### iterate 7 points around max
##run = 1
##for value in range(madj-3,madj+4,1):
##    set_AFmicroadjustment(value, auto_cam, cameras)
##    current_image_name = "AFtest_iter_"+str(run)+"_adj_"+str(value)+".jpg"
##    get_image(current_image_name)
##    sharpness = estimate_sharpness(current_image_name, x_window, y_window, False)
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
