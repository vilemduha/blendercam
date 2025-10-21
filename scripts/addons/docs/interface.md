# User Interface

**Fabex**'s user interface was designed to facilitate multiple different workflows, layouts and experience levels.

**Fabex** has a lot of functionality, and tries to balance not overwhelming new users with settings they may not need, with giving access to the many parameters necessary for advanced users to complete complex jobs.

**Interface** allows users to hide options below a certain level, simplifying the layout for beginners.
- **Basic** - displays only necessary panels and options
- **Advanced** - displays more panels and options
- **Complete** - displays all Stable options
- **Experimental** - all previous options, plus those marked EXPERIMENTAL

**Layout** will rearrange where the panels are placed onscreen. 
- **Modern** - splits the panels between the Properties and Sidebar areas
- **Classic** - preserves the original BlenderCAM layout
- **User** - can be edited in Preferences

**Shading** offers quick preset viewport settings for users unfamiliar with **Blender**'s interface.
- **Default** - standard **Blender** viewport shading
- **Deluxe** - enables extra shading options to help view mesh details or organize comples scenes
- **Clean Default** - same as Default with the Viewport Grid turned off
- **Clean Deluxe** - same as Deluxe with the Viewport Grid turned off
- **Preview** - enables HDRI and material shaders

## Enter CNC/CAM Mode
**Fabex** hides most of its interface when it is not active. 

To display it you need to enter CNC/CAM mode.

In the **Properties** area, in the **Render** tab, set the **Render Engine** to **Fabex CNC/CAM**

![Renderer selection](_static/RenderEngine.png)

```{note}
*(Most functionality can also be accessed through menus, pie menus or the Search operator.)*
```

## Panels

### [ Operations ]
The **[ Operations ]** panel allows you to add, remove, copy, rename, re-arrange, calculate, export and simulate Operations. 

Click the **+** button to add a new Operation, or choose an Operation Preset.

![CAM operations](_static/OperationsPanelSuzanne.png)
- **Calculate Path & Export Gcode** - This calculates the currently selected operation from the CAM operations list. The Button will stay selected until the calculation is completed.
- **Simulate This Operation** - Works for most 3 axis operations. It creates a new object which shows the simulation - the subdivision of the object can be increased, and the resolution of the simulation also depends on simulation sampling raster detail, which is in the optimization panel
- **Operation Name** - Select this field to change the name of the currently selected operation.
- **File Name** - Name of the Gcode file. _Post Processor sets the file extension. See [Machine](#-machine-)._
- **Data Source** - This can be either 1 object, a group of objects, or an image.
  - **Object** - a **Blender** object.  This could be a mesh, or a curve.
  - **Collection** - Objects can be combined into a Collection in the Outliner.
  - **Image** - Open an image that will be used as a height/depth map.
- **Object** - the **Blender** object that will be used in the CAM operation. Select the object from a drop down list. Write it's name in the field, it should auto-complete and give a list of objects to select from.
```{note}
*If you change the object's name later on then you must also change it here. The field will turn red if the object can not be found.*
```
---
### [ Machine ]
The **[ Machine ]** panel lets you setup your CNC machine parameters within **Blender**. 

You can set up your machine, then save your default file with `Ctrl+U` command. This way you will always start with the settings you need.

![Cam machine](_static/MachineParameters.png)

- **Post Processor** - this defines the formatting of the output file.
- **Unit System** - Metric or Imperial
- **Length Unit** - Feet, Inches, Millimeters, Meters
- **Collet Size**
- **Work Area** - if the Operation has a larger area than this, you will get a warning in the info panel
- **4th Axis** - enable if your machine has a 4th Axis
- **5th Axis** - enable if your machine has a 5th Axis
- **Position Definitions** - set custom positions for job start, end and tool change
- **Feedrate (/min)** - minimum, maximum and default feedrate for the machine
- **Spindle Speed (RPM)** - minimum, maximum and default spindle speed for the machine
- **Machine G-code** - Gcode options to be included in every file produced for this machine
- **Price ($/hour)** - used in the Estimates in the Info Panel

```{note}
If your machine is not in the list, you can try the ISO code, which is standardized Gcode, or see the [FAQ](faq.md) for details on writing your own Post Processor (EXPERIMENTAL!)
```
---
### [ Info ]
The **[ Info ]** panel shows important information about your Operation.

![Cam Info & warnings](_static/InfoPanel.png)

- **Estimates** give rough calculations based on current Operation settings for:
  - **Time** - in hours, minutes and seconds
  - **Chipload** - if applicable, _does not currently include Stepover_
  - **Cost** - based on the **Price** set in the **[ Machine ]** panel and the **Time** estimate above
- **Warnings** will be displayed in **RED** when calculations indicate a problem like:
  - an Operation that exceeds your Machine's Work Area
  - a potential Collision
  - high Cutter engagement

```{note}
**Warnings** should always be heeded, and can usually be fixed by adjusting your Operation parameters. 

Failure to resolve issues with your Operation could result in damage, injury or death. We do our best to ensure that Fabex is safe to use, but we accept no liability for any harm or loss resulting from its use.

**Warnings** are there to keep you, your machine and your material safe, and we urge you to take all necessary precautions when working with CNC Machines.
```
---
### [ Operation Setup ]
The **[ Operation Setup ]** panel gives you access to milling strategies and settings specific to those strategies.

![Strategy](_static/OperationSetupPanel.png)

- **Axis Count** - how many axes will be used _(Default is 3, additional axes should be enabled in the Machine panel first)_
- **Strategy** sets one of the milling strategies.

Depending on which **Strategy** is selected, the options will differ. Below is a sampling of some common settings: 
- **Inverse Milling** - used if you want to mill a form directly from positive of the object. Does not work in exact mode. Only works for 3 axis strategies.
- **Skin** - useful for roughing, leaves a layer on the surface for finishing
- **Angle of Paths** - this rotates the parallel and cross strategies by the specified amount. Note that e.g. rotating by 90 changes the basic axis from X to Y
- **Toolpath Distance**
  * **Between** - also called Stepover
  * **Along** - how dense will be the operation path. This can influence accuracy of the machining. 
- **Direction** - for Block and Spiral strategy, decides if the path progresses from inside or from outside
- **Carve** 
  * **Depth** - decides how deep below the surface will go the carve operation
- **Outlines**
  * **Don't Merge** - for cutout strategy. Does not merge outlines - this results into cutting in the object area! It is usefully when milling PCBs, where you don't need exact shape but need to separate areas with engraving.
- **Bridges (Tabs)** - for cutout operation, places automatically bridges by the rules set by options that will appear after this is enabled: width, height, minimum per curve, distance.
```{note}
*(see the [Strategies](strategies.md) page for a full list of options for each Strategy)*
```
---
### [ Operation G-code ]
The **[ Operation G-code]** panel lets you specify commands or macros to be executed at the beginning and end of Operations.

The Gcode options in the **[ Machine ]** panel are global across all Operations, while the **[ Operation G-code ]** panel options apply only to the current Operation.

![](_static/OperationGcodePanel.png)

- **Output Header**
- **Output Trailer**
- **Dust Collector**
- **Hold Down**
- **Mist**
---
### [ Optimization ]
The **[ Optimisation ]** panel is crucial for performance. 

Toolpaths and Simulations can quickly end up with many points to calculate, and if you accidentally try to calculate a giant toolpath with a tiny resolution then you could run out of memory and crash.

These settings allow you to balance performance and accuracy by limiting how many points will be generated in the toolpaths and simulations.

![Cam Optimization](_static/OptimisationPanel.png)

* **Reduce Path Points** - reduces number of commands in the operation, so the resulting gcode is shorter and can run smoother on the machine
  * **Threshold (um)** - points with smaller distance (in micrometers) to the path direction will be reduced
* **Exact mode** - exact mode is related to the strategies that are fully 3d - parallel, cross, block, spiral, circles, waterline, outline fill, carve. It's a very important setting.
  * **Non exact mode:** In non-exact mode, an image is used to estimate the cutter offsets, and the Sampling raster detail is used to estimate the resolution of the image. Non exact mode is good for high poly meshes, several millions of polygons shouldn't be problem for it, but the sampling raster detail setting is crucial then. Memory overflow can happen if you use e.g. default blender cube that you have by startup, since the cube is 2 meter in size in blender units. For artistic use with high poly meshes, non exact mode is good for most of the cases.
  * **Exact mode:** a real collision simulation is used, so the collisions are exact. But the speed goes down with increasing number of polygons. It is recommended in these situations: Your model is too big for the non exact mode, you need high precision, your model doesn't have too many faces.
* **Sampling raster detail** - this parameter is crucial for memory use and mainly speed of blender CAM. In non-exact mode, blenderCAM uses an image to compute the cutter offset positions. If the raster detail is 0.1mm, then a 10x10 cm object will use a 1000x1000 image. If the object size would be 1m, the image would be 10000 x 10000 pixels, which will probably fill the memory of your computer. Check your object size before computing operations.
* **Simulation sampling raster detail** - same as sampling raster detail, but only for simulation
* **Detail of circles used for curve offsets** - exactly what it says
* **Use OpenCAMLib** - use external library for calculating toolpaths, improving toolpath quality (especially with waterlines) and calculation time. Has to be used with exact mode. [[Using-BlenderCAM-with-OpenCAMLib]]
---
### [ Operation Area ]
The **[ Operation Area ]** panel controls the area where the Cutter is allowed to move and sets limits on depth and travel height.

![CAM Operation Area](_static/OperationArea.png)

- **Z Clearance**
  - **Safe Height** - how high will the cutter travel when moving between toolpaths.  Keep it as low as possible to reduce total cutting time.  The Z axis usually has the slowest rapid rates compared to the other two axis X and Y.
- **Operation Depth**
  - **Start**
  - **Max**
    - **Object** - takes object depth and sets up the total depth of the operation from it. Otherwise, you can use Operation depth to do the same manually.
- **Layers** - sets up layers for roughing.
  - **Layer Height** - specifies thickness of the layers for roughing
- **Ambient** - how much space surrounding the object will be used for the milling
  - **Surfaces All** - a rectangular area will be used
  - **Surfaces Around** - object silhouette will be used, with a radius specified by Ambient radius
---
### [ Material ]
The **[ Material ]** panel handles the size and position of your stock material - the raw material that you are planning to mill. You can enter values manually, or allow Fabex to calculate them for you based on the object you have selected.

![CAM material size and position](_static/MaterialPanel.png)

- **Size**
  - **Size from Model** - will assume the workpiece/material has the same size as the model, with radius around the model.
  If not enabled then the Material origin and Material size are used in case when the material/workpiece is not the same as the model.  The 3D view will show the machine work area with a hashed outline and the material size and position will be a lighter grey.  The material object is not selectable in the 3D view but can be selected in the Outliner and has the name CAM_Material.
  - **Additional Radius**
- **Position**
  -  **Center on X Axis**
  -  **Center on Y Axis**
  -  **Z Placement**
  - **Position Object** - this will move the object to positive X and Y and negative Z so that it is fully in the work area and closest to the origin.
---
### [ Movement ]
The **[ Movement ]** panel handles how the Cutter moves during the Operation, the direction the Cutter spins, and has a little overlap with the **[ Operation Area ]** panel for the most important settings.

![CAM Movement](_static/MovementPanel.png)

- **Milling Type** - is supported only for some of the strategies, sets up how the cutter moves into the material
  - **Meander/ZigZag** - sometimes also called ZigZag , this means you don't care which direction the cutter goes into the material.
  - **Climb/Down Milling** - the default movement, and mostly used when doing CNC machining if the machine has no or very little backlash. The cutter rotates with the direction of the feed. It can produce a better finish, less stress on the bit, and less power required. If the machine has backlash then Conventional milling is a better choice.
  - **Conventional/Up Milling** - The cutter rotates against the direction of the feed.  If the machine has backlash that can not be compensated for then this is the better choice.  Some woods cut better with this method but grain direction also has to be considered.
- **Cutter Spin** - this parameter is not exported, but it is used when setting up the movement type, because with the spindle rotating CCW, all operations go in opposite direction.
- **Z Clearance**
  - **Safe Height** - how high will the cutter travel when moving between toolpaths.  Keep it as low as possible to reduce total cutting time.  The Z axis usually has the slowest rapid rates compared to the other two axis X and Y.
- **Stay Low if possible** - tries to not lift the cutter when going from 1 path to other, when the paths are closer to each other than the cutter radius, which means no extra material will be cut during this travel move.
- **Parallel Step Back** - this function is only for finishing pass, where you still have to cut some substantial amount of material, and want also to save the cutter. If you set up to climb movement, it goes with climb into material, then goes in the other direction one step back - this uses the back movement of the machine for finishing the surface. Note that this also means the cutting into material will happen with a rate which is 2x of distance between toolpaths If you don't know what this all means, don't use this function.
- **G64 Trajectory** This enables the "naive cam detector" and enables blending with a tolerance. If you program G64 P0.05, you tell the planner that you want continuous feed, but at programmed corners you want it to slow down enough so that the tool path can stay within 0.05 user units of the programmed path. The exact amount of slowdown depends on the geometry of the programmed corner and the machine constraints, but the only thing the programmer needs to worry about is the tolerance. This gives the programmer complete control over the path following compromise. 
- **Protect vertical** - when the angle of the path is above verticality limit, the move will be made vertical. this way vertical surfaces won't get a slope because of the distance between the path points.
- **First down** - for cutout strategy. If on, the paths are cut one by one to the full depth(all layers), otherwise first all the silhouettes are cut on layer 1, then 2....
- **Ramp Contour** - for cutout strategy, instead of going layer by layer, it goes down all the way on a ramp.
- **Ramp Out** - also going out is performed on a ramp, to prevent burning of the finished piece by staying on one place in XY axes.
---
### [ Feedrate ]
The **[ Feedrate ]** panel sets the Operation feedrate, Cutter speed and more.

![CAM feedrate](_static/FeedratePanel.png)

- **Feedrate (/min)** - How much will the machine travel in 1 minute
- **Spindle (RPM)** - spindle revolutions per minute
- **Plunge**
  - **Speed** - the feed speed gets reduced when the slope of the path is above the Plunge angle
  - **Angle** - any angle greater than the plunge angle will activate plunge speed
---
### [ Cutter ]
The **[ Cutter ]** panel allows you to select a pre-defined cutting tool, or define your own with custom Tool Number and Description.

![CAM cutter](_static/CutterPanel.png)

* **Type** - supported types are listed in the table below
* **Diameter** - The exact diameter of the cutting tool.  _Used in toolpath calculation.  For V-bits its the maximum diameter of the bit._
* **Flutes** - this parameter is used only for chipload computation.
* **Tool Number** - this parameter is exported with toolchange command
* **Description** - A description of the tool.  Currently this is not used for anything.
* **Cutter object** - a 3D object of your choice available in the drop down list.

| Cutter Types  |   |
|----------:|---|
| End      | ![End](_static/cut-end.jpg)  |
| Ballnose | ![Ballnose](_static/cut-ballnose.jpg)  |
| Bullnose | ![Bullnose](_static/cut-bullnose.jpg)  |
| V-Carve  |  ![v-carve](_static/cut-v-carve.jpg) |
| Ballcone |  ![Ballcone](_static/cut-ballcone.jpg) |
| Laser    |  ![Laser](_static/cut-laser.jpg) |
| Custom   |  ![Custom](_static/cut-custom.jpg) |

---
### [ Chains ]
The **[ Chains ]** panel allows you to combine multiple operations. It is useful for simulating more operations or exporting a chain of operations if you have automatic toolchanger or use the same tool for several operations.

![New chain](_static/ChainsPanel.png)

## Menus
Many of **Fabex**'s Tools can be accessed through the **Fabex CNC** menus located in the 3D viewport.

![](_static/FabexMenus.png)

## Pie Menu
**Fabex**'s entire panel, tool and menu layout can also be accessed through a multi-level Pie Menu system.

![](_static/FabexPieMenu.png)

```{note}
The Pie Menu is bound to the shortcut - `Alt + C` by default, but can be changed in Preferences.
```

## Search Operator (F3)
Any of **Fabex**'s Operators can be searched and executed using Blender's built-in Search Operator, activated with F3.

![](_static/F3Search.png)