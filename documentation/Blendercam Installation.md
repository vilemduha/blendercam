# How to install Blendercam ?

## Use Blendercam from github 

Using Blendercam from github is a great way to try out the newest features and fixes.  The latest build (dailybuild) of Blender can be used with the latest Master branch of Blendercam and then you can live on the bleeding edge.

The easiest way to "install" is not to install but instead just tell Blender where to find the add-on.  This way you don't have to worry about copying/moving files around.  You can keep Blendercam source files separate from Blender if using source control (ie git for development) and still easily test your changes in Blender.

If you are using Arch Linux, you can just install `blendercam-git` from the AUR and skip to [Enable Blendercam add-on](#enable-blendercam-add-on). OpenCAMLib is also available as `opencamlib-git`.

---


You can watch the video using the documentation below.

[![How To Install on Linux](images/installLinux.png)](http://www.youtube.com/watch?v=7_Qq8Zv4SEo)

---

* [1. Obtaining Blender](#obtaining-blender)
* [2. Get Blendercam source code](#get-blendercam-source-code)
* [3. Setup Blender scripts alternate path](#setup-blender-scripts-alternate-file-path)
* [4. Enable Blendercam and required add-ons](#enable-blendercam-add-on)
* [5. (Optional) Install OpenCAMLib](#optional-install-opencamlib)
* [6. Updating Blendercam](#updating-blendercam)


## Obtaining Blender
Blendercam is an addon of Blender. It works now with Blender version 2.83, 2.92, 2.93 and 3.0.
You can download Blender portable version for linux64 2.83 or 2.93 or 3.0 and install dependencies from command lines.

```
$ cd ~/
$ mkdir Apps
$ cd Apps
$ wget https://ftp.nluug.nl/pub/graphics/blender/release/Blender3.0/blender-3.0.0-linux-x64.tar.xz
$ tar xf blender-3.0.0-linux64.tar.xz
$ cd blender-3.0.0-linux64/3.0/python/bin
$ ./python3.9 -m ensurepip
$ ./pip3 install shapely
$ ./pip3 install Equation
$ sudo apt-get install libgeos-c1v5
```

## Dependencies

| Python dependencies        | Version           |
| ------------- |:-------------:|
| shapely  | >= 1.5 |
| numpy    | ...      |
| Equation | ...      |
| libgeos_c | libgeos-c1v5|






**Note:** if you are using a Blender with a bundled Python then shapely and numpy must be installed in the `site-packages` directory of the bundled python. For Blender 2.8 only Shapely is needed. To install it, open terminal, get to Blender directory and use PIP:

`cd 3.0/python/bin/`

`./python3.9 -m ensurepip`

`./python3.9 -m pip install shapely`


## Get Blendercam source code
The first step is to get the source code from the github repository.
 1. Assuming that Git is installed on your machine, at the command prompt change into the directory where blendercam will be and then type:
 2. `git clone https://github.com/vilemnovak/blendercam.git` (Master branch is now upgraded to Blender 2.8, 2.8_BETA branch will soon be removed)

 ![git clone](https://cloud.githubusercontent.com/assets/648108/12068782/8942a84a-afeb-11e5-86c4-31a60475fd27.png)

 3. git will make a subdirectory called `blendercam` in the current directory then download the most recent version of blendercam from github.

## Setup Blender scripts alternate file path
The second step is to tell blender to also search an alternate path for add-ons.  When blender starts up it will search its own paths for add-ons and will also search the alternate path that you add.  This way an external source add-on can be used in Blender.

 1. select **User Preferences** panel

 ![File User Preferences](images/addonInstall1.png)

 2. select **File** tab
 3. select the file button on the **Scripts** input field and select the path to your *blendercam/scripts* directory

 ![File Paths](images/addonInstall2.png)

 4. select **Save User Settings**
 5. restart Blender

## Enable Blendercam and required add-ons
The next step is to enable the Blendercam add-on.

![Enable Addon](images/addonInstall3.png)

 1. select **User Preference** panel
 2. select **Add-ons** tab
 3. select **Scene** category
 4. enable the CAM addon by left clicking on the check box. (Note: the checkbox is on the left side in daily builds of Blender after 11 Jan 2016)  
   4a. the file path should match your Blendercam git path
 5. Optional: enable the experimental features
 6. enable additional bundled add-ons required by some Blendercam features:
    - Add Curve: Extra Objects
 7. select **Save User Settings**

Now when ever blender is started, the external blendercam add-on will be enabled.

## (Optional) Install Opencamlib

To install OpenCamLib, you can follow [this link](Opencamlib%20Installation.md).

[OpenCAMLib](https://github.com/aewallin/opencamlib) is an open source CAM library created by Anders Wallin. It offers high quality waterline generation and drop cutter sampling algorithms. For drop cutter algorithms it's more reliable than Bullet Physics (Blender's built-in collision detection library) and offers better performance (up to 30 times faster than regular algorithm on 24-core machine).

To use OpenCAMLib with BlenderCAM, it needs to be built from source and installed inside Python distribution bundled with Blender.

To use OpenCAMLib waterlines, select "Show experimental features" in Blender User Preferences / Addons / CAM - gcode generation tools. Then select Waterline strategy and "Use OpenCAMLib". The current version lacks dialog for waterline resolution and automatic determination of cutter length, those can be adjusted in `scripts/addons/cam/opencamlib/opencamlib.py`.

For "parallel" strategy and other drop cutter sampling operations select both "Use exact mode" and "Use OpenCAMLib".


## Updating Blendercam
Every once in a while, maybe even daily, you will want to update your copy of Blendercam to match what is on Github.
 1. at the command line, change to the directory of blendercam
 2. tell git to pull all the latest changes from Github and update your copy
  `git pull`

After git finishes updating blendercam you can run blender.  If blender was already running, restart it (close blender and then start it).
