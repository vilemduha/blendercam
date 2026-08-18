# ! IMPORTANT ! BEFORE YOU INSTALL !
Most issues during installation can be avoided by checking a few settings first:
### Python must be v3.11 or v3.13
Download Blender from blender.org to ensure that it comes with a supported Python version. Blender installed via Package Managers may use a different, incompatible Python version. Fabex includes Python 3.11 dependencies for Blender 4.2 through 5.0 on all supported platforms and Python 3.13 dependencies for Blender 5.1+ on Windows x64.
### Enable Online Access
Fabex requires addons that used to ship as part of Blender, but have now been moved to an online repository. `Enable Online Access` in Blender's `Preferences > System` before installing and Fabex will automatically download what it needs.
### Restart After Installation
Fabex needs Blender to restart once before all of its functionality can be activated. The first time you install it, if you attempt to use it right away you will likely encounter errors. Restarting Blender should resolve all those errors - you do not need to reboot your system, simply quit and re-open Blender.

## Installation
Download `fabexcnc.zip`

Open Blender, go to `Preferences > Get Extensions`, click the arrow in the top right and click `Install from Disk`, select `fabexcnc.zip` that you just downloaded and click `Install from Disk`.

### Restart Blender
Fabex will not work correctly if Blender is not restarted after installing the addon.

## Fabex is Installed and Ready to Use!
Activate Fabex by going to `Properties`, in the `Render` tab and switch the `Render Engine` to Fabex. 

![image](/docs/_static/RenderEngine.png)

## Resources

Check out the [Getting Started Guide](https://spectralvectors.github.io/blendercam/starting.html)

See the [FAQ](https://spectralvectors.github.io/blendercam/faq.html) for answers to the most common questions.

For more info check out the full [Documentation](https://spectralvectors.github.io/blendercam/index.html)

For anything not covered above, head over to the [Matrix Chat](https://riot.im/app/#/room/#blendercam:matrix.org)
