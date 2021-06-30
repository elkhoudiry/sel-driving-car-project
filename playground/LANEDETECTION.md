As we know, the image can be written as a matrix ( an array of pixles ), each pixel contains the light intensity in specific part of an image ( light intensity goes from 0 ~ 255 )

Gradiant is change in brightness in each pixel, higher gradient means higher light intensity in adjecant pixels, this is how we will detect edges in an image

To be able to detect lanes we need to detect edges in picture.
Canny method detects edges by finding difference in light intensity in an image ( sharp change in color )
