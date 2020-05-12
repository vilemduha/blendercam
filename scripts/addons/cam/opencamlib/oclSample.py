import os
import ocl
import tempfile
import camvtk
import bpy

from .VTKBlender import BlenderToPolyData
from cam.simple import activate

OCL_SCALE = 1000


# ---- misc helper functions
def vtkPolyData2OCLSTL(vtkPolyData, oclSTL):
    """ read vtkPolyData and add each triangle to an ocl.STLSurf """
    i = 0
    for cellId in range(0, vtkPolyData.GetNumberOfCells()):
        cell = vtkPolyData.GetCell(cellId)
        points = cell.GetPoints()
        plist = [ocl.Point(0.0, 0.0, 0.0),
                 ocl.Point(0.0, 0.0, 0.0),
                 ocl.Point(0.0, 0.0, 0.0)]
        for pointId in range(0, points.GetNumberOfPoints()):
            vertex = points.GetPoint(pointId)
            p = ocl.Point(vertex[0], vertex[1], vertex[2])
            plist[pointId] = p
        i += 1
        t = ocl.Triangle(plist[0], plist[1], plist[2])
        oclSTL.addTriangle(t)


def get_mesh(operation):
    me = None

    for collision_object in operation.objects:
        activate(collision_object)
        bpy.ops.object.duplicate(linked=False)
        # bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        if collision_object.type == "MESH":
            bpy.ops.transform.resize(value=(OCL_SCALE, OCL_SCALE, OCL_SCALE), constraint_axis=(False, False, False),
                                     orient_type='GLOBAL', mirror=False, use_proportional_edit=False,
                                     proportional_edit_falloff='SMOOTH', proportional_size=1, snap=False,
                                     snap_target='CLOSEST', snap_point=(0, 0, 0), snap_align=False,
                                     snap_normal=(0, 0, 0),
                                     texture_space=False, release_confirm=False)
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
            me = collision_object.data
        bpy.ops.object.delete()

        # FIXME needs to work with collections
    return me


def ocl_sample(operation, chunks):

    me = get_mesh(operation)
    b2pd = BlenderToPolyData.convert(me=me)

    stl_surf = ocl.STLSurf()
    vtkPolyData2OCLSTL(b2pd, stl_surf)

    op_cutter_type = operation.cutter_type
    op_cutter_diameter = operation.cutter_diameter
    op_minz = operation.minz
    if op_cutter_type == "VCARVE":
        op_cutter_tip_angle = operation['cutter_tip_angle']

    # with open(os.path.join(tempfile.gettempdir(), 'ocl_settings.txt'), 'r') as csv_file:
    #     op_cutter_type = csv_file.readline().split()[0]
    #     op_cutter_diameter = float(csv_file.readline())
    #     if op_cutter_type == "VCARVE":
    #         op_cutter_tip_angle = float(csv_file.readline())
    #     op_minz = float(csv_file.readline())

    cutter = None
    cutter_length = 5

    if op_cutter_type == 'END':
        cutter = ocl.CylCutter(op_cutter_diameter * 1000, cutter_length)
    elif op_cutter_type == 'BALLNOSE':
        cutter = ocl.BallCutter(op_cutter_diameter * 1000, cutter_length)
    elif op_cutter_type == 'VCARVE':
        cutter = ocl.ConeCutter(op_cutter_diameter * 1000, op_cutter_tip_angle, cutter_length)
    else:
        print("Cutter unsupported: {0}\n".format(op_cutter_type))
        quit()

    # add BullCutter
    bdc = ocl.BatchDropCutter()
    bdc.setSTL(stl_surf)
    bdc.setCutter(cutter)

    for chunk in chunks:
        for coord in chunk.points:
            bdc.appendPoint(ocl.CLPoint(coord[0] * 1000, coord[1] * 1000, op_minz * 1000))

    bdc.run()

    cl_points = bdc.getCLPoints()

    # with open(os.path.join(tempfile.gettempdir(), 'ocl_chunk_samples.txt'), 'w') as csv_file:
    #     for point in cl_points:
    #         csv_file.write(str(point.z) + '\n')

    return cl_points
