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
from cam import utils, pack
from bpy.props import *

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
		
	for area in bpy.context.screen.areas:
		if area.type == 'PROPERTIES':
			area.tag_redraw()
			
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
		else:
			o.onlycurves=False
			
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

class CamPolyBoolean(bpy.types.Operator):
	'''Boolean operation on two curves'''
	bl_idname = "object.curve_boolean"
	bl_label = "Curve Boolean operation"
	bl_options = {'REGISTER', 'UNDO'}
	
	boolean_type = EnumProperty(name='type',
		items=(('UNION','Union',''),('DIFFERENCE','Difference',''),('INTERSECT','Intersect','')),
		description='boolean type',
		default='UNION')
		
	#@classmethod
	#def poll(cls, context):
	#	return context.active_object is not None and context.active_object.type=='CURVE' and len(bpy.context.selected_objects)==2

	def execute(self, context):
		utils.polygonBoolean(context,self.boolean_type)
		return {'FINISHED'}
		
	#def draw(self, context):
	#	layout = self.layout
	#	layout.prop(self, "boolean_type")
	
class CamOffsetSilhouete(bpy.types.Operator):
	'''Curve offset operation '''
	bl_idname = "object.silhouete_offset"
	bl_label = "Silhouete offset"
	bl_options = {'REGISTER', 'UNDO'}
	
	offset = bpy.props.FloatProperty(name="offset", default=.003, min=-100, max=100,precision=4, unit="LENGTH")
		
	#@classmethod
	##def poll(cls, context):
	#	return context.active_object is not None and context.active_object.type=='CURVE'

	def execute(self, context):#this is almost same as getobjectoutline, just without the need of operation data
		utils.silhoueteOffset(context,self.offset)
		return {'FINISHED'}
		
	#def draw(self, context):
	#	layout = self.layout
	#	layout.prop(self, "boolean_type")
	
class CamObjectSilhouete(bpy.types.Operator):
	'''Object silhouete '''
	bl_idname = "object.silhouete"
	bl_label = "Object silhouete"
	bl_options = {'REGISTER', 'UNDO'}
	
	
	#offset = bpy.props.FloatProperty(name="offset", default=.0001, min=-100, max=100,precision=4)
		
	#@classmethod
	##def poll(cls, context):
	#	return context.active_object is not None and context.active_object.type=='CURVE'
	#
		
		
	def execute(self, context):#this is almost same as getobjectoutline, just without the need of operation data
		ob=bpy.context.active_object
		self.silh=utils.getObjectSilhouete('OBJECTS', objects=bpy.context.selected_objects)
		poly=Polygon.Polygon()
		for p in self.silh:
			for ci in range(0,len(p)):
				poly.addContour(p[ci])
		bpy.context.scene.cursor_location=(0,0,0)
		polygon_utils_cam.polyToMesh(poly,0)#
		bpy.ops.object.convert(target='CURVE')
		bpy.context.scene.cursor_location=ob.location
		bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
		#utils.chunksToMesh(silh)
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
