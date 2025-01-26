# FAQ

## What happened to **BlenderCAM**? Why did the name change?
**Blender Foundation** owns the rights to the name **Blender** and they have requested that external projects not use their name or logo. **BlenderCAM** used both the name and logo, and so both needed to change.

For a time, seeing the word **Blender** in a product name would mean that it was made _for_ **Blender**, but from now on it will mean that it is made _by_ **Blender**.

**FabexCNC** was chosen because it combines _fabrication_ with _extension (the new format and location in Blender)_. 

CNC replaced CAM in the name as it seemed more widely recognizable, and avoids any confusion with 'camera' that may come from Blender's many 'camera' functions.

```{note}
**Fabex** was **BlenderCAM** (now it is **Fabex** _not_ **BlenderCAM**), it hasn't been a long time now, since **BlenderCAM** and still a machinist's delight, on a moonlit night. 
```

## When will you have full support for 4 and 5 axis Operations?
None of the developers currently have access to a 4+ Axis machine, so until one of the developers acquires a 4th axis, or someone with a 4+ axis machine joins the development team, 4 and 5 axis Operations will remain officially unsupported (outside of manual indexing).

## When will the Experimental features become Stable?
The short answer is: it depends.

The long answer is: there are generally 2 reasons why a feature is marked Experimental:

1 - It was developed for a specific machine or operation that cannot currently be tested or verified.

*or*

2 - It worked with some previous combination of Python and Blender versions and needs to be rewritten.

**Fabex** has been in continuous development since 2012, between Python 2 - 3.11, Blender 2.7 - 4.2, and 30+ volunteer developers with different machines, needs and approaches to coding.

Everyone puts in effort to make sure that all of **Fabex**'s features are supported and stable, but sometimes a feature will be introduced by someone who stops development, the feature will rely on a deprecated Python or Blender function, or there might be an intermittent issue that is difficult to diagnose.

It is not always possible to resolve these problems quickly, and there may be other users who are not experiencing any issues with the same feature who do not want it to be removed because someone else filed a Bug Report.

In these cases, a feature may be marked Experimental and, like 4+ axis operation, 

## What should I do if something in **Fabex** isn't working?
The first step is to check the docs or the chat to make sure that it is supposed to work the way you think.

*e.g. some tools will only work with a mesh or a curve, while others will accept any type of object, and certain CAM options will only appear alongside certain Strategies.*

The next step is to check the Known Issues - long-standing bugs and workarounds will be posted there.

After that, you can file a Bug Report!

## How Do I File a Bug Report?
On Github, on the Fabex page, click Issues.

Check to see if any of the Open Issues deal with the same problem you faced - someone else may have found a fix!

If not, click the New Issue button.

On the next screen, click Bug Report.

A template is provided for you, and though you don't need to follow it exactly, it helps to at least include:
- your OS
- your Blender version number
- your Fabex version number
- a description of what the bug is
- steps to take for a developer to reproduce the bug

Bonus points for including:
- a .blend file where the bug can be recreated
- the Error message from the console
- your Python version (just kidding, it's 3.11)

## How can I contribute?
Bug Reports are one form of contribution, but there are a lot of other ways to contribute:
- If you're not a coder:
  - documentation can be edited, updated and expanded
  - icons can be designed and added
- If you are a coder:
  - tackle one of the open Issues on Github
  - fix a bug you've found
  - stabilize or add a feature

Either way, you're going to start by forking the repository and submitting pull requests.

And you can always check in with the chat!

## Can I use Fabex with **Blender** 3 and earlier? Why support 4.2.1 and later?
If you want to use **Fabex** with earlier versions of **Blender** then you need to use on of the **blendercam.zip** releases, and you will also have to manually manage the Python dependencies (opencamlib, shapely), which might involve admin privilege.

Blender 4.2 came with the Extensions system, which offered two benefits:
- one-click install for official Extensions
- a Python dependency management solution

It also came with a bug in the Preset system, which was patched in 4.2.1, and so, 4.2.1 became the start of support for **Fabex**.

Since difficulty with installation and cross-platform support were some of the more common issues with **BlenderCAM** it was decided to pursue the Extension platform which offered solutions for both.

Unfortunately, the Extension system is not without issues, leading to the next most frequently asked question...

## I can't install or enable **Fabex**, I get an error that says `No module name 'shapely.lib'`, but I can still `import shapely`, what's going on?
**Blender** officially supports Python 3.11. At the time of this writing, Python 3.13 is the latest release.

Users whose **Blender** installs do not come from the **Blender** website may not come with their own Python binary, and will fall back on their system's Python installation.

If this is Python 3.12 or higher, then **Fabex** will not work, but most of **Blender** still will.

If you are not comfortable with Python version or dependency management, then the easiest option is to just download **Blender** from their website - it will include Python 3.11, and **Fabex** and all other Extensions will work.

If you have installed **Blender** from a package manager and you want to make **Fabex** work, you have a couple of options:
- manually manage the dependencies by `pip install`-ing `shapely`, and `opencamlib`
- manually manage Python versions by installing 3.11, or using a version management tool like `pyenv`

## What do I do if I have a question that isn't covered in the FAQ or elsewhere in the docs?
Your best bet is to ask in the chat. 

## What do I do with the Gcode file that **Fabex** outputs?
That will need to be sent to your machine so that it can be run.

The specifics of how to do it will vary between manufacturers, but, generally the Gcode file will be loaded into a Gcode sender which then connects or transmits the file to your CNC.

Some free, open-source Gcode senders include:
- [UGS - Universal Gcode Sender](https://github.com/winder/Universal-G-Code-Sender)
- [CNCJS](https://cnc.js.org/)
- [Gsender](https://github.com/Sienci-Labs/gsender)
- [bCNC](https://github.com/vlachoudis/bCNC)

```{note}
There is also a prototype Gcode sender Extension for Blender called [gControl](https://github.com/SpectralVectors/gControl) for grbl-based machines - it allows for connection, jog control and sending simple jobs and commands, but should be considered Experimental until further notice.
```