# blender CAM ops.py (c) 2012 Vilem Novak
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ***** END GPL LICENCE BLOCK *****

#blender operators definitions are in this file. They mostly call the functions from utils.py

import bpy
import subprocess,os, sys, threading
from cam import utils, pack,polygon_utils_cam,chunk,simple
from bpy.props import *
import shapely

from shapely import geometry as sgeometry
import mathutils
from mathutils import *
import math


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
			o=s.cam_operations[tcom.opname]#changes
			o.outtext=tcom.lasttext#changes
			#text=text+('# %s %s #' % (tcom.opname,tcom.lasttext))#CHANGES
	#s.cam_text=text#changes
	
	# commented out by NFZ: asking every property area to redraw
	# causes my netbook to come to a crawl and cpu overheats
	# need to find a better way of doing this
	# doesn't effect normal path calculation when commented out
	# maybe this should only be enabled when when background calc selected
	#if bpy.context.screen!=None:
	#	for area in bpy.context.screen.areas:
	#		if area.type == 'PROPERTIES':
	#			area.tag_redraw()
			
class PathsBackground(bpy.types.Operator):
	'''calculate CAM paths in background. File has to be saved before.'''
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
		
		for p in bpy.utils.script_paths():
			scriptpath=p+os.sep+'addons'+os.sep+'cam'+os.sep+'backgroundop.py_'
			print(scriptpath)
			if os.path.isfile(scriptpath):
				break;
		proc= subprocess.Popen([bpath, '-b', fpath,'-P',scriptpath,'--', '-o='+str(s.cam_active_operation) ],bufsize=1, stdout=subprocess.PIPE,stdin=subprocess.PIPE)
		
		tcom=threadCom(o,proc)
		readthread=threading.Thread(target=threadread, args = ([tcom]), daemon=True)
		readthread.start()
		#self.__class__.cam_processes=[]
		if not hasattr(bpy.ops.object.calculate_cam_paths_background.__class__,'cam_processes'):
			bpy.ops.object.calculate_cam_paths_background.__class__.cam_processes=[]
		bpy.ops.object.calculate_cam_paths_background.__class__.cam_processes.append([readthread,tcom])
		return {'FINISHED'}
		
class KillPathsBackground(bpy.types.Operator):
	'''Remove CAM path processes in background.'''
	bl_idname = "object.kill_calculate_cam_paths_background"
	bl_label = "Kill background computation of an operation"
	bl_options = {'REGISTER', 'UNDO'}
	
	#processes=[]
	
	#@classmethod
	#def poll(cls, context):
	#	return context.active_object is not None
	
	def execute(self, context):
		s=bpy.context.scene
		o=s.cam_operations[s.cam_active_operation]
		self.operation=o
		
		
		if hasattr(bpy.ops.object.calculate_cam_paths_background.__class__,'cam_processes'):
			processes=bpy.ops.object.calculate_cam_paths_background.__class__.cam_processes
			for p in processes:
				#proc=p[1].proc
				#readthread=p[0]
				tcom=p[1]
				if tcom.opname==o.name:
					processes.remove(p)
					tcom.proc.kill()
					o.computing=False
				
		return {'FINISHED'}
				

		
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
		
		o.operator=self
		
		if o.use_layers:
			o.parallel_step_back = False
			
		utils.getPath(context,o)
		
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

class CamSliceObjects(bpy.types.Operator):
	'''Slice a mesh object horizontally'''
	#warning, this is a separate and neglected feature, it's a mess - by now it just slices up the object.
	bl_idname = "object.cam_slice_objects"
	bl_label = "Slice object - usefull for lasercut puzzles e.t.c."
	bl_options = {'REGISTER', 'UNDO'}
		
	def execute(self, context):
		from cam import slice
		ob=bpy.context.active_object
		slice.sliceObject(ob)
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
	
		
class PathExport(bpy.types.Operator):
	'''Export gcode. Can be used only when the path object is present'''
	bl_idname = "object.cam_export"
	bl_label = "Export operation gcode"
	bl_options = {'REGISTER', 'UNDO'}
		
	def execute(self, context):
		import bpy
		s=bpy.context.scene
		operation = s.cam_operations[s.cam_active_operation]
		utils.exportGcodePath( operation.filename , [bpy.data.objects[operation.path_object_name].data] , [operation])
		return {'FINISHED'}
	

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


class CamChainAdd(bpy.types.Operator):
	'''Add new CAM chain'''
	bl_idname = "scene.cam_chain_add"
	bl_label = "Add new CAM chain"
	bl_options = {'REGISTER', 'UNDO'}
	
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
	bl_options = {'REGISTER', 'UNDO'}
	
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
	bl_options = {'REGISTER', 'UNDO'}
	
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

class CamChainOperationUp(bpy.types.Operator):
	'''Add operation to chain'''
	bl_idname = "scene.cam_chain_operation_up"
	bl_label = "Add operation to chain"
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		return context.scene is not None

	def execute(self, context):
		s=bpy.context.scene
		chain=s.cam_chains[s.cam_active_chain]
		a=chain.active_operation
		if a>0:
			chain.operations.move(a,a-1)
			chain.active_operation-=1
		return {'FINISHED'}

class CamChainOperationDown(bpy.types.Operator):
	'''Add operation to chain'''
	bl_idname = "scene.cam_chain_operation_down"
	bl_label = "Add operation to chain"
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		return context.scene is not None

	def execute(self, context):
		s=bpy.context.scene
		chain=s.cam_chains[s.cam_active_chain]
		a=chain.active_operation
		if a<len(chain.operations)-1:
			chain.operations.move(a,a+1)
			chain.active_operation+=1
		return {'FINISHED'}		
		
class CamChainOperationRemove(bpy.types.Operator):
	'''Remove operation from chain'''
	bl_idname = "scene.cam_chain_operation_remove"
	bl_label = "Remove operation from chain"
	bl_options = {'REGISTER', 'UNDO'}
	
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

def fixUnits():
	'''Sets up units for blender CAM'''
	s=bpy.context.scene
	# dhull: leave unit settings alone - may also need to comment out scale_length below
	#if s.unit_settings.system=='NONE':#metric is hereby default
	#	s.unit_settings.system='METRIC'
		
	s.unit_settings.system_rotation='DEGREES'	
	
	s.unit_settings.scale_length=1.0 # Blender CAM doesn't respect this property and there were users reporting problems, not seeing this was changed. 
	
class CamOperationAdd(bpy.types.Operator):
	'''Add new CAM operation'''
	bl_idname = "scene.cam_operation_add"
	bl_label = "Add new CAM operation"
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		return context.scene is not None

	def execute(self, context):
		#main(context)
		s=bpy.context.scene
		
		fixUnits()
		
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
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		return context.scene is not None

	def execute(self, context):
		#main(context)
		s=bpy.context.scene
		
		fixUnits()
		
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
			
		return {'FINISHED'}
	
class CamOperationRemove(bpy.types.Operator):
	'''Remove CAM operation'''
	bl_idname = "scene.cam_operation_remove"
	bl_label = "Remove CAM operation"
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		return context.scene is not None

	def execute(self, context):
		scene = context.scene
		try:
			ao = scene.cam_operations[scene.cam_active_operation]
			ob = bpy.data.objects[ao.path_object_name]
			scene.objects.active = ob
			bpy.ops.object.delete(True)
		except:
			pass
		
		scene.cam_operations.remove(scene.cam_active_operation)
		if scene.cam_active_operation>0:
			scene.cam_active_operation-=1
		
		return {'FINISHED'}
	
#move cam operation in the list up or down
class CamOperationMove(bpy.types.Operator):
	'''Move CAM operation'''
	bl_idname = "scene.cam_operation_move"
	bl_label = "Move CAM operation in list"
	bl_options = {'REGISTER', 'UNDO'}
	
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

		

class CamOrientationAdd(bpy.types.Operator):
	'''Add orientation to cam operation, for multiaxis operations'''
	bl_idname = "scene.cam_orientation_add"
	bl_label = "Add orientation"
	bl_options = {'REGISTER', 'UNDO'}
	
		
	@classmethod
	def poll(cls, context):
		return context.scene is not None

	def execute(self, context):
		#main(context)
		s=bpy.context.scene
		a=s.cam_active_operation
		o=s.cam_operations[a]
		gname=o.name+'_orientations'
		bpy.ops.object.empty_add(type='ARROWS')
		
		oriob=bpy.context.active_object
		oriob.empty_draw_size=0.02 # 2 cm
		
		simple.addToGroup(oriob,gname)
		oriob.name='ori_'+o.name+'.'+str(len(bpy.data.groups[gname].objects)).zfill(3)
		
		return {'FINISHED'}
		

class CamBridgesAdd(bpy.types.Operator):
	'''Add bridge objects to curve'''
	bl_idname = "scene.cam_bridges_add"
	bl_label = "Add bridges"
	bl_options = {'REGISTER', 'UNDO'}
	
		
	@classmethod
	def poll(cls, context):
		return context.scene is not None

	def execute(self, context):
		#main(context)
		s=bpy.context.scene
		a=s.cam_active_operation
		o=s.cam_operations[a]
		utils.addAutoBridges(o)
		return {'FINISHED'}
		
		
#boolean operations for curve objects
class CamCurveBoolean(bpy.types.Operator):
	'''perform Boolean operation on two or more curves'''
	bl_idname = "object.curve_boolean"
	bl_label = "Curve Boolean"
	bl_options = {'REGISTER', 'UNDO'}
	
	boolean_type = EnumProperty(name='type',
		items=(('UNION','Union',''),('DIFFERENCE','Difference',''),('INTERSECT','Intersect','')),
		description='boolean type',
		default='UNION')
		
	@classmethod
	def poll(cls, context):
		return context.active_object is not None and context.active_object.type in ['CURVE','FONT']

	def execute(self, context):
		if len(context.selected_objects)>1:
			utils.polygonBoolean(context,self.boolean_type)
			return {'FINISHED'}
		else:
			self.report({'ERROR'}, 'at least 2 curves must be selected')
			return {'CANCELLED'}

#intarsion or joints
class CamCurveIntarsion(bpy.types.Operator):
	'''makes curve cuttable both inside and outside, for intarsion and joints'''
	bl_idname = "object.curve_intarsion"
	bl_label = "Intarsion"
	bl_options = {'REGISTER', 'UNDO'}
	
	diameter = bpy.props.FloatProperty(name="cutter diameter", default=.001, min=0, max=100,precision=4, unit="LENGTH")
		
	@classmethod	
	def poll(cls, context):
		return context.active_object is not None and (context.active_object.type in ['CURVE','FONT'])

	def execute(self, context):
		utils.silhoueteOffset(context,-self.diameter/2)
		o1=bpy.context.active_object

		utils.silhoueteOffset(context,self.diameter)
		o2=bpy.context.active_object
		utils.silhoueteOffset(context,-self.diameter/2)
		o3=bpy.context.active_object
		o1.select=True
		o2.select=True
		o3.select=False
		bpy.ops.object.delete(use_global=False)
		o3.select=True
		return {'FINISHED'}	

#intarsion or joints
class CamCurveOvercuts(bpy.types.Operator):
	'''Adds overcuts for slots'''
	bl_idname = "object.curve_overcuts"
	bl_label = "Add Overcuts"
	bl_options = {'REGISTER', 'UNDO'}
	
	
	diameter = bpy.props.FloatProperty(name="diameter", default=.003, min=0, max=100,precision=4, unit="LENGTH")
	threshold = bpy.props.FloatProperty(name="threshold", default=math.pi/2*.99, min=-3.14, max=3.14,precision=4, subtype="ANGLE" , unit="ROTATION")
	do_outer = bpy.props.BoolProperty(name="Outer polygons", default=True)
	invert = bpy.props.BoolProperty(name="Invert", default=False)
	@classmethod
	def poll(cls, context):
		return context.active_object is not None and (context.active_object.type in ['CURVE','FONT'])

	def execute(self, context):
		#utils.silhoueteOffset(context,-self.diameter)
		o1=bpy.context.active_object
		shapes=utils.curveToShapely(o1)
		negative_overcuts=[]
		positive_overcuts=[]
		diameter = self.diameter*1.001
		for s in shapes:
				s=shapely.geometry.polygon.orient(s,1)
				if s.boundary.type == 'LineString':
					loops = [s.boundary]#s=shapely.geometry.asMultiLineString(s)
				else:	
					loops = s.boundary
				
				for ci,c in enumerate(loops):
					if ci>0 or self.do_outer:
						#c=s.boundary
						for i,co in enumerate(c.coords):
							i1=i-1
							if i1==-1:
								i1=-2
							i2=i+1
							if i2 == len(c.coords):
								i2=0
								
							v1 = Vector(co) - Vector(c.coords[i1])
							v1 = v1.xy#Vector((v1.x,v1.y,0))
							v2 = Vector(c.coords[i2]) - Vector(co)
							v2 = v2.xy#v2 = Vector((v2.x,v2.y,0))
							if not v1.length==0 and not v2.length == 0:
								a=v1.angle_signed(v2)
								sign=1
								#if ci==0:
								#	sign=-1
								#else:
								#	sign=1
								
								if self.invert:# and ci>0:
									sign*=-1
								if (sign<0 and a<-self.threshold) or (sign>0 and a>self.threshold):
									p=Vector((co[0],co[1]))
									v1.normalize()
									v2.normalize()
									v=v1-v2
									v.normalize()
									p=p-v*diameter/2
									if abs(a)<math.pi/2:
										shape=utils.Circle(diameter/2,64)
										shape= shapely.affinity.translate(shape,p.x,p.y)
									else:
										l=math.tan(a/2)*diameter/2
										p1=p-sign*v*l
										l=shapely.geometry.LineString((p,p1))
										shape=l.buffer(diameter/2, resolution = 64)
									
									if sign>0:
										negative_overcuts.append(shape)
									else:	
										positive_overcuts.append(shape)
									
								print(a)
					
							
				#for c in s.boundary:
		negative_overcuts = shapely.ops.unary_union(negative_overcuts)
		positive_overcuts = shapely.ops.unary_union(positive_overcuts)
		#shapes.extend(overcuts)
		fs=shapely.ops.unary_union(shapes)
		fs = fs.union(positive_overcuts)
		fs = fs.difference(negative_overcuts)
		o=utils.shapelyToCurve(o1.name+'_overcuts',fs,o1.location.z)
		#o=utils.shapelyToCurve('overcuts',overcuts,0)
		return {'FINISHED'}	

#Overcut type B
class CamCurveOvercutsB(bpy.types.Operator):
	'''Adds overcuts for slots'''
	bl_idname = "object.curve_overcuts_b"
	bl_label = "Add Overcuts-B"
	bl_options = {'REGISTER', 'UNDO'}
	
	
	diameter = bpy.props.FloatProperty(name="Tool diameter", default=.003, description='Tool bit diameter used in cut operation', min=0, max=100,precision=4, unit="LENGTH")
	style = bpy.props.EnumProperty(
				name="style",
				items=(('OPEDGE', 'opposite edge', 'place corner overcuts on opposite edges'),
					('DOGBONE', 'Dog-bone / Corner Point', 'place overcuts at center of corners'),
					('TBONE', 'T-bone', 'place corner overcuts on the same edge')),
				default='DOGBONE',
				description='style of overcut to use')
	threshold = bpy.props.FloatProperty(name="Max Inside Angle", default=math.pi/2, min=-3.14, max=3.14, description='The maximum angle to be considered as an inside corner', precision=4, subtype="ANGLE" , unit="ROTATION")
	do_outer = bpy.props.BoolProperty(name="Include outer curve", description='Include the outer curve if there are curves inside', default=True)
	do_invert = bpy.props.BoolProperty(name="Invert", description='invert overcut operation on all curves', default=True)
	otherEdge = bpy.props.BoolProperty(name="other edge", description='change to the other edge for the overcut to be on', default=False)

	@classmethod
	def poll(cls, context):
		return context.active_object is not None and context.active_object.type=='CURVE'

	def execute(self, context):
		o1 = bpy.context.active_object
		shapes = utils.curveToShapely(o1)
		negative_overcuts = []
		positive_overcuts = []
		# count all the corners including inside and out
		cornerCnt = 0
		# a list of tuples for defining the inside corner 
		# tuple is: (pos, v1, v2, angle, allCorners list index)
		insideCorners = []
		diameter = self.diameter * 1.001
		radius = diameter / 2
		anglethreshold = math.pi - self.threshold
		centerv = Vector((0,0))
		extendedv = Vector((0,0))
		pos = Vector((0,0))
		sign = -1 if self.do_invert else 1
		isTBone = self.style == 'TBONE'
		# indexes in insideCorner tuple
		POS, V1, V2, A, IDX = range(5)
		
		def addOvercut(a):
			nonlocal pos, centerv, radius, extendedv, sign, negative_overcuts, positive_overcuts
			# move the overcut shape center position 1 radius in direction v
			pos -= centerv * radius
			if abs(a) < math.pi/2:
				shape = utils.Circle(radius, 64)
				shape = shapely.affinity.translate(shape, pos.x, pos.y)
			else: # elongate overcut circle to make sure tool bit can fit into slot
				p1 = pos + (extendedv * radius)
				l = shapely.geometry.LineString((pos, p1))
				shape = l.buffer(radius, resolution = 64)
			
			if sign>0:
				negative_overcuts.append(shape)
			else:	
				positive_overcuts.append(shape)


		def setOtherEdge(v1, v2, a):
			nonlocal centerv, extendedv
			if self.otherEdge:
				centerv = v1
				extendedv = v2
			else:
				centerv = -v2
				extendedv = -v1
			addOvercut(a)
				
		def setCenterOffset(a):
			nonlocal centerv, extendedv, sign
			centerv = v1 - v2
			centerv.normalize()
			extendedv = centerv * math.tan(a/2) * -sign
			addOvercut(a)
			
			
		def getCorner(idx, offset):
			nonlocal insideCorners
			idx += offset
			if idx >= len(insideCorners):
				idx -= len(insideCorners)
			return insideCorners[idx]
			
		def getCornerDelta(curidx, nextidx):
			nonlocal cornerCnt
			delta = nextidx - curidx
			if delta < 0:
				delta += cornerCnt
			return delta
			

		for s in shapes:
			s = shapely.geometry.polygon.orient(s,1)
			loops = [s.boundary] if s.boundary.type == 'LineString'	else s.boundary
			outercurve = self.do_outer or len(loops)==1
			for ci,c in enumerate(loops):
				if ci>0 or outercurve:
					if isTBone:
						cornerCnt = 0
						insideCorners = []
						
					for i,co in enumerate(c.coords):
						i1 = i-1
						if i1==-1:
							i1 = -2
						i2 = i+1
						if i2 == len(c.coords):
							i2 = 0
							
						v1 = Vector(co).xy - Vector(c.coords[i1]).xy
						v2 = Vector(c.coords[i2]).xy - Vector(co).xy

						if not v1.length==0 and not v2.length == 0:
							a = v1.angle_signed(v2)
							insideCornerFound = False
							outsideCornerFound = False
							if a<-anglethreshold:
								if sign<0:
									insideCornerFound = True
								else:
									outsideCornerFound = True
							elif a>anglethreshold:
								if sign>0:
									insideCornerFound = True
								else:
									outsideCornerFound = True
									
							
							if insideCornerFound:
								# an inside corner with an overcut has been found
								# which means a new side has been found
								pos = Vector((co[0],co[1]))
								v1.normalize()
								v2.normalize()
								# figure out which direction vector to use
								# v is the main direction vector to move the overcut shape along
								# ev is the direction vector used to elongate the overcut shape
								if self.style != 'DOGBONE':
									# t-bone and opposite edge styles get treated nearly the same
									if isTBone:
										cornerCnt += 1
										#insideCorner tuplet: (pos, v1, v2, angle, corner index)
										insideCorners.append((pos, v1, v2, a, cornerCnt-1))
										#processing of corners for T-Bone are done after all points are processed
										continue
									
									setOtherEdge(v1, v2, a)
										
								else: # DOGBONE style
									setCenterOffset(a)
									
								
							elif isTBone and outsideCornerFound:
								# add an outside corner to the list
								cornerCnt += 1	

					# check if t-bone processing required
					# if no inside corners then nothing to do
					if isTBone and len(insideCorners) > 0:
						#print(cornerCnt, len(insideCorners))
						# process all of the inside corners
						for i, corner in enumerate(insideCorners):
							pos, v1, v2, a, idx = corner
							# figure out which side of the corner to do overcut
							# if prev corner is outside corner
							# calc index distance between current corner and prev
							prevCorner = getCorner(i, -1)
							#print('first:', i, idx, prevCorner[IDX])
							if getCornerDelta(prevCorner[IDX], idx) == 1:
								# make sure there is an outside corner
								#print(getCornerDelta(getCorner(i, -2)[IDX], idx))
								if getCornerDelta(getCorner(i, -2)[IDX], idx) > 2:
									setOtherEdge(v1, v2, a)
									#print('first won')
									continue
									
							nextCorner = getCorner(i, 1)
							#print('second:', i, idx, nextCorner[IDX])
							if getCornerDelta(idx, nextCorner[IDX]) == 1:
								# make sure there is an outside corner 
								#print(getCornerDelta(idx, getCorner(i, 2)[IDX]))
								if getCornerDelta(idx, getCorner(i, 2)[IDX]) > 2:
									#print('second won')
									setOtherEdge(-v2, -v1, a)
									continue
							
							#print('third')
							if getCornerDelta(prevCorner[IDX], idx) == 3:
								# check if they share the same edge
								a1 = v1.angle_signed(prevCorner[V2])*180.0/math.pi
								#print('third won', a1)
								if a1 < -135 or a1 > 135:
									setOtherEdge(-v2, -v1, a)
									continue
							
							#print('fourth')
							if getCornerDelta(idx, nextCorner[IDX]) == 3:
								# check if they share the same edge
								a1 = v2.angle_signed(nextCorner[V1])*180.0/math.pi
								#print('fourth won', a1)
								if a1 < -135 or a1 > 135:
									setOtherEdge(v1, v2, a)
									continue
							
							#print('***No Win***')
							# the default if no other rules pass	
							setCenterOffset(a)
								
							
						
						
		negative_overcuts = shapely.ops.unary_union(negative_overcuts)
		positive_overcuts = shapely.ops.unary_union(positive_overcuts)
		fs = shapely.ops.unary_union(shapes)
		fs = fs.union(positive_overcuts)
		fs = fs.difference(negative_overcuts)
		o=utils.shapelyToCurve(o1.name+'_overcuts',fs,o1.location.z)
		return {'FINISHED'}	

		
class CamCurveRemoveDoubles(bpy.types.Operator):
	'''curve remove doubles - warning, removes beziers!'''
	bl_idname = "object.curve_remove_doubles"
	bl_label = "C-Remove doubles"
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		return context.active_object is not None and (context.active_object.type=='CURVE')

	def execute(self, context):
		obs=bpy.context.selected_objects
		for ob in obs:
			bpy.context.scene.objects.active=ob
			
			mode=False
			if bpy.context.mode=='EDIT_CURVE':
				bpy.ops.object.editmode_toggle()
				mode=True
			bpy.ops.object.convert(target='MESH')
			bpy.ops.object.editmode_toggle()
			bpy.ops.mesh.select_all(action='TOGGLE')
			bpy.ops.mesh.remove_doubles()
			bpy.ops.object.editmode_toggle()
			bpy.ops.object.convert(target='CURVE')
			a=bpy.context.active_object
			a.data.show_normal_face = False
			if mode:
				bpy.ops.object.editmode_toggle()
		
		return {'FINISHED'}	

class CamMeshGetPockets(bpy.types.Operator):
	'''Detect pockets in a mesh and extract them as curves'''
	bl_idname = "object.mesh_get_pockets"
	bl_label = "Get pocket surfaces"
	bl_options = {'REGISTER', 'UNDO'}

	threshold = bpy.props.FloatProperty(name="horizontal threshold", description="How horizontal the surface must be for a pocket: 1.0 perfectly flat, 0.0 is any orientation", default=.99, min=0, max=1.0, precision=4)
	zlimit = bpy.props.FloatProperty(name="z limit", description="maximum z height considered for pocket operation, default is 0.0", default=0.0, min=-1000.0, max=1000.0, precision=4, unit='LENGTH')

	@classmethod
	def poll(cls, context):
		return context.active_object is not None and (context.active_object.type=='MESH')
	
	def execute(self, context):
		obs = bpy.context.selected_objects
		s=bpy.context.scene
		cobs = []
		for ob in obs:
			if ob.type=='MESH':
				pockets={}
				mw = ob.matrix_world
				mesh = ob.data
				bpy.ops.object.editmode_toggle()
				bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='FACE')
				bpy.ops.mesh.select_all(action='DESELECT')
				bpy.ops.object.editmode_toggle()
				i=0
				for face in mesh.polygons:
					n = mw * face.normal
					if n.z > self.threshold :
						face.select = True
						z = (mw * mesh.vertices[face.vertices[0]].co).z
						if z < self.zlimit:
							if pockets.get(z)==None:
								pockets[z] = [i]
							else:
								pockets[z].append(i)
					i+=1
				print(len(pockets))
				for p in pockets:
					print(p)
				ao = bpy.context.active_object
				i=0
				for p in pockets:
					print(i)
					i+=1
					
					sf = pockets[p]
					for face in mesh.polygons:
						face.select = False
					
					for fi in sf:
						face = mesh.polygons[fi]
						face.select = True
					
					bpy.ops.object.editmode_toggle()
					
					bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')
					bpy.ops.mesh.region_to_loop()
					bpy.ops.mesh.separate(type = 'SELECTED')
					
					bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='FACE')
					bpy.ops.object.editmode_toggle()
					ao.select=False
					s.objects.active=bpy.context.selected_objects[0]
					cobs.append(s.objects.active)
					bpy.ops.object.convert(target='CURVE')
					bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')

					bpy.context.selected_objects[0].select=False
					ao.select=True
					s.objects.active=ao
					#bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')
			
			# turn off selection of all objects in 3d view
			bpy.ops.object.select_all(action='DESELECT')
			# make new curves more visible by making them selected in the 3d view
			# This also allows the active object to still work with the operator
			# if the user decides to change the horizontal threshold property
			for obj in cobs:
				obj.select = True
			bpy.ops.group.create(name = "multi level pocket ")

		return {'FINISHED'}			

#this operator finds the silhouette of objects(meshes, curves just get converted) and offsets it.
class CamOffsetSilhouete(bpy.types.Operator):
	'''Curve offset operation '''
	bl_idname = "object.silhouete_offset"
	bl_label = "Silhouete offset"
	bl_options = {'REGISTER', 'UNDO'}
	
	offset = bpy.props.FloatProperty(name="offset", default=.003, min=-100, max=100,precision=4, unit="LENGTH")
		
	@classmethod
	def poll(cls, context):
		return context.active_object is not None and (context.active_object.type=='CURVE' or context.active_object.type=='FONT' or context.active_object.type=='MESH')

	def execute(self, context):#this is almost same as getobjectoutline, just without the need of operation data
		utils.silhoueteOffset(context,self.offset)
		return {'FINISHED'}

#Finds object silhouette, usefull for meshes, since with curves it's not needed.		
class CamObjectSilhouete(bpy.types.Operator):
	'''Object silhouete '''
	bl_idname = "object.silhouete"
	bl_label = "Object silhouete"
	bl_options = {'REGISTER', 'UNDO'}
		
	@classmethod
	def poll(cls, context):
		return context.active_object is not None and (context.active_object.type=='MESH')

		
		
	def execute(self, context):#this is almost same as getobjectoutline, just without the need of operation data
		ob=bpy.context.active_object
		self.silh=utils.getObjectSilhouete('OBJECTS', objects=bpy.context.selected_objects)
		bpy.context.scene.cursor_location=(0,0,0)
		#smp=sgeometry.asMultiPolygon(self.silh)
		for smp in self.silh:
			polygon_utils_cam.shapelyToCurve(ob.name+'_silhouette',smp,0)#
		#bpy.ops.object.convert(target='CURVE')
		bpy.context.scene.cursor_location=ob.location
		bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
		return {'FINISHED'}
