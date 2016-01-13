import ocl
import tempfile
import pyocl
import camvtk

stl = camvtk.STLSurf(tempfile.gettempdir()+"/model0.stl")
stl_polydata = stl.src.GetOutput()
stl_surf = ocl.STLSurf()
camvtk.vtkPolyData2OCLSTL(stl_polydata, stl_surf)
csv_file = open(tempfile.gettempdir()+'/ocl_settings.txt','r')
op_cutter_type = csv_file.readline().split()[0]
op_cutter_diameter = float( csv_file.readline() )
op_minz = float( csv_file.readline() )
csv_file.close();

cutter_length=5
if op_cutter_type == 'END':
	cutter = ocl.CylCutter( op_cutter_diameter*1000, cutter_length)
elif op_cutter_type == 'BALL':
	cutter = ocl.BallCutter( op_cutter_diameter*1000, cutter_length)
elif op_cutter_type == 'VCARVE':
	cutter = ocl.ConeCutter( op_cutter_diameter*1000, 1, cutter_length)
else:
	print "Cutter unsupported: " + op_cutter_type + '\n'
	quit()
#add BullCutter
bdc = ocl.BatchDropCutter()
bdc.setSTL(stl_surf)
bdc.setCutter(cutter)

csv_file = open(tempfile.gettempdir()+'/ocl_chunks.txt','r')
for text_line in csv_file:
	sample_point = [ float(coord) for coord in text_line.split() ]
	bdc.appendPoint( ocl.CLPoint( sample_point[0]*1000, sample_point[1]*1000, op_minz * 1000 ) )
csv_file.close()
	
bdc.run()

cl_points = bdc.getCLPoints()

csv_file = open(tempfile.gettempdir()+'/ocl_chunk_samples.txt', 'w')
for point in cl_points:
	csv_file.write( str(point.z) + '\n' )
csv_file.close()
	

