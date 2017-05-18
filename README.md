# dual-camera-edof
Extract the EDOF from JPEG photos captured with Dual Camera smartphones

The result is a grayscale image depth map where higher depth is represented as higher luminosity values. The original and processed images can also be extracted as separated images for postprocesing.

The resulting image can be used in a image editor to add depth specific effects.

Tested with a Huawei P9 but it may work with smartphones using the same technologies.

## Usage

```
Usage: extract_edof.py [options] img1 img2 img3...
Options:
    -p: Save the originaly processed image to the same directory
    -o: Save the originaly unprocessed image to the same directory
    -e: Save the EDOF as an image to the same directory
    -v: View the EDOF image
    -d: Delete file and only keep extracted (will enforce -o -e)
```

## Requirements

* Python3
* Pillow


## Caveats

* Simple and not throughly tested. Works in my setup.