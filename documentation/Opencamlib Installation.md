# Installation

## Obtaining Blender
Download portable version for linux64 2.83 or 2.92
from a command line as user to download and extract blender

```
$ cd ~/
$ mkdir Apps
$ cd Apps
$ wget https://ftp.nluug.nl/pub/graphics/blender/release/Blender2.92/blender-2.92.0-linux64.tar.xz
$ tar xf blender-2.92.0-linux64.tar.xz
$ cd blender-2.92.0-linux64/2.92/python/bin
$ ./python3.7m -m ensurepip
$ ./pip3 install shapely
$ ./pip3 install vtk
$ ./pip3 install Equation
```

## Obtaining OpenCamLib

installing python and libboost-python headers

 
```
$ sudo apt install python3-dev libboost-python-dev
```

get the latest aewallin opencamlib sources

```
$ cd ~/Apps
$ git clone https://github.com/aewallin/opencamlib.git
$ cd opencamlib
$ mkdir build
$ cd build
$ cmake -DBUILD_PY_LIB=ON -DBUILD_CXX_LIB=ON -DUSE_PY_3=ON ..
$ make
```
this is optional
```
$ sudo make install
```
at this point opencamlib is compiled 
if you ran ```make install```the terminal may show messages similar to this

```
[0/1] Install the project...
-- Install configuration: ""
-- Installing: /usr/lib/python3.8/site-packages/ocl.so
-- Up-to-date: /usr/lib/python3.8/site-packages
-- Up-to-date: /usr/lib/python3.8/site-packages/STLTools.py
-- Up-to-date: /usr/lib/python3.8/site-packages/procmemory.py
-- Up-to-date: /usr/lib/python3.8/site-packages/camvtk.py
-- Up-to-date: /usr/lib/python3.8/site-packages/pyocl.py
```

the python 3 version may depend on your system


## Installing OpenCamLib in Blender

now we need to link some files to the blender python3.7 interpreter


Depending on your base system python files may be in other place


from system if ran ```make install``` files should be here

```
/usr/lib/python3/dist-packages/ocl.so
```

or from opencamlib src dir

```
opencamlib/build/src/ocl.so
opencamlib/src/lib/STLTools.py
opencamlib/src/lib/procmemory.py
opencamlib/src/lib/camvtk.py
opencamlib/src/lib/pyocl.py
```

please change the following instrutions to macth

```
$ ln -s /usr/lib/python3.8/site-packages/ocl.so ~/Apps/blender-2.92.0-linux64/2.92/python/lib/python3.7/site-packages/
$ ln -s /usr/lib/python3.8/site-packages/STLTools.py ~/Apps/blender-2.92.0-linux64/2.92/python/lib/python3.7/site-packages/
$ ln -s /usr/lib/python3.8/site-packages/procmemory.py ~/Apps/blender-2.92.0-linux64/2.92/python/lib/python3.7/site-packages/
$ ln -s /usr/lib/python3.8/site-packages/camvtk.py ~/Apps/blender-2.92.0-linux64/2.92/python/lib/python3.7/site-packages/
$ ln -s /usr/lib/python3.8/site-packages/pyocl.py ~/Apps/blender-2.92.0-linux64/2.92/python/lib/python3.7/site-packages/
```
or


```
$ ln -s /home/blendercam/projects/opencamlib/build/src/ocl.so ~/Apps/blender-2.92.0-linux64/2.92/python/lib/python3.7/site-packages/
$ ln -s /home/blendercam/projects/opencamlib/src/lib/STLTools.py ~/Apps/blender-2.92.0-linux64/2.92/python/lib/python3.7/site-packages/
$ ln -s /home/blendercam/projects/opencamlib/src/lib/procmemory.py ~/Apps/blender-2.92.0-linux64/2.92/python/lib/python3.7/site-packages/
$ ln -s /home/blendercam/projects/opencamlib/src/lib/camvtk.py ~/Apps/blender-2.92.0-linux64/2.92/python/lib/python3.7/site-packages/
$ ln -s /home/blendercam/projects/opencamlib/src/lib/pyocl.py ~/Apps/blender-2.92.0-linux64/2.92/python/lib/python3.7/site-packages/
```
## next steps can be found in this link
https://github.com/vilemduha/blendercam/wiki/Using-Blendercam-from-github

## Tips
### OpenSuSE 15.1
I got an python error, because print was used without () in the cmake file. I changed in the file ~/Apps/opencamlib/src/pythonlib/pythonlib.cmake in line 51 and 57 the python print command:
* old line 51 and 57

```
COMMAND ${PYTHON_EXECUTABLE} -c "from distutils.sysconfig import get_python_lib; print get_python_lib(0,0,\"/usr/local\")"
..
COMMAND ${PYTHON_EXECUTABLE} -c "from distutils.sysconfig import get_python_lib; print get_python_lib(plat_specific=1,standard_lib=0,prefix=\"/usr/local\")"
```

* new

```
COMMAND ${PYTHON_EXECUTABLE} -c "from distutils.sysconfig import get_python_lib; print( get_python_lib(0,0,\"/usr/local\"))"
..
COMMAND ${PYTHON_EXECUTABLE} -c "from distutils.sysconfig import get_python_lib; print( get_python_lib(plat_specific=1,standard_lib=0,prefix=\"/usr/local\"))"
```
