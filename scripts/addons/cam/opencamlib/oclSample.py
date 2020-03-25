import os
import ocl
import tempfile
import camvtk


def ocl_sample(operation, chunks):

    stl = camvtk.STLSurf(os.path.join(tempfile.gettempdir(), "model0.stl"))
    stl_polydata = stl.src.GetOutput()
    stl_surf = ocl.STLSurf()
    camvtk.vtkPolyData2OCLSTL(stl_polydata, stl_surf)

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
