
### Import required modules


```python
# manipulate arrays and have math
import numpy as np
# plot results
import matplotlib.pyplot as plt
# plot them inline in jupyter
%matplotlib inline
# make matplotlib load images
import matplotlib.image as mpimg
```

## Load  test images


```python
sharp_image = mpimg.imread('picture.png')
soft_image = mpimg.imread('picture_gaussian_10.png')
```

#### Display the raw images


```python
plt.imshow(sharp_image)
print 'sharp image'
plt.show()
plt.imshow(soft_image)
print 'soft image'
plt.show()
```

    sharp image



![png](output_5_1.png)


    soft image



![png](output_5_3.png)


#### Extract smaller region from images


```python
sharp_test = sharp_image[1000:1400,2000:2400].copy()
soft_test = soft_image[1000:1400,2000:2400].copy()
```

#### Display said regions


```python
plt.imshow(sharp_test)
print 'sharp image'
plt.show()
plt.imshow(soft_test)
print 'soft image'
plt.show()
```

    sharp image



![png](output_9_1.png)


    soft image



![png](output_9_3.png)


#### Again extract smaller region from image, now adding noise and small shift
(hoping to mimick some differences when taking pictures)


```python
sharp_test_noise = sharp_image[1000:1400,2000:2400].copy()
soft_test_noise = soft_image[1005:1405,2012:2412].copy()
```


```python
# add noise
def noise(data, noise_value):
    noisy_data = data + noise_value * np.random.random([400,400,3]) - noise_value/2
    # shift values to be within bounds
    for value in np.nditer(noisy_data, op_flags=['readwrite']):
        if (value < 0):
            value[...] = np.abs(value)
        if (value > 1):
            value[...] = -value + 2
    return noisy_data
```

#### Display those images


```python
sharp_test_noise = noise(sharp_test_noise, 0.2)
soft_test_noise = noise(soft_test_noise, 0.2)
plt.imshow(sharp_test_noise)
plt.show()
plt.imshow(soft_test_noise)
plt.show()
```


![png](output_14_0.png)



![png](output_14_1.png)


## Check gradients of test images


```python
# compute a gradients measure that should prefer an edgy result, thus a sharper one
def gradient_sharpness_metric(data):
    # limit gradients to one colour channel (greyscale, remember)
    gy, gx = np.gradient(data[:,:,0], 2)
    # get norm of the gradients, thus looking at both directions simultaneously
    gnorm = np.sqrt(gx**2 + gy**2)
    # and produce a single number
    metric = np.mean(gnorm)
    
    return metric
```

#### Inspect clean images first:


```python
print '    metric (sharp) :', gradient_sharpness_metric(sharp_test)
print '    metric  (soft) :', gradient_sharpness_metric(soft_test)
```

        metric (sharp) : 0.023001
        metric  (soft) : 0.00670288


#### Now inspect 'realistic' images:


```python
print '    metric (sharp) :', gradient_sharpness_metric(sharp_test_noise)
print '    metric  (soft) :', gradient_sharpness_metric(soft_test_noise)
```

        metric (sharp) : 0.0353682247934
        metric  (soft) : 0.0212411010106


### Check robustness of metric, looking at the ratio of things
A higher ratio should hint towards a clearer identification (or so the idea)


```python
print '    ratio/cleanliness of results:', \
gradient_sharpness_metric(sharp_test_noise)/gradient_sharpness_metric(soft_test_noise)
```

        ratio/cleanliness of results: 1.66508434642



```python

```
