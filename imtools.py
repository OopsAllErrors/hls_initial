#imtools.py
#
#Just a bunch of image processing methods. Common processing stacks at the bottom.

import math
import numpy as np
from scipy.ndimage import convolve

#Accepts an image and a list of functions to run on that image.
#  Outputs the new image.
def process(im,operations):
    for function in operations:
        im = function(im)
    return im

#Remove nodata values.
def remove_nodata(im):
    im[im==-9999] = np.nan
    return 

'''#########################################################################
## Convolutions for image sharpening, blur, and edge detection
#########################################################################'''

#A collection of useful kernels.
class kernel(object):
    def __init__(self):
        
        self.high_pass = np.array([[ 0,-1, 0],
                                   [ -1, 5,-1],
                                   [ 0,-1, 0]])
        
        self.blur = np.array([[ 1, 1, 1],
                              [ 1, 1, 1],
                              [ 1, 1, 1]])*(1.0/9.0)
        
        self.gaussian_blur = np.array([[ 0, 2, 0],
                                       [ 2, 4, 2],
                                       [ 0, 2, 0]])
        
        self.edge = np.array([[-1,-1,-1],
                              [-1, 8,-1],
                              [-1,-1,-1]])

#Applications of the kenerls to imagery.
class convolution(object):
    def sharpen(im):
        return convolve(im,kernel.high_pass)
    def blur(im):
        return convolve(im,kernel.low_pass)

'''#########################################################################
## Methods for enhancing or otherwise operation on the colors of imagery
#########################################################################'''

#RGB images only - emphasizes colors. Pretty slow.
class contrast(object):
    
    #Significantly increase contrast
    def emphasize(im):
        alpha = 1.4 # Simple contrast control
        beta = 0    # Simple brightness control
        return scale_alpha_beta(im,alpha,beta)
    
    #Significantly increase contrast
    def exaggerate(im):
        alpha = 2.0 # Simple contrast control
        beta = 0    # Simple brightness control
        return scale_alpha_beta(im,alpha,beta)

#
def scale_alpha_beta(im,alpha,beta):
    for y in range(im.shape[0]):
        for x in range(im.shape[1]):
            for c in range(im.shape[2]):
                im[y,x,c] = np.clip(alpha*im[y,x,c] + beta, 0, 255)
    return im

'''#########################################################################
## Remaps and rescales
#########################################################################'''

#Accepts an NDArray, outputs a scaled 8-bit array ready for conversion to a file.
class remap(object):
    
    def linear(im):
        low_value = 0
        high_value = 255
        low_threshold = 1
        high_threshold = 254
        return scale(im,low_value,high_value,low_threshold,high_threshold)
    
    def log(im):
        low_value = math.e
        high_value = 255
        low_threshold = math.log(250)
        high_threshold = math.log(7500)
        im = np.log(im)
        return scale(im,low_value,high_value,low_threshold,high_threshold)

def scale(im,low_value,high_value,low_threshold,high_threshold):
    im[np.where(im <= low_threshold)] = low_value
    im[np.where(im >= high_threshold)] = high_value
    indices = np.where( (im > low_value) & (im < high_value) )
    im[indices] = ( high_value * (im[indices] - low_threshold) / (high_threshold - low_threshold) )
    return im

'''#########################################################################
## Upsampling and downsampling
#########################################################################'''

place = 'holder'

#Upsample

#Downsample

'''#########################################################################
## Common band combinations and processing stacks
#########################################################################'''

class stack(object):
    simpleRGB = [remap.log]
    rgb = [remap.log,contrast.emphasize]


class band_combinations(object):
    rgb = ['B04','B03','B02']