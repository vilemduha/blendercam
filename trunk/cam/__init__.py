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

import bpy
import mathutils
import math
from mathutils import *
from bpy_extras.object_utils import object_data_add
from bpy.props import *
import bl_operators
from bpy.types import Menu, Operator, UIList
from . import utils#, post_processors
import numpy
import Polygon

#from .utils import *

bl_info = {
	"name": "CAM - gcode generation tools",
	"author": "Vilem Novak",
	"version": (0, 3, 0),
	"blender": (2, 6, 7),
	"location": "Properties > render",
	"description": "Generate machining paths for CNC",
	"warning": "there is no warranty for the produced gcode by now",
	"wiki_url": "blendercam.blogspot.com",
	"tracker_url": "",
	"category": "Scene"}
  
  
PRECISION=5
	
  
class machineSettings(bpy.types.PropertyGroup):
	#name = bpy.props.StringProperty(name="Machine Name", default="Machine")
	post_processor = EnumProperty(name='Post processor',
		items=(('ISO','Iso','this should export a standardized gcode'),('MACH3','Mach3','default mach3'),('EMC','EMC - LinuxCNC','default emc'),('HEIDENHAIN','Heidenhain  - experimental','heidenhain'),('TNC151','Heidenhain TNC151  - experimental','Post Processor for the Heidenhain TNC151 machine'),('SIEGKX1','Sieg KX1 - experimental','Sieg KX1'),('HM50','Hafco HM-50 - experimental','Hafco HM-50'),('CENTROID','Centroid M40 - experimental','Centroid M40'),('ANILAM','Anilam Crusader M - experimental','Anilam Crusader M')),
		description='Post processor',
		default='MACH3')
	#units = EnumProperty(name='Units', items = (('IMPERIAL', ''))
	working_area=bpy.props.FloatVectorProperty(name = 'Work Area', default=(0.500,0.500,0.100), unit='LENGTH', precision=PRECISION,subtype="XYZ")
	feedrate_min=bpy.props.FloatProperty(name="Feedrate minimum /min", default=0.0, min=0.00001, max=320000,precision=PRECISION, unit='LENGTH')
	feedrate_max=bpy.props.FloatProperty(name="Feedrate maximum /min", default=2, min=0.00001, max=320000,precision=PRECISION, unit='LENGTH')
	feedrate_default=bpy.props.FloatProperty(name="Feedrate default /min", default=1.5, min=0.00001, max=320000,precision=PRECISION)
	#UNSUPPORTED:
	spindle_min=bpy.props.FloatProperty(name="#Spindlespeed minimum /min", default=5000, min=0.00001, max=320000,precision=1)
	spindle_max=bpy.props.FloatProperty(name="#Spindlespeed maximum /min", default=30000, min=0.00001, max=320000,precision=1)
	spindle_default=bpy.props.FloatProperty(name="#Spindlespeed default /min", default=20000, min=0.00001, max=320000,precision=1)
	axis4 = bpy.props.BoolProperty(name="#4th axis",description="Machine has 4th axis", default=0)
	axis5 = bpy.props.BoolProperty(name="#5th axis",description="Machine has 5th axis", default=0)
	collet_size=bpy.props.FloatProperty(name="#Collet size", description="Collet size for collision detection",default=33, min=0.00001, max=320000,precision=PRECISION , unit="LENGTH")
	#exporter_start = bpy.props.StringProperty(name="exporter start", default="%")

'''
def updateScale():
	#TODO: move this to own update function.
	if ob.scale.x!=ob.scale.y or ob.scale.y!=ob.scale.z:
		if ob.scale.x!=ob.scale.y and ob.scale.y==ob.scale.z:
			ob.scale.y=ob.scale.x
			ob.scale.z=ob.scale.z
		elif ob.scale.y!=ob.scale.x and ob.scale.y!=ob.scale.z:
			ob.scale.x=ob.scale.y
			ob.scale.z=ob.scale.y
		elif ob.scale.z!=ob.scale.y and ob.scale.z!=ob.scale.x:
			ob.scale.s=ob.scale.z
			ob.scale.y=ob.scale.z
'''
	 
def updateChipload(self,context):
	o=self;
	self.chipload = int((o.feedrate/(o.spindle_rpm*o.cutter_flutes))*1000000)/1000

def operationValid(self,context):
	o=self
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
	#print('validity ')
	#print(o.valid)
	

class camOperation(bpy.types.PropertyGroup):
	
	name = bpy.props.StringProperty(name="Operation Name", default="Operation")
	filename = bpy.props.StringProperty(name="File name", default="Operation")
	
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
			('END', 'End', 'a'),
			('BALL', 'Ball', 'a'),
			('VCARVE', 'V-carve', 'a')),
		description='Type of cutter used',
		default='END')
	strategy = EnumProperty(name='Strategy',
		items=(
			('PARALLEL','Parallel', 'Parallel lines on any angle'),
			('CROSS','Cross', 'Cross paths'),
			('BLOCK','Block', 'Block path'),
			('SPIRAL','Spiral', 'Spiral path'),
			('CIRCLES','Circles - EXPERIMENTAL', 'Circles path'),
			('WATERLINE','Waterline - EXPERIMENTAL', 'Waterline paths - constant z'),
			('OUTLINEFILL','Outline Fill - EXPERIMENTAL', 'Detect outline and fill it with paths as pocket. Then sample these paths on the 3d surface'),
			('CUTOUT','Cutout', 'Cut the silhouette with offset'),
			('POCKET','Pocket - EXPERIMENTAL', 'Pocket operation'),
			('CARVE','Carve', 'Pocket operation'),
			('PENCIL','Pencil - EXPERIMENTAL', 'Pencil operation - detects negative corners in the model and mills only those.'),
			('DRILL','Drill', 'Drill operation')),
		description='Strategy',
		default='PARALLEL')#,('SLICES','Slices','this prepares model for cutting from sheets of material')
	#for cutout	   
	cut_type = EnumProperty(name='Cut:',items=(('OUTSIDE', 'Outside', 'a'),('INSIDE', 'Inside', 'a'),('ONLINE', 'On line', 'a')),description='Type of cutter used',default='OUTSIDE')  
	#render_all = bpy.props.BoolProperty(name="Use all geometry",description="use also other objects in the scene", default=True)#replaced with groups support
	inverse = bpy.props.BoolProperty(name="Inverse milling",description="Male to female model conversion", default=False)
	
	cutter_id = IntProperty(name="Tool number", description="For machines which support tool change based on tool id", min=0, max=10000, default=0)
	cutter_diameter = FloatProperty(name="Cutter diameter", description="Cutter diameter = 2x cutter radius", min=0.000001, max=0.1, default=0.003, precision=PRECISION, unit="LENGTH")
	cutter_length = FloatProperty(name="#Cutter length", description="#not supported#Cutter length", min=0.0, max=100.0, default=25.0,precision=PRECISION, unit="LENGTH")
	cutter_flutes = IntProperty(name="Cutter flutes", description="Cutter flutes", min=1, max=20, default=2, update = updateChipload)
	cutter_tip_angle = FloatProperty(name="Cutter v-carve angle", description="Cutter v-carve angle", min=0.0, max=180.0, default=60.0,precision=PRECISION)
	
	dist_between_paths = bpy.props.FloatProperty(name="Distance between toolpaths", default=0.001, min=0.00001, max=32,precision=PRECISION, unit="LENGTH")
	dist_along_paths = bpy.props.FloatProperty(name="Distance along toolpaths", default=0.0002, min=0.00001, max=32,precision=PRECISION, unit="LENGTH")
	parallel_angle = bpy.props.FloatProperty(name="Angle of paths", default=0, min=-360, max=360 , precision=0, subtype="ANGLE" , unit="ROTATION" )
	carve_depth = bpy.props.FloatProperty(name="Carve depth", default=0.001, min=-.100, max=32,precision=PRECISION, unit="LENGTH")
	drill_type = EnumProperty(name='Holes on',items=(('MIDDLE_SYMETRIC', 'Middle of symetric curves', 'a'),('MIDDLE_ALL', 'Middle of all curve parts', 'a'),('ALL_POINTS', 'All points in curve', 'a')),description='Strategy to detect holes to drill',default='MIDDLE_SYMETRIC')	
	
	slice_detail = bpy.props.FloatProperty(name="Distance betwen slices", default=0.001, min=0.00001, max=32,precision=PRECISION, unit="LENGTH")
	waterline_fill = bpy.props.BoolProperty(name="Fill areas between slices",description="Fill areas between slices in waterline mode", default=True)
	
	
	circle_detail = bpy.props.IntProperty(name="Detail of circles used for curve offsets", default=64, min=12, max=512)
	use_layers = bpy.props.BoolProperty(name="Use Layers",description="Use layers for roughing", default=True)
	stepdown = bpy.props.FloatProperty(name="Step down", default=0.01, min=0.00001, max=32,precision=PRECISION, unit="LENGTH")
	first_down = bpy.props.BoolProperty(name="First down",description="First go down on a contour, then go to the next one", default=False)
	helix_down = bpy.props.BoolProperty(name="Ramp contour",description="Ramps down the whole contour, so the cutline looks like helix", default=False)
	ramp_out = bpy.props.BoolProperty(name="Ramp out",description="Ramp out to not leave mark on surface", default=False)
	ramp_out_angle = bpy.props.FloatProperty(name="Ramp out angle", default=math.pi/6, min=0, max=89 , precision=0, subtype="ANGLE" , unit="ROTATION" )

	minz_from_ob = bpy.props.BoolProperty(name="Depth from object",description="Operation depth from object", default=True)
	minz = bpy.props.FloatProperty(name="Operation depth", default=-0.01, min=-32, max=0,precision=PRECISION, unit="LENGTH")#this is input minz. True minimum z can be something else, depending on material e.t.c.
	
	source_image_scale_z=bpy.props.FloatProperty(name="Image source depth scale", default=0.01, min=-1, max=1,precision=PRECISION, unit="LENGTH")
	source_image_size_x=bpy.props.FloatProperty(name="Image source x size", default=0.1, min=-10, max=10,precision=PRECISION, unit="LENGTH")
	source_image_offset=bpy.props.FloatVectorProperty(name = 'Image offset', default=(0,0,0), unit='LENGTH', precision=PRECISION,subtype="XYZ")
	source_image_crop=bpy.props.BoolProperty(name="Crop source image",description="Crop source image - the position of the sub-rectangle is relative to the whole image, so it can be used for e.g. finishing just a part of an image", default=True)
	source_image_crop_start_x= bpy.props.FloatProperty(name = 'crop start x', default=0,min=0, max=100, precision=PRECISION,subtype='PERCENTAGE')
	source_image_crop_start_y= bpy.props.FloatProperty(name = 'crop start y', default=0,min=0, max=100, precision=PRECISION,subtype='PERCENTAGE')
	source_image_crop_end_x=   bpy.props.FloatProperty(name = 'crop end x', default=100,min=0, max=100, precision=PRECISION,subtype='PERCENTAGE')
	source_image_crop_end_y=   bpy.props.FloatProperty(name = 'crop end y', default=100,min=0, max=100, precision=PRECISION,subtype='PERCENTAGE')
	
	protect_vertical = bpy.props.BoolProperty(name="Protect vertical",description="The path goes only vertically next to steep areas", default=True)
	
		
	ambient_behaviour = EnumProperty(name='Ambient',items=(('ALL', 'All', 'a'),('AROUND', 'Around', 'a')   ),description='handling ambient surfaces',default='ALL')
	

	ambient_radius = FloatProperty(name="Ambient radius", description="Radius around the part which will be milled if ambient is set to Around", min=0.0, max=100.0, default=0.01, precision=PRECISION, unit="LENGTH")
	use_limit_curve=bpy.props.BoolProperty(name="Use limit curve",description="A curve limits the operation area", default=False)
	limit_curve=   bpy.props.StringProperty(name='Limit curve', description='curve used to limit the area of the operation')
	skin = FloatProperty(name="Skin", description="Material to leave when roughing ", min=0.0, max=1.0, default=0.0,precision=PRECISION, unit="LENGTH")
	#feeds
	feedrate = FloatProperty(name="Feedrate/minute", description="Feedrate m/min", min=0.00005, max=50.0, default=1.0,precision=PRECISION, unit="LENGTH", update = updateChipload)
	plunge_feedrate = FloatProperty(name="Plunge speed ", description="% of feedrate", min=0.1, max=100.0, default=50.0,precision=1, subtype='PERCENTAGE')
	spindle_rpm = FloatProperty(name="#Spindle rpm", description="#not supported#Spindle speed ", min=1000, max=60000, default=12000, update = updateChipload)
	#movement parallel_step_back 
	movement_type = EnumProperty(name='Movement type',items=(('CONVENTIONAL','Conventional', 'a'),('CLIMB', 'Climb', 'a'),('MEANDER', 'Meander' , 'a')	 ),description='movement type', default='CLIMB')
	spindle_rotation_direction = EnumProperty(name='Spindle rotation', items=(('CW','Clock wise', 'a'),('CCW', 'Counter clock wise', 'a')),description='Spindle rotation direction',default='CW')
	free_movement_height = bpy.props.FloatProperty(name="Free movement height", default=0.01, min=0.0000, max=32,precision=PRECISION, unit="LENGTH")
	movement_insideout = EnumProperty(name='Direction', items=(('INSIDEOUT','Inside out', 'a'),('OUTSIDEIN', 'Outside in', 'a')),description='approach to the piece',default='INSIDEOUT')
	parallel_step_back =  bpy.props.BoolProperty(name="Parallel step back", description='For roughing and finishing in one pass: mills material in climb mode, then steps back and goes between 2 last chunks back', default=False)
	stay_low = bpy.props.BoolProperty(name="Stay low if possible", default=False)
	#optimization and performance
	use_exact = bpy.props.BoolProperty(name="Use exact mode",description="Exact mode allows greater precision, but is slower with complex meshes", default=True)
	pixsize=bpy.props.FloatProperty(name="sampling raster detail", default=0.0001, min=0.00001, max=0.01,precision=PRECISION, unit="LENGTH")
	simulation_detail=bpy.props.FloatProperty(name="Simulation sampling raster detail", default=0.0001, min=0.00001, max=0.01,precision=PRECISION, unit="LENGTH")
	optimize = bpy.props.BoolProperty(name="Reduce path points",description="Reduce path points", default=True)
	optimize_threshold=bpy.props.FloatProperty(name="Reduction threshold", default=0.000005, min=0.00000001, max=1,precision=PRECISION, unit="LENGTH")
	dont_merge = bpy.props.BoolProperty(name="Dont merge outlines when cutting",description="this is usefull when you want to cut around everything", default=False)
	
	pencil_threshold=bpy.props.FloatProperty(name="Pencil threshold", default=0.00002, min=0.00000001, max=1,precision=PRECISION, unit="LENGTH")
	#calculations
	duration = bpy.props.FloatProperty(name="Estimated time", default=0.01, min=0.0000, max=32,precision=PRECISION, unit="TIME")
	#chip_rate
	
	#optimisation panel
	#testing = bpy.props.IntProperty(name="developer testing ", description="This is just for script authors for help in coding, keep 0", default=0, min=0, max=512)
	offset_image=numpy.array([],dtype=float)
	zbuffer_image=numpy.array([],dtype=float)

	#internal properties
	###########################################
	silhouete=Polygon.Polygon()
	ambient = Polygon.Polygon()
	operation_limit=Polygon.Polygon()
	borderwidth=50
	object=None
	path_object_name=bpy.props.StringProperty(name='Path object', description='actual cnc path')
	
	
	update_zbufferimage_tag=bpy.props.BoolProperty(name="mark zbuffer image for update",description="mark for update", default=True)
	#update_zbufferimage_tag=True
	update_offsetimage_tag=bpy.props.BoolProperty(name="mark offset image for update",description="mark for update", default=True)
	#update_offsetimage_tag=True
	update_silhouete_tag=bpy.props.BoolProperty(name="mark silhouette image for update",description="mark for update", default=True)
	update_ambient_tag=bpy.props.BoolProperty(name="mark ambient polygon for update",description="mark for update", default=True)
	update_bullet_collision_tag=bpy.props.BoolProperty(name="mark bullet collisionworld for update",description="mark for update", default=True)
	#update_silhouete_tag=True

	#material settings
	material_from_model = bpy.props.BoolProperty(name="Estimate from model",description="Estimate material size from model", default=True)
	material_radius_around_model = bpy.props.FloatProperty(name="radius around model",description="How much to add to model size on all sides", default=0.0, unit='LENGTH', precision=PRECISION)
	material_origin=bpy.props.FloatVectorProperty(name = 'Material origin', default=(0,0,0), unit='LENGTH', precision=PRECISION,subtype="XYZ")
	material_size=bpy.props.FloatVectorProperty(name = 'Material size', default=(0.200,0.200,0.100), unit='LENGTH', precision=PRECISION,subtype="XYZ")
	min=bpy.props.FloatVectorProperty(name = 'Operation minimum', default=(0,0,0), unit='LENGTH', precision=PRECISION,subtype="XYZ")
	max=bpy.props.FloatVectorProperty(name = 'Operation maximum', default=(0,0,0), unit='LENGTH', precision=PRECISION,subtype="XYZ")
	warnings = bpy.props.StringProperty(name='warnings', description='warnings', default='')
	chipload = bpy.props.FloatProperty(name="chipload",description="Calculated chipload", default=0.0, unit='LENGTH', precision=PRECISION)

	valid = bpy.props.BoolProperty(name="Valid",description="True if operation is ok for calculation", default=True);

#class camOperationChain(bpy.types.PropertyGroup):
   # c=bpy.props.collectionProperty()
'''
class ModalTimerOperator(bpy.types.Operator):
	"""Operator which runs its self from a timer"""
	bl_idname = "wm.modal_timer_operator"
	bl_label = "Modal Timer Operator"

	_timer = None

	def modal(self, context, event):
		if event.type == 'ESC':
			return self.cancel(context)

		if event.type == 'TIMER':
			# change theme color, silly!
			color = context.user_preferences.themes[0].view_3d.space.gradients.high_gradient
			color.s = 1.0
			color.h += 0.01

		return {'PASS_THROUGH'}

	def execute(self, context):
		self._timer = context.window_manager.event_timer_add(0.1, context.window)
		context.window_manager.modal_handler_add(self)
		return {'RUNNING_MODAL'}

	def cancel(self, context):
		context.window_manager.event_timer_remove(self._timer)
		return {'CANCELLED'}
'''
"""
class PathsModal(bpy.types.Operator):
	'''calculate CAM paths'''
	bl_idname = "object.calculate_cam_paths_modal"
	bl_label = "Calculate CAM paths modal"
	bl_options = {'REGISTER', 'UNDO'}

	#this property was actually ignored, so removing it in 0.3
	#operation= StringProperty(name="Operation",
	#					   description="Specify the operation to calculate",default='Operation')
						   
	
		
	def execute(self, context):
		#getIslands(context.object)
		s=bpy.context.scene
		operation = s.cam_operations[s.cam_active_operation]
		if not operation.valid:
				self.report({'ERROR_INVALID_INPUT'}, "Operation can't be performed, see warnings for info")
				#print("Operation can't be performed, see warnings for info")
				return {'FINISHED'}
		
			
		#these tags are for some optimisations, unfinished 
		operation.update_offsetimage_tag=True
		operation.update_zbufferimage_tag=True
		operation.update_silhouete_tag=True
		operation.update_ambient_tag=True
		operation.update_bullet_collision_tag=True
		#operation.material=bpy.context.scene.cam_material[0]
		operation.operator=self
		#'''#removed for groups support, this has to be done object by object...
		if operation.geometry_source=='OBJECT':
			
			#bpy.ops.object.select_all(action='DESELECT')
			ob=bpy.data.objects[operation.object_name]
			operation.objects=[ob]
		elif operation.geometry_source=='GROUP':
			group=bpy.data.groups[operation.group_name]
			operation.objects=group.objects
		elif operation.geometry_source=='IMAGE':
			operation.use_exact=False;
		if operation.geometry_source=='OBJECT' or operation.geometry_source=='GROUP':
			operation.onlycurves=True
			for ob in operation.objects:
				if ob.type=='MESH':
					operation.onlycurves=False;
		operation.warnings=''
		
		self.operation=operation
		self.operation.test=0
		self._timer = context.window_manager.event_timer_add(0.1, context.window)
		context.window_manager.modal_handler_add(self)
		return {'RUNNING_MODAL'}
		#utils.getPaths(context,operation)
		
	def modal(self, context, event):
		if event.type == 'ESC':
			return self.cancel(context)

		if event.type == 'TIMER':
			#print('running')
			self.operation.test+=1
			for a in range(0,10000):
				b=round(100*200/532/567.5)
			# change theme color, silly!
			
			context.area.header_text_set("doing heavy calculations here " + str( self.operation.test))

		return {'PASS_THROUGH'}

	def cancel(self, context):
		context.window_manager.event_timer_remove(self._timer)
		context.area.header_text_set()
		return {'CANCELLED'}
		#return {'FINISHED'}
"""
class PathsSimple(bpy.types.Operator):
	'''calculate CAM paths'''
	bl_idname = "object.calculate_cam_paths"
	bl_label = "Calculate CAM paths"
	bl_options = {'REGISTER', 'UNDO'}

	#this property was actually ignored, so removing it in 0.3
	#operation= StringProperty(name="Operation",
	#					   description="Specify the operation to calculate",default='Operation')
						   
	
		
	def execute(self, context):
		#getIslands(context.object)
		s=bpy.context.scene
		operation = s.cam_operations[s.cam_active_operation]
		if not operation.valid:
				self.report({'ERROR_INVALID_INPUT'}, "Operation can't be performed, see warnings for info")
				#print("Operation can't be performed, see warnings for info")
				return {'FINISHED'}
		
			
		#these tags are for some optimisations, unfinished 
		operation.update_offsetimage_tag=True
		operation.update_zbufferimage_tag=True
		operation.update_silhouete_tag=True
		operation.update_ambient_tag=True
		operation.update_bullet_collision_tag=True
		#operation.material=bpy.context.scene.cam_material[0]
		operation.operator=self
		#'''#removed for groups support, this has to be done object by object...
		if operation.geometry_source=='OBJECT':
			
			#bpy.ops.object.select_all(action='DESELECT')
			ob=bpy.data.objects[operation.object_name]
			operation.objects=[ob]
		elif operation.geometry_source=='GROUP':
			group=bpy.data.groups[operation.group_name]
			operation.objects=group.objects
		elif operation.geometry_source=='IMAGE':
			operation.use_exact=False;
		if operation.geometry_source=='OBJECT' or operation.geometry_source=='GROUP':
			operation.onlycurves=True
			for ob in operation.objects:
				if ob.type=='MESH':
					operation.onlycurves=False;
		operation.warnings=''
		utils.getPaths(context,operation)

		return {'FINISHED'}
	
	#def draw(self, context):
		#layout = self.layout
		#layout.prop_search(self, "operation", bpy.context.scene, "cam_operations")
		
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
			bpy.ops.object.calculate_cam_paths()
			i+=1

		return {'FINISHED'}
	
	def draw(self, context):
		layout = self.layout
		layout.prop_search(self, "operation", bpy.context.scene, "cam_operations")	 
			 
class CAMSimulate(bpy.types.Operator):
	'''simulate CAM operation'''
	bl_idname = "object.cam_simulate"
	bl_label = "CAM simulation"
	bl_options = {'REGISTER', 'UNDO'}

	operation = StringProperty(name="Operation",
						   description="Specify the operation to calculate",default='Operation')

	def execute(self, context):
		s=bpy.context.scene
		operation = s.cam_operations[s.cam_active_operation]
		#operation.material=bpy.context.scene.cam_material[0]#TODO: check if this works after the change.
		#if operation.geometry_source=='OBJECT' and operation.object_name in bpy.data.objects and #bpy.data.objects[operation.object_name].type=='CURVE':
		#	print('simulation of curve operations is not available')
		#	return {'FINISHED'}
		if operation.path_object_name in bpy.data.objects:
			utils.doSimulation(operation)
		else:
		   print('no computed path to simulate')
		   return {'FINISHED'}
		return {'FINISHED'}
	
	def draw(self, context):
		layout = self.layout
		layout.prop_search(self, "operation", bpy.context.scene, "cam_operations")

class CAMPositionObject(bpy.types.Operator):
	'''position object for CAM operation'''
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
		if len(s.cam_machine)==0:
			s.cam_machine.add()
		if s.objects.get('CAM_machine')==None:
			utils.addMachineObject()
		#if len(s.cam_material)==0:
		#	 s.cam_material.add()
		  
		s=bpy.context.scene
		s.cam_operations.add()
		o=s.cam_operations[-1]
		copyop=s.cam_operations[s.cam_active_operation]
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
		if len(s.cam_machine)==0:
			s.cam_machine.add()
		#if len(s.cam_material)==0:
		#	 s.cam_material.add()
		  
		s=bpy.context.scene
		s.cam_operations.add()
		copyop=s.cam_operations[s.cam_active_operation]
		s.cam_active_operation+=1
		l=len(s.cam_operations)-1
		s.cam_operations.move(l,s.cam_active_operation)
		o=s.cam_operations[s.cam_active_operation]

		for k in copyop.keys():
			o[k]=copyop[k]
		
		o.name=o.name+'_copy'
		o.filename=o.filename+'_copy'
		ob=bpy.context.active_object
		if ob!=None:
			o.object_name=ob.name
			o.minz=ob.location.z+ob.bound_box[0][2]
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
		"d = bpy.context.scene.cam_machine[0]",
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
			   
	
class CAM_CUTTER_Panel(bpy.types.Panel):   
	"""CAM cutter panel"""
	bl_label = " "
	bl_idname = "WORLD_PT_CAM_CUTTER"
	
	bl_space_type = "PROPERTIES"
	bl_region_type = "WINDOW"
	bl_context = "render"
	
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
   
class CAM_MACHINE_Panel(bpy.types.Panel):	
	"""CAM machine panel"""
	bl_label = " "
	bl_idname = "WORLD_PT_CAM_MACHINE"
	
	bl_space_type = "PROPERTIES"
	bl_region_type = "WINDOW"
	bl_context = "render"
	
	def draw_header(self, context):
	   self.layout.menu("CAM_MACHINE_presets", text="CAM Machine")
		
	def draw(self, context):
		layout = self.layout
		s=bpy.context.scene
		us=s.unit_settings
		if len(s.cam_machine)>0:
			ao=s.cam_machine[0]
		
			if ao:
				#cutter preset
				row = layout.row(align=True)
				row.menu("CAM_MACHINE_presets", text=bpy.types.CAM_MACHINE_presets.bl_label)
				row.operator("render.cam_preset_machine_add", text="", icon='ZOOMIN')
				row.operator("render.cam_preset_machine_add", text="", icon='ZOOMOUT').remove_active = True
				#layout.prop(ao,'name')
				layout.prop(ao,'post_processor')
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

def test():
	print('running')			   
	
class CAM_MATERIAL_Panel(bpy.types.Panel):	 
	"""CAM material panel"""
	bl_label = "CAM Material size and position"
	bl_idname = "WORLD_PT_CAM_MATERIAL"
	
	bl_space_type = "PROPERTIES"
	bl_region_type = "WINDOW"
	bl_context = "render"
	
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
		#if self.layout_type in {'DEFAULT', 'COMPACT'}:
		layout.label(text=operation.name, translate=False, icon_value=icon)
			#icon = 'LOCKED' if vgroup.lock_weight else 'UNLOCKED'
			#layout.prop(vgroup, "lock_weight", text="", icon=icon, emboss=False)
		#elif self.layout_type in {'GRID'}:
		#	 layout.alignment = 'CENTER'
		#	 layout.label(text="", icon_value=icon)
  
	
class CAM_OPERATIONS_Panel(bpy.types.Panel):
	"""CAM operations panel"""
	bl_label = "CAM operations"
	bl_idname = "WORLD_PT_CAM"
	
	bl_space_type = "PROPERTIES"
	bl_region_type = "WINDOW"
	bl_context = "render"
	
	

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
				#if ao.warnings!='':
			   #	 layout.label(ao.warnings)	 
				layout.operator("object.calculate_cam_paths", text="Calculate path")
				
				layout.operator("object.cam_simulate", text="Simulate this operation")
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
									 
class CAM_INFO_Panel(bpy.types.Panel):
	"""CAM info panel"""
	bl_label = "CAM info & warnings"
	bl_idname = "WORLD_PT_CAM_INFO"	  
	bl_space_type = "PROPERTIES"
	bl_region_type = "WINDOW"
	bl_context = "render"

	def draw(self, context):
		layout = self.layout
		scene=bpy.context.scene
		row = layout.row() 
		if len(scene.cam_operations)==0:
			layout.label('Add operation first')
		if len(scene.cam_operations)>0:
			ao=scene.cam_operations[scene.cam_active_operation]
			if ao.warnings!='':
				layout.label(ao.warnings)
			if ao.valid:
				#ob=bpy.data.objects[ao.object_name]
				#layout.separator()
				if ao.duration>0:
					layout.label('operation time: '+str(int(ao.duration*100)/100.0)+' min')	   
				#layout.prop(ao,'chipload')
				layout.label(  'chipload: '+str(round(ao.chipload,6))+getUnit()+' / tooth')
				#layout.label(str(ob.dimensions.x))
				#row=layout.row()
			   
				
				
				
		
class CAM_OPERATION_PROPERTIES_Panel(bpy.types.Panel):
	"""CAM operation properties panel"""
	bl_label = "CAM operation setup"
	bl_idname = "WORLD_PT_CAM_OPERATION"
	
	bl_space_type = "PROPERTIES"
	bl_region_type = "WINDOW"
	bl_context = "render"
	
	

	def draw(self, context):
		layout = self.layout
		scene=bpy.context.scene
		
			
		row = layout.row() 
		if len(scene.cam_operations)==0:
			layout.label('Add operation first')
		if len(scene.cam_operations)>0:
			ao=scene.cam_operations[scene.cam_active_operation]
			if ao.valid:
				layout.prop(ao,'strategy')
				
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
					
				elif ao.strategy=='WATERLINE':
					layout.prop(ao,'slice_detail')	
					layout.prop(ao,'waterline_fill')  
					if ao.waterline_fill:
						layout.prop(ao,'dist_between_paths')			
					
					layout.prop(ao,'skin')
					layout.prop(ao,'inverse')
				elif ao.strategy=='CARVE':
					layout.prop(ao,'carve_depth')
					layout.prop(ao,'dist_along_paths')
				elif ao.strategy=='PENCIL':
					layout.prop(ao,'dist_along_paths')
					layout.prop(ao,'pencil_threshold')
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
					
				#layout.prop(ao,'testing')
				
class CAM_MOVEMENT_Panel(bpy.types.Panel):
	"""CAM movement panel"""
	bl_label = "CAM movement"
	bl_idname = "WORLD_PT_CAM_MOVEMENT"	  
	bl_space_type = "PROPERTIES"
	bl_region_type = "WINDOW"
	bl_context = "render"

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
						layout.prop(ao,'helix_down')
						if ao.helix_down:
							layout.prop(ao,'ramp_out')
							if ao.ramp_out:
								layout.prop(ao,'ramp_out_angle')
							
				layout.prop(ao,'stay_low')
				layout.prop(ao,'protect_vertical')
			  
				
class CAM_FEEDRATE_Panel(bpy.types.Panel):
	"""CAM feedrate panel"""
	bl_label = "CAM feedrate"
	bl_idname = "WORLD_PT_CAM_FEEDRATE"	  
	bl_space_type = "PROPERTIES"
	bl_region_type = "WINDOW"
	bl_context = "render"

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
				layout.prop(ao,'spindle_rpm')

class CAM_OPTIMISATION_Panel(bpy.types.Panel):
	"""CAM optimisation panel"""
	bl_label = "CAM optimisation"
	bl_idname = "WORLD_PT_CAM_OPTIMISATION"
	
	bl_space_type = "PROPERTIES"
	bl_region_type = "WINDOW"
	bl_context = "render"
	
	

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
				
				layout.prop(ao,'simulation_detail')
				layout.prop(ao,'circle_detail')
				#if not ao.use_exact:#this will be replaced with groups of objects.
				#layout.prop(ao,'render_all')# replaced with groups support
				

		
class CAM_AREA_Panel(bpy.types.Panel):
	"""CAM operation area panel"""
	bl_label = "CAM operation area "
	bl_idname = "WORLD_PT_CAM_OPERATION_AREA"
	
	bl_space_type = "PROPERTIES"
	bl_region_type = "WINDOW"
	bl_context = "render"
	
	

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
				#layout.prop(ao,'use_limit_curve')				   
				#if ao.use_limit_curve:
				#	layout.prop_search(ao, "limit_curve", bpy.data, "objects")
				
				
 
def get_panels():
	types = bpy.types
	return (
	CAM_UL_operations,
	camOperation,
	machineSettings,
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
	
	PathsSimple,
	#PathsModal,
	PathsAll,
	CAMPositionObject,
	CAMSimulate,
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
	)
	
def register():
	for p in get_panels():
		bpy.utils.register_class(p)
		
	d = bpy.types.Scene
	d.cam_operations = bpy.props.CollectionProperty(type=camOperation)
	d.cam_active_operation = bpy.props.IntProperty(name="CAM Active Operation", description="The selected operation")
	d.cam_machine = bpy.props.CollectionProperty(type=machineSettings)
	
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
	d = bpy.types.Scene
	del d.cam_operations
	del d.cam_active_operation
	del d.cam_machine
	#del d.cam_material

if __name__ == "__main__":
	register()
	
