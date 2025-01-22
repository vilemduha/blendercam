<div align="center">

![Fabex CNC CAM extension for Blender](documentation/images/logo.png)

- - -

### An Open Source Solution for Artistic or Industrial CAM with Blender 3D

[![Chat on Matrix](https://img.shields.io/matrix/blendercam:matrix.org?label=Chat%20on%20Matrix)](https://riot.im/app/#/room/#blendercam:matrix.org)

[![Issues](https://img.shields.io/github/issues/vilemduha/blendercam)](https://github.com/vilemduha/blendercam)
![Last commit](https://img.shields.io/github/last-commit/vilemduha/blendercam)
![Contributors](https://img.shields.io/github/contributors/vilemduha/blendercam)

![Size](https://img.shields.io/github/repo-size/vilemduha/blendercam)
![License](https://img.shields.io/github/license/vilemduha/blendercam)

- - -

### [About](#-about) • [How to Use](#-how-to-use-wiki) • [Features](#-features) • [Post-Processors](#-post-processors) • [Files](#-files-organisation) • [Contribute](#-contribute) • [License](#-license) • [Disclaimer](#-disclaimer)

- - - 

![Fabex CNC CAM extension for Blender](documentation/images/suzanne.gif)

- - -

</div>

## 👁️ About
[**Fabex CNC CAM extension for Blender**](https://blendercam.com/) is an open source solution for artistic, personal, commercial or industrial CAM - Computer aided machining - a g-code generation tool.  It was called Blendercam but the name Blender can no longer be used in the name due to Trademark.


It has been used for many milling projects _(artistic, personal, commercial and industrial)_ since its creation in 2012, and is actively developed. 

> [!NOTE]
> _If you are a developer who would like to help, check out the section on [Contributing](#-contribute)._

## 👨‍🎓 How to Use (Wiki)

![Linux](https://img.shields.io/badge/Plateform-Linux%20|%20MacOS%20|%20Windows-brightgreen.svg)

Fabex CNC CAM extension for Blender (formerly Blendercam) works on Windows or Linux and MacOS.

* [Fabex CNC CAM extension Installation](documentation/Blendercam%20Installation.md)
* [Getting Started](documentation/Getting%20started.md)
* [Panel Descriptions](documentation/Blendercam-Panel-Descriptions.md)
* [Tools](documentation/Blendercam-Tools.md)
* [Example of using Profile and Pocket operations](documentation/Profile%20and%20Pocket%20operations.md)

(The full [documentation](https://blendercam.com/documentation/) can also be found on the website)
## 👌 Features

| Feature | Description | Status |
| :---: | :--- | :---: | 
| 2D & 3D Milling Strategies | _Profile, Pocket, Drill, Parallel, Cross, Block, Spiral, Medial Axis and more!_ | ✅ |
| Cutter Types | _Ballnose, Ballcone, Bullnose, Flat Endmill, V-Carve, User Defined and more!_ | ✅ |
| Use 3D Data or 2D Images | _Model an object in Blender, or import any 3D object or Black & White image, and generate toolpaths!_ | ✅ |
| Layers & Skin for Roughing | _Leave material during roughing passes to ensure that your finishing passes have enough to work with_ | ✅ |
| Inverse Milling | _description_ | ✅ |
| Ambient Around Model | _description_ | ✅ |
| Protection of Vertical Surfaces | _description_ | ✅ |
| Stay Low | _Option for Movement_ | ✅ |
| Stock Material Setup | _Set up the dimensions and location of your stock material, or auto-generate them from your 3D model!_ | ✅ |
| Simulation of 3D Operations | _Use your toolpaths to generate a 3D mesh simulation of your finished product!_ | ✅ |
| Arc Retract | _Retracts cutter in an arc, rather than straight lines to reduce travel time_ | ✅ |
| Pack Curves | _Auto-arrange all selected curves to fit on a plywood sheet_ | ✅ |
| Slice Model | _Vertically slices model into a series of curves to be cut and stacked to recreate the 3D shape_ | ✅ |
| Automatic Bridges / Tabs | _One click to add Bridges/Tabs to keep your work in place during Cutout Operations_ | ✅ |
| Chain Export & Simulation | _Combine multiple CAM operations into a Chain, then export them as gcode, or simulate the result of all combined operations!_ | ✅ |
| Adaptive Milling Speed | _Adjusts the operation feedrate relative to the chipload calculation_ | ✅ |
| :warning: Helix Entry :warning: | _EXPERIMENTAL - Available in the Extension, but not yet fully supported_ | ⏳ |
| :warning: Ramp Down :warning: | _EXPERIMENTAL - Available in the Extension, but not yet fully supported_ | ⏳ |
| :warning: 4 Axis Milling :warning: | _Currently only possible via manual indexing_ | ⏳ |
| :warning: 5 axis Milling :warning: | _Currently only possible via manual indexing_ | ⏳ |

> [!NOTE]
> _All features listed above are for Blender 4.2.1 and up. For previous versions of Blender, check the Releases page._

## 💻 Post-processors
* GRBL
* Iso
* LinuxCNC - EMC2
* Fadal
* Heidenhain
* Sieg KX1
* Hafco HM-50
* Centroïd M40
* Anilam Crusader M
* Gravos
* WinPC-NC
* ShopBot MTC
* Lynx Otter o
* ...


## 📒 Files Organisation

```graphql
.
├── config/ - # 'startup' and 'userpref' blend files
├── documentation/ - # How to Use (Wiki) - files
├── Examples/ - # Bas Relief & Intarsion operation demo files and images
├── scripts/
│   └── addons/
│       └── cam/ - # Main Addon Folder
│           ├── operators/ - # Blender Operators
│           ├── post_processors/ - # CAM Post-Processors
│           ├── presets/ - # Quick access to pre-defined cutting tools, machines and operations
│           │   ├── cam_cutters/
│           │   ├── cam_machines/
│           │   └── cam_operations/
│           ├── properties/ - # Blender PropertyGroups to store Machine, Operation, Cutter data
│           ├── tests/ - # Developer Tests
│           │   └── test_data/ - # Test output
│           ├── ui/ - # Blender User Interface
│           │   ├── icons/ - # .png files for custom icons
│           │   ├── menus/
│           │   ├── panels/
│           │   └── pie_menu/
│           ├── utilities/ - # Low level helper functions
│           └── wheels/ - # Python Dependencies (as binary wheels)
└── static/ - # Logo

```



## 🤝 Contribute
#### Fabex CNC CAM extension for Blender is in active development.

Originally created by [Vilem Novak](https://github.com/vilemduha), the addon is currently maintained by [Alain Pelletier](https://github.com/pppalain) and a team of contributors. 

If you are a developer who would like to contribute to the project, please fork and open pull requests.

If you wish to contribute to the addon, your code must be GPL or a more permissive license (e.g.: MIT, Public Domain).

> [!TIP]
> _If you need help or want to discuss about BlenderCAM you can join the [Chat Room #BlenderCAM:matrix.org on Matrix](https://riot.im/app/#/room/#blendercam:matrix.org)._

### Contributors
<a href="https://github.com/pppalain/blendercam/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=pppalain/blendercam" />
</a>

### Additional Contributors & Acknowledgements
Hirutso Enni, Kurt Jensen, Dan Falck, Dan Heeks, Brad Collette, Michael Haberler, dhull, jonathanwin, Leemon Baird, Devon (Gorialis) R, Steven Fortune, Bill Simons, Carson Farmer, domlysz, Mihai Moldoveanu

## 🪪 License
Fabex CNC CAM extension for Blender is licensed under GPLv3, __UNLESS OTHERWISE INDICATED__.

> [!NOTE]
> _Some files in this addon use code from other sources, see the file docstring a the top of each file for attribution and license information._
> 
> _Please ensure that you read and abide by the license terms given for each file._

## 🤕 DISCLAIMER
> [!WARNING]
THE AUTHORS OF THIS SOFTWARE ACCEPT ABSOLUTELY NO LIABILITY FOR
ANY HARM OR LOSS RESULTING FROM ITS USE.
> 
> IT IS _EXTREMELY_ UNWISE
TO RELY ON SOFTWARE ALONE FOR SAFETY.
> 
> Any machinery capable of
harming persons must have provisions for completely removing power
from all motors, etc, before persons enter any danger area.
>
> All
machinery must be designed to comply with local and national safety
codes, and the authors of this software can not, and do not, take
any responsibility for such compliance.
