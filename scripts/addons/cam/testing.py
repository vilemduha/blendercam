"""Fabex 'testing.py' © 2012 Vilem Novak

Functions for automated testing.
"""

import bpy

from .gcode_path import getPath

from .utilities.simple_utils import activate


def addTestCurve(loc):
    """Add a test curve to the Blender scene.

    This function creates a Bezier circle at the specified location in the
    Blender scene. It first adds a primitive Bezier circle, then enters edit
    mode to duplicate the circle twice, resizing each duplicate to half its
    original size. The function ensures that the transformations are applied
    in the global orientation and does not use proportional editing.

    Args:
        loc (tuple): A tuple representing the (x, y, z) coordinates where
            the Bezier circle will be added in the 3D space.
    """
    bpy.ops.curve.primitive_bezier_circle_add(
        radius=0.05, align="WORLD", enter_editmode=False, location=loc
    )
    bpy.ops.object.editmode_toggle()
    bpy.ops.curve.duplicate()
    bpy.ops.transform.resize(
        value=(0.5, 0.5, 0.5),
        constraint_axis=(False, False, False),
        orient_type="GLOBAL",
        mirror=False,
        use_proportional_edit=False,
        proportional_edit_falloff="SMOOTH",
        proportional_size=1,
    )
    bpy.ops.curve.duplicate()
    bpy.ops.transform.resize(
        value=(0.5, 0.5, 0.5),
        constraint_axis=(False, False, False),
        orient_type="GLOBAL",
        mirror=False,
        use_proportional_edit=False,
        proportional_edit_falloff="SMOOTH",
        proportional_size=1,
    )
    bpy.ops.object.editmode_toggle()


def addTestMesh(loc):
    """Add a test mesh to the Blender scene.

    This function creates a monkey mesh and a plane mesh at the specified
    location in the Blender scene. It first adds a monkey mesh with a small
    radius, rotates it, and applies the transformation. Then, it toggles
    into edit mode, adds a plane mesh, resizes it, and translates it
    slightly before toggling back out of edit mode.

    Args:
        loc (tuple): A tuple representing the (x, y, z) coordinates where
            the meshes will be added in the Blender scene.
    """
    bpy.ops.mesh.primitive_monkey_add(
        radius=0.01, align="WORLD", enter_editmode=False, location=loc
    )
    bpy.ops.transform.rotate(
        value=-1.5708, axis=(1, 0, 0), constraint_axis=(True, False, False), orient_type="GLOBAL"
    )
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.primitive_plane_add(radius=1, align="WORLD", enter_editmode=False, location=loc)
    bpy.ops.transform.resize(
        value=(0.01, 0.01, 0.01), constraint_axis=(False, False, False), orient_type="GLOBAL"
    )
    bpy.ops.transform.translate(
        value=(-0.01, 0, 0), constraint_axis=(True, False, False), orient_type="GLOBAL"
    )

    bpy.ops.object.editmode_toggle()


def deleteFirstVert(ob):
    """Delete the first vertex of a given object.

    This function activates the specified object, enters edit mode,
    deselects all vertices, selects the first vertex, and then deletes it.
    The function ensures that the object is properly updated after the
    deletion.

    Args:
        ob (bpy.types.Object): The Blender object from which the first
    """
    activate(ob)
    bpy.ops.object.editmode_toggle()

    bpy.ops.mesh.select_all(action="DESELECT")

    bpy.ops.object.editmode_toggle()
    for i, v in enumerate(ob.data.vertices):
        v.select = False
        if i == 0:
            v.select = True
    ob.data.update()

    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.delete(type="VERT")
    bpy.ops.object.editmode_toggle()


def testCalc(o):
    """Test the calculation of the camera path for a given object.

    This function invokes the Blender operator to calculate the camera path
    for the specified object and then deletes the first vertex of that
    object. It is intended to be used within a Blender environment where the
    bpy module is available.

    Args:
        o (Object): The Blender object for which the camera path is to be calculated.
    """
    bpy.ops.object.calculate_cam_path()
    deleteFirstVert(bpy.data.objects[o.name])


def testCutout(pos):
    """Test the cutout functionality in the scene.

    This function adds a test curve based on the provided position, performs
    a camera operation, and sets the strategy to 'CUTOUT'. It then calls the
    `testCalc` function to perform further calculations on the camera
    operation.

    Args:
        pos (tuple): A tuple containing the x and y coordinates for the
            position of the test curve.
    """
    addTestCurve((pos[0], pos[1], -0.05))
    bpy.ops.scene.cam_operation_add()
    o = bpy.context.scene.cam_operations[-1]
    o.strategy = "CUTOUT"
    testCalc(o)


def testPocket(pos):
    """Test the pocket operation in a 3D scene.

    This function sets up a pocket operation by adding a test curve based on
    the provided position. It configures the camera operation settings for
    the pocket strategy, enabling helix entry and tangential retraction.
    Finally, it performs a calculation based on the configured operation.

    Args:
        pos (tuple): A tuple containing the x and y coordinates for
            the position of the test curve.
    """
    addTestCurve((pos[0], pos[1], -0.01))
    bpy.ops.scene.cam_operation_add()
    o = bpy.context.scene.cam_operations[-1]
    o.strategy = "POCKET"
    o.movement.helix_enter = True
    o.movement.retract_tangential = True
    testCalc(o)


def testParallel(pos):
    """Test the parallel functionality of the camera operations.

    This function adds a test mesh at a specified position and then performs
    camera operations in the Blender environment. It sets the ambient
    behavior of the camera operation to 'AROUND' and configures the material
    radius around the model. Finally, it calculates the camera path based on
    the current scene settings.

    Args:
        pos (tuple): A tuple containing the x and y coordinates for
            positioning the test mesh.
    """
    addTestMesh((pos[0], pos[1], -0.02))
    bpy.ops.scene.cam_operation_add()
    o = bpy.context.scene.cam_operations[-1]
    o.ambient_behaviour = "AROUND"
    o.material.radius_around_model = 0.01
    bpy.ops.object.calculate_cam_path()


def testWaterline(pos):
    """Test the waterline functionality in the scene.

    This function adds a test mesh at a specified position and then performs
    a camera operation with the strategy set to 'WATERLINE'. It also
    configures the optimization pixel size for the operation. The function
    is intended for use in a 3D environment where waterline calculations are
    necessary for rendering or simulation.

    Args:
        pos (tuple): A tuple containing the x and y coordinates for
            the position of the test mesh.
    """
    addTestMesh((pos[0], pos[1], -0.02))
    bpy.ops.scene.cam_operation_add()
    o = bpy.context.scene.cam_operations[-1]
    o.strategy = "WATERLINE"
    o.optimisation.pixsize = 0.0002
    # o.ambient_behaviour='AROUND'
    # o.material_radius_around_model=0.01

    testCalc(o)


# bpy.ops.object.cam_simulate()


def testSimulation():
    """Testsimulation function."""
    pass


def cleanUp():
    """Clean up the Blender scene by removing all objects and camera
    operations.

    This function selects all objects in the current Blender scene and
    deletes them. It also removes any camera operations that are present in
    the scene. This is useful for resetting the scene to a clean state
    before performing further operations.
    """
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    while len(bpy.context.scene.cam_operations):
        bpy.ops.scene.cam_operation_remove()


def testOperation(i):
    """Test the operation of a camera path in Blender.

    This function tests a specific camera operation by comparing the
    generated camera path with an existing reference path. It retrieves the
    camera operation from the scene and checks if the generated path matches
    the expected path in terms of vertex count and positions. If there is no
    existing reference path, it marks the new result as comparable. The
    function generates a report detailing the results of the comparison,
    including any discrepancies found.

    Args:
        i (int): The index of the camera operation to test.

    Returns:
        str: A report summarizing the results of the operation test.
    """
    s = bpy.context.scene
    o = s.cam_operations[i]
    report = ""
    report += "testing operation " + o.name + "\n"

    getPath(bpy.context, o)

    newresult = bpy.data.objects[o.path_object_name]
    origname = "test_cam_path_" + o.name
    if origname not in s.objects:
        report += "Operation Test Has Nothing to Compare with, Making the New Result as Comparable Result.\n\n"
        newresult.name = origname
    else:
        testresult = bpy.data.objects[origname]
        m1 = testresult.data
        m2 = newresult.data
        test_ok = True
        if len(m1.vertices) != len(m2.vertices):
            report += "Vertex Counts Don't Match\n\n"
            test_ok = False
        else:
            different_co_count = 0
            for i in range(0, len(m1.vertices)):
                v1 = m1.vertices[i]
                v2 = m2.vertices[i]
                if v1.co != v2.co:
                    different_co_count += 1
            if different_co_count > 0:
                report += "Vertex Position Is Different on %i Vertices \n\n" % (different_co_count)
                test_ok = False
        if test_ok:
            report += "Test Ok\n\n"
        else:
            report += "Test Result Is Different\n \n "
    print(report)
    return report


def testAll():
    """Run tests on all camera operations in the current scene.

    This function iterates through all camera operations defined in the
    current Blender scene and executes a test for each operation. The
    results of these tests are collected into a report string, which is then
    printed to the console. This is useful for verifying the functionality
    of camera operations within the Blender environment.
    """
    s = bpy.context.scene
    report = ""
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
    p = i * 0.2
    t((p, 0, 0))
# 	cleanUp()


# cleanUp()
