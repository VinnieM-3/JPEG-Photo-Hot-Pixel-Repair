# MIT License
#
# Copyright (c) 2017 VinnieM
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import argparse
import random
from datetime import datetime
from skimage.io import imread

mskdir = './masks/' # directory containing mask files and pixel maps

# record start time of script.
startTime = datetime.now()

parser = argparse.ArgumentParser()

# you must provide a mask filename and the mask jpg file must be placed in 
# the 'masks' subfolder.  The mask file is used to locate all the
# hot pixels.  Suggest taking a photo at ISO 1600 for at least 1/10sec with 
# the lens cap on.  But you can create mask files pixel maps 
# for multiple ISO settings and shutter speeds (and camera temps).
parser.add_argument('-m', '--maskfile',
                    help='name of jpg mask file', required=True)

# you may provide a threshold level or the default value will be used.  This 
# threshold is the limiting magnitude of any rgb color channel. 
# The default is 16, meaning any pixel in the mask jpg file that has a red,
# green, or blue component that exceeds 16 will be considered a hot pixel.
parser.add_argument('-t', '--threshold', type=int,
                    help='threshold value 8 - 255', required=False,
                    default=16)

# parse the input mask filename and optional threshold value.
# for example: python hot_pixel_remapper.py -m D200_1600.JPG -t 32
args = parser.parse_args()
maskfilename = args.maskfile
threshold = args.threshold


# simple algorithm used to select potential replacement pixels from those 
# surrounding the hot pixel.  If the hot pixel is surrounded by other
# hot pixels, the distance from the hot pixel is increased
# until a suitable nearby replacement is found.  Some randomness is also 
# added to avoid any potential patterns caused by a bunch of hot pixels located
# adjacent to one another.
random.seed(9)
def candidate_offsets(dist):
    c = []   
    for x in range(-dist, dist+1):
        c.append((x,-dist))
    for x in range(-dist, dist+1):
        c.append((x,dist))
    for x in range(-dist+1, dist):
        c.append((-dist,x))
    for x in range(-dist+1, dist):
        c.append((dist,x))
    random.shuffle(c)   
    return c

# read the mask file from the 'masks' subfolder
img_mask = imread(mskdir + maskfilename)


# scan the file for hot pixels and record coordinates in the hot_pixels list.
numhotpixels = 0 
hot_pixels = []
rows = img_mask.shape[0]
cols = img_mask.shape[1]
for y in range(0,rows):
    for x in range(0,cols):
        if (img_mask[y,x,0] > threshold or 
            img_mask[y,x,1] > threshold or 
            img_mask[y,x,2] > threshold):
            hot_pixels.append((y,x))
            numhotpixels += 1
            if numhotpixels > 10000:
                break
    if numhotpixels > 10000:
        break

if numhotpixels <= 10000:
    # create a pixal map by selecting a replacement pixel for each hot pixel.
    pixel_map = []
    max_dist = 1  # keep track of the maximum distance for reporting purposes.
    for orgpix in hot_pixels:
        dist = 1
        cand_selected = False
        while not cand_selected:
            co = candidate_offsets(dist)
            for offset in co:
                cand_pix = (orgpix[0]+offset[0], orgpix[1]+offset[1])
                
                # check that the candidate pixel coordinates aren't negative
                # and that the candidate pixel isn't also a hot pixel.
                if (cand_pix[0] >= 0 and cand_pix[0] < rows and
                    cand_pix[1] >= 0 and cand_pix[1] < cols and
                    cand_pix not in hot_pixels):
                    pixel_map.append([orgpix,cand_pix])
                    cand_selected = True
                    break
            if not cand_selected:
                dist += 1
                max_dist = max(max_dist,dist)
    
    
    # save the pixel map to a text file with the same name as the mask file
    # but with a .txt extension.  Pixel map text files are stored in 'masks'
    # subfolder.
    with open(mskdir + maskfilename + '.txt', 'w') as f:
        for p in pixel_map:
            f.write(str(p[0][0]) + ',' + str(p[0][1]) + ":"
                    + str(p[1][0]) + "," + str(p[1][1]) + '\n')
    
    # calculate elapsed time.  It can take a few minutes to create a pixel map
    # but you only need to do it once.
    elapsed_time = datetime.now() - startTime
    
    # output summary of results.
    s = 'mask file = {}, threshold = {}, '
    s += 'num of pixel remappings = {}, max pixel distance = {}, '
    s += 'elapsed time = {}'
    print(s.format(maskfilename, threshold, len(pixel_map), 
                   max_dist, elapsed_time))     
else:
    s = 'Error: More than 10,000 hot pixels found. '
    s += 'Threshold set too low?'    
    print(s)
