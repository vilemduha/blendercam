# blender CAM __init__.py (c) 2012 Vilem Novak
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

import bpy, bgl,blf 
import mathutils
import math, time
from mathutils import *
from bpy_extras.object_utils import object_data_add
from bpy.props import *
import bl_operators
from bpy.types import Menu, Operator, UIList
#from . import patterns
#from . import chunk_operations
from cam import utils, simple,polygon_utils_cam, pack#, post_processors
import numpy
import Polygon
from bpy.app.handlers import persistent
import subprocess,os, sys, threading
import pickle
#from .utils import *

bl_info = {
	"name": "CAM - gcode generation tools",
	"author": "Vilem Novak",
	"version": (0, 7, 0),
	"blender": (2, 6, 7),
	"location": "Properties > render",
	"description": "Generate machining paths for CNC",
	"warning": "there is no warranty for the produced gcode by now",
	"wiki_url": "blendercam.blogspot.com",
	"tracker_url": "",
	"category": "Scene"}
  
  
PRECISION=5


def updateMachine(self,context):
	utils.addMachineAreaObject()

class machineSettings(bpy.types.PropertyGroup):
	'''stores all data for machines'''
	#name = bpy.props.StringProperty(name="Machine Name", default="Machine")
	post_processor = EnumProperty(name='Post processor',
		items=(('ISO','Iso','this should export a standardized gcode'),('MACH3','Mach3','default mach3'),('EMC','EMC - LinuxCNC','default emc'),('HEIDENHAIN','Heidenhain','heidenhain'),('TNC151','Heidenhain TNC151','Post Processor for the Heidenhain TNC151 machine'),('SIEGKX1','Sieg KX1','Sieg KX1'),('HM50','Hafco HM-50','Hafco HM-50'),('CENTROID','Centroid M40','Centroid M40'),('ANILAM','Anilam Crusader M','Anilam Crusader M')),
		description='Post processor',
		default='MACH3')
	#units = EnumProperty(name='Units', items = (('IMPERIAL', ''))
	working_area=bpy.props.FloatVectorProperty(name = 'Work Area', default=(0.500,0.500,0.100), unit='LENGTH', precision=PRECISION,subtype="XYZ",update = updateMachine)
	feedrate_min=bpy.props.FloatProperty(name="Feedrate minimum /min", default=0.0, min=0.00001, max=320000,precision=PRECISION, unit='LENGTH')
	feedrate_max=bpy.props.FloatProperty(name="Feedrate maximum /min", default=2, min=0.00001, max=320000,precision=PRECISION, unit='LENGTH')
	feedrate_default=bpy.props.FloatProperty(name="Feedrate default /min", default=1.5, min=0.00001, max=320000,precision=PRECISION)
	#UNSUPPORTED:
	spindle_min=bpy.props.FloatProperty(name="#Spindlespeed minimum /min", default=5000, min=0.00001, max=320000,precision=1)
	spindle_max=bpy.props.FloatProperty(name="#Spindlespeed maximum /min", default=30000, min=0.00001, max=320000,precision=1)
	spindle_default=bpy.props.FloatProperty(name="#Spindlespeed default /min", default=20000, min=0.00001, max=320000,precision=1)
	axis4 = bpy.props.BoolProperty(name="#4th axis",description="Machine has 4th axis", default=0)
	axis5 = bpy.props.BoolProperty(name="#5th axis",description="Machine has 5th axis", default=0)
	
	eval_splitting = bpy.props.BoolProperty(name="Split files",description="split gcode file with large number of operations", default=True)#split large files
	split_limit = IntProperty(name="Operations per file", description="Split files with larger number of operations than this", min=10000, max=20000000, default=800000)
	'''rotary_axis1 = EnumProperty(name='Axis 1',
		items=(
			('X', 'X', 'x'),
			('Y', 'Y', 'y'),
			('Z', 'Z', 'z')),
		description='Number 1 rotational axis',
		default='X', update = updateOffsetImage)
	'''
	collet_size=bpy.props.FloatProperty(name="#Collet size", description="Collet size for collision detection",default=33, min=0.00001, max=320000,precision=PRECISION , unit="LENGTH")
	#exporter_start = bpy.props.StringProperty(name="exporter start", default="%")

class PackObjectsSettings(bpy.types.PropertyGroup):
	'''stores all data for machines'''
	#name = bpy.props.StringProperty(name="Machine Name", default="Machine")
	sheet_fill_direction = EnumProperty(name='Fill direction',
		items=(('X','X','Fills sheet in X axis direction'),('Y','Y','Fills sheet in Y axis direction')),
		description='Fill direction of the packer algorithm',
		default='Y')
	sheet_x = FloatProperty(name="X size", description="Sheet size", min=0.001, max=10, default=0.5, precision=PRECISION, unit="LENGTH")
	sheet_y = FloatProperty(name="Y size", description="Sheet size", min=0.001, max=10, default=0.5, precision=PRECISION, unit="LENGTH")
	distance = FloatProperty(name="Minimum distance", description="minimum distance between objects(should be at least cutter diameter!)", min=0.001, max=10, default=0.01, precision=PRECISION, unit="LENGTH")
	rotate = bpy.props.BoolProperty(name="enable rotation",description="Enable rotation of elements", default=True)

		
def getChangeData(o):####this is a function to check if object props have changed, to see if image updates are needed
	s=bpy.context.scene
	changedata=''
	obs=[]
	if o.geometry_source=='OBJECT':
		obs=[bpy.data.objects[o.object_name]]
	elif o.geometry_source=='GROUP':
		obs=bpy.data.groups[o.group_name].objects
	for ob in obs:
		changedata+=str(ob.location)
		changedata+=str(ob.rotation_euler)
		changedata+=str(ob.dimensions)
		
	return changedata
	
def operationValid(self,context):
	o=self
	o.changed=True
	o.valid=True
	o.warnings=""
	o=bpy.context.scene.cam_operations[bpy.context.scene.cam_active_operation]
	if o.geometry_source=='OBJECT':
		if not o.object_name in bpy.data.objects :
			o.valid=False;
			o.warnings="Operation has no valid data input"
	if o.geometry_source=='GROUP':
		if not o.group_name in bpy.data.groups:
			o.valid=False;
			o.warnings="Operation has no valid data input"
		elif len(bpy.data.groups[o.group_name].objects)==0: 
			o.valid=False;
			o.warnings="Operation has no valid data input"
		
	if o.geometry_source=='IMAGE':
		if not o.source_image_name in bpy.data.images:
			o.valid=False
			o.warnings="Operation has no valid data input"

		o.use_exact=False
	o.update_offsetimage_tag=True
	o.update_zbufferimage_tag=True
	print('validity ')
	#print(o.valid)
	
#Update functions start here
def updateChipload(self,context):
	'''this is very simple computation of chip size, could be very much improved'''
	o=self;
	self.changed=True
	self.chipload = int((o.feedrate/(o.spindle_rpm*o.cutter_flutes))*1000000)/1000
	
	
def updateOffsetImage(self,context):
	'''refresh offset image tag for rerendering'''
	#print('update offset')
	self.changed=True

	self.update_offsetimage_tag=True

def checkMemoryLimit(o):
	#utils.getBounds(o)
	sx=o.max.x-o.min.x
	sy=o.max.y-o.min.y
	resx=sx/o.pixsize
	resy=sy/o.pixsize
	res=resx*resy
	limit=o.imgres_limit*1000000
	#print('co se to deje')
	#if res>limit:
	#	ratio=(res/limit)
	#	o.pixsize=o.pixsize*math.sqrt(ratio)
	#	o.warnings=o.warnings+'sampling resolution had to be reduced!\n'
	#print('furt nevim')
	#print(ratio)


def updateZbufferImage(self,context):
	#print('updatezbuf')
	#print(self,context)
	self.changed=True
	self.update_zbufferimage_tag=True
	self.update_offsetimage_tag=True
	getOperationSources(self)
	checkMemoryLimit(self)

def updateStrategy(o,context):
	o.changed=True
	#print('update strategy')
	if o.axes=='5':
		utils.addOrientationObject(o)
	else:
		utils.removeOrientationObject(o)
	updateExact(o,context)


	
def updateExact(o,context):
	o.changed=True
	o.update_zbufferimage_tag=True
	o.update_offsetimage_tag=True
	if o.use_exact and (o.strategy=='WATERLINE' or o.strategy=='POCKET' or o.inverse):
		o.use_exact=False
		
def updateBridges(o,context):
	o.changed=True
	utils.setupBridges(o)
def updateRest(o,context):
	o.changed=True

class camOperation(bpy.types.PropertyGroup):
	
	name = bpy.props.StringProperty(name="Operation Name", default="Operation", update = updateRest)
	filename = bpy.props.StringProperty(name="File name", default="Operation", update = updateRest)
	
	#group = bpy.props.StringProperty(name='Object group', description='group of objects which will be included in this operation')
	object_name = bpy.props.StringProperty(name='Object', description='object handled by this operation', update=operationValid)
	group_name = bpy.props.StringProperty(name='Group', description='Object group handled by this operation', update=operationValid)
	curve_object = bpy.props.StringProperty(name='Curve object', description='curve which will be sampled along the 3d object', update=operationValid)
	source_image_name = bpy.props.StringProperty(name='image_source', description='image source', update=operationValid)
	geometry_source = EnumProperty(name='Source of data',
		items=(
			('OBJECT','object', 'a'),('GROUP','Group of objects', 'a'),('IMAGE','Image', 'a')),
		description='Geometry source',
		default='OBJECT', update=operationValid)
	cutter_type = EnumProperty(name='Cutter',
		items=(
			('END', 'End', 'end - flat cutter'),
			('BALL', 'Ball', 'ball cutter'),
			('VCARVE', 'V-carve', 'v carve cutter'),
			('CUSTOM', 'Custom-EXPERIMENTAL', 'modelled cutter - not well tested yet.')),
		description='Type of cutter used',
		default='END', update = updateZbufferImage)
	cutter_object_name = bpy.props.StringProperty(name='Object', description='object used as custom cutter for this operation', update=updateZbufferImage)

	axes = EnumProperty(name='Number of axes',
		items=(
			('3', '3 axis', 'a'),
			('4', '#4 axis - EXPERIMENTAL', 'a'),
			('5', '#5 axis - NOT WORKING', 'a')),
		description='How many axes will be used for the operation',
		default='3', update = updateStrategy)
	strategy = EnumProperty(name='Strategy',
		items=(
			('PARALLEL','Parallel', 'Parallel lines on any angle'),
			('CROSS','Cross', 'Cross paths'),
			('BLOCK','Block', 'Block path'),
			('SPIRAL','Spiral', 'Spiral path'),
			('CIRCLES','Circles', 'Circles path'),
			('WATERLINE','Waterline - EXPERIMENTAL', 'Waterline paths - constant z'),
			('OUTLINEFILL','Outline Fill', 'Detect outline and fill it with paths as pocket. Then sample these paths on the 3d surface'),
			('CUTOUT','Cutout', 'Cut the silhouette with offset'),
			('POCKET','Pocket', 'Pocket operation'),
			('CARVE','Carve', 'Pocket operation'),
			('PENCIL','Pencil - EXPERIMENTAL', 'Pencil operation - detects negative corners in the model and mills only those.'),
			('DRILL','Drill', 'Drill operation'),('CRAZY','Crazy path - EXPERIMENTAL', 'Crazy paths - dont even think about using this!')),
		description='Strategy',
		default='PARALLEL',
		update = updateStrategy)#,('SLICES','Slices','this prepares model for cutting from sheets of material')
	strategy4axis = EnumProperty(name='Strategy',
		items=(
			('PARALLELA','Parallel around A', 'Parallel lines around A axis'),
			('PARALLELX','Parallel along X', 'Parallel lines along X axis'),
			('CROSS','Cross', 'Cross paths')),
		description='Strategy',
		default='PARALLELA',
		update = updateStrategy)
	strategy5axis = EnumProperty(name='Strategy',
		items=(
			('PARALLEL','Parallel', 'Parallel lines on any angle'),
			('CROSS','Cross', 'Cross paths'),
			('BLOCK','Block', 'Block path'),
			('SPIRAL','Spiral', 'Spiral path'),
			('CIRCLES','Circles', 'Circles path'),
			('WATERLINE','Waterline - EXPERIMENTAL', 'Waterline paths - constant z'),
			('OUTLINEFILL','Outline Fill', 'Detect outline and fill it with paths as pocket. Then sample these paths on the 3d surface'),
			('CUTOUT','Cutout', 'Cut the silhouette with offset'),
			('POCKET','Pocket', 'Pocket operation'),
			('CARVE','Carve', 'Pocket operation'),
			('PENCIL','Pencil - EXPERIMENTAL', 'Pencil operation - detects negative corners in the model and mills only those.')),
		description='Strategy',
		default='PARALLEL',
		update = updateStrategy)
	#for cutout	   
	cut_type = EnumProperty(name='Cut',items=(('OUTSIDE', 'Outside', 'a'),('INSIDE', 'Inside', 'a'),('ONLINE', 'On line', 'a')),description='Type of cutter used',default='OUTSIDE', update = updateRest)  
	#render_all = bpy.props.BoolProperty(name="Use all geometry",description="use also other objects in the scene", default=True)#replaced with groups support
	inverse = bpy.props.BoolProperty(name="Inverse milling",description="Male to female model conversion", default=False, update = updateOffsetImage)
	
	cutter_id = IntProperty(name="Tool number", description="For machines which support tool change based on tool id", min=0, max=10000, default=1, update = updateRest)
	cutter_diameter = FloatProperty(name="Cutter diameter", description="Cutter diameter = 2x cutter radius", min=0.000001, max=0.1, default=0.003, precision=PRECISION, unit="LENGTH", update = updateOffsetImage)
	cutter_length = FloatProperty(name="#Cutter length", description="#not supported#Cutter length", min=0.0, max=100.0, default=25.0,precision=PRECISION, unit="LENGTH",  update = updateOffsetImage)
	cutter_flutes = IntProperty(name="Cutter flutes", description="Cutter flutes", min=1, max=20, default=2, update = updateChipload)
	cutter_tip_angle = FloatProperty(name="Cutter v-carve angle", description="Cutter v-carve angle", min=0.0, max=180.0, default=60.0,precision=PRECISION,	 update = updateOffsetImage)
	
	dist_between_paths = bpy.props.FloatProperty(name="Distance between toolpaths", default=0.001, min=0.00001, max=32,precision=PRECISION, unit="LENGTH", update = updateRest)
	dist_along_paths = bpy.props.FloatProperty(name="Distance along toolpaths", default=0.0002, min=0.00001, max=32,precision=PRECISION, unit="LENGTH", update = updateRest)
	parallel_angle = bpy.props.FloatProperty(name="Angle of paths", default=0, min=-360, max=360 , precision=0, subtype="ANGLE" , unit="ROTATION" , update = updateRest)
	carve_depth = bpy.props.FloatProperty(name="Carve depth", default=0.001, min=-.100, max=32,precision=PRECISION, unit="LENGTH", update = updateRest)
	drill_type = EnumProperty(name='Holes on',items=(('MIDDLE_SYMETRIC', 'Middle of symetric curves', 'a'),('MIDDLE_ALL', 'Middle of all curve parts', 'a'),('ALL_POINTS', 'All points in curve', 'a')),description='Strategy to detect holes to drill',default='MIDDLE_SYMETRIC', update = updateRest)	
	
	slice_detail = bpy.props.FloatProperty(name="Distance betwen slices", default=0.001, min=0.00001, max=32,precision=PRECISION, unit="LENGTH", update = updateRest)
	waterline_fill = bpy.props.BoolProperty(name="Fill areas between slices",description="Fill areas between slices in waterline mode", default=True, update = updateRest)
	waterline_project = bpy.props.BoolProperty(name="Project paths",description="Project paths in areas between slices", default=True, update = updateRest)
	
	circle_detail = bpy.props.IntProperty(name="Detail of circles used for curve offsets", default=64, min=12, max=512, update = updateRest)
	use_layers = bpy.props.BoolProperty(name="Use Layers",description="Use layers for roughing", default=True, update = updateRest)
	stepdown = bpy.props.FloatProperty(name="Step down", default=0.01, min=0.00001, max=32,precision=PRECISION, unit="LENGTH", update = updateRest)
	first_down = bpy.props.BoolProperty(name="First down",description="First go down on a contour, then go to the next one", default=False, update = updateRest)
	contour_ramp = bpy.props.BoolProperty(name="Ramp contour - EXPERIMENTAL",description="Ramps down the whole contour, so the cutline looks like helix", default=False, update = updateRest)
	ramp_out = bpy.props.BoolProperty(name="Ramp out - EXPERIMENTAL",description="Ramp out to not leave mark on surface", default=False, update = updateRest)
	ramp_out_angle = bpy.props.FloatProperty(name="Ramp out angle", default=math.pi/6, min=0, max=math.pi*0.4999 , precision=1, subtype="ANGLE" , unit="ROTATION" , update = updateRest)
	helix_enter = bpy.props.BoolProperty(name="Helix enter - EXPERIMENTAL",description="Enter material in helix", default=False, update = updateRest)
	helix_angle =	bpy.props.FloatProperty(name="Helix ramp angle", default=3*math.pi/180, min=0.00001, max=math.pi*0.4999,precision=1, subtype="ANGLE" , unit="ROTATION" , update = updateRest)
	helix_diameter = bpy.props.FloatProperty(name = 'Helix diameter % of cutter D', default=90,min=10, max=100, precision=1,subtype='PERCENTAGE', update = updateRest)
	retract_tangential = bpy.props.BoolProperty(name="Retract tangential - EXPERIMENTAL",description="Retract from material in circular motion", default=False, update = updateRest)
	retract_radius =  bpy.props.FloatProperty(name = 'Retract arc radius', default=0.001,min=0.000001, max=100, precision=PRECISION, unit="LENGTH", update = updateRest)
	retract_height =  bpy.props.FloatProperty(name = 'Retract arc height', default=0.001,min=0.00000, max=100, precision=PRECISION, unit="LENGTH", update = updateRest)
	
	minz_from_ob = bpy.props.BoolProperty(name="Depth from object",description="Operation depth from object", default=True, update = updateRest)
	minz = bpy.props.FloatProperty(name="Operation depth", default=-0.01, min=-3, max=0,precision=PRECISION, unit="LENGTH", update = updateRest)#this is input minz. True minimum z can be something else, depending on material e.t.c.
	maxz = bpy.props.FloatProperty(name="Operation depth start", default=0, min=-3, max=1,precision=PRECISION, unit="LENGTH", update = updateRest)#EXPERIMENTAL
	
	source_image_scale_z=bpy.props.FloatProperty(name="Image source depth scale", default=0.01, min=-1, max=1,precision=PRECISION, unit="LENGTH",  update = updateZbufferImage)
	source_image_size_x=bpy.props.FloatProperty(name="Image source x size", default=0.1, min=-10, max=10,precision=PRECISION, unit="LENGTH",  update = updateZbufferImage)
	source_image_offset=bpy.props.FloatVectorProperty(name = 'Image offset', default=(0,0,0), unit='LENGTH', precision=PRECISION,subtype="XYZ",	 update = updateZbufferImage)
	source_image_crop=bpy.props.BoolProperty(name="Crop source image",description="Crop source image - the position of the sub-rectangle is relative to the whole image, so it can be used for e.g. finishing just a part of an image", default=False,	update = updateZbufferImage)
	source_image_crop_start_x= bpy.props.FloatProperty(name = 'crop start x', default=0,min=0, max=100, precision=PRECISION,subtype='PERCENTAGE',  update = updateZbufferImage)
	source_image_crop_start_y= bpy.props.FloatProperty(name = 'crop start y', default=0,min=0, max=100, precision=PRECISION,subtype='PERCENTAGE',  update = updateZbufferImage)
	source_image_crop_end_x=   bpy.props.FloatProperty(name = 'crop end x', default=100,min=0, max=100, precision=PRECISION,subtype='PERCENTAGE',  update = updateZbufferImage)
	source_image_crop_end_y=   bpy.props.FloatProperty(name = 'crop end y', default=100,min=0, max=100, precision=PRECISION,subtype='PERCENTAGE',  update = updateZbufferImage)
	
	protect_vertical = bpy.props.BoolProperty(name="Protect vertical",description="The path goes only vertically next to steep areas", default=True)
	protect_vertical_limit = bpy.props.FloatProperty(name="Verticality limit", description="What angle is allready considered vertical", default=math.pi/45, min=0, max=math.pi*0.5 , precision=0, subtype="ANGLE" , unit="ROTATION" , update = updateRest)
		
	ambient_behaviour = EnumProperty(name='Ambient',items=(('ALL', 'All', 'a'),('AROUND', 'Around', 'a')   ),description='handling ambient surfaces',default='ALL', update = updateZbufferImage)
	

	ambient_radius = FloatProperty(name="Ambient radius", description="Radius around the part which will be milled if ambient is set to Around", min=0.0, max=100.0, default=0.01, precision=PRECISION, unit="LENGTH", update = updateRest)
	#ambient_cutter = EnumProperty(name='Borders',items=(('EXTRAFORCUTTER', 'Extra for cutter', "Extra space for cutter is cut around the segment"),('ONBORDER', "Cutter on edge", "Cutter goes exactly on edge of ambient with it's middle") ,('INSIDE', "Inside segment", 'Cutter stays within segment')	 ),description='handling of ambient and cutter size',default='INSIDE')
	use_limit_curve=bpy.props.BoolProperty(name="Use limit curve",description="A curve limits the operation area", default=False, update = updateRest)
	ambient_cutter_restrict=bpy.props.BoolProperty(name="Cutter stays in ambient limits",description="Cutter doesn't get out from ambient limits otherwise goes on the border exactly", default=True, update = updateRest)#restricts cutter inside ambient only
	limit_curve=   bpy.props.StringProperty(name='Limit curve', description='curve used to limit the area of the operation', update = updateRest)
	
	skin = FloatProperty(name="Skin", description="Material to leave when roughing ", min=0.0, max=1.0, default=0.0,precision=PRECISION, unit="LENGTH", update = updateOffsetImage)
	#feeds
	feedrate = FloatProperty(name="Feedrate/minute", description="Feedrate m/min", min=0.00005, max=50.0, default=1.0,precision=PRECISION, unit="LENGTH", update = updateChipload)
	plunge_feedrate = FloatProperty(name="Plunge speed ", description="% of feedrate", min=0.1, max=100.0, default=50.0,precision=1, subtype='PERCENTAGE', update = updateRest)
	plunge_angle =	bpy.props.FloatProperty(name="Plunge angle", description="What angle is allready considered to plunge", default=math.pi/6, min=0, max=math.pi*0.5 , precision=0, subtype="ANGLE" , unit="ROTATION" , update = updateRest)
	spindle_rpm = FloatProperty(name="#Spindle rpm", description="#not supported#Spindle speed ", min=1000, max=60000, default=12000, update = updateChipload)
	#movement parallel_step_back 
	movement_type = EnumProperty(name='Movement type',items=(('CONVENTIONAL','Conventional', 'a'),('CLIMB', 'Climb', 'a'),('MEANDER', 'Meander' , 'a')	 ),description='movement type', default='CLIMB', update = updateRest)
	spindle_rotation_direction = EnumProperty(name='Spindle rotation', items=(('CW','Clock wise', 'a'),('CCW', 'Counter clock wise', 'a')),description='Spindle rotation direction',default='CW', update = updateRest)
	free_movement_height = bpy.props.FloatProperty(name="Free movement height", default=0.01, min=0.0000, max=32,precision=PRECISION, unit="LENGTH", update = updateRest)
	movement_insideout = EnumProperty(name='Direction', items=(('INSIDEOUT','Inside out', 'a'),('OUTSIDEIN', 'Outside in', 'a')),description='approach to the piece',default='INSIDEOUT', update = updateRest)
	parallel_step_back =  bpy.props.BoolProperty(name="Parallel step back", description='For roughing and finishing in one pass: mills material in climb mode, then steps back and goes between 2 last chunks back', default=False, update = updateRest)
	stay_low = bpy.props.BoolProperty(name="Stay low if possible", default=False, update = updateRest)
	#optimization and performance
	use_exact = bpy.props.BoolProperty(name="Use exact mode",description="Exact mode allows greater precision, but is slower with complex meshes", default=True, update = updateExact)
	pixsize=bpy.props.FloatProperty(name="sampling raster detail", default=0.0001, min=0.00001, max=0.01,precision=PRECISION, unit="LENGTH", update = updateZbufferImage)
	simulation_detail=bpy.props.FloatProperty(name="Simulation sampling raster detail", default=0.0001, min=0.00001, max=0.01,precision=PRECISION, unit="LENGTH", update = updateRest)
	imgres_limit = bpy.props.IntProperty(name="Maximum resolution in megapixels", default=10, min=1, max=512,description="This property limits total memory usage and prevents crashes. Increase it if you know what are doing.", update = updateZbufferImage)
	optimize = bpy.props.BoolProperty(name="Reduce path points",description="Reduce path points", default=True, update = updateRest)
	optimize_threshold=bpy.props.FloatProperty(name="Reduction threshold", default=0.000001, min=0.00000001, max=1,precision=PRECISION, unit="LENGTH", update = updateRest)
	
	dont_merge = bpy.props.BoolProperty(name="Dont merge outlines when cutting",description="this is usefull when you want to cut around everything", default=False, update = updateRest)
	
	pencil_threshold=bpy.props.FloatProperty(name="Pencil threshold", default=0.00002, min=0.00000001, max=1,precision=PRECISION, unit="LENGTH", update = updateRest)
	crazy_threshold1=bpy.props.FloatProperty(name="Crazy threshold 1", default=0.02, min=0.00000001, max=100,precision=PRECISION, update = updateRest)
	crazy_threshold2=bpy.props.FloatProperty(name="Crazy threshold 2", default=0.2, min=0.00000001, max=100,precision=PRECISION, update = updateRest)
	crazy_threshold3=bpy.props.FloatProperty(name="Crazy threshold 3", default=3.0, min=0.00000001, max=100,precision=PRECISION, update = updateRest)
	crazy_threshold4=bpy.props.FloatProperty(name="Crazy threshold 4", default=1.0, min=0.00000001, max=100,precision=PRECISION, update = updateRest)
	#calculations
	duration = bpy.props.FloatProperty(name="Estimated time", default=0.01, min=0.0000, max=32,precision=PRECISION, unit="TIME", update = updateRest)
	#chip_rate
	#bridges
	use_bridges =  bpy.props.BoolProperty(name="Use bridges",description="use bridges in cutout", default=False, update = updateBridges)
	bridges_width = bpy.props.FloatProperty(name = 'width of bridges', default=0.002, unit='LENGTH', precision=PRECISION, update = updateBridges)
	bridges_height = bpy.props.FloatProperty(name = 'height of bridges', description="Height from the bottom of the cutting operation", default=0.0005, unit='LENGTH', precision=PRECISION, update = updateBridges)
	bridges_per_curve = bpy.props.IntProperty(name="minimum bridges per curve", description="", default=4, min=1, max=512, update = updateBridges)
	bridges_max_distance = bpy.props.FloatProperty(name = 'Maximum distance between bridges', default=0.08, unit='LENGTH', precision=PRECISION, update = updateBridges)
	#optimisation panel
	
	#material settings
	material_from_model = bpy.props.BoolProperty(name="Estimate from model",description="Estimate material size from model", default=True, update = updateZbufferImage)
	material_radius_around_model = bpy.props.FloatProperty(name="radius around model",description="How much to add to model size on all sides", default=0.0, unit='LENGTH', precision=PRECISION, update = updateZbufferImage)
	material_origin=bpy.props.FloatVectorProperty(name = 'Material origin', default=(0,0,0), unit='LENGTH', precision=PRECISION,subtype="XYZ", update = updateZbufferImage)
	material_size=bpy.props.FloatVectorProperty(name = 'Material size', default=(0.200,0.200,0.100), unit='LENGTH', precision=PRECISION,subtype="XYZ", update = updateZbufferImage)
	min=bpy.props.FloatVectorProperty(name = 'Operation minimum', default=(0,0,0), unit='LENGTH', precision=PRECISION,subtype="XYZ", update = updateRest)
	max=bpy.props.FloatVectorProperty(name = 'Operation maximum', default=(0,0,0), unit='LENGTH', precision=PRECISION,subtype="XYZ", update = updateRest)
	warnings = bpy.props.StringProperty(name='warnings', description='warnings', default='', update = updateRest)
	chipload = bpy.props.FloatProperty(name="chipload",description="Calculated chipload", default=0.0, unit='LENGTH', precision=PRECISION, update = updateRest)
	#internal properties
	###########################################
	#testing = bpy.props.IntProperty(name="developer testing ", description="This is just for script authors for help in coding, keep 0", default=0, min=0, max=512)
	offset_image=numpy.array([],dtype=float)
	zbuffer_image=numpy.array([],dtype=float)
	
	silhouete=Polygon.Polygon()
	ambient = Polygon.Polygon()
	operation_limit=Polygon.Polygon()
	borderwidth=50
	object=None
	path_object_name=bpy.props.StringProperty(name='Path object', description='actual cnc path')
	
	changed=bpy.props.BoolProperty(name="True if any of the operation settings has changed",description="mark for update", default=False)
	update_zbufferimage_tag=bpy.props.BoolProperty(name="mark zbuffer image for update",description="mark for update", default=True)
	update_offsetimage_tag=bpy.props.BoolProperty(name="mark offset image for update",description="mark for update", default=True)
	update_silhouete_tag=bpy.props.BoolProperty(name="mark silhouette image for update",description="mark for update", default=True)
	update_ambient_tag=bpy.props.BoolProperty(name="mark ambient polygon for update",description="mark for update", default=True)
	update_bullet_collision_tag=bpy.props.BoolProperty(name="mark bullet collisionworld for update",description="mark for update", default=True)
	
	
	valid = bpy.props.BoolProperty(name="Valid",description="True if operation is ok for calculation", default=True);
	changedata = bpy.props.StringProperty(name='changedata', description='change data for checking if stuff changed.')
	###############process related data
	computing = bpy.props.BoolProperty(name="Computing right now",description="", default=False)
	pid = bpy.props.IntProperty(name="process id", description="Background process id", default=-1)
	outtext = bpy.props.StringProperty(name='outtext', description='outtext', default='')
	

class opReference(bpy.types.PropertyGroup):#this type is defined just to hold reference to operations for chains
	name = bpy.props.StringProperty(name="Operation name", default="Operation")
	computing = False;#for UiList display
	
class camChain(bpy.types.PropertyGroup):#chain is just a set of operations which get connected on export into 1 file.
	index = bpy.props.IntProperty(name="index", description="index in the hard-defined camChains", default=-1)
	active_operation = bpy.props.IntProperty(name="active operation", description="active operation in chain", default=-1)
	name = bpy.props.StringProperty(name="Chain Name", default="Chain")
	filename = bpy.props.StringProperty(name="File name", default="Chain")#filename of 
	valid = bpy.props.BoolProperty(name="Valid",description="True if whole chain is ok for calculation", default=True);
	computing = bpy.props.BoolProperty(name="Computing right now",description="", default=False)
	operations= bpy.props.CollectionProperty(type=opReference)#this is to hold just operation names.

   
class threadCom:#object passed to threads to read background process stdout info 
	def __init__(self,o,proc):
		self.opname=o.name
		self.outtext=''
		self.proc=proc
		self.lasttext=''
	
def threadread( tcom):
	'''reads stdout of background process, done this way to have it non-blocking'''
	inline = tcom.proc.stdout.readline()
	inline=str(inline)
	s=inline.find('progress{')
	if s>-1:
		e=inline.find('}')
		tcom.outtext=inline[ s+9 :e]


def header_info(self, context):
	'''writes background operations data to header'''
	s=bpy.context.scene
	self.layout.label(s.cam_text)

@bpy.app.handlers.persistent
def timer_update(context):
	'''monitoring of background processes'''
	text=''
	s=bpy.context.scene
	if hasattr(bpy.ops.object.calculate_cam_paths_background.__class__,'cam_processes'):
		processes=bpy.ops.object.calculate_cam_paths_background.__class__.cam_processes
		for p in processes:
			#proc=p[1].proc
			readthread=p[0]
			tcom=p[1]
			if not readthread.is_alive():
				readthread.join()
				#readthread.
				tcom.lasttext=tcom.outtext
				if tcom.outtext!='':
					print(tcom.opname,tcom.outtext)
					tcom.outtext=''
					
				if 'finished' in tcom.lasttext:
					processes.remove(p)
					
					o=s.cam_operations[tcom.opname]
					o.computing=False;
					utils.reload_paths(o)
					update_zbufferimage_tag = False
					update_offsetimage_tag = False
				else:
					readthread=threading.Thread(target=threadread, args = ([tcom]), daemon=True)
					readthread.start()
					p[0]=readthread
				
			text=text+('# %s %s #' % (tcom.opname,tcom.lasttext))
	s.cam_text=text
		
	for area in bpy.context.screen.areas:
		if area.type == 'INFO':
			area.tag_redraw()
			
@bpy.app.handlers.persistent
def check_operations_on_load(context):
	'''checks any broken computations on load and reset them.'''
	s=bpy.context.scene
	for o in s.cam_operations:
		if o.computing:
			o.computing=False

class PathsBackground(bpy.types.Operator):
	'''calculate CAM paths in background'''
	bl_idname = "object.calculate_cam_paths_background"
	bl_label = "Calculate CAM paths in background"
	bl_options = {'REGISTER', 'UNDO'}
	
	#processes=[]
	
	#@classmethod
	#def poll(cls, context):
	#	return context.active_object is not None
	
	def execute(self, context):
		s=bpy.context.scene
		o=s.cam_operations[s.cam_active_operation]
		self.operation=o
		o.computing=True
		#if bpy.data.is_dirty:
		#bpy.ops.wm.save_mainfile()#this has to be replaced with passing argument or pickle stuff.. 
		#picklepath=getCachePath(o)+'init.pickle'

		bpath=bpy.app.binary_path
		fpath=bpy.data.filepath
		scriptpath=bpy.utils.script_paths()[0]+os.sep+'addons'+os.sep+'cam'+os.sep+'backgroundop.py_'
		
		proc= subprocess.Popen([bpath, '-b', fpath,'-P',scriptpath,'--', '-o='+str(s.cam_active_operation) ],bufsize=1, stdout=subprocess.PIPE,stdin=subprocess.PIPE)
		
		tcom=threadCom(o,proc)
		readthread=threading.Thread(target=threadread, args = ([tcom]), daemon=True)
		readthread.start()
		#self.__class__.cam_processes=[]
		if not hasattr(bpy.ops.object.calculate_cam_paths_background.__class__,'cam_processes'):
			bpy.ops.object.calculate_cam_paths_background.__class__.cam_processes=[]
		bpy.ops.object.calculate_cam_paths_background.__class__.cam_processes.append([readthread,tcom])
		return {'FINISHED'}
		
		
def getOperationSources(o):
	if o.geometry_source=='OBJECT':
		#bpy.ops.object.select_all(action='DESELECT')
		ob=bpy.data.objects[o.object_name]
		o.objects=[ob]
	elif o.geometry_source=='GROUP':
		group=bpy.data.groups[o.group_name]
		o.objects=group.objects
	elif o.geometry_source=='IMAGE':
		o.use_exact=False;
		
class CalculatePath(bpy.types.Operator):
	'''calculate CAM paths'''
	bl_idname = "object.calculate_cam_path"
	bl_label = "Calculate CAM paths"
	bl_options = {'REGISTER', 'UNDO'}

	#this property was actually ignored, so removing it in 0.3
	#operation= StringProperty(name="Operation",
	#					   description="Specify the operation to calculate",default='Operation')
						
	def execute(self, context):
		#getIslands(context.object)
		s=bpy.context.scene
		o = s.cam_operations[s.cam_active_operation]
		if not o.valid:
				self.report({'ERROR_INVALID_INPUT'}, "Operation can't be performed, see warnings for info")
				#print("Operation can't be performed, see warnings for info")
				return {'FINISHED'}
		if o.computing:
			return {'FINISHED'}
			
		#print('ahoj0')
		#these tags are for caching of some of the results.
		chd=getChangeData(o)
		#print(chd)
		#print(o.changedata)
		if o.changedata!=chd:
			#print('ojojojo')
			o.update_offsetimage_tag=True
			o.update_zbufferimage_tag=True
			o.changedata=chd
		o.update_silhouete_tag=True
		o.update_ambient_tag=True
		o.update_bullet_collision_tag=True
		#o.material=bpy.context.scene.cam_material[0]
		o.operator=self
		#'''#removed for groups support, this has to be done object by object...
		getOperationSources(o)
		#print('áhoj1')
		if o.geometry_source=='OBJECT' or o.geometry_source=='GROUP':
			o.onlycurves=True
			for ob in o.objects:
				if ob.type=='MESH':
					o.onlycurves=False;
		o.warnings=''
		checkMemoryLimit(o)
		#print('áhoj2')
		utils.getPath(context,o)
		o.changed=False
		return {'FINISHED'}

class PathsAll(bpy.types.Operator):
	'''calculate all CAM paths'''
	bl_idname = "object.calculate_cam_paths_all"
	bl_label = "Calculate all CAM paths"
	bl_options = {'REGISTER', 'UNDO'}
		
	def execute(self, context):
		import bpy
		i=0
		for o in bpy.context.scene.cam_operations:
			bpy.context.scene.cam_active_operation=i
			print('\nCalculating path :'+o.name)
			print('\n')
			bpy.ops.object.calculate_cam_paths_background()
			i+=1

		return {'FINISHED'}
	
	def draw(self, context):
		layout = self.layout
		layout.prop_search(self, "operation", bpy.context.scene, "cam_operations")
		
class CamPackObjects(bpy.types.Operator):
	'''calculate all CAM paths'''
	bl_idname = "object.cam_pack_objects"
	bl_label = "Pack curves on sheet"
	bl_options = {'REGISTER', 'UNDO'}
		
	def execute(self, context):
		
		obs=bpy.context.selected_objects
		pack.packCurves()
		#layout.
		return {'FINISHED'}
	
	def draw(self, context):
		layout = self.layout
		
		
def getChainOperations(chain):
	'''return chain operations, currently chain object can't store operations directly due to blender limitations'''
	chop=[]
	for cho in chain.operations:
		for so in bpy.context.scene.cam_operations:
			if so.name==cho.name:
				chop.append(so)
	return chop
	
class PathsChain(bpy.types.Operator):
	'''calculate a chain and export the gcode alltogether. '''
	bl_idname = "object.calculate_cam_paths_chain"
	bl_label = "Calculate CAM paths in current chain and export chain gcode"
	bl_options = {'REGISTER', 'UNDO'}
		
	def execute(self, context):
		import bpy
		s=bpy.context.scene
		
		chain=s.cam_chains[s.cam_active_chain]
		chainops=getChainOperations(chain)
		meshes=[]
		for o in chainops:
			#bpy.ops.object.calculate_cam_paths_background()
			meshes.append(bpy.data.objects[o.path_object_name].data)
		utils.exportGcodePath(chain.filename,meshes,chainops)
		return {'FINISHED'}
	
	def draw(self, context):
		layout = self.layout
		layout.prop_search(self, "operation", bpy.context.scene, "cam_operations")	 

class CAMSimulate(bpy.types.Operator):
	'''simulate CAM operation
	this is performed by: creating an image, painting Z depth of the brush substractively. Works only for some operations, can not be used for 4-5 axis.'''
	bl_idname = "object.cam_simulate"
	bl_label = "CAM simulation"
	bl_options = {'REGISTER', 'UNDO'}

	operation = StringProperty(name="Operation",
						   description="Specify the operation to calculate",default='Operation')

	def execute(self, context):
		s=bpy.context.scene
		operation = s.cam_operations[s.cam_active_operation]
		
		#if operation.geometry_source=='OBJECT' and operation.object_name in bpy.data.objects and #bpy.data.objects[operation.object_name].type=='CURVE':
		#	print('simulation of curve operations is not available')
		#	return {'FINISHED'}
		if operation.path_object_name in bpy.data.objects:
			utils.doSimulation(operation.name,[operation])
		else:
		   print('no computed path to simulate')
		   return {'FINISHED'}
		return {'FINISHED'}
	
	def draw(self, context):
		layout = self.layout
		layout.prop_search(self, "operation", bpy.context.scene, "cam_operations")

		
class CAMSimulateChain(bpy.types.Operator):
	'''simulate CAM chain, compared to single op simulation just writes into one image and thus enables to see how ops work together.'''
	bl_idname = "object.cam_simulate_chain"
	bl_label = "CAM simulation"
	bl_options = {'REGISTER', 'UNDO'}

	operation = StringProperty(name="Operation",
						   description="Specify the operation to calculate",default='Operation')

	def execute(self, context):
		s=bpy.context.scene
		chain=s.cam_chains[s.cam_active_chain]
		chainops=getChainOperations(chain)
		
		canSimulate=True
		for operation in chainops:
			if not operation.path_object_name in bpy.data.objects:
				canSimulate=False
		if canSimulate:
			utils.doSimulation(chain.name,chainops)
		else:
		   print('no computed path to simulate')
		   return {'FINISHED'}
		return {'FINISHED'}
	
	def draw(self, context):
		layout = self.layout
		layout.prop_search(self, "operation", bpy.context.scene, "cam_operations")

class CAMPositionObject(bpy.types.Operator):
	'''position object for CAM operation. Tests object bounds and places them so the object is aligned to be positive from x and y and negative from z.'''
	bl_idname = "object.cam_position"
	bl_label = "position object for CAM operation"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		s=bpy.context.scene
		operation = s.cam_operations[s.cam_active_operation]
		if operation.object_name in bpy.data.objects:
			utils.positionObject(operation)
		else:
		   print('no object assigned')
		   return {'FINISHED'}
		return {'FINISHED'}
	
	def draw(self, context):
		layout = self.layout
		layout.prop_search(self, "operation", bpy.context.scene, "cam_operations")

class CamChainAdd(bpy.types.Operator):
	'''Add new CAM chain'''
	bl_idname = "scene.cam_chain_add"
	bl_label = "Add new CAM chain"

	@classmethod
	def poll(cls, context):
		return context.scene is not None

	def execute(self, context):
		#main(context)
		s=bpy.context.scene
		s.cam_chains.add()
		chain=s.cam_chains[-1]
		s.cam_active_chain=len(s.cam_chains)-1
		chain.name='Chain_'+str(s.cam_active_chain+1)
		chain.filename=chain.name
		chain.index=s.cam_active_chain
		
		return {'FINISHED'}

		
class CamChainRemove(bpy.types.Operator):
	'''Remove  CAM chain'''
	bl_idname = "scene.cam_chain_remove"
	bl_label = "Remove CAM chain"

	@classmethod
	def poll(cls, context):
		return context.scene is not None

	def execute(self, context):
		bpy.context.scene.cam_chains.remove(bpy.context.scene.cam_active_chain)
		if bpy.context.scene.cam_active_chain>0:
			bpy.context.scene.cam_active_chain-=1
		
		return {'FINISHED'}

class CamChainOperationAdd(bpy.types.Operator):
	'''Add operation to chain'''
	bl_idname = "scene.cam_chain_operation_add"
	bl_label = "Add operation to chain"

	@classmethod
	def poll(cls, context):
		return context.scene is not None

	def execute(self, context):
		s=bpy.context.scene
		chain=s.cam_chains[s.cam_active_chain]
		s=bpy.context.scene
		#s.chaindata[chain.index].remove(chain.active_operation+1,s.cam_operations[s.cam_active_operation])
		chain.operations.add()
		chain.active_operation+=1
		chain.operations[-1].name=s.cam_operations[s.cam_active_operation].name
		return {'FINISHED'}
		
class CamChainOperationRemove(bpy.types.Operator):
	'''Remove operation from chain'''
	bl_idname = "scene.cam_chain_operation_remove"
	bl_label = "Remove operation from chain"

	@classmethod
	def poll(cls, context):
		return context.scene is not None

	def execute(self, context):
		#main(context)
		s=bpy.context.scene
		chain=s.cam_chains[s.cam_active_chain]
		s=bpy.context.scene
		#s.chaindata[chain.index].append(s.cam_operations[s.cam_active_operation])
		chain.operations.remove(chain.active_operation)
		chain.active_operation-=1
		if chain.active_operation<0:
			chain.active_operation = 0
		return {'FINISHED'}

		
class CamOperationAdd(bpy.types.Operator):
	'''Add new CAM operation'''
	bl_idname = "scene.cam_operation_add"
	bl_label = "Add new CAM operation"

	@classmethod
	def poll(cls, context):
		return context.scene is not None

	def execute(self, context):
		#main(context)
		s=bpy.context.scene
		if s.unit_settings.system=='NONE':
			s.unit_settings.system='METRIC'
		s.unit_settings.system_rotation='DEGREES'	
		
		if s.objects.get('CAM_machine')==None:
			utils.addMachineAreaObject()
		#if len(s.cam_material)==0:
		#	 s.cam_material.add()
		  
		s.cam_operations.add()
		o=s.cam_operations[-1]
		s.cam_active_operation=len(s.cam_operations)-1
		o.name='Operation_'+str(s.cam_active_operation+1)
		o.filename=o.name
		ob=bpy.context.active_object
		if ob!=None:
			o.object_name=ob.name
			minx,miny,minz,maxx,maxy,maxz=utils.getBoundsWorldspace([ob])
			o.minz=minz
		
		return {'FINISHED'}
	
class CamOperationCopy(bpy.types.Operator):
	'''Copy CAM operation'''
	bl_idname = "scene.cam_operation_copy"
	bl_label = "Copy active CAM operation"

	@classmethod
	def poll(cls, context):
		return context.scene is not None

	def execute(self, context):
		#main(context)
		s=bpy.context.scene
		if s.unit_settings.system=='NONE':
			s.unit_settings.system='METRIC'
		s.unit_settings.system_rotation='DEGREES'	
		  
		s=bpy.context.scene
		s.cam_operations.add()
		copyop=s.cam_operations[s.cam_active_operation]
		s.cam_active_operation+=1
		l=len(s.cam_operations)-1
		s.cam_operations.move(l,s.cam_active_operation)
		o=s.cam_operations[s.cam_active_operation]

		for k in copyop.keys():
			o[k]=copyop[k]
		o.computing=False
		
		####get digits in the end
		####
		isdigit=True
		numdigits=0
		num=0
		if o.name[-1].isdigit():
			numdigits=1
			while isdigit:
				numdigits+=1
				isdigit=o.name[-numdigits].isdigit()
			numdigits-=1
			o.name=o.name[:-numdigits]+str(int(o.name[-numdigits:])+1).zfill(numdigits)
			o.filename=o.name
		else:
			o.name=o.name+'_copy'
			o.filename=o.filename+'_copy'
		#ob=bpy.context.active_object
		#if ob!=None:
		#	o.object_name=ob.name
		#	o.minz=ob.location.z+ob.bound_box[0][2]
		return {'FINISHED'}
	
class CamOperationRemove(bpy.types.Operator):
	'''Remove CAM operation'''
	bl_idname = "scene.cam_operation_remove"
	bl_label = "Remove CAM operation"

	@classmethod
	def poll(cls, context):
		return context.scene is not None

	def execute(self, context):
		#main(context)
		bpy.context.scene.cam_operations.remove(bpy.context.scene.cam_active_operation)
		if bpy.context.scene.cam_active_operation>0:
			bpy.context.scene.cam_active_operation-=1
		
		return {'FINISHED'}

class CamOperationMove(bpy.types.Operator):
	'''Move CAM operation'''
	bl_idname = "scene.cam_operation_move"
	bl_label = "Move CAM operation in list"
	
	direction = EnumProperty(name='direction',
		items=(('UP','Up',''),('DOWN','Down','')),
		description='direction',
		default='DOWN')
		
	@classmethod
	def poll(cls, context):
		return context.scene is not None

	def execute(self, context):
		#main(context)
		a=bpy.context.scene.cam_active_operation
		cops=bpy.context.scene.cam_operations
		if self.direction=='UP':
			if a>0:
				cops.move(a,a-1)
				bpy.context.scene.cam_active_operation -= 1

		else:
			if a<len(cops)-1:
				cops.move(a,a+1)
				bpy.context.scene.cam_active_operation += 1

		return {'FINISHED'}



class CAM_CUTTER_presets(Menu):
	bl_label = "Cutter presets"
	preset_subdir = "cam_cutters"
	preset_operator = "script.execute_preset"
	draw = Menu.draw_preset

class CAM_MACHINE_presets(Menu):
	bl_label = "Machine presets"
	preset_subdir = "cam_machines"
	preset_operator = "script.execute_preset"
	draw = Menu.draw_preset
	
class AddPresetCamCutter(bl_operators.presets.AddPresetBase, Operator):
	'''Add a Cutter Preset'''
	bl_idname = "render.cam_preset_cutter_add"
	bl_label = "Add Cutter Preset"
	preset_menu = "CAM_CUTTER_presets"
	
	preset_defines = [
		"d = bpy.context.scene.cam_operations[bpy.context.scene.cam_active_operation]"
	]

	preset_values = [
		"d.cutter_id",
		"d.cutter_type",
		"d.cutter_diameter",
		"d.cutter_length",
		"d.cutter_flutes",
		"d.cutter_tip_angle",
	]

	preset_subdir = "cam_cutters"

class CAM_OPERATION_presets(Menu):
	bl_label = "Operation presets"
	preset_subdir = "cam_operations"
	preset_operator = "script.execute_preset"
	draw = Menu.draw_preset
		
class AddPresetCamOperation(bl_operators.presets.AddPresetBase, Operator):
	'''Add an Operation Preset'''
	bl_idname = "render.cam_preset_operation_add"
	bl_label = "Add Operation Preset"
	preset_menu = "CAM_OPERATION_presets"
	
	preset_defines = [
		"o = bpy.context.scene.cam_operations[bpy.context.scene.cam_active_operation]"
	]
	'''
	d1=dir(bpy.types.machineSettings.bl_rna)

	d=[]
	for prop in d1:
		if (prop[:2]!='__' 
			and prop!='bl_rna'
			and prop!='translation_context'
			and prop!='base'
			and prop!='description'
			and prop!='identifier'
			and prop!='name'
			and prop!='name_property'):
				d.append(prop)
	'''
	preset_values = ['use_layers', 'duration', 'chipload', 'material_from_model', 'stay_low', 'carve_depth', 'dist_along_paths', 'source_image_crop_end_x', 'source_image_crop_end_y', 'material_size', 'material_radius_around_model', 'use_limit_curve', 'cut_type', 'use_exact', 'minz_from_ob', 'free_movement_height', 'source_image_crop_start_x', 'movement_insideout', 'spindle_rotation_direction', 'skin', 'source_image_crop_start_y', 'movement_type', 'source_image_crop', 'limit_curve', 'spindle_rpm', 'ambient_behaviour', 'cutter_type', 'source_image_scale_z', 'cutter_diameter', 'source_image_size_x', 'curve_object', 'cutter_flutes', 'ambient_radius', 'simulation_detail', 'update_offsetimage_tag', 'dist_between_paths', 'max', 'min', 'pixsize', 'slice_detail', 'parallel_step_back', 'drill_type', 'source_image_name', 'dont_merge', 'update_silhouete_tag', 'material_origin', 'inverse', 'waterline_fill', 'source_image_offset', 'circle_detail', 'strategy', 'update_zbufferimage_tag', 'stepdown', 'feedrate', 'cutter_tip_angle', 'cutter_id', 'path_object_name', 'pencil_threshold',	 'geometry_source', 'optimize_threshold', 'protect_vertical', 'plunge_feedrate', 'minz', 'warnings', 'object_name', 'optimize', 'parallel_angle', 'cutter_length']

	preset_subdir = "cam_operations"   
	 
class AddPresetCamMachine(bl_operators.presets.AddPresetBase, Operator):
	'''Add a Cam Machine Preset'''
	bl_idname = "render.cam_preset_machine_add"
	bl_label = "Add Machine Preset"
	preset_menu = "CAM_MACHINE_presets"

	preset_defines = [
		"d = bpy.context.scene.cam_machine",
		"s = bpy.context.scene.unit_settings"
	]
	preset_values = [
		"d.post_processor",
		"s.system",
		"d.working_area",
		"d.feedrate_min",
		"d.feedrate_max",
		"d.feedrate_default",
		"d.spindle_min",
		"d.spindle_max",
		"d.spindle_default",
		"d.axis4",
		"d.axis5",
		"d.collet_size",
	]

	preset_subdir = "cam_machines"
			   
	
####Panel definitions
class CAMButtonsPanel():
	bl_space_type = 'PROPERTIES'
	bl_region_type = 'WINDOW'
	bl_context = "render"
	# COMPAT_ENGINES must be defined in each subclass, external engines can add themselves here
	
	@classmethod
	def poll(cls, context):
		rd = context.scene.render
		return rd.engine in cls.COMPAT_ENGINES
	

class CAM_CUTTER_Panel(CAMButtonsPanel, bpy.types.Panel):   
	"""CAM cutter panel"""
	bl_label = " "
	bl_idname = "WORLD_PT_CAM_CUTTER"
		
	COMPAT_ENGINES = {'BLENDERCAM_RENDER'}
	
	def draw_header(self, context):
	   self.layout.menu("CAM_CUTTER_presets", text="CAM Cutter")
		
	def draw(self, context):
		layout = self.layout
		d=bpy.context.scene
		if len(d.cam_operations)>0:
			ao=d.cam_operations[d.cam_active_operation]
		
			if ao:
				#cutter preset
				row = layout.row(align=True)
				row.menu("CAM_CUTTER_presets", text=bpy.types.CAM_CUTTER_presets.bl_label)
				row.operator("render.cam_preset_cutter_add", text="", icon='ZOOMIN')
				row.operator("render.cam_preset_cutter_add", text="", icon='ZOOMOUT').remove_active = True
				layout.prop(ao,'cutter_id')
				layout.prop(ao,'cutter_type')
				layout.prop(ao,'cutter_diameter')
				#layout.prop(ao,'cutter_length')
				layout.prop(ao,'cutter_flutes')
				if ao.cutter_type=='VCARVE':
					layout.prop(ao,'cutter_tip_angle')
				if ao.cutter_type=='CUSTOM':
					layout.prop_search(ao, "cutter_object_name", bpy.data, "objects")

   
class CAM_MACHINE_Panel(CAMButtonsPanel, bpy.types.Panel):	
	"""CAM machine panel"""
	bl_label = " "
	bl_idname = "WORLD_PT_CAM_MACHINE"
		
	COMPAT_ENGINES = {'BLENDERCAM_RENDER'}
	
	def draw_header(self, context):
	   self.layout.menu("CAM_MACHINE_presets", text="CAM Machine")
		
	def draw(self, context):
		layout = self.layout
		s=bpy.context.scene
		us=s.unit_settings
		
		ao=s.cam_machine
	
		if ao:
			#cutter preset
			row = layout.row(align=True)
			row.menu("CAM_MACHINE_presets", text=bpy.types.CAM_MACHINE_presets.bl_label)
			row.operator("render.cam_preset_machine_add", text="", icon='ZOOMIN')
			row.operator("render.cam_preset_machine_add", text="", icon='ZOOMOUT').remove_active = True
			#layout.prop(ao,'name')
			layout.prop(ao,'post_processor')
			layout.prop(ao,'eval_splitting')
			if ao.eval_splitting:
				layout.prop(ao,'split_limit')
			
			layout.prop(us,'system')
			layout.prop(ao,'working_area')
			layout.prop(ao,'feedrate_min')
			layout.prop(ao,'feedrate_max')
			#layout.prop(ao,'feedrate_default')
			layout.prop(ao,'spindle_min')
			layout.prop(ao,'spindle_max')
			#layout.prop(ao,'spindle_default')
			#layout.prop(ao,'axis4')
			#layout.prop(ao,'axis5')
			#layout.prop(ao,'collet_size')
			#

class CAM_MATERIAL_Panel(CAMButtonsPanel, bpy.types.Panel):	 
	"""CAM material panel"""
	bl_label = "CAM Material size and position"
	bl_idname = "WORLD_PT_CAM_MATERIAL"
		
	COMPAT_ENGINES = {'BLENDERCAM_RENDER'}
	
	def draw(self, context):
		layout = self.layout
		scene=bpy.context.scene
		
		if len(scene.cam_operations)==0:
			layout.label('Add operation first')
		if len(scene.cam_operations)>0:
			ao=scene.cam_operations[scene.cam_active_operation]
			if ao:
				#print(dir(layout))
				layout.template_running_jobs()
				if ao.geometry_source=='OBJECT' or ao.geometry_source=='GROUP':
					row = layout.row(align=True)
					layout.prop(ao,'material_from_model')
					
					if ao.material_from_model:
						layout.prop(ao,'material_radius_around_model')
						layout.operator("object.cam_position", text="Position object")
					else:
						layout.prop(ao,'material_origin')
						layout.prop(ao,'material_size')
				else:
					layout.label('Estimated from image')
		
class CAM_UL_operations(UIList):
	def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
		# assert(isinstance(item, bpy.types.VertexGroup)
		operation = item
		if self.layout_type in {'DEFAULT', 'COMPACT'}:
			
			layout.label(text=item.name, translate=False, icon_value=icon)
			icon = 'LOCKED' if operation.computing else 'UNLOCKED'
			if operation.computing:
				layout.label(text="computing" )
		elif self.layout_type in {'GRID'}:
			 layout.alignment = 'CENTER'
			 layout.label(text="", icon_value=icon)
			 
class CAM_UL_chains(UIList):
	def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
		# assert(isinstance(item, bpy.types.VertexGroup)
		chain = item
		if self.layout_type in {'DEFAULT', 'COMPACT'}:
			
			layout.label(text=item.name, translate=False, icon_value=icon)
			icon = 'LOCKED' if chain.computing else 'UNLOCKED'
			if chain.computing:
				layout.label(text="computing" )
		elif self.layout_type in {'GRID'}:
			 layout.alignment = 'CENTER'
			 layout.label(text="", icon_value=icon)
			 
class CAM_CHAINS_Panel(CAMButtonsPanel, bpy.types.Panel):
	"""CAM chains panel"""
	bl_label = "CAM chains"
	bl_idname = "WORLD_PT_CAM_CHAINS"
		
	COMPAT_ENGINES = {'BLENDERCAM_RENDER'}
	
	

	def draw(self, context):
		layout = self.layout
		
		row = layout.row() 
		scene=bpy.context.scene
		
		row.template_list("CAM_UL_chains", '', scene, "cam_chains", scene, 'cam_active_chain')
		col = row.column(align=True)
		col.operator("scene.cam_chain_add", icon='ZOOMIN', text="")
		#col.operator("scene.cam_operation_copy", icon='COPYDOWN', text="")
		col.operator("scene.cam_chain_remove",icon='ZOOMOUT', text="")
		#if group:
		#col.separator()
		#col.operator("scene.cam_operation_move", icon='TRIA_UP', text="").direction = 'UP'
		#col.operator("scene.cam_operation_move", icon='TRIA_DOWN', text="").direction = 'DOWN'
		#row = layout.row() 
	   
		if len(scene.cam_chains)>0:
			chain=scene.cam_chains[scene.cam_active_chain]

			row = layout.row(align=True)
			
			if chain:
				row.template_list("CAM_UL_operations", '', chain, "operations", chain, 'active_operation')
				col = row.column(align=True)
				col.operator("scene.cam_chain_operation_add", icon='ZOOMIN', text="")
				col.operator("scene.cam_chain_operation_remove",icon='ZOOMOUT', text="")

				if not chain.computing:
					if chain.valid:
						pass
						layout.operator("object.calculate_cam_paths_chain", text="Export chain gcode")
						#layout.operator("object.calculate_cam_paths_background", text="Calculate path in background")
						layout.operator("object.cam_simulate_chain", text="Simulate this chain")
					else:
						layout.label("chain invalid, can't compute")
				else:
					layout.label('chain is currently computing')
					#layout.prop(ao,'computing')
				
				layout.prop(chain,'name')
				layout.prop(chain,'filename')
		
			 
class CAM_OPERATIONS_Panel(CAMButtonsPanel, bpy.types.Panel):
	"""CAM operations panel"""
	bl_label = "CAM operations"
	bl_idname = "WORLD_PT_CAM_OPERATIONS"
	
	
	COMPAT_ENGINES = {'BLENDERCAM_RENDER'}
	
	

	def draw(self, context):
		layout = self.layout
		
		row = layout.row() 
		scene=bpy.context.scene
		row.template_list("CAM_UL_operations", '', scene, "cam_operations", scene, 'cam_active_operation')
		col = row.column(align=True)
		col.operator("scene.cam_operation_add", icon='ZOOMIN', text="")
		col.operator("scene.cam_operation_copy", icon='COPYDOWN', text="")
		col.operator("scene.cam_operation_remove",icon='ZOOMOUT', text="")
		#if group:
		col.separator()
		col.operator("scene.cam_operation_move", icon='TRIA_UP', text="").direction = 'UP'
		col.operator("scene.cam_operation_move", icon='TRIA_DOWN', text="").direction = 'DOWN'
		#row = layout.row() 
	   
		if len(scene.cam_operations)>0:
			ao=scene.cam_operations[scene.cam_active_operation]

			row = layout.row(align=True)
			row.menu("CAM_OPERATION_presets", text=bpy.types.CAM_OPERATION_presets.bl_label)
			row.operator("render.cam_preset_operation_add", text="", icon='ZOOMIN')
			row.operator("render.cam_preset_operation_add", text="", icon='ZOOMOUT').remove_active = True
			
			if ao:
				if not ao.computing:
					if ao.valid:
						layout.operator("object.calculate_cam_path", text="Calculate path")
						layout.operator("object.calculate_cam_paths_background", text="Calculate path in background")
						layout.operator("object.cam_simulate", text="Simulate this operation")
					else:
						layout.label("operation invalid, can't compute")
				else:
					layout.label('operation is currently computing')
					#layout.prop(ao,'computing')
				
				layout.prop(ao,'name')
				layout.prop(ao,'filename')
				layout.prop(ao,'geometry_source')
				if ao.geometry_source=='OBJECT':
					layout.prop_search(ao, "object_name", bpy.data, "objects")
				elif ao.geometry_source=='GROUP':
					layout.prop_search(ao, "group_name", bpy.data, "groups")
				else:
					layout.prop_search(ao, "source_image_name", bpy.data, "images")
					
 
				if ao.strategy=='CARVE':
					layout.prop_search(ao, "curve_object", bpy.data, "objects")
			   

def getUnit():
	if bpy.context.scene.unit_settings.system == 'METRIC':
		return 'mm'
	elif bpy.context.scene.unit_settings.system == 'IMPERIAL':
		return "''"
									 
class CAM_INFO_Panel(CAMButtonsPanel, bpy.types.Panel):
	"""CAM info panel"""
	bl_label = "CAM info & warnings"
	bl_idname = "WORLD_PT_CAM_INFO"	  
	
	COMPAT_ENGINES = {'BLENDERCAM_RENDER'}
	
	def draw(self, context):
		layout = self.layout
		scene=bpy.context.scene
		row = layout.row() 
		if len(scene.cam_operations)==0:
			layout.label('Add operation first')
		if len(scene.cam_operations)>0:
			ao=scene.cam_operations[scene.cam_active_operation]
			if ao.warnings!='':
				lines=ao.warnings.split('\n')
				for l in lines:
					layout.label(l)
			if ao.valid:
				#ob=bpy.data.objects[ao.object_name]
				#layout.separator()
				if ao.duration>0:
					layout.label('operation time: '+str(int(ao.duration*100)/100.0)+' min')	   
				#layout.prop(ao,'chipload')
				layout.label(  'chipload: '+str(round(ao.chipload,6))+getUnit()+' / tooth')
				#layout.label(str(ob.dimensions.x))
				#row=layout.row()
		
class CAM_OPERATION_PROPERTIES_Panel(CAMButtonsPanel, bpy.types.Panel):
	"""CAM operation properties panel"""
	bl_label = "CAM operation setup"
	bl_idname = "WORLD_PT_CAM_OPERATION"
	
	
	COMPAT_ENGINES = {'BLENDERCAM_RENDER'}
	
	

	def draw(self, context):
		layout = self.layout
		scene=bpy.context.scene
		
			
		row = layout.row() 
		if len(scene.cam_operations)==0:
			layout.label('Add operation first')
		if len(scene.cam_operations)>0:
			ao=scene.cam_operations[scene.cam_active_operation]
			if ao.valid:
				#layout.prop(ao,'axes')
				if ao.axes=='3':
					layout.prop(ao,'strategy')
				elif ao.axes=='4':
					layout.prop(ao,'strategy4axis')
				elif ao.axes=='5':
					layout.prop(ao,'strategy5axis')
				if ao.strategy=='BLOCK' or ao.strategy=='SPIRAL' or ao.strategy=='CIRCLES':
					layout.prop(ao,'movement_insideout')
					
				#if ao.geometry_source=='OBJECT' or ao.geometry_source=='GROUP':
					'''
					o=bpy.data.objects[ao.object_name]
					
					if o.type=='MESH' and (ao.strategy=='DRILL'):
						layout.label('Not supported for meshes')
						return
					'''
					#elif o.type=='CURVE' and (ao.strategy!='CARVE' and ao.strategy!='POCKET' and ao.strategy!='DRILL' and ao.strategy!='CUTOUT'):
					 #	 layout.label('Not supported for curves')
					 #	 return
					
				if ao.strategy=='CUTOUT':
					layout.prop(ao,'cut_type')
					layout.prop(ao,'dont_merge')
					layout.prop(ao,'use_bridges')
					if ao.use_bridges:
						layout.prop(ao,'bridges_width')
						layout.prop(ao,'bridges_height')
						layout.prop(ao,'bridges_per_curve')
						layout.prop(ao,'bridges_max_distance')
					
				elif ao.strategy=='WATERLINE':
					layout.prop(ao,'slice_detail')	
					layout.prop(ao,'waterline_fill')  
					if ao.waterline_fill:
						layout.prop(ao,'dist_between_paths')			
						layout.prop(ao,'waterline_project')
					layout.prop(ao,'skin')
					layout.prop(ao,'inverse')
				elif ao.strategy=='CARVE':
					layout.prop(ao,'carve_depth')
					layout.prop(ao,'dist_along_paths')
				elif ao.strategy=='PENCIL':
					layout.prop(ao,'dist_along_paths')
					layout.prop(ao,'pencil_threshold')
				elif ao.strategy=='CRAZY':
					layout.prop(ao,'crazy_threshold1')
					layout.prop(ao,'crazy_threshold2')
					layout.prop(ao,'crazy_threshold3')
					layout.prop(ao,'crazy_threshold4')
					layout.prop(ao,'dist_between_paths')
					layout.prop(ao,'dist_along_paths')
				elif ao.strategy=='DRILL':
					layout.prop(ao,'drill_type')
				else:				 
					layout.prop(ao,'dist_between_paths')
					layout.prop(ao,'dist_along_paths')
					if ao.strategy=='PARALLEL' or ao.strategy=='CROSS':
						layout.prop(ao,'parallel_angle')
						layout.prop(ao,'parallel_step_back')
						
					layout.prop(ao,'skin')
					layout.prop(ao,'inverse')
				#elif ao.strategy=='SLICES':
				#	layout.prop(ao,'slice_detail')	  
				
class CAM_MOVEMENT_Panel(CAMButtonsPanel, bpy.types.Panel):
	"""CAM movement panel"""
	bl_label = "CAM movement"
	bl_idname = "WORLD_PT_CAM_MOVEMENT"	  
	
	COMPAT_ENGINES = {'BLENDERCAM_RENDER'}
	
	def draw(self, context):
		layout = self.layout
		scene=bpy.context.scene
		row = layout.row() 
		if len(scene.cam_operations)==0:
			layout.label('Add operation first')
		if len(scene.cam_operations)>0:
			ao=scene.cam_operations[scene.cam_active_operation]
			if ao.valid:
				layout.prop(ao,'movement_type')
				if ao.movement_type=='BLOCK' or ao.movement_type=='SPIRAL' or ao.movement_type=='CIRCLES':
					layout.prop(ao,'movement_insideout')
				   
				layout.prop(ao,'spindle_rotation_direction')
				layout.prop(ao,'free_movement_height')
				if ao.strategy=='CUTOUT':
					layout.prop(ao,'first_down')
					if ao.first_down:
						layout.prop(ao,'contour_ramp')
						if ao.contour_ramp:
							layout.prop(ao,'ramp_out')
							if ao.ramp_out:
								layout.prop(ao,'ramp_out_angle')
				if ao.strategy=='POCKET':
					layout.prop(ao,'helix_enter')
					if ao.helix_enter:
						layout.prop(ao,'helix_angle')
						layout.prop(ao,'helix_diameter')
					layout.prop(ao,'retract_tangential')
					if ao.retract_tangential:
						layout.prop(ao,'retract_radius')
						layout.prop(ao,'retract_height')
						
					
				layout.prop(ao,'stay_low')
				layout.prop(ao,'protect_vertical')
				if ao.protect_vertical:
					layout.prop(ao,'protect_vertical_limit')
			  
				
class CAM_FEEDRATE_Panel(CAMButtonsPanel, bpy.types.Panel):
	"""CAM feedrate panel"""
	bl_label = "CAM feedrate"
	bl_idname = "WORLD_PT_CAM_FEEDRATE"	  
	
	COMPAT_ENGINES = {'BLENDERCAM_RENDER'}
	
	def draw(self, context):
		layout = self.layout
		scene=bpy.context.scene
		row = layout.row() 
		if len(scene.cam_operations)==0:
			layout.label('Add operation first')
		if len(scene.cam_operations)>0:
			ao=scene.cam_operations[scene.cam_active_operation]
			if ao.valid:
				layout.prop(ao,'feedrate')
				layout.prop(ao,'plunge_feedrate')
				layout.prop(ao,'plunge_angle')
				layout.prop(ao,'spindle_rpm')

class CAM_OPTIMISATION_Panel(CAMButtonsPanel, bpy.types.Panel):
	"""CAM optimisation panel"""
	bl_label = "CAM optimisation"
	bl_idname = "WORLD_PT_CAM_OPTIMISATION"
	
	COMPAT_ENGINES = {'BLENDERCAM_RENDER'}
	
	

	def draw(self, context):
		layout = self.layout
		scene=bpy.context.scene
		
			
		row = layout.row() 
		if len(scene.cam_operations)==0:
			layout.label('Add operation first')
		if len(scene.cam_operations)>0:
			ao=scene.cam_operations[scene.cam_active_operation]
			if ao.valid: 
				layout.prop(ao,'optimize')
				if ao.optimize:
					layout.prop(ao,'optimize_threshold')
				if ao.geometry_source=='OBJECT' or ao.geometry_source=='GROUP':
					exclude_exact= ao.strategy=='CUTOUT' or ao.strategy=='DRILL' or ao.strategy=='PENCIL'
					if not exclude_exact:
						layout.prop(ao,'use_exact')
					#if not ao.use_exact or:
					layout.prop(ao,'pixsize')
					layout.prop(ao,'imgres_limit')
					
					sx=ao.max.x-ao.min.x
					sy=ao.max.y-ao.min.y
					resx=int(sx/ao.pixsize)
					resy=int(sy/ao.pixsize)
					l='resolution:'+str(resx)+'x'+str(resy)
					layout.label( l)
					
				layout.prop(ao,'simulation_detail')
				layout.prop(ao,'circle_detail')
				#if not ao.use_exact:#this will be replaced with groups of objects.
				#layout.prop(ao,'render_all')# replaced with groups support
		
class CAM_AREA_Panel(CAMButtonsPanel, bpy.types.Panel):
	"""CAM operation area panel"""
	bl_label = "CAM operation area "
	bl_idname = "WORLD_PT_CAM_OPERATION_AREA"
	
	COMPAT_ENGINES = {'BLENDERCAM_RENDER'}
	

	def draw(self, context):
		layout = self.layout
		scene=bpy.context.scene
		row = layout.row() 
		if len(scene.cam_operations)==0:
			layout.label('Add operation first')
		if len(scene.cam_operations)>0:
			ao=scene.cam_operations[scene.cam_active_operation]
			if ao.valid:
				#o=bpy.data.objects[ao.object_name]
				layout.prop(ao,'use_layers')
				if ao.use_layers:
					layout.prop(ao,'stepdown')
				
				layout.prop(ao,'ambient_behaviour')
				if ao.ambient_behaviour=='AROUND':
					layout.prop(ao,'ambient_radius')
				
				layout.prop(ao,'maxz')#experimental
				if ao.geometry_source=='OBJECT' or ao.geometry_source=='GROUP':
					layout.prop(ao,'minz_from_ob')
					if not ao.minz_from_ob:
						layout.prop(ao,'minz')
				else:
					layout.prop(ao,'source_image_scale_z') 
					layout.prop(ao,'source_image_size_x') 
					if ao.source_image_name!='':
						i=bpy.data.images[ao.source_image_name]
						if i!=None:
							sy=int((ao.source_image_size_x/i.size[0])*i.size[1]*1000000)/1000
							layout.label('image size on y axis: '+ str(sy)+getUnit())
							#print(dir(layout))
							layout.separator()
					layout.prop(ao,'source_image_offset') 
					col = layout.column(align=True)
					#col.label('image crop:')
					#col=layout.column()
					col.prop(ao,'source_image_crop',text='Crop source image') 
					if ao.source_image_crop:
						col.prop(ao,'source_image_crop_start_x',text='start x') 
						col.prop(ao,'source_image_crop_start_y',text='start y') 
						col.prop(ao,'source_image_crop_end_x',text='end x')
						col.prop(ao,'source_image_crop_end_y',text='end y')
				layout.prop(ao,'use_limit_curve')				   
				if ao.use_limit_curve:
					layout.prop_search(ao, "limit_curve", bpy.data, "objects")
				layout.prop(ao,"ambient_cutter_restrict")
				
class CAM_PACK_Panel(CAMButtonsPanel, bpy.types.Panel):	 
	"""CAM material panel"""
	bl_label = "Pack curves on sheet"
	bl_idname = "WORLD_PT_CAM_PACK"
		
	COMPAT_ENGINES = {'BLENDERCAM_RENDER'}
	
	def draw(self, context):
		layout = self.layout
		scene=bpy.context.scene
		settings=scene.cam_pack
		layout.label('warning - algorithm is slow.' )
		layout.label('only for curves now.' )
		
		layout.operator("object.cam_pack_objects")
		layout.prop(settings,'sheet_fill_direction')
		layout.prop(settings,'sheet_x')
		layout.prop(settings,'sheet_y')
		layout.prop(settings,'distance')
		layout.prop(settings,'rotate')
		
class BLENDERCAM_ENGINE(bpy.types.RenderEngine):
	bl_idname = 'BLENDERCAM_RENDER'
	bl_label = "Blender CAM"
				
def get_panels():#convenience function for bot register and unregister functions
	types = bpy.types
	return (
	CAM_UL_operations,
	CAM_UL_chains,
	camOperation,
	opReference,
	camChain,
	machineSettings,
	CAM_CHAINS_Panel,
	CAM_OPERATIONS_Panel,
	CAM_INFO_Panel,
	CAM_MATERIAL_Panel,
	CAM_OPERATION_PROPERTIES_Panel,
	CAM_OPTIMISATION_Panel,
	CAM_AREA_Panel,
	CAM_MOVEMENT_Panel,
	CAM_FEEDRATE_Panel,
	CAM_CUTTER_Panel,
	CAM_MACHINE_Panel,
	
	PathsBackground,
	CalculatePath,
	PathsChain,
	PathsAll,
	CAMPositionObject,
	CAMSimulate,
	CAMSimulateChain,
	CamChainAdd,
	CamChainRemove,
	CamChainOperationAdd,
	CamChainOperationRemove,
	CamOperationAdd,
	CamOperationCopy,
	CamOperationRemove,
	CamOperationMove,
	
	
	CAM_CUTTER_presets,
	CAM_OPERATION_presets,
	CAM_MACHINE_presets,
	AddPresetCamCutter,
	AddPresetCamOperation,
	AddPresetCamMachine,
	BLENDERCAM_ENGINE,
	#CamBackgroundMonitor
	#pack module:
	PackObjectsSettings,
	CamPackObjects,
	CAM_PACK_Panel
	)
	
def register():
	for p in get_panels():
		bpy.utils.register_class(p)
	
	s = bpy.types.Scene
	
	s.cam_chains = bpy.props.CollectionProperty(type=camChain)
	s.cam_active_chain = bpy.props.IntProperty(name="CAM Active Chain", description="The selected chain")

	s.cam_operations = bpy.props.CollectionProperty(type=camOperation)
	
	s.cam_active_operation = bpy.props.IntProperty(name="CAM Active Operation", description="The selected operation")
	s.cam_machine = bpy.props.PointerProperty(type=machineSettings)
	
	s.cam_text= bpy.props.StringProperty()
	bpy.app.handlers.scene_update_pre.append(timer_update)
	bpy.app.handlers.load_post.append(check_operations_on_load)
	bpy.types.INFO_HT_header.append(header_info)
	
	s.cam_pack = bpy.props.PointerProperty(type=PackObjectsSettings)
	
	'''
	try:
		bpy.utils.unregister_class(bpy.types.RENDER_PT_render)
		bpy.utils.unregister_class(bpy.types.RENDER_PT_dimensions)
		bpy.utils.unregister_class(bpy.types.RENDER_PT_antialiasing)
		bpy.utils.unregister_class(bpy.types.RENDER_PT_motion_blur)
		bpy.utils.unregister_class(bpy.types.RENDER_PT_shading)
		bpy.utils.unregister_class(bpy.types.RENDER_PT_performance)
		bpy.utils.unregister_class(bpy.types.RENDER_PT_post_processing)
		bpy.utils.unregister_class(bpy.types.RENDER_PT_stamp)
		bpy.utils.unregister_class(bpy.types.RENDER_PT_output)
		bpy.utils.unregister_class(bpy.types.RENDER_PT_bake)
		bpy.utils.unregister_class(bpy.types.RENDER_PT_freestyle)
	except:
		pass;
	'''
	

def unregister():
	for p in get_panels():
		bpy.utils.unregister_class(p)
	s = bpy.types.Scene
	del s.cam_operations
	#cam chains are defined hardly now.
	del s.cam_chains
	
	
	del s.cam_active_operation
	del s.cam_machine
	bpy.app.handlers.scene_update_pre.remove(timer_update)
	bpy.types.INFO_HT_header.remove(header_info)

if __name__ == "__main__":
	register()
	
