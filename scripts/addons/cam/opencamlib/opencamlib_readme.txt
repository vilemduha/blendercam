BlenderCAM OpenCAMLib support currently allows high quality, multithreaded sampling for 3-axis operations (parallel, spiral, etc.) and generation of waterlines.
Known issues:
- "skin" option is not supported yet
- waterline fill is not supported yet
- waterlines inside model have reversed direction (climb vs conventional)
- for waterlines cutter length is fixed, should be determined from maximum operation depth
- waterline sampling density is fixed, option to change it will be added soon

To use OpenCAMLib, you will need Python 2.7 installation, with "python2.7" executable added to your path and OpenCAMLib library installed.

OpenCAMLib installation instructions can be found at:
https://github.com/vilemnovak/blendercam/wiki/Using-BlenderCAM-with-OpenCAMLib
