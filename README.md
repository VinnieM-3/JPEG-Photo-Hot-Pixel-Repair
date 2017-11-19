# JPEG Photo Hot Pixel Repair
This Python tool can be used to remove hot pixels from JPEG photographs.

Requires: Python 3, scikit-image, and piexif.
 
Copy hot_pixel_remapper.py and hot_pixel_repair.py to a folder.  Then create three subfolders with the names 'originals', 'masks', and 'repaired'.
 
Now take a jpeg photo with your lens cap ON.  Set ISO to 1600 and shutter speed to 1/10sec or longer.  Save this 'mask file' to the 'masks' subfolder and run the hot_pixel_remapper.py script, passing the mask filename as a parameter.  
For example: python hot_pixel_remapper.py -m D200_1600.JPG.
 
Next, copy the jpeg files you want repaired to the 'originals' subfolder and run the hot_pixel_repair.py script and pass the mask file name as a parameter.  
For example: python hot_pixel_repair.py -m D200_1600.JPG.  

When the script is done running the 'repaired' subfolder will contain the repaired jpeg files.

example:

image from camera:
![image from camera](https://github.com/VinnieM-3/JPEG-Photo-Hot-Pixel-Repair/blob/master/image.JPG)

closeup section with multiple hot pixels, before running script:
![closeup section with hot pixels - before](https://github.com/VinnieM-3/JPEG-Photo-Hot-Pixel-Repair/blob/master/before.jpg)

closeup section after running script
![closep section with hot pixels - after](https://github.com/VinnieM-3/JPEG-Photo-Hot-Pixel-Repair/blob/master/after.jpg)
