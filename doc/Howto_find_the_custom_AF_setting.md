### Identifying the custom AF adjustment settings

## Canon

# In short

1. Use a recent gphoto2 library (ver. 2.5.11 works for me)
2. Connect your camera to your computer
3. Make use of gphoto2's debugging output to get a lot of information from your camera
4. Change the Micro-Adjustment settings
5. Repeat steps 3+4 a few times
6. Look for differences

# Some examples

Assume you start with no Micro-Adjustments set, so setting zero. Then query the custom functions via a call to gphoto2, saving the output/debugging log to a file
```bash
mkdir customfuncex && cd customfuncex
gphoto2 --debug --debug-logfile=MAdj_0.log --get-config customfuncex
```
Then change the camera's setting for the micro-adjustment (say to 5) and try again
```bash
gphoto2 --debug --debug-logfile=MAdj_+50.log --get-config customfuncex
```

Next, you want to filter for the interesting lines and inspect the differences
```bash
for fil in MAdj*log; do grep custom "$fil" > "$fil".filter; done
diff MAdj*log.filter
```

## Nikon

Similar to the above?
