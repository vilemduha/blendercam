# bpypolyskel

![Logo](./misc/logo.jpg)

How to fit a hipped roof to the walls of a building? No problem, the _bpypolyskel_ library provides a single function that does the whole task automatically. From the footprint of a building, its [_straight skeleton_](https://en.wikipedia.org/wiki/Straight_skeleton) gets computed. From this skeleton all _faces_ get extracted and the height for every vertex of the straight skeleton is calculated. All these computations can easily be done in [Blender](https://www.blender.org/), but the library may also be used in general purpose applications.

The _bpypolyskel_ library was [tested](https://github.com/prochitecture/bpypolyskel/wiki/Testing) against all 320.000 hipped roofs in the OpenStreetMap database. It runs successfully for 99.99% of them.

## Usage
The library _bpypolyskel_ provides two functions:

- `polygonize()`

_polygonize()_ is the main function to compute the faces of a hipped roof from the footprint of a building, it does the whole task described above. It accepts a simple description of the contour of the footprint polygon, including those of eventual holes, and returns a list of polygon faces. See more details in its [documentation](https://github.com/prochitecture/bpypolyskel/wiki/polygonize).

- `skeletonize()`

_skeletonize()_ creates the [straight skeleton](https://en.wikipedia.org/wiki/Straight_skeleton) of the footprint. It gets a list of the edges of the footprint polygon, including those of eventual holes, and creates a straight skeleton. This function is called from _polygonize()_, but may also be used independently. See more details in its [documentation](https://github.com/prochitecture/bpypolyskel/wiki/skeletonize)

### Note
The straight skeleton computed by _skeletonize()_ does not provide a straight skeleton in a mathematical sense. Several cleaning and merging algorithms repair issues produced by inaccuracies of the footprint and issues in the skeletonize algorithm. Its goal is to create a skeleton that fits best for a hipped roof. 

## Installation and Demos
You find all required files in the folder [bpypolyskel](./bpypolyskel). There are two main applications of this project:

### Within a Blender addon
Copy the whole folder [bpypolyskel](./bpypolyskel) to your addon. Include the functions using
```
from .bpypolyskel import bpypolyskel
```
The file [__init__.py](./__init__.py) shows a simple code for usage in an addon. It adds an object created by _bpypolyskel_ to a scene. The demo object is created in Blender by Add -> Mesh -> Add bpypolyskel Demo Object.

### General purpose application
The functions of _bpypolyskel_ are also usable using a Python interpreter, but then the installation of the package _mathutils_ is required. Install it using:
```
pip install mathutils
```
A simple demo in the file [demo.py](./demo.py) shows this type of usage and displays the result using  `matplotlib`.

## Credits
The implementation of the straight skeleton algorithm is based on the description by Felkel and Obdržálek in their 1998 conference paper 
[Straight skeleton implementation](http://www.dma.fi.upm.es/personal/mabellanas/tfcs/skeleton/html/documentacion/Straight%20Skeletons%20Implementation.pdf). The code for the function _skeletonize()_ has been ported from the implementation by [Botffy](https://github.com/Botffy/polyskel).

The main adaptations compared to Botffy's original code are:

- The order of the vertices of the polygon has been changed to a right-handed coordinate system (as used in Blender). The positive x and y axes point right and up, and the z axis points into your face. Positive rotation is counterclockwise around the z-axis.
- The geometry objects used from the library `euclid3` in the implementation of Bottfy have been replaced by objects based on `mathutils.Vector`. These objects are defined in the new library [bpyeuclid](./bpypolyskel/bpyeuclid.py).
- The signature of `skeletonize()` has been changed to lists of edges for the polygon and eventual hole. These are of type `Edge2`, defined in [bpyeuclid](./bpypolyskel/bpyeuclid.py). 
- Some parts of the skeleton computations have been changed to fix errors produced by the original implementation.
- Algorithms to merge clusters of skeleton nodes and to filter ghost edges have been added.
- A pattern matching algorithm to detect apses, that creates a multi-edge event to create a proper apse skeleton.
