# Installation

**FabexCNC** is an Extension for **Blender** v4.21 and later.

```{note}
To use **Fabex** with **Blender** 4.1 and earlier use one of the **blendercam.zip** releases from the Github Releases page.
```

## Get Blender
[Download Blender from the official site.](https://www.blender.org/download/)

```{note}
If you are a Linux user, it is recommended that you download **Blender** from their website, and **NOT install via a Package Manager.**
**Blender** has elected to support only Python 3.11 for Extensions, so Fabex is packaged with dependencies that are only compatible with Python 3.11.
Since many distros will allow you to install **Blender** and Python separately this can lead to version mismatch and a broken Extension.

*For details on how to work around this issue, see the FAQ.*
```
## Get Fabex
### For Users
#### Stable Version
[Download the Stable version here.](https://github.com/vilemduha/blendercam/releases)

The Stable version will not have all the latest features right away, but it is more thoroughly tested and generally more reliable than the latest version. 

```{note}
_If you're not sure which version you want, then you probably want the Stable version!_
```

#### Experimental Version
[Download the Experimental version here.](https://github.com/pppalain/blendercam/releases)

The Experimental version will have all the latest features, but is more likely to encounter bugs and errors and is recommended for more experienced users, developers and testers.

```{note}
[The latest (Daily) build of Blender](https://builder.blender.org/download/daily/) can be used with the Experimental branch of FabexCNC to live on the bleeding edge!
```

From the Releases page, download **fabexcnc.zip**.

*(Don't extract it, Blender is expecting a .zip file!)*

#### Install Fabex
- Open **Blender**
- Click **Edit** > **Preferences** > **Get Extension**

![image](https://github.com/user-attachments/assets/7776b3dd-2411-4348-b4d7-b0262f683f90)
- Click the small arrow in the top right of the window, then click **Install from Disk**

![image](https://github.com/user-attachments/assets/1bec6168-5b57-48c4-afe7-310664fa979d)
- Select the **fabexcnc.zip** file you downloaded, then click **Install from Disk**
- Blender may need to be restarted to ensure the dependencies are correctly installed.

```{note}
*If you experience difficulty installing the Extension, check out the FAQ for common installation issues and fixes, or try the Matrix chat for help from developers and other users.*
```

You're now ready to start using **Fabex**!

```{note}
*If you're not sure what to do next, check out the [Getting Started](starting.md) page.*
```

### For Developers
If you intend to contribute to the **Fabex** codebase, or if you want to modify the Extension to suit your own needs, you may find that the installation method outlined above is not the best for rapid iteration and updates.

For these users we recommend cloning the repository from Github, then creating a symlink (alias, shortcut) for the **'cam'** folder and moving that into [Blender's Extension directory.](https://docs.blender.org/manual/en/latest/advanced/blender_directory_layout.html)

For more details, see the [Developers Guide](developers.rst) and the [FAQ](faq.md).