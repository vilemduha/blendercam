# FAQ

## What happened to **BlenderCAM**? Why did the name change?
**Blender Foundation** owns the rights to the name **Blender** and they have requested that external projects not use their name or logo. **BlenderCAM** used both the name and logo, and so both needed to change.

For a time, seeing the word **Blender** in a product name would mean that it was made _for_ **Blender**, but from now on it will mean that it is made _by_ **Blender**.

**FabexCNC** was chosen because it combines _fabrication_ with _extension (the new format and location in **Blender**)_. 

CNC replaced CAM in the name as it seemed more widely recognizable, and avoids any confusion between **CAM** *(Computer-Aided-Machining)* *and* **Camera** *(abbreviated to Cam)* that may come from **Blender**'s many Camera-related functions and settings.

```{note}
**Fabex** was **BlenderCAM** (now it is **Fabex** _not_ **BlenderCAM**), it hasn't been a long time now, since **BlenderCAM** and still a machinist's delight, on a moonlit night. 
```

---
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
---
## When will you have full support for 4 and 5 Axis Operations?
None of the developers currently have access to a 4+ Axis machine, so until one of the developers acquires a 4th axis, or someone with a 4+ axis machine joins the development team, 4 and 5 axis Operations will remain officially unsupported (outside of manual indexing).

---
## When will the Experimental features become Stable?
The short answer is: it depends.

The long answer is: there are generally 2 reasons why a feature is marked Experimental:

- It was developed for a specific machine or operation that cannot currently be tested or verified.

  *or*

- It worked with some previous combination of Python and **Blender** versions and needs to be rewritten.

**Fabex** has been in continuous development since 2012, between Python 2 - 3.11, **Blender** 2.7 - 4.2, and 30+ volunteer developers with different machines, needs and approaches to coding.

Everyone puts in effort to make sure that all of **Fabex**'s features are supported and stable, but sometimes a feature will be introduced by someone who stops development, the feature will rely on a deprecated Python or **Blender** function, or there might be an intermittent issue that is difficult to diagnose.

It is not always possible to resolve these problems quickly, and there may be other users who are not experiencing any issues with the same feature who do not want it to be removed because someone else filed a Bug Report.

In these cases, a feature may be marked Experimental and, like 4+ axis operation, it may have to wait until a developer with the right combination of experience and equipment is available to develop, test and stabilize it.

---
## What should I do if something in **Fabex** isn't working?
The first step is to check the docs or the [chat](https://riot.im/app/#/room/#blendercam:matrix.org) to make sure that it is supposed to work the way you think.

The next step is to check the Known Issues - long-standing bugs and workarounds will be posted there.

After that, you can file a Bug Report!

```{note}
*Some tools will only work with a mesh, others will only work with a curve, while others will accept any type of object. 

Some CAM options will ONLY appear with certain Milling Strategies - e.g. the **Parallel** strategy has a **Stepover** option, but the **Drill** strategy does not.*
```

---
## How Do I File a Bug Report?
On **Github**, in the **Fabex** repository, click Issues.

Check to see if any of the **Open Issues** deal with the same problem you faced - someone else may have found a fix!

If not, click the **New Issue** button.

On the next screen, click **Bug Report**.

A template is provided for you, and though you don't need to follow it exactly, it helps to at least include:
- your OS
- your **Blender** version number
- your **Fabex** version number
- a description of what the bug is
- steps to take for a developer to reproduce the bug

Bonus points for including:
- a .blend file where the bug can be recreated
- the Error message from the console
- your Python version _(just kidding, it's 3.11!)_

---
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

And you can always check in with the [chat!](https://riot.im/app/#/room/#blendercam:matrix.org)

---
## Can I use Fabex with **Blender** 3 and earlier? Why support 4.2.1 and later?
If you want to use **Fabex** with earlier versions of **Blender** then you need to use on of the **blendercam.zip** releases, and you will also have to manually manage the Python dependencies (opencamlib, shapely), which might involve admin privilege.

**Blender** 4.2 came with the Extensions system, which offered two benefits:
- one-click install for official Extensions
- a Python dependency management solution

It also came with a bug in the Preset system, which was patched in 4.2.1, and so, 4.2.1 became the start of support for **Fabex**.

Since difficulty with installation and cross-platform support were some of the more common issues with **BlenderCAM** it was decided to pursue the Extension platform which offered solutions for both.

Unfortunately, the Extension system is not without issues, leading to the next most frequently asked question...

---
## I can't install or enable **Fabex**, what's going on?
*Or - 'I get an error that says `No module name 'shapely.lib'`, but I can still `import shapely`'*

**Blender** officially supports Python 3.11. At the time of this writing, Python 3.13 is the latest release.

Users whose **Blender** installs do not come from the **Blender** website may not come with their own Python binary, and will fall back on their system's Python installation.

If this is Python 3.12 or higher, then **Fabex** will not work, but most of **Blender** still will.

If you are not comfortable with Python version or dependency management, then the easiest option is to just download **Blender** from their website - it will include Python 3.11, and **Fabex** and all other Extensions will work.

If you have installed **Blender** from a package manager and you want to make **Fabex** work, you have a couple of options:
- manually manage the dependencies by `pip install`-ing `shapely`, and `opencamlib`
- manually manage Python versions by installing 3.11, or using a version management tool like `pyenv`

---
## Where is **Fabex** installed?
### Linux
`$HOME/.config/blender/4.3/extensions/user_default/fabex/`
### macOS
`/Users/$USER/Library/Application Support/Blender/4.3/extensions/user_default/fabex/`
### Windows
`%USERPROFILE%\AppData\Roaming\Blender Foundation\Blender\4.3\extensions\user_default\fabex`
```{note}
If you choose the Developer Install option you will create a symlink for the `cam` folder and place it in the `user_default` folder described above.

The location of this addon changed with the introduction of the Extension system, the old file path was `blender/4.3/scripts/addons/cam`.
```

---
## How Do I Add a Post-Processor?
If you find that your post-processor is not included with the addon, and the ISO post-processor does not work for you, or you simply wish you write your own, it is possible to add a custom post-processor to **Fabex**.

This is considered **Experimental**, and a more advanced use case, all the prior **warnings** about **safety** apply here, and more!

**Fabex**'s post-processors are a modified version of the [`nc` *(Numerical Control)*](https://github.com/danheeks/PyCAM/tree/master/nc) module of [Dan Heeks](https://github.com/danheeks)' [PyCAM](https://github.com/danheeks/PyCAM).

As such, you can use his [documentation as a guide to edit post-processor files.](https://sites.google.com/site/heekscad/help/editing-post-processor-script-files)

We have had a user report successfully implementing their own custom post-processor using the following steps:

- go to the `post-processors` folder
- `grbl` is a good choice to customize as it is a single file, some of the others are 2 or more separate files
- after creating and customizing your post-processor file, you will need to add the code that allows the addon to load it inside **Blender**
- ~line 135 in the gcodepath file is where all the post-processors are listed for the actual calculation part
- ~line 23 in the machine_settings file is where the post-processors are listed in the UI

So, write your post-processor, place it in the nc folder, then add references to it in the gcodepath and machine_settings files and you should be able to select and use your custom post-processor.

Again, please double-check all your code to ensure that it is outputting what you expect, we do not currently have any way to test custom Post Processors, so we are depending on users to solve their own issues.

---
## My CNC uses a Router, how do I set Spindle Speed (RPM)?
Thanks to the efforts of people with access to tachometers and high-speed cameras, we know that an off-the-shelf trim router *(e.g. Makita RT0701C, DeWalt DWP611)* will have a range of roughly 10,000 - 30,000 RPM.

Routers generally cannot spin as slow as Spindles, they have less power, and typically aren't made to the same kinds of tolerances as a Spindle, so the range may vary.

Some tests showed Routers spinning as low as 7,000 - 9,000, or reaching a maximum of 24,000, but as a general rule of thumb you can consider the power dial on your router *(e.g. 1 - 6)* to correspond to a range of ~10,000 - 30,000 RPM.

---
## What do I do if I have a question that isn't covered in the FAQ or elsewhere in the docs?
Your best bet is to ask in the [chat.](https://riot.im/app/#/room/#blendercam:matrix.org)

---