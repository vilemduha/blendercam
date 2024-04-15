<div align="center">

![BlenderCAM](documentation/images/logo.png)

- - -

### An Open Source Solution for Artistic or Industrial CAM with Blender 3D

[![Chat on Matrix](https://img.shields.io/matrix/blendercam:matrix.org?label=Chat%20on%20Matrix)](https://riot.im/app/#/room/#blendercam:matrix.org)
[![Chat on Freenode](https://img.shields.io/badge/chat-on%20freenode-brightgreen.svg)](http://webchat.freenode.net/?channels=%23blendercam)

[![Issues](https://img.shields.io/github/issues/vilemduha/blendercam)](https://github.com/vilemduha/blendercam)
![Last commit](https://img.shields.io/github/last-commit/vilemduha/blendercam)
![Contributors](https://img.shields.io/github/contributors/vilemduha/blendercam)

![Size](https://img.shields.io/github/repo-size/vilemduha/blendercam)
![License](https://img.shields.io/github/license/vilemduha/blendercam)

- - -

### •  [About](#About)  •  [How to Use](#-how-to-use-wiki)  •  [Features](#-features)  •  [Post-Processors](#-post-processors)  •  [Files](#-files-organisation)  •  [Contributing](#-contributing)  •  [License](#-license)  •  [Disclaimer](#-disclaimer)  •

- - - 

![BlenderCAM](documentation/images/suzanne.gif)

- - -

</div>

## 👁️ About
BlenderCAM is an add-on for the free open-source [Blender 3D package](https://www.blender.org/).

It offers an open source solution for [CAM _(Computer Aided Machining)_](https://en.wikipedia.org/wiki/Computer-aided_manufacturing) toolpath creation, simulation and [G-code](https://en.wikipedia.org/wiki/G-code) generation and export.

It has been used for many milling projects _(artistic, personal, commercial and industrial)_ since its creation in 2012, and is actively developed. 

> [!NOTE]
> _If you are a developer who would like to help, check out the section on [Contributing](#-contributing)._

## 👨‍🎓 How to Use (Wiki)

![Linux](https://img.shields.io/badge/Platform-Linux%20|%20Windows-brightgreen.svg)

BlenderCAM works on Windows or Linux.

* [BlenderCAM Installation](documentation/Blendercam%20Installation.md)
* [Getting Started](documentation/Getting%20started.md)
* [Panel Descriptions](documentation/Blendercam-Panel-Descriptions.md)
* [Tools](documentation/Blendercam-Tools.md)
* [Example of using Profile and Pocket operations](documentation/Profile%20and%20Pocket%20operations.md)

> [!NOTE]
> BlenderCAM _should_ work on MacOS, but it has not been tested.

## 👌 Features

|                            | Blender from 2.80 to 4.1
| -------------------------- | :----------------: |
| Several Milling Strategies for 2D and 3D          |         ✔️        |
| Cutter Types: Ball, Ballcone, Endmill Flat, V-Carve _(various angles)_, User Defined             |         ✔️         |  
| Work with 3D Data or Depth Images       |         ✔️         |  
| Layers and Skin for Roughing |         ✔️         |  
| Inverse Milling   |         ✔️         |  
| Various Options for Ambient around Model  |         ✔️         |  
| Protection of Vertical Surfaces       |         ✔️         |  
| Stay Low - Option for Movement       |         ✔️         |  
| Material Size Setup  |         ✔️         |  
| Simulation of 3D Operations        |         ✔️         |  
| Arc Retract   |         ✔️         |  
| Pack Curves and Slice Model   |         ✔️         |  
| Automatic Bridges for Cutout Operation   |         ✔️         |  
| Chain Export and Simulation  |         ✔️         |   

### Pending Features
* Helix entry and ramp down are experimental.
* 4 and 5 axis milling are only manual


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
├── config - # 'startup' and 'userpref' blend files
├── documentation - # How to Use (Wiki) - files
├── Examples - # Bas Relief & Intarsion operation demo files and images
├── scripts
│   └── addons
│       └── cam - # Main Addon Folder
│           ├── nc - # Post-Processors
│           ├── opencamlib - # OpenCAMLib functions
│           ├── presets - # Quick access to pre-defined cutting tools, machines and operations
│           │   ├── cam_cutters
│           │   ├── cam_machines
│           │   └── cam_operations
│           ├── tests - # Developer Tests
│           │   └── test_data - # Test output
│           └── ui_panels - # User Interface
└── static - # Logo

```



## 🤝 Contributing
#### BlenderCAM is in active development.

Originally created by [Vilem Novak](https://github.com/vilemduha), the addon is currently maintained by [Alain Pelletier](https://github.com/pppalain) and a team of contributors. 

If you wish to contribute to the addon, your code must be GPL or a more permissive license (e.g.: MIT, Public Domain).

If you are a developer who would like to contribute to the project, please fork and open pull requests.

> [!TIP]
> _If you need help or want to discuss about BlenderCAM you can join the [Chat Room #BlenderCAM:matrix.org on Matrix](https://riot.im/app/#/room/#blendercam:matrix.org)._

### Contributors
<a href="https://github.com/pppalain/blendercam/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=pppalain/blendercam" />
</a>

### Additional Contributors & Acknowledgements
Hirutso Enni, Kurt Jensen, Dan Falck, Dan Heeks, Brad Collette, Michael Haberler, dhull, jonathanwin, Leemon Baird, Devon (Gorialis) R, Steven Fortune, Bill Simons, Carson Farmer, domlysz

## 🪪 License
BlenderCAM is licensed under GPLv3, __UNLESS OTHERWISE INDICATED__.

> [!NOTE]
> Some files in this addon use code from other sources, see the file docstring a the top of each file for attribution and license information.
> 
> Please ensure that you read and abide by the license terms given for each file.

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
