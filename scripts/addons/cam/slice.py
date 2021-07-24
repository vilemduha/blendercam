# blender CAM slice.py (c) 2021 Alain Pelletier
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ***** END GPL LICENCE BLOCK *****

# very simple slicing for 3d meshes, useful for plywood cutting.
# completely rewritten April 2021

import bpy

from cam import utils



def slicing2d(ob, height):  # April 2020 Alain Pelletier
    # let's slice things
    bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)
    bpy.ops.object.mode_set(mode='EDIT')  # force edit mode
    bpy.ops.mesh.select_all(action='SELECT')  # select all vertices
    # actual slicing here
    bpy.ops.mesh.bisect(plane_co=(0.0, 0.0, height), plane_no=(0.0, 0.0, 1.0), use_fill=True, clear_inner=True,
                        clear_outer=True)
    # slicing done
    bpy.ops.object.mode_set(mode='OBJECT')  # force object mode
    # bring all the slices to 0 level and reset location transform
    ob.location[2] = -1 * height
    bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)
    bpy.ops.object.convert(target='CURVE')  # convert it to curve
    if bpy.context.active_object.type != 'CURVE':  # conversion failed because mesh was empty so delete mesh
        bpy.ops.object.delete(use_global=False, confirm=False)
        return False
    bpy.ops.object.select_all(action='DESELECT')  # deselect everything
    return True

def slicing3d(ob, start, end):  # April 2020 Alain Pelletier
    # let's slice things
    bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)
    bpy.ops.object.mode_set(mode='EDIT')  # force edit mode
    bpy.ops.mesh.select_all(action='SELECT')  # select all vertices
    # actual slicing here
    bpy.ops.mesh.bisect(plane_co=(0.0, 0.0, start), plane_no=(0.0, 0.0, 1.0), use_fill=False, clear_inner=True,
                        clear_outer=False)
    bpy.ops.mesh.select_all(action='SELECT')  # select all vertices which
    bpy.ops.mesh.bisect(plane_co=(0.0, 0.0, end), plane_no=(0.0, 0.0, 1.0), use_fill=True, clear_inner=False,
                        clear_outer=True)
    # slicing done
    bpy.ops.object.mode_set(mode='OBJECT')  # force object mode
    # bring all the slices to 0 level and reset location transform
    ob.location[2] = -1 * start
    bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)

    bpy.ops.object.select_all(action='DESELECT')  # deselect everything


def sliceObject(ob):  # April 2020 Alain Pelletier
    # get variables from menu
    thickness = bpy.context.scene.cam_slice.slice_distance
    slice3d = bpy.context.scene.cam_slice.slice_3d
    indexes = bpy.context.scene.cam_slice.indexes
    above0 = bpy.context.scene.cam_slice.slice_above0
    # setup the collections
    scollection = bpy.data.collections.new("Slices")
    bpy.context.scene.collection.children.link(scollection)
    if indexes:
        tcollection = bpy.data.collections.new("Text")
        bpy.context.scene.collection.children.link(tcollection)

    # show object information
    print(ob.dimensions)
    print(ob.location)

    layeramt = 1 + int(ob.dimensions.z // thickness)  # calculate amount of layers needed

    bpy.ops.object.mode_set(mode='OBJECT')  # force object mode
    minx, miny, minz, maxx, maxy, maxz = utils.getBoundsWorldspace([ob])

    start_height = minz
    if above0 and minz < 0:
        start_height = 0

    layeramt = 1 + int((maxz - start_height) // thickness)  # calculate amount of layers needed

    for layer in range(layeramt):
        height = round(layer * thickness, 6)  # height of current layer
        t = str(layer) + "-" + str(height * 1000)
        slicename = "slice_" + t  # name for the current slice
        tslicename = "t_" + t  # name for the current slice text
        height += start_height
        print(slicename)

        ob.select_set(True)  # select object to be sliced
        bpy.context.view_layer.objects.active = ob  # make object to be sliced active
        bpy.ops.object.duplicate()  # make a copy of object to be sliced
        bpy.context.view_layer.objects.active.name = slicename  # change the name of object

        obslice = bpy.context.view_layer.objects.active  # attribute active object to obslice
        scollection.objects.link(obslice)  # link obslice to scollecton
        if slice3d:
            slicing3d(obslice, height, height + thickness)  # slice 3d at desired height and stop at desired height
        else:
            slicesuccess=slicing2d(obslice, height)  # slice object at desired height

        if indexes and slicesuccess:
            # text objects
            bpy.ops.object.text_add()  # new text object
            textob = bpy.context.active_object
            textob.data.size = 0.006  # change size of object
            textob.data.body = t  # text content
            textob.location = (0, 0, 0)  # text location
            textob.name = tslicename  # change the name of object
            bpy.ops.object.select_all(action='DESELECT')  # deselect everything
            tcollection.objects.link(textob)  # add to text collection
            textob.parent = obslice  # make textob child of obslice

    # select all slices
    for obj in bpy.data.collections['Slices'].all_objects: obj.select_set(True)
