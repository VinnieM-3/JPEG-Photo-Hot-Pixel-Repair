#!/usr/bin/env python3
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

orgdir = './originals/' # directory containing files to repair.
repdir = './repaired/' # directory containing repaired files
mskdir = './masks/' # directory containing mask files and pixel maps

parser = argparse.ArgumentParser()

# you must provide a mask file name from those in the 'masks' subfolder.
parser.add_argument('-m', '--maskfilename',
                    help='name of jpg mask file',
                    required=True)

# you may provide the file name of the jpg that you want repaired.  It must be
# placed in the the 'originals' subfolder.  Repaired files are generated in 
# 'repaired' subfolder. if you don't provide a filename, 
# all files in the 'originals' subfolder will be repaired. 
parser.add_argument('-f', '--jpgfilename',
                    help='name of jpg file needing hot pixel repair',
                    required=False, default='None')

# parse the input mask file name and optional jpg file needing repair.
args = parser.parse_args()
maskfilename = args.maskfilename
imgfile = args.jpgfilename

# read in pixel map from text file that matches mask file name.
# the pixel map text file is created by hot_pixel_remapper.py
pixel_map = []
with open(mskdir + maskfilename + '.txt', 'r') as f:
    lines = f.read().splitlines()
    for line in lines:
        pnts = line.split(':')
        orgpix = pnts[0].split(',')
        reppix = pnts[1].split(',')               
        if (orgpix[0].isdigit() and
            orgpix[1].isdigit() and
            reppix[0].isdigit() and
            reppix[1].isdigit()):
            pixel_map.append([(int(orgpix[0]),int(orgpix[1])),
                              (int(reppix[0]),int(reppix[1]))])
        else:
            print('Error = {}'.format(line))

# if you supply a filename, only that file will be repaired.  The file must be 
# placed in the 'originals' folder.
if imgfile != 'None':

    # make sure the file has a jpg or jpeg extension
    if imgfile.lower().endswith(('.jpg', '.jpeg')):
        
        # check that repair file does not already exist.
        if not isfile(repdir + imgfile.replace('.', 'a.')):
    
            startTime = datetime.now()
        
            img = imread(orgdir + imgfile)
            for pix in pixel_map:
                img[pix[0][0],pix[0][1],0] = img[pix[1][0],pix[1][1],0]
                img[pix[0][0],pix[0][1],1] = img[pix[1][0],pix[1][1],1]
                img[pix[0][0],pix[0][1],2] = img[pix[1][0],pix[1][1],2]
               
            
            # save file with an 'a' at the end of the filename to indicate 
            # it was repaired. quality=98 appears to create a file of 
            # approx the same size as the original.
            imsave(repdir + imgfile.replace('.', 'a.'), img, quality=98)
        
            # copy the EXIF data from the original file to the repaired file.
            transplant(orgdir + imgfile, repdir + imgfile.replace('.', 'a.'))
            
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
    
else: # repair all files in the 'originals' folder.

    numfilesrepaired = 0
      
    s = 'mask file = {}, num of pixel remappings = {}'
    print(s.format(maskfilename, len(pixel_map)))
    
    # get list of files in the 'originals' subfolder
    onlyfiles = [f for f in listdir(orgdir) if isfile(join(orgdir, f))]
    
    for imgfile in onlyfiles:
        
        # make sure the file has a jpg or jpeg extension
        if imgfile.lower().endswith(('.jpg', '.jpeg')):
            
            # check that repair file does not already exist.
            if not isfile(repdir + imgfile.replace('.', 'a.')):
        
                startTime = datetime.now()
                
                img = imread(orgdir + imgfile)
                for pix in pixel_map:
                    img[pix[0][0],pix[0][1],0] = img[pix[1][0],pix[1][1],0]
                    img[pix[0][0],pix[0][1],1] = img[pix[1][0],pix[1][1],1]
                    img[pix[0][0],pix[0][1],2] = img[pix[1][0],pix[1][1],2]
                   
                # save repaired file in 'repaired' subfolder
                imsave(repdir + imgfile.replace('.', 'a.'), img, quality=98)
                
                # copy EXIF data from original file to repaired file.
                transplant(orgdir + imgfile, repdir + imgfile.replace('.',
                                                                      'a.'))
            
                elapsed_time = datetime.now() - startTime
            
                s = 'file = {}, elapsed time = {}'
                print(s.format(imgfile, elapsed_time))
                
                numfilesrepaired += 1
            else:
                s = 'Error: File {} already exists'
                print(s.format(repdir + imgfile.replace('.', 'a.')))                
    
    s = 'Done! Number of files repaired = {}'
    print(s.format(numfilesrepaired))   
