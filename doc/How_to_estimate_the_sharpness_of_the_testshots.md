# The 'sharpness parameter'

By this I mean some metric that can tell whether or not the pictures taken actually become more or less focussed.

Of course considerable science already went into this and there are many methods. No need to reinvent the wheel. A quick internet search revealed several ways of doing this, some easier than others. What comes to mind is: looking at the contrast of the images (more contrast will mean sharper), finding edges (a blurry picture won't have (m)any), or being fancy applying an FFT and comparing the factors to the high frequency components.

Do your own search and see what you like. I've probably missed **the** standard method, I surely have ignored what other packages do, and I probably exploit all the power Python can deliver. I'm fiddling and having fun, reinventing the wheel nevertheless.

Resources I came across involved (nothing an internet search doesn't find):

1. a [talk](http://www.csl.cornell.edu/~cbatten/pdfs/batten-image-processing-sem-slides-scanning2001.pdf) on sharpness for SEMs
2. various discussions on stackoverflow, [1](https://stackoverflow.com/questions/6123443/calculating-image-acutance/6129542#6129542), [2](https://stackoverflow.com/questions/6646371/detect-which-image-is-sharper), [3](https://stackoverflow.com/questions/17887883/image-sharpness-metric) (actually lead me to the paper above)
3. [examples](https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_gradients/py_gradients.html#gradients) of sorts

## Implemented/tested within the script
* 'Variance method'

  This should favour more contrasty pictures which should be sharper.
  ```python
  avg_img = reduced_img.sum()/np.size(reduced_img)
  var = (reduced_img-avg_img)**2
  score = var.sum()/np.size(var)
  ```
  Here, `reduced_img` is a selected smaller region including parts of the target. Also, all images are processed in greyscale. The first line computes the average grey value, the second line estimates the variance of the pixels, the last line normalises to a score value.

* 'Gradient method'

  Computing gradients in x- and y-direction
  ```python
  gy, gx = np.gradient(reduced_img,2)
  gnorm = np.sqrt(gx**2 + gy**2)
  score = np.average(gnorm)
  ```
  Line 1 uses numpy for computing the gradients in `x` and `y` that line 2 will combine to an average per pixel which in turn will be averaged over the `reduced_img`.

Yes, the last (two) lines in either case are actually doing the same thing, I noticed (infact, there are yet other ways of writing this). I also noticed another small mishap in the code while typing the above, so it's all a process...


## Todo
* 'FFT method'

  FFTing the images, looking for frequency components.
