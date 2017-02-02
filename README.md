### ! This is a test repository !
Absolutely everything is work-in-progress and will work for me and me alone.
You're on your own and have been warned.
In particular, it may do nasty things to your camera.

It's also a test in the sense that I will learn Python as I go along. No coding style whatsoever and the clumsiest use of Python imaginable. I started out in `bash` and `gnuplot` and took it from there.

# CalMAdju
**Cal**ibrate (Auto-Focus) **M**icro-**Adju**stments

### General idea
1. Find a test target
2. Keep taking pictures while changing the micro-adjustment settings for the camera's AF
3. Try to estimate a sharpness parameter
4. Provide a guesstimate for the best setting
5. *Have sharper pictures*

### Prerequisites
1. A camera that provides adjustments for the auto-focus system to correct for front or back focussing
   (ideally per lens)
2. A supported version of gphoto2 that also supports your camera
3. A target to shoot
   (so far I've used this one [here](http://www.graphics.cornell.edu/~westin/misc/res-chart.html))
4. Stable conditions, i.e. constant lighting, a tripod, etc.
5. Some time to fiddle with the code to make it work
   (e.g. you will probably have to find/fix a suitable region within the pictures of the target)
6. Some commitment to experiement with camera-target distances, different targets, and to keep adjusting those settings (they may be hidden deep in the camera's settings and cumbersome to change)
