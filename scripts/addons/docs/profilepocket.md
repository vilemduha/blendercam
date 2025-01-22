# Profile & Pocket (Step-by-Step)

1. Convert model from CSG to mesh (in this example FreeCAD is used for conversion). Precision setting is very important for correct result.

![Tesselation with Freecad](images/tesselation.png)

![Result with Freecad](images/partFreecad.png)

2. Save mesh as PLY or STL.

3. Import mesh to Blender.

![Import Stl](images/importStl.png)

4. use and apply 'Egde Split' modifier.

![Edge split modifier](images/edgeSplit.png)

5. Enter Edit Mode and select surface (in Face Select mode) that will be a curve source, and 'Separate' it. Use Select Linked (L shortcut) to select whole faces.

![Separate selection](images/partObjSep.png)

6. Repeat with other curve sources.

![Separate selection 2](images/partObjSep2.png)

7. Use 'Set Origin to Geometry' on all separated surfaces.

![Separate selection 2](images/partOrigGeo.png)

8. Exit Edit Mode and select separated surfaces. Convert them to curves using 'Convert to' (Alt C).

![Convert to curve](images/partConvert.png)

or you can use "Object silhouette" from blendercam tool :

![Cam Panel](images/curvecampanel.png)

![Object silhouette](images/partObjectSil.png)

9. Edit curves to separate holes from external contour.

![Object silhouette](images/partSeparateHoles.png)

10. Add Pocket and Profile operations : 

![Pocket 1](images/partPocket1.png)
![Pocket 2](images/partPocket2.png)
![Profile 1](images/partProfile1.png)
![Profile 2](images/partProfile2.png)

for pads/pockets (some curves need to be modified in 'Edit Mode'):

It's highly recommended to create roughing and finishing pass. For roughing pass add offset by altering cutter's diameter. For Profile operation, 'First Down' and 'Ramp In' options are recommended. 'First Down' helps avoid non-cutting moves and 'Ramp In' reduces cutter load by avoiding vertical plunge into material. For Pocket operation instead of 'Ramp In' try using 'Helix enter' option.


