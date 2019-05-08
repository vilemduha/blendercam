# blender CAM testing.py (c) 2012 Vilem Novak
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

import sys
import bpy
from cam import simple, utils
from cam.simple import *


def addTestCurve(loc):
    bpy.ops.curve.primitive_bezier_circle_add(radius=.05, view_align=False, enter_editmode=False, location=loc)
    bpy.ops.object.editmode_toggle()
    bpy.ops.curve.duplicate()
    bpy.ops.transform.resize(value=(0.5, 0.5, 0.5), constraint_axis=(False, False, False),
                             orient_type='GLOBAL', mirror=False, use_proportional_edit=False,
                             proportional_edit_falloff='SMOOTH', proportional_size=1)
    bpy.ops.curve.duplicate()
    bpy.ops.transform.resize(value=(0.5, 0.5, 0.5), constraint_axis=(False, False, False),
                             orient_type='GLOBAL', mirror=False, use_proportional_edit=False,
                             proportional_edit_falloff='SMOOTH', proportional_size=1)
    bpy.ops.object.editmode_toggle()


def addTestMesh(loc):
    bpy.ops.mesh.primitive_monkey_add(radius=.01, view_align=False, enter_editmode=False, location=loc)
    bpy.ops.transform.rotate(value=-1.5708, axis=(1, 0, 0), constraint_axis=(True, False, False),
                             orient_type='GLOBAL')
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.primitive_plane_add(radius=1, view_align=False, enter_editmode=False, location=loc)
    bpy.ops.transform.resize(value=(0.01, 0.01, 0.01), constraint_axis=(False, False, False),
                             orient_type='GLOBAL')
    bpy.ops.transform.translate(value=(-0.01, 0, 0), constraint_axis=(True, False, False),
                                orient_type='GLOBAL')

    bpy.ops.object.editmode_toggle()


def deleteFirstVert(ob):
    activate(ob)
    bpy.ops.object.editmode_toggle()

    bpy.ops.mesh.select_all(action='DESELECT')

    bpy.ops.object.editmode_toggle()
    for i, v in enumerate(ob.data.vertices):
        v.select = False
        if i == 0:
            v.select = True
    ob.data.update()

    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.delete(type='VERT')
    bpy.ops.object.editmode_toggle()


def testCalc(o):
    bpy.ops.object.calculate_cam_path()
    deleteFirstVert(bpy.data.objects[o.name])


def testCutout(pos):
    addTestCurve((pos[0], pos[1], -.05))
    bpy.ops.scene.cam_operation_add()
    o = bpy.context.scene.cam_operations[-1]
    o.strategy = 'CUTOUT'
    testCalc(o)


def testPocket(pos):
    addTestCurve((pos[0], pos[1], -.01))
    bpy.ops.scene.cam_operation_add()
    o = bpy.context.scene.cam_operations[-1]
    o.strategy = 'POCKET'
    o.helix_enter = True
    o.retract_tangential = True
    testCalc(o)


def testParallel(pos):
    addTestMesh((pos[0], pos[1], -.02))
    bpy.ops.scene.cam_operation_add()
    o = bpy.context.scene.cam_operations[-1]
    o.ambient_behaviour = 'AROUND'
    o.material_radius_around_model = 0.01
    bpy.ops.object.calculate_cam_path()


def testWaterline(pos):
    addTestMesh((pos[0], pos[1], -.02))
    bpy.ops.scene.cam_operation_add()
    o = bpy.context.scene.cam_operations[-1]
    o.strategy = 'WATERLINE'
    o.pixsize = .0002
    # o.ambient_behaviour='AROUND'
    # o.material_radius_around_model=0.01

    testCalc(o)


# bpy.ops.object.cam_simulate()


def testSimulation():
    pass;


def cleanUp():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    while len(bpy.context.scene.cam_operations):
        bpy.ops.scene.cam_operation_remove()


def testOperation(i):
    s = bpy.context.scene
    o = s.cam_operations[i]
    report = ''
    report += 'testing operation ' + o.name + '\n'

    utils.getPath(bpy.context, o)

    newresult = bpy.data.objects[o.path_object_name]
    origname = "test_cam_path_" + o.name
    if origname not in s.objects:
        report += 'operation test has nothing to compare with, making the new result as comparable result.\n\n'
        newresult.name = origname
    else:
        testresult = bpy.data.objects[origname]
        m1 = testresult.data
        m2 = newresult.data
        test_ok = True
        if len(m1.vertices) != len(m2.vertices):
            report += "vertex counts don't match\n\n"
            test_ok = False
        else:
            different_co_count = 0
            for i in range(0, len(m1.vertices)):
                v1 = m1.vertices[i]
                v2 = m2.vertices[i]
                if v1.co != v2.co:
                    different_co_count += 1
            if different_co_count > 0:
                report += 'vertex position is different on %i vertices \n\n' % (different_co_count)
                test_ok = False
        if test_ok:
            report += 'test ok\n\n'
        else:
            report += 'test result is different\n \n '
    print(report)
    return report


def testAll():
    s = bpy.context.scene
    report = ''
    for i in range(0, len(s.cam_operations)):
        report += testOperation(i)
    print(report)


tests = [
    testCutout,
    testParallel,
    testWaterline,
    testPocket,

]

cleanUp()

# deleteFirstVert(bpy.context.active_object)
for i, t in enumerate(tests):
    p = i * .2
    t((p, 0, 0))
#	cleanUp()


# cleanUp()
