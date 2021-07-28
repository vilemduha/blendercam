import os
try:
    import ocl
except ImportError:
    pass
import tempfile

from io_mesh_stl import blender_utils
import mathutils
import math
from cam.simple import activate

OCL_SCALE = 1000.0

def get_oclSTL(operation):
    me = None
    oclSTL = ocl.STLSurf()

    for collision_object in operation.objects:
        activate(collision_object)
        if collision_object.type == "MESH":
            global_matrix = mathutils.Matrix.Identity(4)
            faces = blender_utils.faces_from_mesh(collision_object, global_matrix, operation.use_modifiers)
            for face in faces:
                t = ocl.Triangle(ocl.Point(face[0][0]*OCL_SCALE, face[0][1]*OCL_SCALE, (face[0][2]+operation.skin)*OCL_SCALE),
                        ocl.Point(face[1][0]*OCL_SCALE, face[1][1]*OCL_SCALE, (face[1][2]+operation.skin)*OCL_SCALE),
                        ocl.Point(face[2][0]*OCL_SCALE, face[2][1]*OCL_SCALE, (face[2][2]+operation.skin)*OCL_SCALE))
                oclSTL.addTriangle(t)

        # FIXME needs to work with collections
    return oclSTL


def ocl_sample(operation, chunks):

    oclSTL = get_oclSTL(operation)

    op_cutter_type = operation.cutter_type
    op_cutter_diameter = operation.cutter_diameter
    op_minz = operation.minz
    op_cutter_tip_angle = math.radians(operation.cutter_tip_angle)/2
    if op_cutter_type == "VCARVE": 
        cutter_length = (op_cutter_diameter/math.tan(op_cutter_tip_angle))/2
    else:
     cutter_length = 10

    cutter = None

    if op_cutter_type == 'END':
        cutter = ocl.CylCutter((op_cutter_diameter + operation.skin * 2) * 1000, cutter_length)
    elif op_cutter_type == 'BALLNOSE':
        cutter = ocl.BallCutter((op_cutter_diameter + operation.skin * 2) * 1000, cutter_length)
    elif op_cutter_type == 'VCARVE':
        cutter = ocl.ConeCutter((op_cutter_diameter + operation.skin * 2) * 1000, op_cutter_tip_angle, cutter_length)
    elif op_cutter_type =='CYLCONE':
        cutter = ocl.CylConeCutter((operation.cylcone_diameter/2+operation.skin)*2000,(op_cutter_diameter + operation.skin * 2) * 1000, op_cutter_tip_angle)
    elif op_cutter_type == 'BALLCONE':
        cutter = ocl.BallConeCutter((operation.ball_radius + operation.skin) * 2000,
                                    (op_cutter_diameter + operation.skin * 2) * 1000, op_cutter_tip_angle)
    elif op_cutter_type =='BULLNOSE':
        cutter = ocl.BullCutter((op_cutter_diameter + operation.skin * 2) * 1000,operation.bull_corner_radius*1000, cutter_length)
    else:
        print("Cutter unsupported: {0}\n".format(op_cutter_type))
        quit()

    bdc = ocl.BatchDropCutter()
    bdc.setSTL(oclSTL)
    bdc.setCutter(cutter)

    for chunk in chunks:
        for coord in chunk.points:
            bdc.appendPoint(ocl.CLPoint(coord[0] * 1000, coord[1] * 1000, op_minz * 1000))

    bdc.run()

    cl_points = bdc.getCLPoints()

    return cl_points
