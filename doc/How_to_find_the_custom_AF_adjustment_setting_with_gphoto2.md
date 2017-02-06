# Identifying the custom AF adjustment setting

## Canon

### In short

1. Use a recent gphoto2 library (ver. 2.5.11 works for me)
2. Connect your camera to your computer
3. Make use of gphoto2's debugging output to get a lot of information from your camera
4. Change the micro-adjustment settings
5. Repeat steps 3+4 a few times
6. Look for differences

### Some examples

Assume you start with no micro-adjustment set (i.e. set to 0). Then query the custom functions via a call to gphoto2, saving the output/debugging log to a file
```bash
mkdir customfuncex && cd customfuncex
gphoto2 --debug --debug-logfile=MAdj_0.log --get-config customfuncex
```
You will get an output from this call, but this will probably ***not*** tell you the full story, i.e. not all settings. For me, it only shows the last of four lines of settings.
Then change the camera's setting for the micro-adjustment (say to 5) and try again
```bash
gphoto2 --debug --debug-logfile=MAdj_+5.log --get-config customfuncex
```
Repeat the last step with an adjustemt to -5, creating yet another log.

Next, you want to filter for the interesting lines and inspect the differences
```bash
for fil in MAdj*log; do grep custom "$fil" | awk -F ':' '{print $2, $3}' > "$fil".filter; done
diff MAdj*log.filter
```

This may then look like (for two files only, of course)
```bash
4c4
<  event 38  decoded custom function, currentvalue of d1a0 is c4,1,3,b8,d,502,1,1,504,1,0,503,1,0,505,1,0,507,5,2,2,0,2,0,512,2,0,17,513,1,1,510,1,0,514,1,0,515,1,0,50e,1,0,516,1,1,60f,1,0,
---
>  event 38  decoded custom function, currentvalue of d1a0 is c4,1,3,b8,d,502,1,1,504,1,0,503,1,0,505,1,0,507,5,2,2,5,2,0,512,2,0,17,513,1,1,510,1,0,514,1,0,515,1,0,50e,1,0,516,1,1,60f,1,0,
```
You thus find that all HEX values stay the same apart from a `5` popping up in between
```bash
c4,1,3,b8,d,502,1,1,504,1,0,503,1,0,505,1,0,507,5,2,2,
```
and
```bash
,2,0,512,2,0,17,513,1,1,510,1,0,514,1,0,515,1,0,50e,1,0,516,1,1,60f,1,0,
```

I have but one camera to try this with, but I assume this will at least depend on your camera model, possibly on other things. Note, that not every camera has those custom settings (in my case per lens, not as one setting for all lenses). Your mileage **will** vary. A different lens and different day, I consistenly crashed the camera trying to adjust the setting via gphoto2 (I also found this whole process to be very picky in terms of what USB cable I used, so maybe it was the cable, not the gphoto2 command itself that caused the crashes). You would do this via a line like
```bash
gphoto2 --set-config=customfuncex=c4,1,3,b8,d,502,1,1,504,1,0,503,1,0,505,1,0,507,5,2,2,0a,2,0,512,2,0,17,513,1,1,510,1,0,514,1,0,515,1,0,50e,1,0,516,1,1,60f,1,0,
```
(HEX values, remember? So this would set the micro-adjustment to +10 being a 2-byte integer)

I used this to try and automate the changing of the micro-adjustment settings from the script via the `customfuncex` variable. If setting the micro-adjustment via gphoto2 works you, feel free to add your cameras, otherwise you will have to dive into the settings of your camera with every iteration of the script.


## Nikon

Similar to the above?
