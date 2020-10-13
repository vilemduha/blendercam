bl_info = {
	"name": "G - Pack",
	"author": "Velem Novak",
	"version": (0, 2, 0),
	"blender": (2, 77, 0),
	"location": "Object > G-Pack",
	"description": "UV packing game",
	"warning": "",
	"wiki_url": "http://www.blendercam.blogspot.com",
	"category": "Object"
}


import bpy
import math, random, os
import mathutils
from mathutils import *
import bmesh
PRECISION=0.0000000001



def activate(ob):
	bpy.ops.object.select_all(action='DESELECT')
	ob.select=True
	bpy.context.scene.objects.active=ob



def createMeshFromData(name, verts, faces):
	# Create mesh and object
	me = bpy.data.meshes.new(name+'Mesh')
	ob = bpy.data.objects.new(name, me)
	#ob.show_name = True

	# Link object to scene and make active
	scn = bpy.context.scene
	scn.objects.link(ob)
	scn.objects.active = ob
	ob.select = True

	# Create mesh from given verts, faces.
	me.from_pydata(verts, [], faces)
	# Update mesh with new data
	me.update()
	return ob

def getIslands(me):

	bm = bmesh.from_edit_mesh(me)
	for f in bm.faces:
		f.select=False
	all=False
	done={}
	islands=[]
	while not len(done)>=len(bm.faces):
		island=[]
		for i,p in enumerate(bm.faces):

			if done.get(i) == None:
				p.select=True
				done[i]=True
				island.append(p.index)
				break
		nf = [p]
		while len(nf)>0:
			selected_faces = nf
			nf = []

			for f in selected_faces:
				for edge in f.edges:
					if edge.seam==False:
						linkede = edge.link_faces
						for face in linkede:
							if not face.select and done.get(face.index)==None:
								done[face.index]=True
								nf.append(face)
								face.select=True
								island.append(face.index)
		islands.append(island)
	return islands
	#print(islands)

def GameDropOb(ob,margin,enablerotation):

	activate(ob)
	#ob.rotation_euler.x=math.pi/2
	#bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
	#ob.location.z = ob.location.y
	#ob.location.x=0

	ob.select=True
	ob.game.physics_type='RIGID_BODY'
	ob.game.use_collision_bounds=True
	ob.game.collision_bounds_type = 'TRIANGLE_MESH'
	ob.game.collision_margin = margin
	ob.game.velocity_max = 1
	ob.game.damping = 0.5
	ob.game.rotation_damping = 0.9

	ob.game.lock_location_y = True
	ob.game.lock_rotation_x = True
	if not enablerotation:
		ob.game.lock_rotation_y = True#conditional#
	ob.game.lock_rotation_z = True


	bpy.ops.object.game_property_new(name="island")


def UVobs(obs,set):
	uvobs=[]
	zoffset=0
	for ob in obs:
		activate(ob)

		bpy.ops.object.editmode_toggle()
		if set.startConditions=='NEW':
			bpy.ops.uv.pack_islands(margin=0.01)
		#print('a')
		islands = getIslands(ob.data)
		#print('b')
		bpy.ops.object.editmode_toggle()


		print(len(islands))
		for iidx,island in enumerate(islands):
			out_verts=[]
			out_faces=[]

			print(iidx,len(islands))
			vertidx=0

			vertindices= {}
			loops=[]
			for fi in island:
				face = ob.data.polygons[fi]
				oface=[]

				for vert, loop in zip(face.vertices, face.loop_indices):
					uv = ob.data.uv_layers.active.data[loop].uv.copy()

					# if vertindices.get(vert) == None:
					#
					# 	vertindices[vert]=vertidx
					# 	nvertindex = vertidx
					# 	out_verts.append((uv.x,0,uv.y))
					# 	vertidx+=1
					#
					#
					# nvertindex = vertindices[vert]
					#
					# #print(vert,nvertindex, vertindices)
					# #print()
					# oface.append(nvertindex)

					loops.append(loop)
					out_verts.append((uv.x,0,uv.y))
					oface.append(vertidx)
					vertidx+=1
				#print(oface)
				out_faces.append(oface)
			#print(out_verts,out_faces)
			uvob = createMeshFromData(ob.name + 'UVObj', out_verts, out_faces)

			activate(uvob)
			bpy.ops.mesh.uv_texture_add()
			#print(uvob.name)
			#print(bpy.context.active_object.name)
			activate(uvob)
			vertidx = 0
			for fi in island:
				face = ob.data.polygons[fi]
				oface=[]
				for vert, loop in zip(face.vertices, face.loop_indices):
					uvob.data.uv_layers.active.data[vertidx].uv  = (loops[vertidx],0)#ob.data.uv_layers.active.data[loop].uv

					#print('loop',loops[vertidx])
					vertidx+=1

			print(uvob.name)
			bpy.ops.object.editmode_toggle()
			bpy.ops.mesh.remove_doubles(threshold = 0.0000001)

			#print('d')

			bpy.ops.object.editmode_toggle()
			bpy.ops.object.modifier_add(type='SOLIDIFY')
			bpy.context.object.modifiers["Solidify"].thickness = min(0.3, min(uvob.dimensions.x,uvob.dimensions.y)) #0.1

			bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Solidify")
			#print('e')

			uvob['source']=ob.name
			uvob['island']=iidx
			uvob['islandindices']=island
			if set.startConditions=='NEW':
				uvob.location.z+=zoffset#we shift the uv to not collide when packing more objects
			uvobs.append(uvob)
			bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS')
			zoffset+=uvob.dimensions.z+0.005
	#fal
	print('c')
	for ob in uvobs:
		ob.select=True

	s=bpy.context.scene
	s.objects.active=uvobs[0]

	bpy.ops.object.material_slot_add()
	mat=bpy.data.materials.new('GPackMaterial')


	uvobs[0].material_slots[0].material=mat
	mat.use_object_color = True
	for ob in uvobs:
		ob.color = (0.5+random.random(),0.5+random.random(),0.5+random.random(),1)
	mat.diffuse_color = (1,1,1)
	bpy.ops.object.make_links_data(type='MATERIAL')

	return uvobs

def doGameUV(context):

	#getIslands(bpy.context.active_object)
	obs=bpy.context.selected_objects
	activeOb=bpy.context.object
	origscene=bpy.context.scene
	import_scene('GPack')


	set=bpy.context.scene.gpacker_settings

	uvobs = UVobs(obs,set)

	for ob in uvobs:
		GameDropOb(ob,set.initialmargin, set.enablerotation)

	bpy.ops.object.select_all(action='DESELECT')
	for ob in uvobs:
		ob.select=True

	bpy.ops.group.create()
	bpy.ops.object.make_links_scene(scene='GPack')
	bpy.ops.object.delete(use_global=False)
	bpy.context.window.screen.scene = bpy.data.scenes['GPack']

	bpy.ops.view3d.viewnumpad(type='CAMERA')
	bpy.context.space_data.viewport_shade = 'MATERIAL'
	#bpy.ops.view3d.zoom_camera_1_to_1()
	#bpy.context.scene.update()
	for ob in bpy.data.scenes['GPack'].objects:
		if ob.game.properties.get('startconditions')!=None:
			ob.game.properties['startconditions'].value = set.startConditions
			ob.game.properties['doobjects'].value = False
			ob.game.properties['xsize'].value = set.xsize
			ob.game.properties['ysize'].value = set.ysize

	#PLAY THE GAME!
	bpy.ops.view3d.game_start()

	if set.apply==True:
		print('after game')
		#reassign UV's

		bpy.context.scene.update()
		#get size object
		for ob in bpy.context.scene.objects:
			if ob.name[:5]=='ssize':
				scale=ob.location.z+1
		for uvob in uvobs:
			uvobmat=uvob.matrix_world
			ob=bpy.data.objects[uvob['source']]

			assigns=[]

			for uvfi,fi in enumerate(uvob['islandindices']):
				face = ob.data.polygons[fi]
				uvface = uvob.data.polygons[uvfi]

				for vert1, loop1 in zip(uvface.vertices, uvface.loop_indices):
					co=uvobmat*uvob.data.vertices[vert1].co/scale

					idxuv = int(uvob.data.uv_layers.active.data[loop1].uv.x)
					print(idxuv)
					uv=ob.data.uv_layers.active.data[idxuv].uv
					uv.x = co.x
					uv.y = co.z



		#print(fdict)
		assigns=[]


		print(len(assigns))


	bpy.context.window.screen.scene = origscene
	bpy.data.scenes.remove(bpy.data.scenes['GPack'], do_unlink = True)
	bpy.data.texts.remove(bpy.data.texts['root'])
	activate(activeOb)
	for ob in obs:
		ob.select=True

#packing of curves

def getBoundsWorldspace(ob):
	#progress('getting bounds of object(s)')


	maxx=maxy=maxz=-10000000
	minx=miny=minz=10000000

	bb=ob.bound_box
	mw=ob.matrix_world

	for coord in bb:
		#this can work badly with some imported curves, don't know why...
		#worldCoord = mw * Vector((coord[0]/ob.scale.x, coord[1]/ob.scale.y, coord[2]/ob.scale.z))
		worldCoord = mw * Vector((coord[0], coord[1], coord[2]))
		minx=min(minx,worldCoord.x)
		miny=min(miny,worldCoord.y)
		minz=min(minz,worldCoord.z)
		maxx=max(maxx,worldCoord.x)
		maxy=max(maxy,worldCoord.y)
		maxz=max(maxz,worldCoord.z)

	#progress(time.time()-t)
	return minx,miny,minz,maxx,maxy,maxz

def getBoundsSpline(s):
	#progress('getting bounds of object(s)')


	maxx=maxy=maxz=-10000000
	minx=miny=minz=10000000




	for p in s.points:
		#this can work badly with some imported curves, don't know why...
		#worldCoord = mw * Vector((coord[0]/ob.scale.x, coord[1]/ob.scale.y, coord[2]/ob.scale.z))

		minx=min(minx,p.co.x)
		miny=min(miny,p.co.y)
		minz=min(minz,p.co.z)
		maxx=max(maxx,p.co.x)
		maxy=max(maxy,p.co.y)
		maxz=max(maxz,p.co.z)
	for p in s.bezier_points:
		minx=min(minx,p.co.x)
		miny=min(miny,p.co.y)
		minz=min(minz,p.co.z)
		maxx=max(maxx,p.co.x)
		maxy=max(maxy,p.co.y)
		maxz=max(maxz,p.co.z)
	#progress(time.time()-t)
	return minx,miny,minz,maxx,maxy,maxz

def getInstances(obs):
	instanceindices=[]
	data=[]
	dataindices=[]
	counti=0
	#dataindex=0
	for ob in obs:
		if not ob.data in data:# or 1:
			data.append(ob.data)
			instanceindices.append(counti)
			dataindices.append(counti)
			#dataindex+=1

		else:
			i = data.index(ob.data)
			#print(i);
			instanceindices.append(instanceindices[dataindices[i]])
		counti+=1
	print('number of original shapes',str(len(data)))
	print(instanceindices)
	return instanceindices

def prepareCurves(obs, set):
	packobs=[]
	zoffset=0
	instanceindices=getInstances(obs)
	instanceindex=0
	e=mathutils.Euler((math.pi/2,0,0))

	for ob in obs:

		if ob.type=='CURVE':

			oldloc=ob.location.copy()

			if instanceindices[instanceindex]==instanceindex:


				activate(ob)
				bpy.ops.object.duplicate()
				packob=bpy.context.active_object
				#bpy.ops.object.rotation_clear()
				simplify=True
				thickness=0.1
				if simplify:
					c=packob.data
					if len(c.splines)>0:
						maxbounds=-10000
						maxc=0
						for i in range(0,len(c.splines)):
							minx,miny,minz,maxx,maxy,maxz=getBoundsSpline(c.splines[i])
							if maxx-minx+maxy-miny>maxbounds:
								maxc=i
								maxbounds= maxx-minx+maxy-miny
						for i in range(len(c.splines)-1,-1,-1):
							if i!=maxc:
								c.splines.remove(c.splines[i])
					doconvert=False
					for s in c.splines:
						if s.type!='POLY':
							doconvert=True
					if doconvert:
						c.dimensions = '3D'
						bpy.ops.object.convert(target='MESH')
						bpy.ops.object.convert(target='CURVE')

					bpy.ops.curve.simplify(error = 0.001)
					#delete packob here?
					bpy.context.scene.objects.unlink(packob)
					packob=bpy.context.active_object
					activate(packob)
					for s in packob.data.splines:
						s.use_cyclic_u=True

					if min(maxx-minx,maxy-miny)<0.1:
						thickness=min(maxx-minx,maxy-miny)
				packob.data.dimensions = '2D'


				bpy.context.active_object.rotation_euler.rotate(e)
				#packob.rotation_euler=(math.pi/2,0,0)


				#bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS')
				newloc=packob.location.copy()
				#print(newloc-oldloc)

				bpy.ops.object.convert(target='MESH')
				activate(packob)
				bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
				#print(packob.name)
				#print(bpy.context.active_object)
				bpy.ops.object.modifier_add(type='SOLIDIFY')
				bpy.context.object.modifiers["Solidify"].thickness = thickness
				bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Solidify")
				#bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
			else:
				print(instanceindex)
				source_packob=packobs[instanceindices[instanceindex]][0]

				activate(source_packob)
				bpy.ops.object.duplicate(linked=True)
				packob=bpy.context.active_object

				packob.rotation_euler=(math.pi/2,-ob.rotation_euler.z,0)
				#packob.rotation_euler.rotate()
				#packob.rotation_euler.rotate(e)

			packob['source']=ob.name
			if set.startConditions=='TWEAK' or set.startConditions=='FIXED':
				packob.location=(oldloc.x,0,oldloc.y)
			if set.startConditions=='NEW':
				packob.location=(0,0,0)
				bpy.ops.object.location_clear()
				packob.rotation_euler=(math.pi/2,0,0)
				minx,maxx,miny,maxy,minz,maxz=getBoundsWorldspace(packob)
				packob.location.x=-minx
				packob.location.z= -miny+zoffset
				zoffset+= maxy-miny

			#bpy.ops.object.editmode_toggle()
			#bpy.ops.mesh.separate(type='LOOSE')
			#bpy.ops.object.editmode_toggle()
			packobs.append((packob,ob, newloc-oldloc))
		instanceindex+=1
	return packobs


def doGameObs(context):
	#getIslands(bpy.context.active_object)
	obs=bpy.context.selected_objects
	origscene=bpy.context.scene
	import_scene('GPack')
	set=bpy.context.scene.gpacker_settings

	packobs=prepareCurves(obs,set)
	gobs=[]
	for data in packobs:
		ob=data[0]
		GameDropOb(ob,set.initialmargin, set.enablerotation)
	for data in packobs:
			data[0].select=True
	bpy.ops.group.create()
	print('done')

	bpy.ops.object.make_links_scene(scene='GPack')
	bpy.ops.object.delete(use_global=False)
	bpy.context.window.screen.scene = bpy.data.scenes['GPack']

	bpy.ops.view3d.viewnumpad(type='CAMERA')
	bpy.context.space_data.viewport_shade = 'MATERIAL'
	#pass data to game:
	for ob in bpy.data.scenes['GPack'].objects:
		if ob.game.properties.get('startconditions')!=None:
			ob.game.properties['startconditions'].value = set.startConditions
			ob.game.properties['doobjects'].value = True
			ob.game.properties['xsize'].value = set.xsize
			ob.game.properties['ysize'].value = set.ysize

	bpy.ops.view3d.game_start()
	for s in bpy.data.scenes:
		s.gpacker_settings.doobjects=False
	print('repack')

	if set.apply:
		for data in packobs:
			print(data[0].location,data[1].location)
			data[1].location.x=data[0].location.x
			data[1].location.y=data[0].location.z
			data[1].rotation_euler.z=-data[0].rotation_euler.y

			#bpy.context.scene.objects.unlink(data[0])
		for s in bpy.data.scenes:
			s.gpacker_settings.apply=False
	bpy.context.window.screen.scene = origscene
	bpy.data.scenes.remove(bpy.data.scenes['GPack'])
	for ob in obs:
		ob.select=True


#####################################################################
# Import Functions

def import_scene(obname):
	opath = "//data.blend\\Scene\\" + obname
	s = os.sep
	for p in bpy.utils.script_paths():
		fname= p + '%saddons%sGPack%spack_scene.blend' % (s,s,s)
		dpath = p + \
			'%saddons%sGPack%spack_scene.blend\\Scene\\' % (s, s, s)
		if os.path.isfile(fname):
			break
	# DEBUG
	#print('import_object: ' + opath)
	print(dpath,opath)
	result = bpy.ops.wm.append(
			filepath=opath,
			filename=obname,
			directory=dpath,
			filemode=1,
			link=False,
			autoselect=True,
			active_layer=True,
			instance_groups=True
		   )
	print(result)


import bpy


class GPackUVOperator(bpy.types.Operator):
	"""Tooltip"""
	bl_idname = "object.gpack_uv"
	bl_label = "Gravity Pack UVs"

	@classmethod
	def poll(cls, context):
		return len(context.selected_objects)>0

	def execute(self, context):
		doGameUV(context)
		return {'FINISHED'}

class GPackCurvesOperator(bpy.types.Operator):
	"""Tooltip"""
	bl_idname = "object.gpack"
	bl_label = "Gravity Pack Curves"

	@classmethod
	def poll(cls, context):
		return len(context.selected_objects)>0

	def execute(self, context):
		doGameObs(context)
		return {'FINISHED'}


class GPackSettings(bpy.types.PropertyGroup):


	#lpgroup =   bpy.props.StringProperty(name="low poly group", default="")
	#hpgroup =   bpy.props.StringProperty(name="high poly group", default="")
	apply =  bpy.props.BoolProperty(name="apply",description="", default=False)
	doobjects =  bpy.props.BoolProperty(name="doobjects",description="", default=False)

	startConditions = bpy.props.EnumProperty(name='start state', items=(('NEW','Drop All','all parts are dropped into the layout'),('FIXED','Fixed','All objects are still in beginning, just tweak the extra additions'),('TWEAK','Tweak','start from current state, position objects before to drop properly')),
		description='start conditions',
		default='TWEAK')
	xsize =  bpy.props.FloatProperty(name="X-sheet-size",description="", default=1)
	ysize =  bpy.props.FloatProperty(name="Y-size",description="", default=1)
	initialmargin =  bpy.props.FloatProperty(name="initial margin",description="", default=0.003)
	enablerotation =  bpy.props.BoolProperty(name="rotation",description="", default=True)

class GPackCurvesPanel(bpy.types.Panel):
	"""Creates a Panel in the Object properties window"""
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'TOOLS'
	bl_label = "Gravity Packer"
	bl_idname = "WORLD_PT_GPACKER"

	bl_context = "objectmode"
	bl_options = {'DEFAULT_CLOSED'}
	bl_category = "Tools"

	def draw(self, context):
		layout = self.layout

		obj = bpy.context.active_object
		#s=bpy.context.scene
		s=bpy.context.scene.gpacker_settings
		row = layout.row()
		layout.operator("object.gpack")
		layout.operator("object.gpack_uv")
		#layout.prop_search(s, "lpgroup", bpy.data, "groups")
		#layout.prop_search(s, "hpgroup", bpy.data, "groups")

		layout.prop(s,'startConditions')
		layout.prop(s,'xsize')
		layout.prop(s,'ysize')
		layout.prop(s,'initialmargin')
		layout.prop(s,'enablerotation')

		#layout.prop(s,'pass_combined')

# separate UV's????
# class GPackUVPanel(bpy.types.Panel):
# 	'''Creates a Panel in the Object properties window"""
# 	bl_label = "Gravity Packer"
# 	bl_idname = "WORLD_PT_GPACKER"
# 	bl_space_type = 'PROPERTIES'
# 	bl_region_type = 'WINDOW'
# 	bl_context = "object"
#
#
# 	def draw(self, context):
# 		layout = self.layout
#
# 		obj = bpy.context.active_object
# 		#s=bpy.context.scene
# 		s=bpy.context.scene.gpacker_settings
# 		row = layout.row()
# 		layout.operator("object.gpack_uv")
# 		#layout.prop_search(s, "lpgroup", bpy.data, "groups")
# 		#layout.prop_search(s, "hpgroup", bpy.data, "groups")
#
# 		layout.prop(s,'startConditions')
# 		layout.prop(s,'xsize')
# 		layout.prop(s,'ysize')
# 		layout.prop(s,'initialmargin')
#
#
# 		#layout.prop(s,'pass_combined')

def register():
	s = bpy.types.Scene
	bpy.utils.register_class(GPackUVOperator)
	bpy.utils.register_class(GPackCurvesOperator)
	bpy.utils.register_class(GPackSettings)
	bpy.utils.register_class(GPackCurvesPanel)
	s.gpacker_settings = bpy.props.PointerProperty(type= GPackSettings)

def unregister():
	bpy.utils.unregister_class(GPackUVOperator)
	bpy.utils.unregister_class(GPackCurvesOperator)
	bpy.utils.unregister_class(GPackSettings)
	bpy.utils.unregister_class(GPackCurvesPanel)


if __name__ == "__main__":
	register()


