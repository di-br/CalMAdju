### ! This is a test repository !
Absolutely everything is work-in-progress and will work for me and me alone.
You're on your own and have been warned.
In particular, it may do nasty things to your camera.

It's also a test in the sense that I will learn Python as I go along. No coding style whatsoever and the clumsiest use of Python imaginable. I started out in `bash` and `gnuplot` and took it from there.

# CalMAdju
**Cal**ibrate (Auto-Focus) **M**icro-**Adju**stments

Some cameras allow for adjusting the [auto-focus system](http://www.the-digital-picture.com/Photography-Tips/canon-eos-dslr-autofocus-explained.aspx). As far as I can tell, the necessity for this stems from a certain variance in the manufacturing process of lenses and camera bodies where the deviation from the exact spec will lead to inaccuracies when finding the focus point. This is known as [front- or back-focussing](https://photo.stackexchange.com/questions/14437/what-do-frontfocus-and-backfocus-mean). One resource explaining this might be found [here](http://www.the-digital-picture.com/Photography-Tips/af-microadjustment-tips.aspx), another search found [this](http://www.picturecorrect.com/tips/how-to-recalibrate-your-cameras-focus/) as one possible explanation of what I'm on about (haven't read it though).

### General idea
1. Find a test target
2. Keep taking pictures while changing the micro-adjustment settings for the camera's AF
3. Try to estimate a [sharpness parameter](https://github.com/di-br/CalMAdju/blob/master/doc/How_to_estimate_the_sharpness_of_the_testshots.md)
4. Provide a guesstimate for the best setting
5. *Have sharper pictures*

All of this isn't new of course, it's simply my take on it. I found commercial software that has all the bells and whistles, but where's the fun in that?

### Prerequisites
1. A camera that provides adjustments for the auto-focus system to correct for front- or back-focussing
   (ideally per lens)
2. A (supported version of) gphoto2 that also supports your camera
3. A target to shoot
   (so far I've used this one [here](http://www.graphics.cornell.edu/~westin/misc/res-chart.html))
4. Stable conditions, i.e. constant lighting, a tripod, etc.
5. Some time to fiddle with the code to make it work
   (e.g. you will probably have to find/fix a suitable region within the pictures of the target)
6. Some commitment to experiement with camera-target distances, different targets, and to keep adjusting those settings (they may be hidden deep in the camera's settings and cumbersome to change)

## Current status
I have (had?) it working for my camera and one lens. Thanks to a recent version of gphoto2, I was able to [script the changes of the micro-adjustment settings](https://github.com/di-br/CalMAdju/blob/master/doc/How_to_find_the_custom_AF_adjustment_setting_with_gphoto2.md) (so I did not have to go though the camera's menus all the time and was instead able to sit back and enjoy 'the show').

The sharpness parameter(s) certainly are wild guesses, the setup possibly wasn't ideal, but the plots did reveal a trend in the adjustment setting. I say 'reveal a trend': it may all be noise and a foolish setting after all - tests out and about are still pending.

This shows an early screenshot with two `gnuplot` windows showing two sharpness parameters for either two focal lengths or simply two iterations of the script (can't remember, my guess is focal lengths).
![an early screenshot](https://github.com/di-br/CalMAdju/blob/master/examples/AFMADJ_01.png "an early screenshot")

The current evolution of things is shown in the next few pictures. Starting with a 'progress window' while the script is running:
![progress](https://github.com/di-br/CalMAdju/blob/master/examples/AFMADJ_02.png "progress")

A 'final status', also showing a simple minded fit the sharpness values:
![result](https://github.com/di-br/CalMAdju/blob/master/examples/AFMADJ_03.png "result")

And the final line from the script with the suggested adjustment value:
![suggestion](https://github.com/di-br/CalMAdju/blob/master/examples/AFMADJ_04.png "suggestion")
