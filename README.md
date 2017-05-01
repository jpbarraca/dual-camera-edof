# dual-camera-edof
Extract the EDOF from JPEG photos captured with Dual Camera smartphones

The result is a grayscale image depth map where higher depth is represented as higher luminosity values. The original and processed images can also be extracted as separated images for postprocesing.

The resulting image can be used in a image editor to add depth specific effects.

Tested with a Huawei P9 but it may work with smartphones using the same technologies.

## Requirements

* Python3
* Pillow


## Caveats

* Simple and not throughly tested. Works in my setup.