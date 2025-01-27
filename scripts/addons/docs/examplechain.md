# Example Chain Workflow

1. Convert model from CSG to mesh (in this example FreeCAD is used for conversion). Precision setting is very important for correct result.

![Tesselation with Freecad](_static/tesselation.png)

![Result with Freecad](_static/partFreecad.png)

2. Save mesh as PLY or STL.

3. Import mesh to Blender.

![Import Stl](_static/importStl.png)

4. use and apply 'Egde Split' modifier.

![Edge split modifier](_static/edgeSplit.png)

5. Enter Edit Mode and select surface (in Face Select mode) that will be a curve source, and 'Separate' it. Use Select Linked (L shortcut) to select whole faces.

![Separate selection](_static/partObjSep.png)

6. Repeat with other curve sources.

![Separate selection 2](_static/partObjSep2.png)

7. Use 'Set Origin to Geometry' on all separated surfaces.

![Separate selection 2](_static/partOrigGeo.png)

8. Exit Edit Mode and select separated surfaces. Convert them to curves using 'Convert to' (Alt C).

![Convert to curve](_static/partConvert.png)

or you can use "Object silhouette" from blendercam tool :

![Cam Panel](_static/curvecampanel.png)

![Object silhouette](_static/partObjectSil.png)

9. Edit curves to separate holes from external contour.

![Object silhouette](_static/partSeparateHoles.png)

10. Add Pocket and Profile operations : 

![Pocket 1](_static/partPocket1.png)
![Pocket 2](_static/partPocket2.png)
![Profile 1](_static/partProfile1.png)
![Profile 2](_static/partProfile2.png)

for pads/pockets (some curves need to be modified in 'Edit Mode'):

It's highly recommended to create roughing and finishing pass. For roughing pass add offset by altering cutter's diameter. For Profile operation, 'First Down' and 'Ramp In' options are recommended. 'First Down' helps avoid non-cutting moves and 'Ramp In' reduces cutter load by avoiding vertical plunge into material. For Pocket operation instead of 'Ramp In' try using 'Helix enter' option.


