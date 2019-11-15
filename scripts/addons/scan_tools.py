import bpy
import mathutils
from mathutils import Vector
from bpy_extras import view3d_utils

bl_info = {
	"name": "Scan tools",
	"author": "Vilem Novak",
	"version": (1, 0),
	"blender": (2, 69, 0),
	"location": "View3D > Scan tools",
	"description": "Various tools for postprocessing scan results",
	"warning": "",
	"wiki_url": "",
	"tracker_url": "",
	"category": "Object"}

def floor(self,context, event, ray_max=100000.0):
	"""Run this function on left mouse, execute the ray cast"""
	# get the context arguments
	scene = context.scene
	region = context.region
	rv3d = context.region_data
	coord = event.mouse_region_x, event.mouse_region_y


	# get the ray from the viewport and mouse
	view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
	ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)
	ray_target = ray_origin + (view_vector * ray_max)



	def obj_ray_cast(obj, matrix):
		"""Wrapper for ray casting that moves the ray into object space"""

		# get the ray relative to the object
		matrix_inv = matrix.inverted()
		ray_origin_obj = matrix_inv * ray_origin
		ray_target_obj = matrix_inv * ray_target
		vec = ray_target_obj - ray_origin_obj
		# cast the ray
		result, hit, normal, face_index = obj.ray_cast(ray_origin_obj, vec, vec.length)

		if face_index != -1:
			return hit, normal, face_index
		else:
			return None, None, None

	# cast rays and find the closest object
	best_length_squared = ray_max * ray_max
	best_obj = None

	obj=bpy.context.active_object
	matrix = obj.matrix_world.copy()
	if obj.type == 'MESH':
		hit, normal, face_index = obj_ray_cast(obj, matrix)
		print(hit)
		if hit is not None:

			hit_world = matrix * hit
			scene.cursor_location = hit_world
			self.hits.append(hit)
			print(len(self.hits))
			#if len(self.hits)==1:
			#
			n=mathutils.Vector((0,0,0))
			if len(self.hits)>=3:
				for a in range(0,len(self.hits)-2):
					v1=matrix * self.hits[a]
					v2=matrix * self.hits[a+1]
					v3=matrix * self.hits[a+2]

					ntri=mathutils.geometry.normal(v1,v2,v3)
					n+=ntri
				up=mathutils.Vector((0,0,1))
				r=n.rotation_difference(up)#.to_euler()
				print(n,r)

				print(obj.rotation_quaternion)
				print(matrix)
				#print(r)
				v=matrix * ((self.hits[0]+self.hits[1]+self.hits[2])/3)
				obj.location-=v
				m=obj.rotation_mode
				bpy.ops.object.transform_apply(location=True, rotation=False, scale=True)
				obj.rotation_mode='QUATERNION'
				obj.rotation_quaternion.rotate(r)
				obj.rotation_mode=m
				#obj.rotation_euler=obj.rotation_euler
				#obj.update()
				matrix = obj.matrix_world.copy()
				print(matrix)


				bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
				return True
	return False

class ObjectFloor(bpy.types.Operator):
	"""define floor on scan mesh"""
	bl_idname = "object.align_floor"
	bl_label = "Floor"
	bl_options = {'REGISTER', 'UNDO'}
	@classmethod
	def poll(cls, context):
		return context.active_object is not None

	def modal(self, context, event):
		#self.report({'OPERATOR'}, "Select 3 or more points on the floor, Esc exits")
		if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
			# allow navigation
			return {'PASS_THROUGH'}
		elif event.type == 'LEFTMOUSE' and event.value=='PRESS':
			#print(dir(event))
			#print(event.value)
			finish = floor(self,context, event)
			if finish:
				return{'FINISHED'}
			return {'RUNNING_MODAL'}
		elif event.type in {'RIGHTMOUSE', 'ESC'}:
			#self.hits=[]
			return {'CANCELLED'}

		return {'RUNNING_MODAL'}

	def invoke(self, context, event):
		if context.space_data.type == 'VIEW_3D':
			self.hits=[]
			context.window_manager.modal_handler_add(self)
			return {'RUNNING_MODAL'}
		else:
			self.report({'WARNING'}, "Active space must be a View3d")
			return {'CANCELLED'}

def removeFloor(context,threshold):
	ob=bpy.context.active_object
	m=ob.data
	matrix = ob.matrix_world.copy()
	sel=0
	bpy.ops.object.editmode_toggle()

	bpy.ops.mesh.select_all(action='DESELECT')
	bpy.ops.object.editmode_toggle()
	for vert in m.vertices:
		v=matrix*vert.co
		if v.z<threshold:
			vert.select=True
			sel+=1
		else:
			vert.select=False
	print(len(m.vertices),sel)
	m.update()
	bpy.ops.object.editmode_toggle()
	for a in range(0,5):
		bpy.ops.mesh.select_more()
	for a in range(0,8):# this is larger, so legs etc won't be cut
		bpy.ops.mesh.select_less()
	bpy.ops.mesh.delete(type='VERT')
	bpy.ops.object.editmode_toggle()



class RemoveFloor(bpy.types.Operator):
	"""Remove floor (distance from XY plane in world coordinates) on aligned mesh"""
	bl_idname = "object.remove_floor"
	bl_label = "Remove Floor"
	bl_options = {'REGISTER', 'UNDO'}

	threshold = bpy.props.FloatProperty(
			name="threshold",
			description="Distance in world units from axis plane",
			min=0.00001, max=100.0,
			default=.01)
	@classmethod
	def poll(cls, context):
		return context.active_object is not None

	def execute(self, context):
		removeFloor(context,self.threshold)
		return {'FINISHED'}


def makeLOD(context):
	ob=bpy.context.active_object
	bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
	parent=None
	if ob.parent!=None:
		parent=ob.parent
	bpy.ops.object.duplicate()
	bpy.ops.object.modifier_add(type='DECIMATE')
	bpy.context.object.modifiers["Decimate"].ratio = 0.05
	bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Decimate")
	lod=bpy.context.active_object
	ob.select=True
	bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
	ob.hide=True
	par=bpy.context.active_object
	par.hide_render=True
	if parent!=None:
		par.parent


class MakeLOD(bpy.types.Operator):
	"""Add low poly mesh for view and hide high poly mesh"""
	bl_idname = "object.make_lod"
	bl_label = "make LOD"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		return context.active_object is not None

	def execute(self, context):
		makeLOD(context)
		return {'FINISHED'}

class ReconstructmeTransform(bpy.types.Operator):
	"""Transform import from reconstructme to blender axes/scale"""
	bl_idname = "object.reconstructme_trans"
	bl_label = "Reconstructme transform"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		return context.active_object is not None

	def execute(self, context):
		reconstructmTransform(context)
		return {'FINISHED'}

def reconstructmTransform(context):
	ob=bpy.context.active_object
	ob.scale=(0.001,0.001,0.001)
	ob.rotation_euler.x=90
	bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
	ob.location=(0,0,0)
	bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

class RemoveSmallParts(bpy.types.Operator):
	"""Transform import from reconstructme to blender axes/scale"""
	bl_idname = "object.remove_small_parts"
	bl_label = "Remove small parts"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		return context.active_object is not None

	def execute(self, context):
		removeSmallParts(context)
		return {'FINISHED'}

def removeSmallParts(context):
	actob=bpy.context.active_object
	bpy.ops.object.editmode_toggle()
	bpy.ops.mesh.separate(type='LOOSE')
	bpy.ops.object.editmode_toggle()
	obs=bpy.context.selected_objects
	rem=[]
	nrem=[]
	for ob in obs:
		if len(ob.data.vertices)<300:
			print(ob.name)
			rem.append(ob)
		else:
			nrem.append(ob)
	bpy.ops.object.select_all(action='DESELECT')
	for ob in rem:
		ob.select=True
	bpy.ops.object.delete(use_global=False)
	for ob in nrem:
		ob.select=True
	bpy.context.scene.objects.active=nrem[0]
	bpy.ops.object.join()



#panel containing all tools
class VIEW3D_PT_tools_scantools(bpy.types.Panel):
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'TOOLS'
	bl_context = "objectmode"
	bl_label = "Scan Tools"
	bl_options = {'DEFAULT_CLOSED'}

	def draw(self, context):
		layout = self.layout
		#col = layout.column(align=True)
		#lt = context.window_manager.looptools
		layout.operator("object.reconstructme_trans")
		layout.operator("object.align_floor")
		layout.operator("object.remove_floor")
		layout.operator("object.remove_small_parts")
		layout.operator("object.make_lod")

def register():
	bpy.utils.register_class(ObjectFloor)
	bpy.utils.register_class(RemoveFloor)
	bpy.utils.register_class(ReconstructmeTransform)
	bpy.utils.register_class(RemoveSmallParts)
	bpy.utils.register_class(MakeLOD)
	bpy.utils.register_class(VIEW3D_PT_tools_scantools)


def unregister():
	bpy.utils.unregister_class(ObjectFloor)
	bpy.utils.unregister_class(RemoveFloor)
	bpy.utils.unregister_class(ReconstructmeTransform)
	bpy.utils.unregister_class(RemoveSmallParts)
	bpy.utils.unregister_class(MakeLOD)
	bpy.utils.unregister_class(VIEW3D_PT_tools_scantools)


if __name__ == "__main__":
	register()