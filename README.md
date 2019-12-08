# ECE 36400 Project: Image Blending and Morphing

## Description
Combining two images into one, or image blending, has many applications in image processing. One application that utilizes image blending is morphing – a special effect in motion pictures and animations that changes (or morphs) one image or shape into another through a seamless transition. While there are many ways to perform morphing, we will use a combination of linear projective transformations to achieve our goal. A projective transformation is a process that applies translation, rotation and scaling to a plane to transform it into a different plane. In this project, we will concentrate on the “Affine Transformation”. We will apply affine transformations to different sections of images to produce the effect of non-linear image warping.

A simple GUI Application is implemented, using PyQt5 and the Qt Framework, that allows for obtaining corresponding points from the two images. These points will then be used to display the result of blending the two images. The purpose of the GUI Application is to help identify the best correspondences for specific images.
