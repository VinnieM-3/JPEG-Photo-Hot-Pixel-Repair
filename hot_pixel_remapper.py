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
from skimage.io import imread
from skimage.io import imsave
from os import listdir
from os.path import isfile, join
from datetime import datetime
import warnings
from piexif import transplant

# stops low contrast image warnings from cluttering output.
warnings.filterwarnings("ignore")

orgdir = './originals/'  # directory containing files to repair.
repdir = './repaired/'  # directory containing repaired files
mskdir = './masks/'  # directory containing mask files and pixel maps

parser = argparse.ArgumentParser()

# you must provide a mask file name from the 'masks' sub-folder.
parser.add_argument('-m', '--maskfilename',
                    help='name of jpg mask file',
                    required=True)

# you may also provide the file name of the jpg that you want repaired.  It must be
# placed in the the 'originals' sub-folder.  Repaired files are placed in
# 'repaired' sub-folder. if you don't provide a filename,
# all files in the 'originals' sub-folder will be repaired.
parser.add_argument('-f', '--jpgfilename',
                    help='name of jpg file needing hot pixel repair',
                    required=False, default='None')

# parse the input mask file name and optional jpg file you want to repair.
args = parser.parse_args()
maskfilename = args.maskfilename
imgfile = args.jpgfilename

# read in pixel map from text file that matches mask file name.
# the pixel map text file is created using hot_pixel_remapper.py
pixel_map = []
with open(mskdir + maskfilename + '.txt', 'r') as f:
    lines = f.read().splitlines()
    for line in lines:
        pnts = line.split(':')
        orgpix = pnts[0].split(',')
        reppix = pnts[1].split(',')               
        if orgpix[0].isdigit() and orgpix[1].isdigit() and reppix[0].isdigit() and reppix[1].isdigit():
            pixel_map.append([(int(orgpix[0]), int(orgpix[1])),
                              (int(reppix[0]), int(reppix[1]))])
        else:
            print('Error = {}'.format(line))

# if you supply a filename, only that file will be repaired.  The file must be 
# located in the 'originals' folder.
if imgfile != 'None':

    # make sure the file has a jpg or jpeg extension
    if imgfile.lower().endswith(('.jpg', '.jpeg')):
        
        # check that repair file does not already exist.
        if not isfile(repdir + imgfile.replace('.', 'r.')):
    
            startTime = datetime.now()
        
            img = imread(orgdir + imgfile)
            for pix in pixel_map:
                img[pix[0][0], pix[0][1]] = img[pix[1][0], pix[1][1]]
            
            # save file with an 'r' at the end of the filename to indicate
            # it was repaired. quality=98 appears to create a file of 
            # approx the same size as the original.
            imsave(repdir + imgfile.replace('.', 'r.'), img, quality=98)
        
            # copy the EXIF data from the original file to the repaired file.
            transplant(orgdir + imgfile, repdir + imgfile.replace('.', 'r.'))
            
            elapsed_time = datetime.now() - startTime   
            
            s = 'orig file = {}, mask file = {}, '
            s += 'elapsed time = {} num of pixel remappings = {}, '
            print(s.format(imgfile, maskfilename, len(pixel_map), 
                           elapsed_time))
        else:
            s = 'Error: File {} already exists'
            print(s.format(repdir + imgfile))
    else:
        s = 'Error: File {} does not end with .jpg or jpeg'
        print(s.format(repdir + imgfile))
    
else:  # repair all files in the 'originals' folder.

    numfilesrepaired = 0
      
    s = 'mask file = {}, num of pixel remappings = {}'
    print(s.format(maskfilename, len(pixel_map)))
    
    # get list of files in the 'originals' sub-folder
    onlyfiles = [f for f in listdir(orgdir) if isfile(join(orgdir, f))]
    
    for imgfile in onlyfiles:
        
        # make sure the file has a jpg or jpeg extension
        if imgfile.lower().endswith(('.jpg', '.jpeg')):
            
            # check that repair file does not already exist.
            if not isfile(repdir + imgfile.replace('.', 'r.')):
        
                startTime = datetime.now()
                
                img = imread(orgdir + imgfile)
                for pix in pixel_map:
                    img[pix[0][0], pix[0][1]] = img[pix[1][0], pix[1][1]]
                   
                # save repaired file in 'repaired' sub-folder
                imsave(repdir + imgfile.replace('.', 'r.'), img, quality=98)
                
                # copy EXIF data from original file to repaired file.
                transplant(orgdir + imgfile, repdir + imgfile.replace('.',
                                                                      'r.'))
            
                elapsed_time = datetime.now() - startTime
            
                s = 'file = {}, elapsed time = {}'
                print(s.format(imgfile, elapsed_time))
                
                numfilesrepaired += 1
            else:
                s = 'Error: File {} already exists'
                print(s.format(repdir + imgfile.replace('.', 'r.')))
    
    s = 'Done! Number of files repaired = {}'
    print(s.format(numfilesrepaired))   
