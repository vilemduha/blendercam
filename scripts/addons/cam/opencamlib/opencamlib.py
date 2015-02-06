#used by OpenCAMLib sampling

import bpy
from subprocess import call
from cam.collision import BULLET_SCALE
from cam import simple
from cam.chunk import camPathChunk
from cam.simple import * 

def operationSettingsToCSV(operation):
	csv_file = open('ocl_settings.txt','w')
	csv_file.write( str(operation.cutter_type) + '\n')
	csv_file.write( str(operation.cutter_diameter) + '\n' )
	csv_file.write( str(operation.minz) + '\n' )
	csv_file.close()

def pointsToCSV(operation, points):
	csv_file = open('ocl_chunks.txt','w')
	for point in points:
		csv_file.write( str(point[0]) + ' ' + str(point[1]) + '\n')
	csv_file.close()

def pointSamplesFromCSV(points):
	csv_file = open('ocl_chunk_samples.txt','r')
	for point in points:
		point[2] = float(csv_file.readline()) / BULLET_SCALE;
		#print(str(point[2]))
	csv_file.close()

def chunkPointsToCSV(operation, chunks):
	csv_file = open('ocl_chunks.txt','w')
	for ch in chunks:
		p_index = 0;
		for point in ch.points:
				if operation.ambient.isInside( point[0], point[1] ):
					csv_file.write( str(point[0]) + ' ' + str(point[1]) + '\n')
				else:
					ch.points[p_index] = ( point[0], point[1], 2 )
				p_index += 1
	csv_file.close()

def chunkPointSamplesFromCSV(chunks):
	csv_file = open('ocl_chunk_samples.txt','r')
	for ch in chunks:
		p_index = 0;
		for point in ch.points:
			if( len(point) == 2 or point[2] != 2 ):
				z_sample = float(csv_file.readline()) / BULLET_SCALE;
				ch.points[p_index] = ( point[0], point[1], z_sample )
				#print(str(point[2]))
			else:
				ch.points[p_index] = ( point[0], point[1], 1 )
			p_index += 1
	csv_file.close()

def resampleChunkPointsToCSV(operation, chunks_to_resample):
	csv_file = open('ocl_chunks.txt','w')
	for chunk, i_start, i_length in chunks_to_resample:
		for p_index in range(i_start, i_start+i_length):
				csv_file.write( str(chunk.points[p_index][0]) + ' ' + str(chunk.points[p_index][1]) + '\n')
	csv_file.close()

def chunkPointsResampleFromCSV(chunks_to_resample):
	csv_file = open('ocl_chunk_samples.txt','r')
	for chunk, i_start, i_length in chunks_to_resample:
		for p_index in range(i_start, i_start+i_length):
			z = float(csv_file.readline()) / BULLET_SCALE;
			if z > chunk.points[p_index][2]:
				chunk.points[p_index][2] = z
	csv_file.close()

def exportModelsToSTL(operation):
	file_number = 0
	for collision_object in operation.objects:
		activate( collision_object )
		bpy.ops.object.duplicate( linked=False )
		collision_object = bpy.context.scene.objects.active
		#bpy.context.scene.objects.selected = collision_object
		file_name = "model"+str(file_number)+".stl"
		bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
		bpy.ops.transform.resize(value=(BULLET_SCALE, BULLET_SCALE, BULLET_SCALE), constraint_axis=(False, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1, snap=False, snap_target='CLOSEST', snap_point=(0, 0, 0), snap_align=False, snap_normal=(0, 0, 0), texture_space=False, release_confirm=False)
		bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
		bpy.ops.export_mesh.stl(check_existing=True, filepath=file_name, filter_glob="*.stl", ascii=False, use_mesh_modifiers=True, axis_forward='Y', axis_up='Z', global_scale=1.0)
		bpy.ops.object.delete()
		file_number += 1
	
def oclSamplePoints(operation, points):
	print("oclSamplePoints\n")
	operationSettingsToCSV(operation)
	pointsToCSV(operation, points)
	exportModelsToSTL(operation)
	call([ "python2.7", "2.70/scripts/addons/cam/opencamlib/oclSample.py"])
	pointSamplesFromCSV(points)

def oclSample(operation, chunks):
	operationSettingsToCSV(operation)
	chunkPointsToCSV(operation, chunks)
	exportModelsToSTL(operation)
	call([ "python2.7", "2.70/scripts/addons/cam/opencamlib/oclSample.py"])
	chunkPointSamplesFromCSV(chunks)

def oclResampleChunks(operation, chunks_to_resample):
	operationSettingsToCSV(operation)
	resampleChunkPointsToCSV(operation, chunks_to_resample)
	#exportModelsToSTL(operation)
	call([ "python2.7", "2.70/scripts/addons/cam/opencamlib/oclSample.py"])
	chunkPointsResampleFromCSV(chunks_to_resample)
def oclWaterlineLayerHeights( operation ):
	layers = []
	l_first = operation.maxz
	l_last = operation.minz
	l_step = operation.stepdown
	l_depth = l_first
	while l_depth > (l_last+0.0000001):
		layers.append(l_depth)
		l_depth -= l_step
	layers.append(l_last)
	return layers

def oclWaterlineHeightsToCSV( operation ):
	layers = oclWaterlineLayerHeights( operation )
	csv_file = open('ocl_wl_heights.txt', 'w')
	for layer in layers:
		csv_file.write( str(layer*1000)+'\n')
	csv_file.close()

def waterlineChunksFromCSV( operation, chunks ):
	layers = oclWaterlineLayerHeights( operation )
	wl_index = 0
	for layer in layers:
		csv_file = open( 'oclWaterline' + str(wl_index) + '.txt', 'r')
		for line in csv_file:
			if( line[0] == 'l'):
				chunks.append( camPathChunk( inpoints = [] ) )
			else:
				point = [ float(coord)/BULLET_SCALE for coord in line.split() ]
				chunks[-1].points.append( (point[0], point[1], point[2] ) )
		wl_index += 1
		csv_file.close()

def oclGetMedialAxis(operation, chunks):
	oclWaterlineHeightsToCSV( operation )
	operationSettingsToCSV( operation )
	curvesToCSV( operation )
	call([ "python2.7", "2.70/scripts/addons/cam/opencamlib/ocl.py"])
	waterlineChunksFromCSV( operation, chunks )

def oclGetWaterline(operation, chunks):
	oclWaterlineHeightsToCSV( operation )
	operationSettingsToCSV( operation )
	exportModelsToSTL( operation )
	call([ "python2.7", "2.70/scripts/addons/cam/opencamlib/oclWaterline.py"])
	waterlineChunksFromCSV( operation, chunks )

#def oclFillMedialAxis(operation):

