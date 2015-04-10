import bpy
import time

from cam import simple
from cam.simple import *

BULLET_SCALE=10000 # this is a constant for scaling the rigidbody collision world for higher precision from bullet library


#
def getCutterBullet(o):
	'''cutter for rigidbody simulation collisions
		note that everything is 100x bigger for simulation precision.'''
	s=bpy.context.scene
	if s.objects.get('cutter')!= None:
		c=s.objects['cutter']
		activate(c)

	type=o.cutter_type
	if type=='END':
		bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=BULLET_SCALE*o.cutter_diameter/2, depth=BULLET_SCALE*o.cutter_diameter, end_fill_type='NGON', view_align=False, enter_editmode=False, location=(-100,-100, -100), rotation=(0, 0, 0))
		bpy.ops.rigidbody.object_add(type='ACTIVE')
		cutter=bpy.context.active_object
		cutter.rigid_body.collision_shape = 'CYLINDER'
	elif type=='BALL' or type=='BALLNOSE':
		if o.strategy!='PROJECTED_CURVE' or type=='BALL':#only sphere, good for 3 axis and real ball cutters for undercuts and projected curve
		
			bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, size=BULLET_SCALE*o.cutter_diameter/2, view_align=False, enter_editmode=False, location=(-100,-100, -100), rotation=(0, 0, 0))
			bpy.ops.rigidbody.object_add(type='ACTIVE')
			cutter=bpy.context.active_object
			cutter.rigid_body.collision_shape = 'SPHERE'
		else:#ballnose ending used mainly when projecting from sides. the actual collision shape is capsule in this case.
			bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, size=BULLET_SCALE*o.cutter_diameter/2, view_align=False, enter_editmode=False, location=(-100,-100, -100), rotation=(0, 0, 0))
			bpy.ops.rigidbody.object_add(type='ACTIVE')
			cutter=bpy.context.active_object
			cutter.dimensions.z=0.2*BULLET_SCALE#should be sufficient for now... 20 cm.
			cutter.rigid_body.collision_shape = 'CAPSULE'
			bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
	
	elif type=='VCARVE':
		
		angle=o.cutter_tip_angle
		s=math.tan(math.pi*(90-angle/2)/180)/2
		bpy.ops.mesh.primitive_cone_add(vertices=32, radius1=BULLET_SCALE*o.cutter_diameter/2, radius2=0, depth = BULLET_SCALE*o.cutter_diameter*s, end_fill_type='NGON', view_align=False, enter_editmode=False, location=(-100,-100, -100), rotation=(math.pi, 0, 0))
		bpy.ops.rigidbody.object_add(type='ACTIVE')
		cutter=bpy.context.active_object
		cutter.rigid_body.collision_shape = 'CONE'
	elif type=='CUSTOM':
		cutob=bpy.data.objects[o.cutter_object_name]
		activate(cutob)
		bpy.ops.object.duplicate()
		bpy.ops.rigidbody.object_add(type='ACTIVE')
		cutter=bpy.context.active_object
		scale=o.cutter_diameter/cutob.dimensions.x
		cutter.scale*=BULLET_SCALE*scale
		bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
		bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
		#print(cutter.dimensions,scale)
		bpy.ops.rigidbody.object_add(type='ACTIVE')
		cutter.rigid_body.collision_shape = 'CONVEX_HULL'
		cutter.location=(-100,-100,-100)
		
	cutter.name='cam_cutter'	
	o.cutter_shape=cutter
	return cutter

def subdivideLongEdges(ob, threshold):
	
	print('subdividing long edges')
	m=ob.data
	scale=(ob.scale.x+ob.scale.y+ob.scale.z)/3
	subdivides=[]
	n=1
	iter=0
	while n>0:
		n=0
		for i,e in enumerate(m.edges):
			v1=m.vertices[e.vertices[0]].co
			v2=m.vertices[e.vertices[1]].co
			vec=v2-v1
			l=vec.length
			if l*scale>threshold:
				n+=1
				subdivides.append(i)
		if n>0:
			print(len(subdivides))
			bpy.ops.object.editmode_toggle()
			

			#bpy.ops.mesh.quads_convert_to_tris(quad_method='BEAUTY', ngon_method='BEAUTY')
			#bpy.ops.mesh.tris_convert_to_quads()

			bpy.ops.mesh.select_all(action='DESELECT')
			bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')
			bpy.ops.object.editmode_toggle()
			for i in subdivides:
				m.edges[i].select=True
			bpy.ops.object.editmode_toggle()
			bpy.ops.mesh.subdivide(smoothness=0)
			if iter==0:
				bpy.ops.mesh.select_all(action='SELECT')
				bpy.ops.mesh.quads_convert_to_tris(quad_method='SHORTEST_DIAGONAL', ngon_method='BEAUTY')
			bpy.ops.mesh.select_all(action='DESELECT')
			bpy.ops.object.editmode_toggle()
			ob.update_from_editmode()
		iter+=1
		#n=0	
		#
		
def prepareBulletCollision(o):
	'''prepares all objects needed for sampling with bullet collision'''
	progress('preparing collisions')
	t=time.time()
	s=bpy.context.scene
	s.gravity=(0,0,0)
	#cleanup rigidbodies wrongly placed somewhere in the scene
	for ob in bpy.context.scene.objects:
		if ob.rigid_body != None and (bpy.data.groups.find('machine')>-1 and ob.name not in bpy.data.groups['machine'].objects):
			activate(ob)
			bpy.ops.rigidbody.object_remove()
			
	for collisionob in o.objects:
		activate(collisionob)
		bpy.ops.object.duplicate(linked=False)
		collisionob=bpy.context.active_object
		if collisionob.type=='CURVE' or collisionob.type=='FONT':#support for curve objects collision
			if collisionob.type=='CURVE':
				odata=collisionob.data.dimensions
				collisionob.data.dimensions='2D'
			bpy.ops.object.convert(target='MESH', keep_original=False)
		#subdivide long edges here:
		if o.exact_subdivide_edges:
			subdivideLongEdges(collisionob, o.cutter_diameter*2)
			
		bpy.ops.rigidbody.object_add(type='ACTIVE')#using active instead of passive because of performance.TODO: check if this works also with 4axis...
		collisionob.rigid_body.collision_shape = 'MESH'
		collisionob.rigid_body.kinematic=True#this fixed a serious bug and gave big speedup, rbs could move since they are now active...
		collisionob.rigid_body.collision_margin = o.skin*BULLET_SCALE
		bpy.ops.transform.resize(value=(BULLET_SCALE, BULLET_SCALE, BULLET_SCALE), constraint_axis=(False, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1, snap=False, snap_target='CLOSEST', snap_point=(0, 0, 0), snap_align=False, snap_normal=(0, 0, 0), texture_space=False, release_confirm=False)
		collisionob.location=collisionob.location*BULLET_SCALE
		bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
		
	getCutterBullet(o)
	
	#machine objects scaling up to simulation scale
	if bpy.data.groups.find('machine')>-1:
		for ob in bpy.data.groups['machine'].objects:
			activate(ob)
			bpy.ops.transform.resize(value=(BULLET_SCALE, BULLET_SCALE, BULLET_SCALE), constraint_axis=(False, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1, snap=False, snap_target='CLOSEST', snap_point=(0, 0, 0), snap_align=False, snap_normal=(0, 0, 0), texture_space=False, release_confirm=False)
			ob.location=ob.location*BULLET_SCALE
	#stepping simulation so that objects are up to date
	bpy.context.scene.frame_set(0)
	bpy.context.scene.frame_set(1)
	bpy.context.scene.frame_set(2)
	progress(time.time()-t)
	
	
def cleanupBulletCollision(o):
	if bpy.data.groups.find('machine')>-1:
		machinepresent=True
	else:
		machinepresent=False
	for ob in bpy.context.scene.objects:
		if ob.rigid_body != None and not (machinepresent and ob.name in bpy.data.groups['machine'].objects):
			delob(ob)
	#machine objects scaling up to simulation scale
	if machinepresent:
		for ob in bpy.data.groups['machine'].objects:
			activate(ob)
			bpy.ops.transform.resize(value=(1.0/BULLET_SCALE, 1.0/BULLET_SCALE, 1.0/BULLET_SCALE), constraint_axis=(False, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1, snap=False, snap_target='CLOSEST', snap_point=(0, 0, 0), snap_align=False, snap_normal=(0, 0, 0), texture_space=False, release_confirm=False)
			ob.location=ob.location/BULLET_SCALE

def getSampleBullet(cutter, x,y, radius, startz, endz):
	'''collision test for 3 axis milling. Is simplified compared to the full 3d test'''
	pos=bpy.context.scene.rigidbody_world.convex_sweep_test(cutter, (x*BULLET_SCALE, y*BULLET_SCALE, startz*BULLET_SCALE), (x*BULLET_SCALE, y*BULLET_SCALE, endz*BULLET_SCALE))
	
	#radius is subtracted because we are interested in cutter tip position, this gets collision object center
	
	if pos[3]==1:
		return (pos[0][2]-radius)/BULLET_SCALE
	else:
		return endz-10;
	
def getSampleBulletNAxis(cutter, startpoint,endpoint,rotation, cutter_compensation):
	'''fully 3d collision test for NAxis milling'''
	cutterVec=Vector((0,0,1))*cutter_compensation#cutter compensation vector - cutter physics object has center in the middle, while cam needs the tip position.
	cutterVec.rotate(Euler(rotation))
	#print(rotation)
	#print(cutterVec)
	#cutterVec=Vector((0,0,0))
	#cutterVec = startpoint-endpoint
	#cutterVec.normalize()
	#cutterVec*=cutter_compensation
	#cutterVec=Vector((0,0,0))
	start=(startpoint*BULLET_SCALE+cutterVec).to_tuple()
	end=((endpoint)*BULLET_SCALE+cutterVec).to_tuple()
	#cutter.rotation_euler=rotation
	pos=bpy.context.scene.rigidbody_world.convex_sweep_test(cutter, start, end)
	
	
	if pos[3]==1:
		pos=Vector(pos[0])
		#rescale and compensate from center to tip.
		
		res=pos/BULLET_SCALE-cutterVec/BULLET_SCALE
		#this is a debug loop that duplicates the cutter on sampling positions, to see where it was moving...
		#if random.random()<0.01:
		#	dupliob(cutter,res)
				
		return res
	else:
		return None;
