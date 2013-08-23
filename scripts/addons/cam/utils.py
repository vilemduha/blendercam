# blender CAM utils.py (c) 2012 Vilem Novak
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
import time
import mathutils
import math
from math import *
from mathutils import *
from bpy.props import *
import bl_operators
from bpy.types import Menu, Operator
from bpy_extras import object_utils
import curve_simplify
import bmesh
import Polygon
import Polygon.Utils as pUtils
import numpy
import random,sys, os
import pickle
import string
#from . import post_processors
#import multiprocessing 

BULLET_SCALE=1000 # this is a constant for scaling the rigidbody collision world for higher precision from bullet library

def activate(o):
	s=bpy.context.scene
	bpy.ops.object.select_all(action='DESELECT')
	o.select=True
	s.objects.active=o
	
def progress(text,n=None):
	#for i in range(n+1):
	#sys.stdout.flush()
	text=str(text)
	if n== None:
		n=''
	else:
		n=' ' + str(int(n*1000)/1000) + '%'
	#d=int(n/2)
	spaces=' '*(len(text)+55)
	sys.stdout.write('progress{%s%s}\n' % (text,n))
	sys.stdout.flush()
	#bpy.data.window_managers['WinMan'].progress_update(n)
	#if bpy.context.scene.o
	#bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
		#time.sleep(0.5)

def getCircle(r,z):
	car=numpy.array((0),dtype=float)
	res=2*r
	m=r
	car.resize(r*2,r*2)
	car.fill(-10)
	v=mathutils.Vector((0,0,0))
	for a in range(0,res):
		v.x=(a+0.5-m)
		for b in range(0,res):
			v.y=(b+0.5-m)
			if(v.length<=r):
				car[a,b]=z
	return car

def getCircleBinary(r):
	car=numpy.array((False),dtype=bool)
	res=2*r
	m=r
	car.resize(r*2,r*2)
	car.fill(False)
	v=mathutils.Vector((0,0,0))
	for a in range(0,res):
		v.x=(a+0.5-m)
		for b in range(0,res):
			v.y=(b+0.5-m)
			if(v.length<=r):
				car.itemset((a,b),True)
	return car
	
# get cutters for the z-buffer image method
def getCutterArray(operation,pixsize):
	type=operation.cutter_type
	#print('generating cutter')
	r=operation.cutter_diameter/2+operation.skin#/operation.pixsize
	res=ceil((r*2)/pixsize)
	#if res%2==0:#compensation for half-pixels issue, which wasn't an issue, so commented out
		#res+=1
		#m=res/2
	m=res/2.0
	car=numpy.array((0),dtype=float)
	car.resize(res,res)
	car.fill(-10)
	
	v=mathutils.Vector((0,0,0))
	ps=pixsize
	if type=='END':
		for a in range(0,res):
			v.x=(a+0.5-m)*ps
			for b in range(0,res):
				v.y=(b+0.5-m)*ps
				if(v.length<=r):
					car.itemset((a,b),0)
	elif type=='BALL':
		for a in range(0,res):
			v.x=(a+0.5-m)*ps
			for b in range(0,res):
				v.y=(b+0.5-m)*ps
				if(v.length<=r):
					z=sin(acos(v.length/r))*r-r
					car.itemset((a,b),z)#[a,b]=z
				
	elif type=='VCARVE' :
		angle=operation.cutter_tip_angle 
		s=math.tan(math.pi*(90-angle/2)/180)
		for a in range(0,res):
			v.x=(a+0.5-m)*ps
			for b in range(0,res):
				v.y=(b+0.5-m)*ps
				if v.length<=r:
					z=(-v.length*s)
					car.itemset((a,b),z)
	return car
				
#cutter for rigidbody simulation collisions
#note that everything is 100x bigger for simulation precision.
def getCutterBullet(o):
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
	elif type=='BALL':
		bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, size=BULLET_SCALE*o.cutter_diameter/2, view_align=False, enter_editmode=False, location=(-100,-100, -100), rotation=(0, 0, 0))
		bpy.ops.rigidbody.object_add(type='ACTIVE')
		cutter=bpy.context.active_object
		cutter.rigid_body.collision_shape = 'SPHERE'
	elif type=='VCARVE':
		
		angle=o.cutter_tip_angle
		s=math.tan(math.pi*(90-angle/2)/180)/2
		bpy.ops.mesh.primitive_cone_add(vertices=32, radius1=BULLET_SCALE*o.cutter_diameter/2, radius2=0, depth = BULLET_SCALE*o.cutter_diameter*s, end_fill_type='NGON', view_align=False, enter_editmode=False, location=(-100,-100, -100), rotation=(math.pi, 0, 0))
		bpy.ops.rigidbody.object_add(type='ACTIVE')
		cutter=bpy.context.active_object
		cutter.rigid_body.collision_shape = 'CONE'
	cutter.name='cam_cutter'	
	o.cutter_shape=cutter
	return cutter

#prepares all objects needed for sampling with bullet collision
def prepareBulletCollision(o):
	progress('preparing collisions')
	t=time.time()
	s=bpy.context.scene
	s.gravity=(0,0,0)
	bpy.ops.object.select_all(action='SELECT')
	bpy.ops.rigidbody.objects_remove()
	for collisionob in o.objects:
		activate(collisionob)
		bpy.ops.object.duplicate(linked=False)
		if collisionob.type=='CURVE' or collisionob.type=='FONT':#support for curve objects collision
			bpy.ops.object.convert(target='MESH', keep_original=False)

		collisionob=bpy.context.active_object
		bpy.ops.rigidbody.object_add(type='ACTIVE')
		collisionob.rigid_body.collision_shape = 'MESH'
		collisionob.rigid_body.collision_margin = o.skin*BULLET_SCALE
		bpy.ops.transform.resize(value=(BULLET_SCALE, BULLET_SCALE, BULLET_SCALE), constraint_axis=(False, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1, snap=False, snap_target='CLOSEST', snap_point=(0, 0, 0), snap_align=False, snap_normal=(0, 0, 0), texture_space=False, release_confirm=False)
		collisionob.location=collisionob.location*BULLET_SCALE
		bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

	getCutterBullet(o)
	#stepping simulation so that objects are up to date
	bpy.context.scene.frame_set(0)
	bpy.context.scene.frame_set(1)
	bpy.context.scene.frame_set(2)
	progress(time.time()-t)
	
	
def cleanupBulletCollision(o):
	for ob in bpy.context.scene.objects:
		if ob.rigid_body != None:
			activate(ob)
			bpy.ops.rigidbody.object_remove()
			bpy.ops.object.delete(use_global=False)

def positionObject(operation):
	ob=bpy.data.objects[operation.object_name]
	minx,miny,minz,maxx,maxy,maxz=getBoundsWorldspace([ob])	
	ob.location.x-=minx
	ob.location.y-=miny
	ob.location.z-=maxz

def getBoundsWorldspace(obs):
	progress('getting bounds of object(s)')
	t=time.time()
		
	maxx=maxy=maxz=-10000000
	minx=miny=minz=10000000
	for ob in obs:
		bb=ob.bound_box
		mw=ob.matrix_world
		if ob.type=='MESH':
			for c in ob.data.vertices:
				coord=c.co
				worldCoord = mw * Vector((coord[0], coord[1], coord[2]))
				minx=min(minx,worldCoord.x)
				miny=min(miny,worldCoord.y)
				minz=min(minz,worldCoord.z)
				maxx=max(maxx,worldCoord.x)
				maxy=max(maxy,worldCoord.y)
				maxz=max(maxz,worldCoord.z)
		else:
			for coord in bb:
				worldCoord = mw * Vector((coord[0], coord[1], coord[2]))
				minx=min(minx,worldCoord.x)
				miny=min(miny,worldCoord.y)
				minz=min(minz,worldCoord.z)
				maxx=max(maxx,worldCoord.x)
				maxy=max(maxy,worldCoord.y)
				maxz=max(maxz,worldCoord.z)
	progress(time.time()-t)
	return minx,miny,minz,maxx,maxy,maxz
 
def getBounds(o):
	if o.geometry_source=='OBJECT' or o.geometry_source=='GROUP':
		if o.material_from_model:
			minx,miny,minz,maxx,maxy,maxz=getBoundsWorldspace(o.objects)

			o.min.x=minx-o.material_radius_around_model
			o.min.y=miny-o.material_radius_around_model
			o.max.z=maxz
				
			if o.minz_from_ob:
					o.min.z=minz
					o.minz=o.min.z
			else:
				o.min.z=o.minz#max(bb[0][2]+l.z,o.minz)#
			
			o.max.x=maxx+o.material_radius_around_model
			o.max.y=maxy+o.material_radius_around_model
		else:
			o.min.x=o.material_origin.x
			o.min.y=o.material_origin.y
			o.min.z=o.material_origin.z-o.material_size.z
			o.max.x=o.min.x+o.material_size.x
			o.max.y=o.min.y+o.material_size.y
			o.max.z=o.material_origin.z
		
			
	else:
		i=bpy.data.images[o.source_image_name]
		sx=int(i.size[0]*o.source_image_crop_start_x/100)
		ex=int(i.size[0]*o.source_image_crop_end_x/100)
		sy=int(i.size[1]*o.source_image_crop_start_y/100)
		ey=int(i.size[1]*o.source_image_crop_end_y/100)
		#operation.image.resize(ex-sx,ey-sy)
		crop=(sx,sy,ex,ey)
		
		o.pixsize=o.source_image_size_x/i.size[0]
		
		o.min.x=o.source_image_offset.x+(sx)*o.pixsize
		o.max.x=o.source_image_offset.x+(ex)*o.pixsize
		o.min.y=o.source_image_offset.y+(sy)*o.pixsize
		o.max.y=o.source_image_offset.y+(ey)*o.pixsize
		o.min.z=o.source_image_offset.z+o.minz
		o.max.z=o.source_image_offset.z
	s=bpy.context.scene
	m=s.cam_machine[0]
	if o.max.x-o.min.x>m.working_area.x or o.max.y-o.min.y>m.working_area.y or o.max.z-o.min.z>m.working_area.z:
		#o.max.x=min(o.min.x+m.working_area.x,o.max.x)
		#o.max.y=min(o.min.y+m.working_area.y,o.max.y)
		#o.max.z=min(o.min.z+m.working_area.z,o.max.z)
		o.warnings+='Operation exceeds your machine limits'
		
	#progress (o.min.x,o.min.y,o.min.z,o.max.x,o.max.y,o.max.z)

def getPathPatternParallel(o,angle):
	#minx,miny,minz,maxx,maxy,maxz=o.min.x,o.min.y,o.min.z,o.max.x,o.max.y,o.max.z
	ob=o.object
	zlevel=1
	pathd=o.dist_between_paths
	pathstep=o.dist_along_paths
	pathchunks=[]
	#progress(o.max.x,stepx)
	#progress(o.max.y,stepy)
	
	#angle=(angle/360)*2*math.pi
	xm=(o.max.x+o.min.x)/2
	ym=(o.max.y+o.min.y)/2
	vm=Vector((xm,ym,0))
	xdim=o.max.x-o.min.x
	ydim=o.max.y-o.min.y
	dim=(xdim+ydim)/2.0
	e=Euler((0,0,angle))
	v=Vector((1,0,0))
	reverse=False
	#if o.movement_type=='CONVENTIONAL'
	#ar=numpy.array((1.1,1.1))
	#ar.resize()
	#if bpy.app.debug_value==0:
	for a in range(int(-dim/pathd), int(dim/pathd)):#this is highly ineffective, computes path2x the area needed...
		chunk=camPathChunk([])
		for b in range(int(-dim/pathstep),int(dim/pathstep)):
			v.x=a*pathd
			v.y=b*pathstep
			
			v.rotate(e)
			v+=vm#shifting for the rotation, so pattern rotates around middle...
			if v.x>o.min.x and v.x<o.max.x and v.y>o.min.y and v.y<o.max.y:
				chunk.points.append((v.x,v.y,zlevel))
		if (reverse and o.movement_type=='MEANDER') or (o.movement_type=='CONVENTIONAL' and o.spindle_rotation_direction=='CW') or (o.movement_type=='CLIMB' and o.spindle_rotation_direction=='CCW') :
			chunk.points.reverse()
			
				
		#elif	 
		if len(chunk.points)>0:
			pathchunks.append(chunk)
		if len(pathchunks)>1 and reverse and o.parallel_step_back:
			#if (o.parallel_step_back and o.movement_type=='MEANDER') or ( o.movement_type=='CLIMB' and o.spindle_rotation_direction=='CW' and  not reverse )or (o.movement_type=='CONVENTIONAL' and o.spindle_rotation_direction=='CCW' and  reverse):
				
			if o.movement_type=='CONVENTIONAL' or o.movement_type=='CLIMB':
				pathchunks[-2].points.reverse()
			pathchunks[-1].points.extend(pathchunks[-2].points)
			pathchunks.pop(-2)
			#pathchunks[-1]=pathchunks[-2]
			#=changechunk
					
		reverse = not reverse
	
	#else:
		'''
		v=Vector((1,0,0))
		v.rotate(e)
		a1res=int(dim/pathd)-int(-dim/pathd)
		a2res=int(dim/pathstep)-int(-dim/pathstep)
		
		axis_across_paths=numpy.array((numpy.arange(int(-dim/pathd), int(dim/pathd))*pathd*v.y+xm,
													numpy.arange(int(-dim/pathd), int(dim/pathd))*pathd*v.x+ym,
													numpy.arange(int(-dim/pathd), int(dim/pathd))*0))
		#axis_across_paths=axis_across_paths.swapaxes(0,1)
		#progress(axis_across_paths)
		
		axis_along_paths=numpy.array((numpy.arange(int(-dim/pathstep),int(dim/pathstep))*pathstep*v.x,
												numpy.arange(int(-dim/pathstep),int(dim/pathstep))*pathstep*v.y,
												numpy.arange(int(-dim/pathstep),int(dim/pathstep))*0+zlevel))#rotate this first
		progress(axis_along_paths)
		#axis_along_paths = axis_along_paths.swapaxes(0,1)
		#progress(axis_along_paths)
		
		chunks=numpy.array((1.0))
		chunks.resize(3,a1res,a2res)

		for a in range(0,len(axis_across_paths[0])):
			#progress(chunks[a,...,...].shape)
			#progress(axis_along_paths.shape)
			nax=axis_along_paths.copy()
			#progress(nax.shape)
			nax[0]+=axis_across_paths[0][a]
			nax[1]+=axis_across_paths[1][a]
			#progress(a)
			#progress(nax.shape)
			#progress(chunks.shape)
			#progress(chunks[...,a,...].shape)
			chunks[...,a,...]=nax
		'''	
		''' 
		for a in range(0,a1res):
			chunks[a,...,1]=axis2
		
		for a in range(0,a1res):
			for b in range(0,a2res):
				v.x=chunks.item(a,b,0)
				v.y=chunks.item(a,b,1)
				v.rotate(e)
				v.x+=xm
				v.y+=ym
				if v.x>o.min.x and v.x<o.max.x and v.y>o.min.y and v.y<o.max.y:
					chunks.itemset(a,b,0,v.x)
					chunks.itemset(a,b,1,v.y)
				else:
					chunks.itemset(a,b,0,-10)
					chunks.itemset(a,b,1,-10)
					chunks.itemset(a,b,2,-10)
		
				
		chunks[...,...,2]=zlevel
		
		pathchunks=chunks 
		'''
		
	return pathchunks 

def getPathPattern(operation):
	o=operation
	t=time.time()
	progress('building path pattern')
	minx,miny,minz,maxx,maxy,maxz=o.min.x,o.min.y,o.min.z,o.max.x,o.max.y,o.max.z
	
	pathchunks=[]
	
	zlevel=1#minz#this should do layers...
	if o.strategy=='PARALLEL':
		pathchunks= getPathPatternParallel(o,o.parallel_angle)
	elif o.strategy=='CROSS':
		
		pathchunks.extend(getPathPatternParallel(o,o.parallel_angle))
		pathchunks.extend(getPathPatternParallel(o,o.parallel_angle-math.pi/2.0))
			
	elif o.strategy=='BLOCK':
		
		pathd=o.dist_between_paths
		pathstep=o.dist_along_paths
		maxxp=maxx
		maxyp=maxy
		minxp=minx
		minyp=miny
		x=0.0
		y=0.0
		incx=1
		incy=0
		chunk=camPathChunk([])
		i=0
		while maxxp-minxp>0 and maxyp-minyp>0:
			
			y=minyp
			for a in range(ceil(minxp/pathstep),ceil(maxxp/pathstep),1):
				x=a*pathstep
				chunk.points.append((x,y,zlevel))
				
			if i>0:
				minxp+=pathd
			chunk.points.append((maxxp,minyp,zlevel))
				
				
			x=maxxp 
			
			for a in range(ceil(minyp/pathstep),ceil(maxyp/pathstep),1):
				
				y=a*pathstep
				chunk.points.append((x,y,zlevel))
				
			minyp+=pathd
			chunk.points.append((maxxp,maxyp,zlevel))
			
			 
			y=maxyp 
			for a in range(floor(maxxp/pathstep),ceil(minxp/pathstep),-1):
				x=a*pathstep
				chunk.points.append((x,y,zlevel))
			
			
			
			 
			maxxp-=pathd
			chunk.points.append((minxp,maxyp,zlevel)) 
			  
			x=minxp 
			for a in range(floor(maxyp/pathstep),ceil(minyp/pathstep),-1):
				y=a*pathstep
				chunk.points.append((x,y,zlevel))
			chunk.points.append((minxp,minyp,zlevel))
				
			
			maxyp-=pathd
			
			i+=1 
		if o.movement_insideout=='INSIDEOUT':
			chunk.points.reverse()
		if (o.movement_type=='CLIMB' and o.spindle_rotation_direction=='CW') or (o.movement_type=='CONVENTIONAL' and o.spindle_rotation_direction=='CCW'):
			for si in range(0,len(chunk.points)):
				s=chunk.points[si]
				chunk.points[si]=(o.max.x+o.min.x-s[0],s[1],s[2])
		#if insideout:
		#  chunk.reverse()
		pathchunks=[chunk]
	
	elif o.strategy=='SPIRAL':
		chunk=camPathChunk([])
		pathd=o.dist_between_paths
		pathstep=o.dist_along_paths
		midx=(o.max.x+o.min.x)/2
		midy=(o.max.y+o.min.y)/2
		x=pathd/4
		y=pathd/4
		v=Vector((pathd/4,0,0))
		
		#progress(x,y,midx,midy)
		e=Euler((0,0,0))
		pi=math.pi 
		chunk.points.append((midx+v.x,midy+v.y,zlevel))
		while midx+v.x>o.min.x or midy+v.y>o.min.y:
			#v.x=x-midx
			#v.y=y-midy
			offset=2*v.length*pi
			e.z=2*pi*(pathstep/offset)
			v.rotate(e)
			
			v.length=(v.length+pathd/(offset/pathstep))
			#progress(v.x,v.y)
			if o.max.x>midx+v.x>o.min.x and o.max.y>midy+v.y>o.min.y:
				chunk.points.append((midx+v.x,midy+v.y,zlevel))
			else:
				pathchunks.append(chunk)
				chunk=camPathChunk([])
		if len(chunk.points)>0:
			pathchunks.append(chunk)
		if o.movement_insideout=='OUTSIDEIN':
			pathchunks.reverse()
		for chunk in pathchunks:
			if o.movement_insideout=='OUTSIDEIN':
				chunk.points.reverse()
				
			if (o.movement_type=='CONVENTIONAL' and o.spindle_rotation_direction=='CW') or (o.movement_type=='CLIMB' and o.spindle_rotation_direction=='CCW'):
				for si in range(0,len(chunk.points)):
					s=chunk.points[si]
					chunk.points[si]=(o.max.x+o.min.x-s[0],s[1],s[2])
		
	
	elif o.strategy=='CIRCLES':
		
		pathd=o.dist_between_paths
		pathstep=o.dist_along_paths
		midx=(o.max.x+o.min.x)/2
		midy=(o.max.y+o.min.y)/2
		rx=o.max.x-o.min.x
		ry=o.max.y-o.min.y
		maxr=math.sqrt(rx*rx+ry*ry)
		#x=pathd/4
		#y=pathd/4
		v=Vector((1,0,0))
		
		#progress(x,y,midx,midy)
		e=Euler((0,0,0))
		pi=math.pi 
		chunk=camPathChunk([])
		chunk.points.append((midx,midy,zlevel))
		pathchunks.append(chunk)
		r=0
		
		while r<maxr:
			#v.x=x-midx
			#v.y=y-midy
			r+=pathd
			chunk=camPathChunk([])
			firstchunk=chunk
			v=Vector((-r,0,0))
			steps=2*pi*r/pathstep
			e.z=2*pi/steps
			for a in range(0,int(steps)):
				
				
				if o.max.x>midx+v.x>o.min.x and o.max.y>midy+v.y>o.min.y:
					chunk.points.append((midx+v.x,midy+v.y,zlevel))
				else:
					if len(chunk.points)>0:
						pathchunks.append(chunk)
						chunk=camPathChunk([])
				v.rotate(e)
			
			
			if len(chunk.points)>0:
				chunk.points.append(firstchunk.points[0])
				pathchunks.append(chunk)
				chunk=camPathChunk([])
		if o.movement_insideout=='OUTSIDEIN':
			pathchunks.reverse()
		for chunk in pathchunks:
			if o.movement_insideout=='OUTSIDEIN':
				chunk.points.reverse()
			if (o.movement_type=='CONVENTIONAL' and o.spindle_rotation_direction=='CW') or (o.movement_type=='CLIMB' and o.spindle_rotation_direction=='CCW'):
				chunk.points.reverse()
				#for si in range(0,len(chunk.points)):
					#s=chunk.points[si]
					#chunk.points[si]=(o.max.x+o.min.x-s[0],s[1],s[2])
		#pathchunks=sortChunks(pathchunks,o)not until they get hierarchy parents!
	elif o.strategy=='OUTLINEFILL':
		
		
		polys=getObjectSilhouette(o)
		pathchunks=[]
		chunks=[]
		for p in polys:
			chunks.extend(polyToChunks(p,0))
		
		pathchunks.extend(chunks)
		lastchunks=chunks
		firstchunks=chunks
		
		#for ch in chunks:
		#	if len(ch.points)>2:
		#		polys.extend()
				
		approxn=(min(maxx-minx,maxy-miny)/o.dist_between_paths)/2
		i=0
		
		for porig in polys:
			p=porig
			while p.nPoints()>0:
				p=outlinePoly(p,o.dist_between_paths,o,False)
				if p.nPoints()>0:
					nchunks=polyToChunks(p,zlevel)
					#parentChildPoly(lastchunks,nchunks,o)
					pathchunks.extend(nchunks)
					lastchunks=nchunks
				percent=int(i/approxn*100)
				progress('outlining polygons ',percent) 
				i+=1
		if not(o.inverse):#dont do ambient for inverse milling
			lastchunks=firstchunks
			for p in polys:
				d=o.dist_between_paths
				steps=o.ambient_radius/o.dist_between_paths
				for a in range(0,int(steps)):
					dist=d
					if a==int(o.cutter_diameter/2/o.dist_between_paths):
						if o.use_exact:
							dist+=o.pixsize*0.85# this is here only because silhouette is still done with zbuffer method, even if we use bullet collisions.
						else:
							dist+=o.pixsize*2.5
					p=outlinePoly(p,dist,o,True)
					if p.nPoints()>0:
						chunks=polyToChunks(p,zlevel)
						pathchunks.extend(chunks)
					lastchunks=chunks
				
		if (o.movement_type=='CLIMB' and o.spindle_rotation_direction=='CW') or (o.movement_type=='CONVENTIONAL' and o.spindle_rotation_direction=='CCW'):
			for ch in pathchunks:
				ch.points.reverse()
		parentChildPoly(pathchunks,pathchunks,o)	
		pathchunks=sortChunks(pathchunks,o)
		pathchunks=chunksRefine(pathchunks,o)
	progress(time.time()-t)
	return pathchunks

def getCachePath(o):
	fn=bpy.data.filepath
	l=len(bpy.path.basename(fn))
	bn=bpy.path.basename(fn)[:-6]
	
	
	iname=fn[:-l]+'temp_cam'+os.sep+bn+'_'+o.name
	return iname
	
#this basically renders blender zbuffer and makes it accessible by saving & loading it again.
#that's because blender doesn't allow accessing pixels in render :(
def renderSampleImage(o):
	t=time.time()
	progress('getting zbuffer')
	
	
	if o.geometry_source=='OBJECT' or o.geometry_source=='GROUP':
		pixsize=o.pixsize

		sx=o.max.x-o.min.x
		sy=o.max.y-o.min.y
	
		resx=ceil(sx/o.pixsize)+2*o.borderwidth
		resy=ceil(sy/o.pixsize)+2*o.borderwidth
		
		####setup image name
		#fn=bpy.data.filepath
		#iname=bpy.path.abspath(fn)
		#l=len(bpy.path.basename(fn))
		iname=getCachePath(o)+'_z.exr'
		if not o.update_zbufferimage_tag:
			try:
				i=bpy.data.images.load(iname)
			except:
				o.update_zbufferimage_tag=True
		if o.update_zbufferimage_tag:
			s=bpy.context.scene
		
			#prepare nodes first
			s.use_nodes=True
			n=s.node_tree
			
			n.links.clear()
			n.nodes.clear()
			n1=n.nodes.new('CompositorNodeRLayers')
			n2=n.nodes.new('CompositorNodeViewer')
			n3=n.nodes.new('CompositorNodeComposite')
			n.links.new(n1.outputs['Z'],n2.inputs['Image'])
			n.links.new(n1.outputs['Z'],n3.inputs['Image']) 
			n.nodes.active=n2
			###################
				
			r=s.render
			r.resolution_x=resx
			r.resolution_y=resy
			
			#resize operation image
			o.offset_image.resize((resx,resy))
			o.offset_image.fill(-10)
			
			#various settings for  faster render
			r.tile_x=1024#ceil(resx/1024)
			r.tile_y=1024#ceil(resy/1024)
			r.resolution_percentage=100
			
			r.engine='BLENDER_RENDER'
			r.use_antialiasing=False
			r.use_raytrace=False
			r.use_shadows=False
			ff=r.image_settings.file_format
			cm=r.image_settings.color_mode
			r.image_settings.file_format='OPEN_EXR'
			r.image_settings.color_mode='BW'
			r.image_settings.color_depth='32'
			
			#camera settings
			camera=s.camera
			if camera==None:
				bpy.ops.object.camera_add(view_align=False, enter_editmode=False, location=(0,0,0), rotation=(0,0,0))
				camera=bpy.context.active_object
				bpy.context.scene.camera=camera
				#bpy.ops.view3d.object_as_camera()

			camera.data.type='ORTHO'
			camera.data.ortho_scale=max(resx*o.pixsize,resy*o.pixsize)
			camera.location=(o.min.x+sx/2,o.min.y+sy/2,1)
			camera.rotation_euler=(0,0,0)
			#if not o.render_all:#removed in 0.3
			
			h=[]
			
			#ob=bpy.data.objects[o.object_name]
			for ob in s.objects:
				h.append(ob.hide_render)
				ob.hide_render=True
			for ob in o.objects:
				ob.hide_render=False
			 
			bpy.ops.render.render()
			
			#if not o.render_all:
			for id,obs in enumerate(s.objects):
				obs.hide_render=h[id]
			
				
			imgs=bpy.data.images
			for isearch in imgs:
				if len(isearch.name)>=13:
					if isearch.name[:13]=='Render Result':
						i=isearch
						
						
						#progress(iname)
						i.save_render(iname)
						
			
			r.image_settings.file_format=ff 		
			r.image_settings.color_mode=cm
		
			i=bpy.data.images.load(iname)
		a=imagetonumpy(i)
		a=1.0-a
		o.zbuffer_image=a
		o.update_zbufferimage_tag=False
		
	else:
		i=bpy.data.images[o.source_image_name]
		sx=int(i.size[0]*o.source_image_crop_start_x/100)
		ex=int(i.size[0]*o.source_image_crop_end_x/100)
		sy=int(i.size[1]*o.source_image_crop_start_y/100)
		ey=int(i.size[1]*o.source_image_crop_end_y/100)
		o.offset_image.resize(ex-sx+2*o.borderwidth,ey-sy+2*o.borderwidth)
		
		
		
		o.pixsize=o.source_image_size_x/i.size[0]
		progress('pixel size in the image source', o.pixsize)
		
		rawimage=imagetonumpy(i)
		maxa=numpy.max(rawimage)
		a=numpy.array((1.0,1.0))
		a.resize(2*o.borderwidth+i.size[0],2*o.borderwidth+i.size[1])
		if o.strategy=='CUTOUT':#cutout strategy doesn't want to cut image border
			a.fill(0)
		else:#other operations want to avoid cutting anything outside image borders.
			a.fill(o.min.z)
		#2*o.borderwidth
		a[o.borderwidth:-o.borderwidth,o.borderwidth:-o.borderwidth]=rawimage
		a=a[sx:ex+o.borderwidth*2,sy:ey+o.borderwidth*2]
		
		a=(a-maxa)
		a*=o.source_image_scale_z
		o.minz=numpy.min(a)
		o.zbuffer_image=a
	#progress('got z buffer also with conversion in:')
	progress(time.time()-t)
	
	#progress(a)
	o.update_zbufferimage_tag=False
	return o.zbuffer_image
	#return numpy.array([])

def numpysave(a,iname):
	inamebase=bpy.path.basename(iname)

	i=numpytoimage(a,inamebase)
	
	r=bpy.context.scene.render
	
	r.image_settings.file_format='OPEN_EXR'
	r.image_settings.color_mode='BW'
	r.image_settings.color_depth='32'
	
	i.save_render(iname)

def numpytoimage(a,iname):
	progress('numpy to image')
	t=time.time()
	progress(a.shape[0],a.shape[1])
	bpy.ops.image.new(name=iname, width=a.shape[0], height=a.shape[1], color=(0, 0, 0, 1), alpha=True, generated_type='BLANK', float=True)
	for image in bpy.data.images:
		
		if image.name[:len(iname)]==iname and image.size[0]==a.shape[0] and image.size[1]==a.shape[1]:
			i=image
			
	d=a.shape[0]*a.shape[1]
	a=a.swapaxes(0,1)
	a=a.reshape(d)
	a=a.repeat(4)
	i.pixels=a
	progress(time.time()-t)
	
	return i

def imagetonumpy(i):
	t=time.time()
	progress('imagetonumpy')
	inc=0
	
	width=i.size[0]
	height=i.size[1]
	x=0
	y=0
	count=0
	na=numpy.array((0.1),dtype=float)
	if bpy.app.debug_value==5:
		size=width*height
		na.resize(size*4)
		
		id=0
		
		for id,v in enumerate(i.pixels):
			#na.itemset(id,v)
			na[id]=v
			#id+=1
		#na=na.reshape(size,4)
		#na=na.swapaxes(0,1)
		#progress(na)
		#na=na[0]
		#progress(na)
		na=na.reshape(width,height,4)
		na=na[...,1]
		#na=na.reshape(width,height)
		#na=na.swapaxes(0,1)
		
	else:
		na.resize(width,height)
		#na=numpy.array(i.pixels)
		percent=0
		id=0
		#progress(len(i.pixels))
		#progress
		for v in i.pixels:
			if inc==0:
				if x==width:
					x=0
					y+=1
					#if int(y/height*100)>percent:
						#percent=int(y/height*100)
						#progress('zbuffer conversion',percent)
				na[x,y]=v
				#na.itemset(x,y,v)
				x+=1
			inc+=1;
			if inc==4:
				inc=0
		
	progress('\ntime '+str(time.time()-t))
	
	return na

def offsetArea(o,samples):
	if o.update_offsetimage_tag:
		minx,miny,minz,maxx,maxy,maxz=o.min.x,o.min.y,o.min.z,o.max.x,o.max.y,o.max.z
		o.offset_image.fill(-10)
		
		sourceArray=samples
		cutterArray=getCutterArray(o,o.pixsize)
		
		#progress('image size', sourceArray.shape)
		
		width=len(sourceArray)
		height=len(sourceArray[0])
		cwidth=len(cutterArray)
		
		t=time.time()
	
		m=int(cwidth/2.0)
		
		
		
		if o.inverse:
			sourceArray=-sourceArray+minz
			
		compare=o.offset_image[m: width-cwidth+m, m:height-cwidth+m]
		#i=0  
		for x in range(0,cwidth):#cwidth):
			text="Offsetting depth "+str(int(x*100/cwidth))
			#o.operator.report({"INFO"}, text)
			progress('offset ',int(x*100/cwidth))
			for y in range(0,cwidth):
				if cutterArray[x,y]>-10:
					#i+=1
					#progress(i)
					compare=numpy.maximum(sourceArray[  x : width-cwidth+x ,y : height-cwidth+y]+cutterArray[x,y],compare)
		
		o.offset_image[m: width-cwidth+m, m:height-cwidth+m]=compare
		#progress('offseting done')
		
		progress('\ntime '+str(time.time()-t))
		
		o.update_offsetimage_tag=False
		#progress('doing offsetimage')
		#numpytoimage(o.offset_image,o)
	return o.offset_image

def outlineImageBinary(o,radius,i,offset):
	t=time.time()
	progress('outline image')
	r=ceil(radius/o.pixsize)
	c=getCircleBinary(r)
	w=len(i)
	h=len(i[0])
	oar=i.copy()
	#oar.fill(-10000000)
	
	ar = i[:,:-1] != i[:,1:] 
	indices1=ar.nonzero()
	if offset:
		dofunc=numpy.logical_or
	else:
		c=numpy.logical_not(c)
		dofunc=numpy.logical_and
	w=i.shape[0]
	h=i.shape[1]
	for id in range(0,len(indices1[0])):
		a=indices1[0].item(id)
		b=indices1[1].item(id)
		if a>r and b>r and a<w-r and b<h-r:
			#progress(oar.shape,c.shape)
			oar[a-r:a+r,b-r:b+r]=dofunc(oar[a-r:a+r,b-r:b+r],c)
		
	ar=i[:-1,:]!=i[1:,:]
	indices2=ar.nonzero()
	for id in range(0,len(indices2[0])):
		a=indices2[0].item(id)
		b=indices2[1].item(id)
		if a>r and b>r and a<w-r and b<h-r:
			#progress(oar.shape,c.shape)
			oar[a-r:a+r,b-r:b+r]=dofunc(oar[a-r:a+r,b-r:b+r],c)
	progress(time.time()-t)
	return oar

def outlineImage(o,radius,i,minz):
	t=time.time()
	progress('outline image')
	r=ceil(radius/o.pixsize)
	c=getCircle(r,minz)
	w=len(i)
	h=len(i[0])
	oar=i.copy()
	#oar.fill(-10000000)
	for a in range(r,len(i)-1-r):
		for b in range(r,len(i[0])-1-r):
			p1=i[a,b]
			p2=i[a+1,b]
			p3=i[a,b+1]
			if p1<minz<p2 or p1>minz>p2 or p1<minz<p3 or p1>minz>p3:
				oar[a-r:a+r,b-r:b+r]=numpy.maximum(oar[a-r:a+r,b-r:b+r],c)
	progress(time.time()-t)
	return oar

def dilateAr(ar,cycles):
	for c in range(cycles):
		ar[1:-1,:]=numpy.logical_or(ar[1:-1,:],ar[:-2,:] )
		#ar[1:-1,:]=numpy.logical_or(ar[1:-1,:],ar[2:,:] )
		ar[:,1:-1]=numpy.logical_or(ar[:,1:-1],ar[:,:-2] )
		#ar[:,1:-1]=numpy.logical_or(ar[:,1:-1],ar[:,2:] )
		
def getImageCorners(o,i):#for pencil operation mainly
	#i=numpy.logical_xor(lastislice , islice)
	progress('detect corners in the offset image')
	vertical=i[:-2,1:-1]-i[1:-1,1:-1]-o.pencil_threshold> i[1:-1,1:-1]-i[2:,1:-1]
	horizontal=i[1:-1,:-2]-i[1:-1,1:-1]-o.pencil_threshold> i[1:-1,1:-1]-i[1:-1,2:]
	#if bpy.app.debug_value==2:
	
	ar=numpy.logical_or(vertical,horizontal)
	#dilateAr(ar,1)
	
	#chunks=imageToChunks(o,ar)
	chunks=imageToChunks(o,ar)
	for ch in chunks:#convert 2d chunks to 3d
		for i,p in enumerate(ch.points):
				ch.points[i]=(p[0],p[1],0)
	
	chunks=chunksRefine(chunks,o)
	
	
	for chi in range(len(chunks)-1,-1,-1):
		chunk=chunks[chi]
		for si in range(len(chunk.points)-1,-1,-1):
			if not(o.min.x<chunk.points[si][0]<o.max.x and o.min.y<chunk.points[si][1]<o.max.y):
				chunk.points.pop(si)
		if len(chunk.points)<2:
			chunks.pop(chi)
	
	#progress(len(polys))
	#progress(polys[0])
	return chunks

def imageToChunks(o,image):
	t=time.time()
	minx,miny,minz,maxx,maxy,maxz=o.min.x,o.min.y,o.min.z,o.max.x,o.max.y,o.max.z
	pixsize=o.pixsize
	
	#progress('detecting outline')
	edges=[]
	ar = image[:,:-1]-image[:,1:] 
	
	indices1=ar.nonzero()
	
	r=o.borderwidth# to prevent outline of the border was 3 before and also (o.cutter_diameter/2)/pixsize+o.borderwidth
	w=image.shape[0]
	h=image.shape[1]
	coef=0.75#compensates for imprecisions
	for id in range(0,len(indices1[0])):
		a=indices1[0][id]
		b=indices1[1][id]
		if r<a<w-r and r<b<h-r:
			edges.append(((a-1,b),(a,b)))
					
	ar=image[:-1,:]-image[1:,:]
	indices2=ar.nonzero()
	for id in range(0,len(indices2[0])):
		a=indices2[0][id]
		b=indices2[1][id]
		if r<a<w-r and r<b<h-r:
			edges.append(((a,b-1),(a,b)))
	
	i=0 
	chi=0
	
	polychunks=[]
	#progress(len(edges))
	
	d={}
	for e in edges:
		d[e[0]]=[]
		d[e[1]]=[]
	for e in edges:
		
		verts1=d[e[0]]
		verts2=d[e[1]]
		verts1.append(e[1])
		verts2.append(e[0])
		
	#progress(time.time()-t)
	t=time.time()
	if len(edges)>0:
	
		ch=[edges[0][0],edges[0][1]]#first and his reference
		
		d[edges[0][0]].remove(edges[0][1])
		#d.pop(edges[0][0])
	
		i=0
		#verts=[123]
		specialcase=0
		closed=False
		#progress('condensing outline')
		while len(d)>0 and i<20000000:# and verts!=[]:  ####bacha na pripade krizku takzvane, kdy dva pixely na sebe uhlopricne jsou
			verts=d.get(ch[-1],[])
			closed=False
			#print(verts)
			
			if len(verts)<=1:# this will be good for not closed loops...some time
				closed=True
				if len(verts)==1:
					ch.append(verts[0])
					verts.remove(verts[0])
			elif len(verts)>=3:
					specialcase+=1
					#if specialcase>=2:
						#print('thisisit')
					v1=ch[-1]
					v2=ch[-2]
					white=image[v1[0],v1[1]]
					comesfromtop=v1[1]<v2[1]
					comesfrombottom=v1[1]>v2[1]
					comesfromleft=v1[0]>v2[0]
					comesfromright=v1[0]<v2[0]
					take=False
					for v in verts:
						if (v[0]==ch[-2][0] and v[1]==ch[-2][1]):
							pass;
							verts.remove(v)
						
						if not take:
							if (not white and comesfromtop)or ( white and comesfrombottom):#goes right
								if v1[0]+0.5<v[0]:
									take=True
							elif (not white and comesfrombottom)or ( white and comesfromtop):#goes left
								if v1[0]>v[0]+0.5:
									take=True
							elif (not white and comesfromleft)or ( white and comesfromright):#goes down
								if v1[1]>v[1]+0.5:
									take=True
							elif (not white and comesfromright)or ( white and comesfromleft):#goes up
								if v1[1]+0.5<v[1]:
									take=True
							if take:
								ch.append(v)
								verts.remove(v)
							#	break
							
			else:#here it has to be 2 always
				done=False
				for vi in range(len(verts)-1,-1,-1):
					if not done:
						v=verts[vi]
						if (v[0]==ch[-2][0] and v[1]==ch[-2][1]):
							pass
							verts.remove(v)
						else:
						
							ch.append(v)
							done=True
							verts.remove(v)
							if (v[0]==ch[0][0] and v[1]==ch[0][1]):# or len(verts)<=1:
								closed=True
								
			if closed:
				polychunks.append(ch)
				for si,s in enumerate(ch):
					#print(si)
					if si>0:#first one was popped 
						if d.get(s,None)!=None and len(d[s])==0:#this makes the case much less probable, but i think not impossible
							d.pop(s)
				if len(d)>0:
					newch=False
					while not newch:
						v1=d.popitem()
						if len(v1[1])>0:
							ch=[v1[0],v1[1][0]]
							newch=True
				
					
					#print(' la problema grandiosa')
			i+=1
			if i%10000==0:
				print(len(ch))
				#print(polychunks)
				print(i)
			
		#polychunks.append(ch)
		
		vecchunks=[]
		#p=Polygon.Polygon()
		
		for ch in polychunks:
			vecchunk=[]
			vecchunks.append(vecchunk)
			for i in range(0,len(ch)):
				ch[i]=((ch[i][0]+coef-o.borderwidth)*pixsize+minx,(ch[i][1]+coef-o.borderwidth)*pixsize+miny,0)
				vecchunk.append(Vector(ch[i]))
		t=time.time()
		#print('optimizing outline')
		
		#print('directsimplify')
		#p=Polygon.Polygon()
		soptions=['distance','distance',o.pixsize*1.25,5,o.pixsize*1.25]
		#soptions=['distance','distance',0.0,5,0,5,0]#o.pixsize*1.25,5,o.pixsize*1.25]
		#polychunks=[]
		nchunks=[]
		for i,ch in enumerate(vecchunks):
			
			s=curve_simplify.simplify_RDP(ch, soptions)
			#print(s)
			nch=camPathChunk([])
			for i in range(0,len(s)):
				nch.points.append((ch[s[i]].x,ch[s[i]].y))
				
			if len(nch.points)>2:
				#polychunks[i].points=nch
				nchunks.append(nch)
		#m=		
		
		return nchunks
	else:
		return []
	
def imageToPoly(o,i):
	polychunks=imageToChunks(o,i)
	polys=chunksToPolys(polychunks)
	
	#polys=orderPoly(polys)
	t=time.time()
	
	return polys#[polys]

def prepareArea(o):
	#if not o.use_exact:
	renderSampleImage(o)
	samples=o.zbuffer_image
	
	iname=getCachePath(o)+'_off.exr'

	if not o.update_offsetimage_tag:
		progress('loading offset image')
		try:
			o.offset_image=imagetonumpy(bpy.data.images.load(iname))
		except:
			o.update_offsetimage_tag=True;
		
	if o.update_offsetimage_tag:
		if o.inverse:
			samples=numpy.maximum(samples,o.min.z-0.00001)
		offsetArea(o,samples)
		if o.ambient_behaviour=='AROUND' and o.ambient_radius>0.0:#TODO: unify ambient generation into 1 function.
			r=o.ambient_radius+o.pixsize*2.5#+(o.cutter_diameter/2.0)
			progress('outline ambient')
			o.offset_image[:]=outlineImage(o,r,o.offset_image,o.minz)
			progress('ambient done')
		numpysave(o.offset_image,iname)
		
def getSampleImage(s,sarray,minz):
	
	x=s[0]
	y=s[1]
	if (x<0 or x>len(sarray)-1) or (y<0 or y>len(sarray[0])-1):
		return -10
		#return None;#(sarray[y,x] bugs
	else:
		#return(sarray[int(x),int(y)])
		minx=floor(x)
		maxx=ceil(x)
		if maxx==minx:
			maxx+=1
		miny=floor(y)
		maxy=ceil(y)
		if maxy==miny:
			maxy+=1
		
		'''
		s1a=sarray[minx,miny]#
		s2a=sarray[maxx,miny]
		s1b=sarray[minx,maxy]
		s2b=sarray[maxx,maxy]
		'''
		s1a=sarray.item(minx,miny)#
		s2a=sarray.item(maxx,miny)
		s1b=sarray.item(minx,maxy)
		s2b=sarray.item(maxx,maxy)
		
		#if s1a==minz and s2a==minz and s1b==minz and s2b==minz:
		#  return
		'''
		if min(s1a,s2a,s1b,s2b)<-10:
			#return -10
			if s1a<-10:
				s1a=s2a
			if s2a<-10:
				s2a=s1a
			if s1b<-10:
				s1b=s2b
			if s2b<-10:
				s2b=s1b
	
			sa=s1a*(maxx-x)+s2a*(x-minx)
			sb=s1b*(maxx-x)+s2b*(x-minx)
			if sa<-10:
				sa=sb
			if sb<-10:
				sb=sa
			z=sa*(maxy-y)+sb*(y-miny)
			return z
			
		else:
		''' 
		sa=s1a*(maxx-x)+s2a*(x-minx)
		sb=s1b*(maxx-x)+s2b*(x-minx)
		z=sa*(maxy-y)+sb*(y-miny)
		return z
def getSampleBullet(cutter, x,y, radius, startz, endz):
	pos=bpy.context.scene.rigidbody_world.convex_sweep_test(cutter, (x*BULLET_SCALE, y*BULLET_SCALE, startz*BULLET_SCALE), (x*BULLET_SCALE, y*BULLET_SCALE, endz*BULLET_SCALE))
	
	#radius is subtracted because we are interested in cutter tip position, this gets collision object center
	
	if pos[3]==1:
		return (pos[0][2]-radius)/BULLET_SCALE
	else:
		return endz-10;
	
def chunksRefine(chunks,o):
	for ch in chunks:
		#print('before',len(ch))
		newchunk=[]
		v2=Vector(ch.points[0])
		#print(ch.points)
		for s in ch.points:
			
			v1=Vector(s)
			#print(v1,v2)
			v=v1-v2
			
			#print(v.length,o.dist_along_paths)
			if v.length>o.dist_along_paths:
				d=v.length
				v.normalize()
				i=0
				vref=Vector((0,0,0))
				
				while vref.length<d:
					i+=1
					vref=v*o.dist_along_paths*i
					if vref.length<d:
						p=v2+vref
						
						newchunk.append((p.x,p.y,p.z))
					
					
			newchunk.append(s)	
			v2=v1
		#print('after',len(newchunk))
		ch.points=newchunk
			
	return chunks

def samplePathLow(o,ch1,ch2,dosample):
	minx,miny,minz,maxx,maxy,maxz=o.min.x,o.min.y,o.min.z,o.max.x,o.max.y,o.max.z
	v1=Vector(ch1.points[-1])
	v2=Vector(ch2.points[0])
	
	v=v2-v1
	d=v.length
	v.normalize()
	
	vref=Vector((0,0,0))
	bpath=camPathChunk([])
	i=0
	while vref.length<d:
		i+=1
		vref=v*o.dist_along_paths*i
		if vref.length<d:
			p=v1+vref
			bpath.points.append([p.x,p.y,p.z])
	#print('between path')
	#print(len(bpath))
	pixsize=o.pixsize
	if dosample:
		if o.use_exact:
			cutterdepth=o.cutter_shape.dimensions.z/2
			for p in bpath.points:
				z=getSampleBullet(o.cutter_shape, p[0],p[1], cutterdepth, 1, o.minz)
				
		else:
			for p in bpath.points:
				xs=(p[0]-minx)/pixsize+o.borderwidth+pixsize/2#-m
				ys=(p[1]-miny)/pixsize+o.borderwidth+pixsize/2#-m
				z=getSampleImage((xs,ys),o.offset_image,o.minz)+o.skin
				if z>p[2]:
					p[2]=z
	return bpath

def parentChildPoly(parents,children,o):
	#print(children)
	#print(parents)
	
	for parent in parents:
		#print(parent.poly)
		for child in children:
			#print(child.poly)
			if child!=parent and len(child.poly)>0:
				if parent.poly.isInside(child.poly[0][0][0],child.poly[0][0][1]):
					parent.children.append(child)
					child.parents.append(parent)

def parentChildDist(parents, children,o):
		for child in children:
			for parent in parents:
				isrelation=False
				if parent!=child:
					for v in child.points:
						for v1 in parent.points:
							dlim=o.dist_between_paths*2
							if (o.strategy=='PARALLEL' or o.strategy=='CROSS') and o.parallel_step_back:
								dlim=dlim*2
							if dist2d(v,v1)<dlim:
								isrelation=True
								break
						if isrelation:
							break
					if isrelation:
						parent.children.append(child)
						child.parents.append(parent)
						
def parentChild(parents, children, o):
	for child in children:
		for parent in parents:
				if parent!=child:
					parent.children.append(child)
					child.parents.append(parent)	

#def threadedSampling():
#samples in both modes now - image and bullet collision too.
def sampleChunks(o,pathSamples,layers):
	#
	minx,miny,minz,maxx,maxy,maxz=o.min.x,o.min.y,o.min.z,o.max.x,o.max.y,o.max.z
	
	if o.use_exact:#prepare collision world
		if o.update_bullet_collision_tag:
			prepareBulletCollision(o)
			#print('getting ambient')
			getAmbient(o)  
			o.update_bullet_collision_tag=False
		#print (o.ambient)
		cutter=o.cutter_shape
		cutterdepth=cutter.dimensions.z/2
	else:
		if o.strategy!='WATERLINE': # or prepare offset image, but not in some strategies.
			prepareArea(o)
		pixsize=o.pixsize
		res=ceil(o.cutter_diameter/o.pixsize)
		m=res/2
		
	t=time.time()
	#print('sampling paths')
	
	totlen=0;#total length of all chunks, to estimate sampling time.
	for ch in pathSamples:
		totlen+=len(ch.points)
	layerchunks=[]
	minz=o.minz
	layeractivechunks=[]
	lastrunchunks=[]
	
	for l in layers:
		layerchunks.append([])
		layeractivechunks.append(camPathChunk([]))
		lastrunchunks.append([])
			
	zinvert=0
	if o.inverse:
		ob=bpy.data.objects[o.object_name]
		zinvert=ob.location.z+maxz#ob.bound_box[6][2]
	
	n=0
	
	lastz=minz
	for patternchunk in pathSamples:
		thisrunchunks=[]
		for l in layers:
			thisrunchunks.append([])
		lastlayer=None
		currentlayer=None
		lastsample=None
		#threads_count=4
		
		#for t in range(0,threads):
			
		for s in patternchunk.points:
			if o.strategy!='WATERLINE' and n/200.0==int(n/200.0):
				progress('sampling paths ',int(100*n/totlen))
			n+=1
			x=s[0]
			y=s[1]
			maxz=minz
			
			sampled=False
			
			#higherlayer=0
			newsample=(0,0,1);
			
			####sampling
			if o.use_exact:
				#try to optimize this, wow that works!lets try more:
				if lastsample!=None:
					maxz=getSampleBullet(cutter, x,y, cutterdepth, 1, lastsample[2]-o.dist_along_paths)#first try to the last sample
					if maxz<minz-1:
						maxz=getSampleBullet(cutter, x,y, cutterdepth, lastsample[2]-o.dist_along_paths, minz)
				else:
					maxz=getSampleBullet(cutter, x,y, cutterdepth, 1, minz)
				if minz>maxz and (o.use_exact and o.ambient.isInside(x,y)):
					maxz=minz;
				#print(maxz)
				#here we have 
			else:
				xs=(x-minx)/pixsize+o.borderwidth+pixsize/2#-m
				ys=(y-miny)/pixsize+o.borderwidth+pixsize/2#-m
				#if o.inverse:
				#  maxz=layerstart
				maxz=getSampleImage((xs,ys),o.offset_image,minz)+o.skin
			################################
			#handling samples
			############################################
			if maxz>=minz or (o.use_exact and o.ambient.isInside(x,y)):
				sampled=True
				#maxz=max(minz,maxz)
				
			if sampled and (not o.inverse or (o.inverse)):
				newsample=(x,y,maxz)
					
			elif o.ambient_behaviour=='ALL' and not o.inverse:#handle ambient here
				newsample=(x,y,minz)
				
			for i,l in enumerate(layers):
				terminatechunk=False
				ch=layeractivechunks[i]
				#print(i,l)
				#print(l[1],l[0])
				if l[1]<=newsample[2]<=l[0]:
					lastlayer=currentlayer
					currentlayer=i
					if lastlayer!=None and currentlayer!=None and lastlayer!=currentlayer:# and lastsample[2]!=newsample[2]:#sampling for sorted paths in layers- to go to the border of the sampled layer at least...#TODO: - fix an ugly ugly bug here! goes down more than should...
						if currentlayer<lastlayer:
							growing=True
							r=range(currentlayer,lastlayer)
							spliti=1
						else:
							r=range(lastlayer,currentlayer)
							growing=False
							spliti=0
						#print(r)
						li=0
						for ls in r:
							splitz=layers[ls][1]
							#print(ls)
						
							v1=lastsample
							v2=newsample
							if o.protect_vertical:
								v1,v2=isVerticalLimit(v1,v2)
							v1=Vector(v1)
							v2=Vector(v2)
							#print(v1,v2)
							ratio=(splitz-v1.z)/(v2.z-v1.z)
							#print(ratio)
							betweensample=v1+(v2-v1)*ratio
							
							#ch.points.append(betweensample.to_tuple())
							
							if growing:
								if li>0:
									layeractivechunks[ls].points.insert(-1,betweensample.to_tuple())
								else:
									layeractivechunks[ls].points.append(betweensample.to_tuple())
								layeractivechunks[ls+1].points.append(betweensample.to_tuple())
							else:
								
								layeractivechunks[ls].points.insert(-1,betweensample.to_tuple())
								layeractivechunks[ls+1].points.insert(0,betweensample.to_tuple())
							li+=1
							#this chunk is terminated, and allready in layerchunks /
								
						#ch.points.append(betweensample.to_tuple())#
					ch.points.append(newsample)
				elif l[1]>newsample[2]:
					ch.points.append((newsample[0],newsample[1],l[1]))
				elif l[0]<newsample[2]:  #terminate chunk
					terminatechunk=True

				if terminatechunk:
					if len(ch.points)>0:
						if len(ch.points)>0: 
							layerchunks[i].append(ch)
							thisrunchunks[i].append(ch)
							layeractivechunks[i]=camPathChunk([])
			lastsample=newsample
				 
		#n+=1
					
		for i,l in enumerate(layers):
			ch=layeractivechunks[i]
			if len(ch.points)>0:  
				
				#if o.stay_low and len(layerchunks[i])>0:
				#	between=samplePathLow(o,layerchunks[i][-1],ch)#this should be moved after sort
				#	layerchunks[i][-1].points.extend(between)
				#	layerchunks[i][-1].points.extend(ch.points) 
				#else:  
					
				layerchunks[i].append(ch)
				thisrunchunks[i].append(ch)
				layeractivechunks[i]=camPathChunk([])
				#parenting: not for outlinefilll!!! also higly unoptimized
			if (o.strategy=='PARALLEL' or o.strategy=='CROSS'):
				parentChildDist(thisrunchunks[i], lastrunchunks[i],o)
				
			
		lastrunchunks=thisrunchunks
				
			#print(len(layerchunks[i]))
	progress('checking relations between paths')
	if (o.strategy=='PARALLEL' or o.strategy=='CROSS'):
		if len(layers)>1:# sorting help so that upper layers go first always
			for i in range(0,len(layers)-1):
				#print('layerstuff parenting')
				parentChild(layerchunks[i+1],layerchunks[i],o)
				
	chunks=[]
	for i,l in enumerate(layers):
		chunks.extend(layerchunks[i])
	return chunks  

def dist2d(v1,v2):
	return math.sqrt((v1[0]-v2[0])*(v1[0]-v2[0])+(v1[1]-v2[1])*(v1[1]-v2[1]))

def polyRemoveDoubles(p,o):
	
	#vecs=[]
	pnew=Polygon.Polygon()
	soptions=['distance','distance',0.0,5,o.optimize_threshold,5,o.optimize_threshold]
	for ci,c in enumerate(p):# in range(0,len(p)):
		
		veclist=[]
		for v in c:
			veclist.append(Vector((v[0],v[1])))
		#progress(len(veclist))
		s=curve_simplify.simplify_RDP(veclist, soptions)
		#progress(len(s))
		nc=[]
		for i in range(0,len(s)):
			nc.append(c[s[i]])
		
		if len(nc)>2:
			pnew.addContour(nc,p.isHole(ci))
			
		else:
			pnew.addContour(p[ci],p.isHole(ci))
	#progress(time.time()-t)
	return pnew
	
def polyToChunks(p,zlevel):#
	chunks=[]
	#p=sortContours(p)
	
	i=0
	for o in p:
		#progress(p[i])
		if p.nPoints(i)>2:
			chunk=camPathChunk([])
			chunk.poly=Polygon.Polygon(o)
			for v in o:
				#progress (v)
				chunk.points.append((v[0],v[1],zlevel))  
			
			chunk.points.append(chunk.points[0])#last point =first point
			chunk.closed=True
			chunks.append(chunk)
		i+=1
	chunks.reverse()#this is for smaller shapes first.
	#
	return chunks

def setChunksZ(chunks,z):
	newchunks=[]
	for ch in chunks:
		chunk=camPathChunk([])
		for i,s in enumerate(ch.points):
			chunk.points.append((s[0],s[1],z))
		newchunks.append(chunk)
	return newchunks
	
def setChunksZRamp(chunks,zstart,zend,o):
	newchunks=[]
	
	if o.use_layers:
		stepdown=o.stepdown
	else:
		stepdown=-o.min.z
	for ch in chunks:
		chunk=camPathChunk([])
		ch.getLength()
		ltraveled=0
		endpoint=None
		for i,s in enumerate(ch.points):
			
			if i>0:
				s2=ch.points[i-1]
				ltraveled+=dist2d(s,s2)
				ratio=ltraveled/ch.length
			else:
				ratio=0
			znew=zstart-stepdown*ratio
			if znew<=zend:
				
				ratio=((z-zend)/(z-znew))
				v1=Vector(chunk.points[-1])
				v2=Vector((s[0],s[1],znew))
				v=v1+ratio*(v2-v1)
				chunk.points.append((v.x,v.y,v.z))
						
				if zend == o.min.z and endpoint==None and ch.closed==True:
					endpoint=i+1
					if endpoint==len(ch.points):
						endpoint=0
					#print(endpoint,len(ch.points))
			#else:
			znew=max(znew,zend)
			chunk.points.append((s[0],s[1],znew))
			z=znew
			if endpoint!=None:
				break;
		if not o.use_layers:
			endpoint=0
		if endpoint!=None:#append final contour on the bottom z level
			i=endpoint
			started=False
			#print('finaliz')
			if i==len(ch.points):
					i=0
			while i!=endpoint or not started:
				started=True
				s=ch.points[i]
				chunk.points.append((s[0],s[1],zend))
				#print(i,endpoint)
				i+=1
				if i==len(ch.points):
					i=0
			if o.ramp_out:
				z=zend
				i=endpoint
				
				while z<0:
					if i==len(ch.points):
						i=0
					s1=ch.points[i]
					i2=i-1
					if i2<0: i2=len(ch.points)-1
					s2=ch.points[i2]
					l=dist2d(s1,s2)
					znew=z+tan(o.ramp_out_angle)*l
					if znew>0:
						ratio=(z/(z-znew))
						v1=Vector(chunk.points[-1])
						v2=Vector((s1[0],s1[1],znew))
						v=v1+ratio*(v2-v1)
						chunk.points.append((v.x,v.y,v.z))
						
					else:
						chunk.points.append((s1[0],s1[1],znew))
					z=znew
					i+=1
					
					
		newchunks.append(chunk)
	return newchunks
			
def chunkToPoly(chunk):
	pverts=[]
	
	for v in chunk.points:
		 
		pverts.append((v[0],v[1]))
	 
	p=Polygon.Polygon(pverts)
	return p

def compare(v1,v2,vmiddle,e):
	#e=0.0001
	v1=Vector(v1)
	v2=Vector(v2)
	vmiddle=Vector(vmiddle)
	vect1=v2-v1
	vect2=vmiddle-v1
	vect1.normalize()
	vect1*=vect2.length
	v=vect2-vect1
	if v.length<e:
		return True
	return False
'''
def compare(v1,v2,vmiddle,e):
	#e=0.0001
	v1=Vector(v1)
	v2=Vector(v2)
	vmiddle=Vector(vmiddle)
	vect1=v2-v1
	vect2=vmiddle-v1
	vect1.normalize()
	vect2.normalize()
	x1=int(vect1.x/e)
	y1=int(vect1.y/e)
	z1=int(vect1.z/e)
	x2=int(vect2.x/e)
	y2=int(vect2.y/e)
	z2=int(vect2.z/e)
	
	if x1==x2 and y1==y2 and z1==z2:
		return True
	return False
'''
def isVerticalLimit(v1,v2):
	z=abs(v1[2]-v2[2])
	verticality=0.05  
	if z>0:
		
		if abs(v1[0]-v2[0])/z<verticality and abs(v1[1]-v2[1])/z<verticality:

			if v1[2]>v2[2]:
				v1=(v2[0],v2[1],v1[2])
				return v1,v2
			else: 
				v2=(v1[0],v1[1],v2[2])
				return v1,v2
	return v1,v2
def optimizeChunk(chunk,operation):
	
	for vi in range(len(chunk)-2,0,-1):
		#vmiddle=Vector()
		#v1=Vector()
		#v2=Vector()
		if compare(chunk[vi-1],chunk[vi+1],chunk[vi],operation.optimize_threshold):

			chunk.pop(vi)
			#vi-=1
	#protect_vertical=True
	if operation.protect_vertical:#protect vertical surfaces
		#print('verticality test')
		
		
		for vi in range(len(chunk)-1,0,-1):
			v1=chunk[vi]
			v2=chunk[vi-1]
			v1c,v2c=isVerticalLimit(v1,v2)
			if v1c!=v1:
				chunk[vi]=v1
			elif v2c!=v2:
				chunk[vi-1]=v2
			
			
		#print(vcorrected)
	return chunk			

#def subcutter()

def doSimulation(name,operations):
	'''perform simulation of operations. '''
	o=operations[0]#initialization now happens from first operation, also for chains.
	
	
	sx=o.max.x-o.min.x
	sy=o.max.y-o.min.y

	resx=ceil(sx/o.simulation_detail)+2*o.borderwidth
	resy=ceil(sy/o.simulation_detail)+2*o.borderwidth

	si=numpy.array((0.1),dtype=float)
	si.resize(resx,resy)
	si.fill(0)
	
	for o in operations:
		verts=bpy.data.objects[o.path_object_name].data.vertices
		
		cutterArray=getCutterArray(o,o.simulation_detail)
		#cb=cutterArray<-1
		#cutterArray[cb]=1
		cutterArray=-cutterArray
		m=int(cutterArray.shape[0]/2)
		size=cutterArray.shape[0]
		print(si.shape)
		#for ch in chunks:
		lasts=verts[1].co
		l=len(verts)
		perc=-1
		vtotal=len(verts)
		for i,vert in enumerate(verts):
			if perc!=int(100*i/vtotal):
				perc=int(100*i/vtotal)
				progress('simulation',perc)
			#progress('simulation ',int(100*i/l))
			if i>0:
				s=vert.co
				v=s-lasts
				
				if v.length>o.simulation_detail:
					l=v.length
					
					v.length=o.simulation_detail
					while v.length<l:
						
						xs=(lasts.x+v.x-o.min.x)/o.simulation_detail+o.borderwidth+o.simulation_detail/2#-m
						ys=(lasts.y+v.y-o.min.y)/o.simulation_detail+o.borderwidth+o.simulation_detail/2#-m
						z=lasts.z+v.z
						if xs>m+1 and xs<si.shape[0]-m-1 and ys>m+1 and ys<si.shape[1]-m-1 :
							si[xs-m:xs-m+size,ys-m:ys-m+size]=numpy.minimum(si[xs-m:xs-m+size,ys-m:ys-m+size],cutterArray+z)
						v.length+=o.simulation_detail
			
				xs=(s.x-o.min.x)/o.simulation_detail+o.borderwidth+o.simulation_detail/2#-m
				ys=(s.y-o.min.y)/o.simulation_detail+o.borderwidth+o.simulation_detail/2#-m
				if xs>m+1 and xs<si.shape[0]-m-1 and ys>m+1 and ys<si.shape[1]-m-1 :
					si[xs-m:xs-m+size,ys-m:ys-m+size]=numpy.minimum(si[xs-m:xs-m+size,ys-m:ys-m+size],cutterArray+s.z)
					
				lasts=s
				
	o=operations[0]
	si=si[o.borderwidth:-o.borderwidth,o.borderwidth:-o.borderwidth]
	si+=-o.min.z
	oname='csim_'+name
	
	cp=getCachePath(o)[:-len(o.name)]+name
	iname=cp+'_sim.exr'#TODO: currently uses still operation path instead of chain path, in case a chain is simulated.
	inamebase=bpy.path.basename(iname)
	i=numpysave(si,iname)
		
	
	
	#if inamebase in bpy.data.images:
	#	i=bpy.data.images[inamebase]
	#	i.reload()
	#else:
	i=bpy.data.images.load(iname)

	if oname in bpy.data.objects:
		ob=bpy.data.objects[oname]
	else:
		bpy.ops.mesh.primitive_plane_add(view_align=False, enter_editmode=False, location=(0,0,0), rotation=(0, 0, 0))
		ob=bpy.context.active_object
		ob.name=oname
		
		bpy.ops.object.modifier_add(type='SUBSURF')
		ss=ob.modifiers[-1]
		ss.subdivision_type='SIMPLE'
		ss.levels=5
		ss.render_levels=6
		bpy.ops.object.modifier_add(type='SUBSURF')
		ss=ob.modifiers[-1]
		ss.subdivision_type='SIMPLE'
		ss.levels=3
		ss.render_levels=3
		bpy.ops.object.modifier_add(type='DISPLACE')
	
	ob.location=((o.max.x+o.min.x)/2,(o.max.y+o.min.y)/2,o.min.z)
	ob.scale.x=(o.max.x-o.min.x)/2
	ob.scale.y=(o.max.y-o.min.y)/2	
	disp=ob.modifiers[-1]
	disp.direction='Z'
	disp.texture_coords='LOCAL'
	disp.mid_level=0
	
	if oname in bpy.data.textures:
		t=bpy.data.textures[oname]
		
		t.type='IMAGE'
		disp.texture=t
		
		
		t.image=i
	else:
		bpy.ops.texture.new()
		for t in bpy.data.textures:
			if t.name=='Texture':
				t.type='IMAGE'
				t.name=oname
				t=t.type_recast()
				t.type='IMAGE'
				t.image=i
				disp.texture=t
	ob.hide_render=True
	

def chunksToMesh(chunks,o):
	##########convert sampled chunks to path, optimization of paths
	s=bpy.context.scene
	origin=(0,0,o.free_movement_height)  
	verts = [origin]
	#verts=[]
	progress('building paths from chunks')
	e=0.0001
	for chi in range(0,len(chunks)):
		ch=chunks[chi]
		ch=ch.points
		if o.optimize:
			ch=optimizeChunk(ch,o)
		
		#lift and drop
		
		if verts[-1][2]==o.free_movement_height:
			v=(ch[0][0],ch[0][1],o.free_movement_height)
			verts.append(v)
		
		verts.extend(ch)
		
		lift = True
		if chi<len(chunks)-1:
			#nextch=
			last=Vector(ch[-1])
			first=Vector(chunks[chi+1].points[0])
			vect=first-last
			if (o.strategy=='PARALLEL' or o.strategy=='CROSS') and vect.z==0 and vect.length<o.dist_between_paths*2.5:#case of neighbouring paths
				lift=False
			if abs(vect.x)<e and abs(vect.y)<e:#case of stepdown by cutting.
				lift=False
			
		if lift:
			v=(ch[-1][0],ch[-1][1],o.free_movement_height)
			verts.append(v)
			
	if o.use_exact:
		cleanupBulletCollision(o)
		
	edges=[]	
	for a in range(0,len(verts)-1):
		edges.append((a,a+1))
		
			
	
	#print(verts[1])
	#print(edges[1])  
	oname="cam_path_"+o.name
		
	mesh = bpy.data.meshes.new(oname)
	mesh.name=oname
	mesh.from_pydata(verts, edges, [])
	#if o.path!='' and o.path in s.objects:
	#  s.objects[oname].data=mesh
	#el
	if oname in s.objects:
		s.objects[oname].data=mesh
	else: 
		ob=object_utils.object_data_add(bpy.context, mesh, operator=None)
		
	ob=s.objects[mesh.name]
	ob.location=(0,0,0)
	o.path_object_name=oname
	verts=ob.data.vertices
	exportGcodePath(o.filename,[verts],[o])

	
def safeFileName(name):#for export gcode
	valid_chars = "-_.()%s%s" % (string.ascii_letters, string.digits)
	filename=''.join(c for c in name if c in valid_chars)
	return filename
	
	
def exportGcodePath(filename,vertslist,operations):
	'''exports gcode with the heeks cnc adopted library.'''
	#verts=[verts]
	#operations=[o]#this is preparation for actual chain exporting
	s=bpy.context.scene
	m=s.cam_machine[0]
	filename=bpy.data.filepath[:-len(bpy.path.basename(bpy.data.filepath))]+safeFileName(filename)
	
	from . import nc
	extension='.tap'
	if m.post_processor=='ISO':
		from .nc import iso as postprocessor
	if m.post_processor=='MACH3':
		from .nc import mach3 as postprocessor
	elif m.post_processor=='EMC':
		extension = '.ngc'
		from .nc import emc2b as postprocessor
	elif m.post_processor=='HM50':
		from .nc import hm50 as postprocessor
	elif m.post_processor=='HEIDENHAIN':
		extension='.H'
		from .nc import heiden as postprocessor
	elif m.post_processor=='TNC151':
		from .nc import tnc151 as postprocessor
	elif m.post_processor=='SIEGKX1':
		from .nc import siegkx1 as postprocessor
	elif m.post_processor=='CENTROID':
		from .nc import centroid1 as postprocessor
	elif m.post_processor=='ANILAM':
		from .nc import anilam_crusader_m as postprocessor
	c=postprocessor.Creator()
	filename+=extension
	c.file_open(filename)
	
	#unit system correction
	###############
	if s.unit_settings.system=='METRIC':
		c.metric()
		unitcorr=1000.0
	else:
		c.imperial()
		unitcorr=1/0.0254;
		
	#start program
	c.program_begin(0,filename)
	c.comment('G-code generated with BlenderCAM and NC library')
	#absolute coordinates
	c.absolute()
	#work-plane, by now always xy, 
	c.set_plane(0)
	c.flush_nc()

	for i,o in enumerate(operations):
		verts=vertslist[i]

		#spindle rpm and direction
		###############
		if o.spindle_rotation_direction=='CW':
			spdir_clockwise=True
		else:
			spdir_clockwise=False

		#write tool, not working yet probably 
		c.comment('Tool change')
		c.tool_change(o.cutter_id)
		c.spindle(o.spindle_rpm,spdir_clockwise)
		c.feedrate(o.feedrate)
		c.flush_nc()
		
		
		#commands=[]
		m=bpy.context.scene.cam_machine[0]
		
		millfeedrate=min(o.feedrate,m.feedrate_max)
		millfeedrate=unitcorr*max(millfeedrate,m.feedrate_min)
		plungefeedrate=	millfeedrate*o.plunge_feedrate/100
		freefeedrate=m.feedrate_max*unitcorr
		
		last=Vector((0,0,0))

		o.duration=0.0
		f=millfeedrate
		downvector= Vector((0,0,-1))
		for vi in range(0,len(verts)):
			v=verts[vi].co
			if v.x==last.x: vx=None; 
			else:	vx=v.x*unitcorr
			if v.y==last.y: vy=None; 
			else:	vy=v.y*unitcorr
			if v.z==last.z: vz=None; 
			else:	vz=v.z*unitcorr
			
			#v=(v.x*unitcorr,v.y*unitcorr,v.z*unitcorr)
			vect=v-last
			plungeratio=1
			if vi>0  and vect.length>0 and downvector.angle(vect)<(pi/2-o.plunge_angle):
				#print('plunge')
				#print(vect)
				f=plungefeedrate
				c.feedrate(plungefeedrate)
				c.feed(x=vx,y=vy,z=vz)
			elif v.z==last.z==o.free_movement_height or vi==0:
				f=freefeedrate
				c.feedrate(freefeedrate)
				c.rapid(x=vx,y=vy,z=vz)
				#gcommand='{RAPID}'
				
			else:
				f=millfeedrate
				c.feedrate(millfeedrate)
				c.feed(x=vx,y=vy,z=vz)
			#v1=Vector(v)
			#v2=Vector(last)
			#vect=v1-v2
			o.duration+=vect.length/(f/unitcorr)
			last=v
	#print('duration')
	#print(o.duration)
	c.program_end()
	c.file_close()

def orderPoly(polys):	#sor poly, do holes e.t.c.
	p=Polygon.Polygon()
	levels=[[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]] 
	for ppart in polys:
		hits=0
		for ptest in polys:
			
			if ppart!=ptest:
				#print (ppart[0][0])
				if ptest.isInside(ppart[0][0][0],ppart[0][0][1]):
					hits+=1
		#hole=0
		#if hits % 2 ==1:
		 # hole=1
		if ppart.nPoints(0)>0:
			ppart.simplify()
			levels[hits].append(ppart)
	li=0
	for l in levels:	
		
		if li%2==1:
			for part in l:
				p=p-part
			#hole=1
		else:
			for part in l:
				p=p+part
			
		if li==1:#last chance to simplify stuff... :)
			p.simplify()
		li+=1
	  
	return p

def curveToPoly(cob):
	c=cob.data
	verts=[]
	pverts=[]
	#contourscount=0
	polys=[]
	
	for s in c.splines:
		chunk=[]
		for v in s.bezier_points:
			chunk.append((v.co.x+cob.location.x,v.co.y+cob.location.y))
		for v in s.points:
			chunk.append((v.co.x+cob.location.x,v.co.y+cob.location.y))
		
		if len(chunk)>2:
			polys.append(Polygon.Polygon(chunk)) 
	p=orderPoly(polys)
	return p
'''
def chunksToPoly(chunks):
	
	verts=[]
	pverts=[]
	p=Polygon.Polygon()
	#contourscount=0
	polys=[]
	
	for ch in chunks:
		pchunk=[]
		for v in ch:
			pchunk.append((v[0],v[1]))
		
		if len(pchunk)>1:
			polys.append(Polygon.Polygon(pchunk)) 
	levels=[[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]] 
	for ppart in polys:
		hits=0
		for ptest in polys:
			
			if ppart!=ptest:
				#print (ppart[0][0])
				if ptest.isInside(ppart[0][0][0],ppart[0][0][1]):
					hits+=1
		#hole=0
		#if hits % 2 ==1:
		 # hole=1
		if ppart.nPoints(0)>0:
			ppart.simplify()
			levels[hits].append(ppart)
	li=0
	for l in levels:	
		
		if li%2==1:
			for part in l:
				p=p-part
			#hole=1
		else:
			for part in l:
				p=p+part
			
		if li==1:#last chance to simplify stuff... :)
			p.simplify()
		li+=1
	  
	return p
'''
def chunksToPolys(chunks):#this does more cleve chunks to Poly with hierarchies... ;)
	#print ('analyzing paths')
	#verts=[]
	#pverts=[]
	polys=[]
	for ch in chunks:
		if len(ch.points)>2:
			pchunk=[]
			for v in ch.points:
				pchunk.append((v[0],v[1]))
			ch.poly=Polygon.Polygon(pchunk)
			#ch.poly.simplify()
		
	for ppart in chunks:
		for ptest in chunks:
			#if len(ptest.poly)==0:
			#	ptest.poly=Polygon.Polygon(ptest.points)
			#if len(ppart.poly)==0:
			#	ppart.poly=Polygon.Polygon(ppart.points)
				
			if ppart!=ptest and len(ptest.poly)>0 and len(ppart.poly)>0 and ptest.poly.nPoints(0)>0 and ppart.poly.nPoints(0)>0:
				if ptest.poly.isInside(ppart.poly[0][0][0],ppart.poly[0][0][1]):
					ptest.children.append(ppart)
					ppart.parents.append(ptest)
 
	parent=[]
	for polyi in range(0,len(chunks)):
		if len(chunks[polyi].parents)%2==1:
			for parent in chunks[polyi].parents:
				if len(parent.parents)+1==len(chunks[polyi].parents):
					chunks[polyi].parents=[parent]
					break
		else:
			chunks[polyi].parents=[]

	for chi in range(0,len(chunks)):
		ch=chunks[chi]
		if len(ch.parents)>0:
			ch.parents[0].poly=ch.parents[0].poly-ch.poly
		
	returnpolys=[]

	for polyi in range(0,len(chunks)):#don't include 'children'
		ch=chunks[polyi]
		if len(ch.parents)==0:
			ch.poly.simplify()
			returnpolys.append(ch.poly)
	return returnpolys  
		
def polyToMesh(p,z):
	verts=[]
	edges=[]
	vi=0
	ci=0
	for c in p:
		vi0=vi
		ei=0
		clen=p.nPoints(ci)
		for v in c:
			verts.append((v[0],v[1],z))
			if ei>0:
				edges.append((vi-1,vi))
			if ei==clen-1:
				edges.append((vi,vi0))
			vi+=1 
			ei+=1
		ci+=1
			
	mesh = bpy.data.meshes.new("test")
	bm = bmesh.new()
	for v_co in verts:
		 bm.verts.new(v_co)
	  
	for e in edges:
		bm.edges.new((bm.verts[e[0]],bm.verts[e[1]]))
		
	bm.to_mesh(mesh)
	mesh.update()
	object_utils.object_data_add(bpy.context, mesh)
	return bpy.context.active_object

def Circle(r,np):
	c=[]
	pi=math.pi  
	v=mathutils.Vector((r,0,0))
	e=mathutils.Euler((0,0,2.0*pi/np))
	for a in range(0,np):
		c.append((v.x,v.y))
		v.rotate(e)
		
	p=Polygon.Polygon(c)
	return p
	
def Helix(r,np, zstart,pend,rev):
	c=[]
	pi=math.pi
	v=mathutils.Vector((r,0,zstart))
	e=mathutils.Euler((0,0,2.0*pi/np))
	zstep=(zstart-pend[2])/(np*rev)
	for a in range(0,int(np*rev)):
		c.append((v.x+pend[0],v.y+pend[1],zstart-(a*zstep)))
		v.rotate(e)
	c.append((v.x+pend[0],v.y+pend[1],pend[2]))
		
	return c
	
def nRect(l,r):
	s=((-l/2.0,-r/10.0),(l/2.0,-r/10.0),(l/2.0,r),(-l/2,r))
	r= Polygon.Polygon(s)
	return r

def comparezlevel(x):
	return x[5]

def overlaps(bb1,bb2):#true if bb1 is child of bb2
	ch1=bb1
	ch2=bb2
	if (ch2[1]>ch1[1]>ch1[0]>ch2[0] and ch2[3]>ch1[3]>ch1[2]>ch2[2]):
		return True

class camPathChunk:
	#parents=[]
	#children=[]
	#sorted=False
	
	#progressIndex=-1# for e.g. parallel strategy, when trying to save time..
	def __init__(self,inpoints):
		if len(inpoints)>2:
			self.poly=Polygon.Polygon(inpoints)
		else:
			self.poly=Polygon.Polygon()
		self.points=inpoints
		self.closed=False
		self.children=[]
		self.parents=[]
		#self.unsortedchildren=False
		self.sorted=False#if the chunk has allready been milled in the simulation
		self.length=0;#this is total length of this chunk.
		
	def dist(self,pos,o):
		if self.closed:
			mind=10000000
			minv=-1
			for vi in range(0,len(self.points)):
				v=self.points[vi]
				#print(v,pos)
				d=dist2d(pos,v)
				if d<mind:
					mind=d
					minv=vi
			return mind
		else:
			if o.movement_type=='MEANDER':
				d1=dist2d(pos,self.points[0])
				d2=dist2d(pos,self.points[-1])
				#if d2<d1:
				#	ch.points.reverse()
				return min(d1,d2)
			else:
				return dist2d(pos,self.points[0])
	
	def adaptdist(self,pos,o):

		if self.closed:
			mind=10000000
			minv=-1
			for vi in range(0,len(self.points)):
				v=self.points[vi]
				#print(v,pos)
				d=dist2d(pos,v)
				if d<mind:
					mind=d
					minv=vi
			
			newchunk=[]
			newchunk.extend(self.points[minv:])
			newchunk.extend(self.points[:minv+1])
			self.points=newchunk


		else:
			if o.movement_type=='MEANDER':
				d1=dist2d(pos,self.points[0])
				d2=dist2d(pos,self.points[-1])
				
		
	def getNext(self):
		for child in self.children:
			if child.sorted==False:
				#unsortedchildren=True
				return child.getNext()	
		#self.unsortedchildren=False		
		return self
	
	def getLength(self):
		self.length=0
		
		for vi,v1 in enumerate(self.points):
			#print(len(self.points),vi)
			v2=Vector(v1)#this is for case of last point and not closed chunk..
			if self.closed and vi==len(self.points)-1:
				v2=Vector(self.points[0])
			elif vi<len(self.points)-1:
				v2=Vector(self.points[vi+1])
			v1=Vector(v1)
			v=v2-v1
			self.length+=v.length
			#print(v,pos)
#def appendChunk(sorted,ch,o,pos)	
	

def sortChunks(chunks,o):
	if o.strategy!='WATERLINE':
		progress('sorting paths')
	sys.setrecursionlimit(100000)# the getNext() function of CamPathChunk was running out of recursion limits. TODO: rewrite CamPathChunk getNext() it to not be recursive- works now won't do it/.
	sortedchunks=[]
	
	lastch=None
	i=len(chunks)
	pos=(0,0,0)
	#for ch in chunks:
	#	ch.getNext()#this stores the unsortedchildren properties
	#print('numofchunks')
	#print(len(chunks))
	while len(chunks)>0:
		ch=None
		if len(sortedchunks)==0 or len(lastch.parents)==0:#first chunk or when there are no parents -> parents come after children here...
			#ch=-1
			mind=10000
			d=100000000000
			
			for chtest in chunks:
				cango=True
				for child in chtest.children:# here was chtest.getNext==chtest, was doing recursion error and slowing down.
					if child.sorted==False:
						cango=False
						break;
				if cango:
					d=chtest.dist(pos,o)
					if d<mind:
						ch=chtest
						mind=d
		elif len(lastch.parents)>0:# looks in parents for next candidate, recursively
			for parent in lastch.parents:
				ch=parent.getNext()
				break
			
		if ch!=None:#found next chunk
			ch.sorted=True
			ch.adaptdist(pos,o)
			chunks.remove(ch)
			
			mergedist=2*o.dist_between_paths
			if o.strategy=='PENCIL':
				mergedist=10*o.dist_between_paths
			if o.stay_low and lastch!=None and (ch.dist(pos,o)<mergedist or (o.parallel_step_back and ch.dist(pos,o)<4*o.dist_between_paths)):
				if o.strategy=='PARALLEL' or o.strategy=='CROSS':# for these paths sorting happens after sampling, thats why they need resample the connection
					between=samplePathLow(o,lastch,ch,True)
				else:
					between=samplePathLow(o,lastch,ch,False)#other paths either dont use sampling or are sorted before it.
			
				sortedchunks[-1].points.extend(between.points)
				sortedchunks[-1].points.extend(ch.points)
			else:
				sortedchunks.append(ch)
			lastch=ch
			pos=lastch.points[-1]
		i-=1	
		'''
		if i<-200:
			for ch in chunks:
				print(ch.sorted)
				print(ch.getNext())
				print(len(ch.points))
		'''
	sys.setrecursionlimit(1000)

	return sortedchunks
		

def outlinePoly(p,r,operation,offset = True):
	'''offsets or insets polygon by radius'''
	#t=Polygon.getTolerance()
	#e=0.0001
	#Polygon.setTolerance(e)
	vref=mathutils.Vector((1,0))
	#p.simplify()
	#print(p)
	if p.nPoints()>2:
		ci=0
		pr=Polygon.Polygon()
		
		pr = pr+p#TODO fix this. this probably ruins depth in outlines! should add contours instead, or do a copy
		
		circle=Circle(r,operation.circle_detail)
		polygons=[]
		for c in p:
			if len(c)>2:
				hole=p.isHole(ci)
				orientation=p.orientation(ci)
				vi=0
				clen=p.nPoints(ci)
				for v in c:
					v1=mathutils.Vector(v)
					
					if vi>0:
						v2=mathutils.Vector(c[vi-1])
					else:
						v2=mathutils.Vector(c[-1])
					if vi<clen-1:
						v3=mathutils.Vector(c[vi+1])
					else:
						v3= mathutils.Vector(c[0]) 
					
					
					vect=v1-v2
					fo=v1+(v2-v1)/2.0
					rect=nRect(vect.length,r)
					rr=0.0
					if not offset:
						rr=math.pi
					
					if (orientation==-1 and hole) or (orientation==1 and not hole):
						rr+=math.pi
					
						
					if vect.length>0:
						rect.rotate(vect.angle_signed(vref)+rr,0.0,0.0)
					rect.shift(fo[0],fo[1])
					
					# this merges the rect with 1 circle and is actually faster... probably because it reduces the circle.
					#TODO: implement proper arcs here, to save computation time , and avoid tiny bugs.. 
					circle.shift(v[0],v[1])
					shape=rect+circle
					circle.shift(-v[0],-v[1])
					if offset:
						pr=pr+shape
					else:
						pr=pr-shape
					
					
					vi+=1
			ci+=1
		
		#pr.simplify()
		#Polygon.setTolerance(e)
		
		if pr.nPoints()>2:
			
			if operation.optimize:
				pr=polyRemoveDoubles(pr,operation)
		p=pr
	return p
	
def meshFromCurveToChunk(object):
	mesh=object.data
	#print('detecting contours from curve')
	chunks=[]
	chunk=camPathChunk([])
	ek=mesh.edge_keys
	d={}
	for e in ek:
		d[e]=1#
		#d=dict(ek)
	dk=d.keys()
	x=object.location.x
	y=object.location.y
	z=object.location.z
	lastvi=0
	vtotal=len(mesh.vertices)
	perc=0
	for vi in range(0,len(mesh.vertices)-1):
		if not dk.isdisjoint([(vi,vi+1)]) and d[(vi,vi+1)]==1:
			chunk.points.append((mesh.vertices[vi].co.x+x,mesh.vertices[vi].co.y+y,mesh.vertices[lastvi].co.z+z))
		else:
			chunk.points.append((mesh.vertices[vi].co.x+x,mesh.vertices[vi].co.y+y,mesh.vertices[lastvi].co.z+z))
			if not(dk.isdisjoint([(vi,lastvi)])) or not(dk.isdisjoint([(lastvi,vi)])):
				#print('itis')
				chunk.closed=True
				chunk.points.append((mesh.vertices[lastvi].co.x+x,mesh.vertices[lastvi].co.y+y,mesh.vertices[lastvi].co.z+z))#add first point to end#originally the z was mesh.vertices[lastvi].co.z+z
				#chunk.append((mesh.vertices[lastvi].co.x+x,mesh.vertices[lastvi].co.y+y,mesh.vertices[lastvi].co.z+z))
			#else:
				#print('itisnot')
			lastvi=vi+1
			chunks.append(chunk)
			chunk=camPathChunk([])
		
		if perc!=int(100*vi/vtotal):
			perc=int(100*vi/vtotal)
			progress('processing curve',perc)
		
	vi=len(mesh.vertices)-1
	chunk.points.append((mesh.vertices[vi].co.x+x,mesh.vertices[vi].co.y+y,mesh.vertices[vi].co.z+z))  
	if not(dk.isdisjoint([(vi,lastvi)])) or not(dk.isdisjoint([(lastvi,vi)])):
		#print('itis')
		chunk.closed=True
		chunk.points.append((mesh.vertices[lastvi].co.x+x,mesh.vertices[lastvi].co.y+y,mesh.vertices[lastvi].co.z+z))
	#else:
		#	print('itisnot')
	chunks.append(chunk)
	return chunks

def meshloopToChunk(mesh):
	progress('detecting contours')
	chunks=[]
	ekeys=mesh.edge_keys
	
	e=ekeys.pop()
	spart=[e[0],e[1]]
	chunk=[]
	while len(ekeys)>0:
		foundsome=False
		for ei in range(len(ekeys)-1,-1,-1):
			e=ekeys[ei]
			#print('checking')
			#print(ei)
			
			if e[0]==spart[-1]:
				spart.append(e[1])
				foundsome=True
				ekeys.remove(e)
				#print('found')
				#print(e)
			elif e[1]==spart[-1]:
				spart.append(e[0])
				foundsome=True
				ekeys.remove(e)
				#print('found')
				#print (e)
		
		if foundsome==False:
			if len(spart)>0:
				chunk=[]
				spart.pop(-1)#otherwise i get double point
				for vi in spart:
					chunk.append((mesh.vertices[vi].co.x,mesh.vertices[vi].co.y,mesh.vertices[vi].co.z))
				#print (spart)
				#chunk.append((chunk[0][0],chunk[0][1],chunk[0][2]))#its the same point, - tuple, but that shouldnt do a harm
				chunks.append(chunk) 
				#print(chunk)
				spart=[]
				#print(len(chunks))
			if len(ekeys)>0:
				e=ekeys.pop()
				spart=[e[0],e[1]]
				
	#print(len(chunks))  
	chunk=[]
	spart.pop(-1)
	for vi in spart:
		chunk.append((mesh.vertices[vi].co.x,mesh.vertices[vi].co.y,mesh.vertices[vi].co.z))
	#print(spart)
	#chunk.append(chunk[0])#its the same point, - tuple, but that shouldnt do a harm
	#chunk.append((chunk[0][0],chunk[0][1],chunk[0][2]))
	#print (spart)
	# print(chunk)
	
	chunks.append(chunk) 
	return chunks

def testbite(pos):
	xs=(pos.x-o.min.x)/o.simulation_detail+o.borderwidth+o.simulation_detail/2#-m
	ys=(pos.y-o.min.y)/o.simulation_detail+o.borderwidth+o.simulation_detail/2#-m
	z=pos.z
	m=int(o.cutterArray.shape[0]/2)

	if xs>m+1 and xs<o.millimage.shape[0]-m-1 and ys>m+1 and ys<o.millimage.shape[1]-m-1 :
		o.millimage[xs-m:xs-m+size,ys-m:ys-m+size]=numpy.minimum(o.millimage[xs-m:xs-m+size,ys-m:ys-m+size],cutterArray+z)
	v.length+=o.simulation_detail
	
def crazyPath(o):#TODO: try to do something with this  stuff, it's just a stub. It should be a greedy adaptive algorithm.
	MAX_BEND=0.1#in radians...#TODO: support operation chains ;)
	prepareArea(o)
	#o.millimage = 
	sx=o.max.x-o.min.x
	sy=o.max.y-o.min.y

	resx=ceil(sx/o.simulation_detail)+2*o.borderwidth
	resy=ceil(sy/o.simulation_detail)+2*o.borderwidth

	o.millimage=numpy.array((0.1),dtype=float)
	o.millimage.resize(resx,resy)
	o.millimage.fill(0)
	o.cutterArray=-getCutterArray(o,o.simulation_detail)#getting inverted cutter
	crazy=camPathChunk([(0,0,0)])
	testpos=(o.min.x,o.min.y,o.min.z)
	
def getSlices(operation, returnCurves):
	ob=operation.object
	layer_thickness=operation.slice_detail
	edges=[]
	verts = []
	i=0
	slices=[]#slice format is [length, minx,miny, maxx, maxy,verts,z]
	firstslice=None
	lastslice=None
	maxzt = -100000000000000000000000000
	minzt = 1000000000000000000000000000
	progress('slicing object')
	m=ob.data
	#d={}#!
	for p in m.polygons:
		#a=i*50+12
		
		v1=m.vertices[p.vertices[0]].co
		v2=m.vertices[p.vertices[1]].co
		v3=m.vertices[p.vertices[2]].co
		if len(p.vertices)==3:
			tris=[[v1,v2,v3]]
		else:
			v4=m.vertices[p.vertices[3]].co
			tris=[[v1,v2,v3],[v3,v4,v1]]
			
		for v in tris:  
			#print(v)
			minz=min(v[0].z,v[1].z,v[2].z)
			maxz=max(v[0].z,v[1].z,v[2].z)
					
					
			t=layer_thickness
			
			start=int(minz // t)
			end=int(maxz // t +2)
			if firstslice==None:
					firstslice = start
					lastslice = end
					#print start, end
					for s in range(firstslice,lastslice):
							sz= s*t
							slices.append([0.0,100000000000.0,100000000000.0,-100000000000.0,-100000000000.0,[],sz])
	
			if start<firstslice:
					ns=[]
					ind=0
					for s in range(start, firstslice):
							sz=s*t
							slices.insert(ind,[0.0,100000000000.0,100000000000.0,-100000000000.0,-100000000000.0,[],sz])
							ind+=1
					firstslice=start
			if end>lastslice:
					for s in range(lastslice,end):
							sz=s*t
							slices.append([0.0,100000000000.0,100000000000.0,-100000000000.0,-100000000000.0,[],sz])
							#i+=1
					lastslice=end
									
								  
			for s in range(start,end):
					si=s-firstslice
					sc=slices[si]
					sz = sc[6]#s * t
					
					over=[]
					under=[]
					onslice=[]
					iv=[]
					for vert in v:
							if vert[2]>sz:
									over.append(vert)
							elif vert[2]<sz:
									under.append(vert)
							elif vert[2]==sz:
									onslice.append(vert)
					if len(onslice)==1:
						#pass		
						iv.append((onslice[0][0],onslice[0][1],sz))
						#iv[-1]=(int(1000000000*iv[-1][0])/1000000000,int(1000000000*iv[-1][1])/1000000000,int(1000000000*iv[-1][2])/1000000000)			
					elif len(onslice)==2:
							#if p.normal.z<1.0:
								#iv.extend([onslice[0],onslice[1]])
							iv.append((onslice[0][0],onslice[0][1],sz))
							iv.append((onslice[1][0],onslice[1][1],sz))
							#iv[-2]=(int(1000000000*iv[-2][0])/1000000000,int(1000000000*iv[-2][1])/1000000000,int(1000000000*iv[-2][2])/1000000000)
							#iv[-1]=(int(1000000000*iv[-1][0])/1000000000,int(1000000000*iv[-1][1])/1000000000,int(1000000000*iv[-1][2])/1000000000)
					elif len(onslice)==3:
							print('flat face')#,v)
					for v1 in under:
							for v2 in over:
									coef=(sz-v1[2])/(v2[2]-v1[2])
									x=v1[0]+(v2[0]-v1[0])*coef
									y=v1[1]+(v2[1]-v1[1])*coef
									z=sz#!
									#iv.append((int(100000000*x)/100000000,int(100000000*y)/100000000,int(100000000*z)/100000000))#! z not needed!
									iv.append((x,y,sz))
					if len(iv)==2:
							#d{iv[0]}
							#sc=slices[si]
							#print(iv)
							sc[5].append(iv[0])
							sc[5].append(iv[1])
							
					else:
							pass
							# print('strange count of layer faces',iv)	
							
					
					
							
			if i % 10000 == 0:
					print ('parsed faces', i, firstslice, lastslice, len(slices))
			i+=1  
	#sliceobs=[]  
	progress('sorting slices') 
	slicechunks=[]
	obs=[]
	for sc in slices:
		if len(sc[5])>0:
			i=0 
			chi=0
			
			edges=[]
			z=sc[5][0][2]
			
			slicechunks.append([])
			
			
			d={}
			for i in range(0,len(sc[5])):
				d[sc[5][i]]=[]
			for i in range(0,int(len(sc[5])/2)):
				verts1=d[sc[5][i*2]]
				verts2=d[sc[5][i*2+1]]
				
				if len(verts1)==2:
					if verts1[0]==verts1[1]:
						verts1.pop()
				if  len(verts1)<2:
					verts1.append(sc[5][i*2+1])
					
				if len(verts2)==2:
					if verts2[0]==verts2[1]:
						verts2.pop()
					
				if len(verts2)<2: 
					verts2.append(sc[5][i*2])
				
				
			
			ch=[sc[5][0],sc[5][1]]#first and his reference
			
			d.pop(ch[0])
		
			i=0
			verts=[123]
			
			while len(d)>0 and i<200000:# and verts!=[]:
				verts=d.get(ch[-1],[])
				if len(verts)<=1:
					if len(ch)>2:
						slicechunks[-1].append(ch)
					v1=d.popitem()
					ch=[v1[0],v1[1][0]] 
					
				elif len(verts)>2:
					pass;
					i+=1
					
					  
				else:
					done=False
					for v in verts:
						
						if not done:
							if v[0]==ch[-2][0] and v[1]==ch[-2][1]:# and v[2]==ch[-2][2]:
								pass
							else:
								#print(v,ch[-2])
								ch.append(v)
								
								d.pop(ch[-2])
								done=True
								if v[0]==ch[0][0] and v[1]==ch[0][1]:# and v[2]==ch[0][2]:
									slicechunks[-1].append(ch)
									print('closed')
									#d.pop(ch[-1])
									if len(d)>0:
										v1=d.popitem()
										ch=[v1[0],v1[1][0]]
				i+=1
		
			slicechunks[-1].append(ch)################3this might be a bug!!!!
		return slicechunks

def curveToChunks(o):
	activate(o)
	
	bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked":False, "mode":'TRANSLATION'}, TRANSFORM_OT_translate={"value":(0, 0, 0), "constraint_axis":(False, False, False), "constraint_orientation":'GLOBAL', "mirror":False, "proportional":'DISABLED', "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "texture_space":False, "release_confirm":False})
	bpy.ops.group.objects_remove_all()
	o=bpy.context.active_object
	if o.type=='FONT':#support for text objects is only and only here.
		bpy.ops.object.convert(target='CURVE', keep_original=False)
	o.data.dimensions='3D'
	try:
		bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)
		bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
		bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
		
	except:
		pass
	
	#o.data.dimensions='3D'
	o.data.bevel_depth=0
	o.data.extrude=0
	bpy.ops.object.convert(target='MESH', keep_original=False)
	
	o=bpy.context.active_object
	chunks=meshFromCurveToChunk(o)
	
		
	o=bpy.context.active_object
	
	bpy.context.scene.objects.unlink(o)
	return chunks

def getVectorRight(lastv,verts):#most right vector from a set
	defa=100
	v1=Vector(lastv[0])
	v2=Vector(lastv[1])
	va=v2-v1
	for i,v in enumerate(verts):
		if v!=lastv[0]:
			vb=Vector(v)-v2
			a=va.angle_signed(Vector(vb))
			#if a<=0:
			#	a=2*pi+a
			
			if a<defa:
				defa=a
				returnvec=i
	return returnvec

def cleanUpDict(ndict):
	print('removing lonely points')#now it should delete all junk first, iterate over lonely verts.
	#found_solitaires=True
	#while found_solitaires:
	found_solitaires=False
	keys=[]
	keys.extend(ndict.keys())
	removed=0
	for k in keys:
		print(k)
		print(ndict[k])
		if len(ndict[k])<=1:
			newcheck=[k]
			while(len(newcheck)>0):
				v=newcheck.pop()
				if len(ndict[v])<=1:
					for v1 in ndict[v]:
						newcheck.append(v)
					dictRemove(ndict,v)
			removed+=1
			found_solitaires=True
	print(removed)
	
def dictRemove(dict,val):
	for v in dict[val]:
		dict[v].remove(val)
	dict.pop(val)

def getArea(poly):
	return poly.area()	

def addLoop(parentloop, start, end):
	added=False
	for l in parentloop[2]:
		if l[0]<start and l[1]>end:
			addLoop(l,start,end)
			return
	parentloop[2].append([start,end,[]])
	
def cutloops(csource,parentloop,loops):
	copy=csource[parentloop[0]:parentloop[1]]
	
	for li in range(len(parentloop[2])-1,-1,-1):
		l=parentloop[2][li]
		#print(l)
		copy=copy[:l[0]-parentloop[0]]+copy[l[1]-parentloop[0]:]
	loops.append(copy)
	for l in parentloop[2]:
		cutloops(csource,l,loops)

def getObjectSilhouette(operation):
	o=operation
	
	if o.geometry_source=='OBJECT' or o.geometry_source=='GROUP':
		
		#for groups of objects, detect silhouette 1 by 1 and merge them in the end.

		if operation.onlycurves==False:#TODO if another silhouette algorithm is used, it needs to be done to support groups.
			if operation.update_silhouete_tag:
					if 1:#bpy.app.debug_value==0:#raster based method - currently only stable one.
						print('detecting silhouette - raster based')
						samples=renderSampleImage(operation)
						i=samples>operation.minz
						#numpytoimage(i,'threshold')
						#i=outlineImageBinary(operation,0.001,i,False)
						chunks=imageToChunks(operation,i)
						silhouete=chunksToPolys(chunks)#this conversion happens because we need the silh to be oriented, for milling directions.
						
						operation.silhouete=silhouete
						#return [silhouete]
					elif bpy.app.debug_value==1:#own method with intersections...
						#first, duplicate the object, so we can split it:
						activate(ob)
						bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked":False, "mode":'TRANSLATION'}, TRANSFORM_OT_translate={"value":(0, 0, 0), "constraint_axis":(False, False, False), "constraint_orientation":'GLOBAL', "mirror":False, "proportional":'DISABLED', "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "texture_space":False, "release_confirm":False})
						#remove doubles, then split the object in parts
						bpy.ops.object.editmode_toggle()
						bpy.ops.mesh.remove_doubles(threshold=0.000001, use_unselected=False)
						bpy.ops.mesh.separate(type='LOOSE')
						bpy.ops.object.editmode_toggle()
						obs=bpy.context.selected_objects
						spoly=Polygon.Polygon()
						spolys=[]
						for ob in obs:
							progress('silh edge candidates detection')
							t=time.time()
							m=ob.data
								
								
							m=ob.data
							d={}
							for e in m.edge_keys:
								d[e]=[]
							for f in m.polygons:
								for ek in f.edge_keys:
									if f.normal.z>0:
										d[ek].append(f)
							silh_candidates=[]
							
							#spoly=Polygon.Polygon()
							for e in m.edge_keys:
								
								if len(d[e])==1:
									v1=m.vertices[e[0]].co
									v2=m.vertices[e[1]].co
									silh_candidates.append((v2.to_tuple(),v1.to_tuple()))
									
							print(time.time()-t)
							t=time.time()
							
							
											
							ndict={}# build a dictionary
							r=10000000
							startpoint=None
							minx=100000000
							for e in silh_candidates:
								v1=(int(e[0][0]*r)/r,int(e[0][1]*r)/r,int(e[0][2]*r)/r)# slight rounding to avoid floating point imprecissions.
								v2=(int(e[1][0]*r)/r,int(e[1][1]*r)/r,int(e[1][2]*r)/r)
								if v1[0]<minx:
									startpoint=v1
									minx=v1[0]
								if v2[0]<minx:
									startpoint=v2
									minx=v2[0]
								ndict[v1]=[]
								ndict[v2]=[]
		
							for e in silh_candidates:# sort intersected edges:
								v1=(int(e[0][0]*r)/r,int(e[0][1]*r)/r,int(e[0][2]*r)/r)
								v2=(int(e[1][0]*r)/r,int(e[1][1]*r)/r,int(e[1][2]*r)/r)
								#if v2 not in ndict[v1]:
								ndict[v1].append(v2)
								#if v1 not in ndict[v2]:
								ndict[v2].append(v1)
								
							chunks=[]	
								
							first=list(ndict.keys())[0]
							ch=[first,ndict[first][0]]#first and his reference
							print(first)
							ndict[first].remove(ndict[first][0])
							#lastv=(startpoint,first[0])
							i=0
							#ndict.pop(ch[0])
							
							while len(ndict)>0 and i<200000:# and verts!=[]:
								done=False
								
								verts=ndict.get(ch[-1],[])
								if len(verts)<1:
									print('unconnected point')
									
									if len(ch)>2:
										chunks.append(ch)
									print(verts)
									#ndict.pop(ch[-1])
									#v2=[]
									#while v2=[]:
									v1=list(ndict.keys())[0]
									if len(ndict[v1])>0:
										v2=ndict[v1][0]
										
										ch=[v1,v2]#first and his reference
										ndict[v1].remove(v2)
									else:
										ndict.pop(v1)
							
								else:
									done=False
									for v in verts:
										if not done:
											if v[0]==ch[-2][0] and v[1]==ch[-2][1]:# and v[2]==ch[-2][2]:
												pass
											else:
												verts.remove(v)
												ch.append(v)
												#ndict[v].remove(ndict[ch[-2]])
												if len(ndict[ch[-2]])<=1:
													ndict.pop(ch[-2])
												#else:
												#	ndict[ch[-2]].remove(ch[-1])
												done=True
												if v[0]==ch[0][0] and v[1]==ch[0][1]:# and v[2]==ch[0][2]:
													if len(ndict[v])==1:
														ndict.pop(ch[-1])
														ch.pop(-1)
														chunks.append(ch)
														if len(ndict)>0:
															v1=list(ndict.keys())[0]
															v2=ndict[v1][0]
															
															ch=[v1,v2]#first and his reference
															ndict[v1].remove(v2)
															
															
															
															
								
								i+=1
								#print(i,verts,len(ndict))
								#if not done and len(ndict)>0:
								#	print('weird things happen')
								#	v1=ndict.popitem()
								#	ch=[v1[0],v1[1][0]] 
								#print(i,len(ndict))
							#if len(ch)>2:
							#	chunks.append(ch)	
							
							print(time.time()-t)
							loc=ob.location.to_2d()
							cchunks=[]
							
							polygons=[]
							for ch in chunks:
								nch=[]
								for v in ch:
									nch.append((v[0],v[1]))
								if len(nch)>2:
									poly=Polygon.Polygon(nch)
									polygons.append(poly)
									
							
							polygons=sorted(polygons, key = getArea)

							v1=Vector((0,0,10))
							v2=Vector((0,0,-10))	
							#obpoly=Polygon.Polygon()
							
							chunks=[]
							print('basic polys found')
							print(len(polygons))
							for p in polygons:
								np=Polygon.Polygon()
								np+=p#.simplify()
								#np.simplify()
								
								
								chops=[]	
								
								looplevel=0
								remove=[]
								print('contours',len(np))
								for c in np:
									intersections=0
									mainloop=[0,len(c),[]]
									i1=0
									for point1 in c:		
										i2=0
										for point2 in c:
											if i1<i2 and point1==point2:# and not(i1==i2 and c1i==c2i):
												intersections+=1
												print (i1,i2)
												addLoop(mainloop,i1,i2)
												
											i2+=1
										i1+=1
									
									loops=[]
									#print(mainloop)
									cutloops(c,mainloop,loops)
									#print(loops)
									#print(len(loops))
									
									print('intersections')
									print(intersections)
							
									for l in loops:
										ch=camPathChunk(l)
										
										chunks.append(ch)
								
							polysort=chunksToPolys(chunks)
							polys=[]
							print('found polygons')
							
							for p in polysort:##################check for non-hole loops
								cont=list(range(len(p)-1,-1,-1))
								for ci in range(0,len(p)):
									
									if p.isHole(ci):
										np=Polygon.Polygon(p[ci])
										
										ishole=True
										
										for a in range(0,30):# checks if this really isnt a hole..
											sample=Vector(np.sample(random.random)).to_3d()
											r=ob.ray_cast(v1+sample,v2+sample)
						
							
											if not(r==(Vector((0.0, 0.0, 0.0)), Vector((0.0, 0.0, 0.0)), -1)):
													ishole=False
										if ishole==False:
											cont.remove(ci)
								newp=Polygon.Polygon()
								for ci in cont:
									newp.addContour(p[ci])
								polys.append(newp)
							
											
							#print(polysort)
							spolys.extend(polys)	
							print('extended by',len(polysort))
							#for poly in polysort:
							#	spoly+=poly
							bpy.context.scene.objects.unlink(ob)
							'''
							
							'''
								#spoly.addContour(c)
							'''	
							for ch in chunks:
								print(ch)
								nchunk=camPathChunk([])
								for v in ch:
									nchunk.points.append((v[0]+loc.x,v[1]+loc.y,0))
								cchunks.append(nchunk)
							'''
							#chunksToMesh(cchunks,operation)
						for spoly in spolys:
							spoly.shift(ob.location.x,ob.location.y)
						operation.silhouete=spolys
					
					elif bpy.app.debug_value==4: # own method - with intersections.
						print('silh edge candidates detection')
						t=time.time()
						m=ob.data
							
							
						m=ob.data
						d={}
						for e in m.edge_keys:
							d[e]=[]
						for f in m.polygons:
							for ek in f.edge_keys:
								if f.normal.z>0:
									d[ek].append(f)
						silh_candidates=[]
						edge_dict={}
						#spoly=Polygon.Polygon()
						for e in m.edge_keys:
							
							if len(d[e])==1:
								v1=m.vertices[e[0]].co
								v2=m.vertices[e[1]].co
								#silh_candidates.append([v1.to_2d(),v2.to_2d()])
															
								edge_dict[(v2.to_2d().to_tuple(),v1.to_2d().to_tuple())]=True
								
								#tup=(v1.to_2d().to_tuple(),v2.to_2d().to_tuple())
								#print(edge_dict.get(tup))
								#if edge_dict.get(tup)==1:
									
									#edge_dict.pop(tup)	
									#print('pop')	
								#print(len(edge_dict))
							#elif len(d[e])==2:
								'''
								####
								f1=d[e][0]
								f2=d[e][1]
								
									
								if f1.normal.z>0>f2.normal.z or f1.normal.z<0<f2.normal.z or ((f1.normal.z==0 or f2.normal.z==0) and f1.normal.z!=f2.normal.z):#
									centers=[]
									v1=m.vertices[e[0]].co
									v2=m.vertices[e[1]].co
									evect=v2-v1
									
									for a in range(0,2):
										f=d[e][a]
										c=Vector((0,0,0))
										for vi in f.vertices:
											c+=m.vertices[vi].co
										c=c/len(f.vertices)
										centers.append(c)
										#c.	
									verts1=[].extend(f1.vertices)
									verts2=[].extend(f2.vertices)
									append=False
									ori=1
									if (centers[0].z>centers[1].z and f1.normal.z>f2.normal.z):
										if verts1.index(e[0])>verts1.index(e[1]):
											ori=-1
										append=True
									elif (centers[0].z<centers[1].z and f1.normal.z<f2.normal.z):
										if verts2.index(e[0])>verts2.index(e[1]):
											ori=-1
										append=True
									if append:
										#if ori==1:
										silh_candidates.append([v1.to_2d(),v2.to_2d()])
										#	
										#else:
										#	silh.candidates.append([v2.to_2d(),v1.to_2d()])
										
										t=(v1.to_2d().to_tuple(),v2.to_2d().to_tuple())
										if edge_dict.get(t,0)==1:
											edge_dict.pop(t)									
										edge_dict[(v2.to_2d().to_tuple(),v1.to_2d().to_tuple())]=1
										print(len(edge_dict))
								'''
										
						print(time.time()-t)
						t=time.time()
						print('silhouete intersections')
						intersects=[]
						silh_candidates=[]
						print(len(edge_dict))
						#print(edge_dict)
						silh_candidates.extend(edge_dict.keys())
						for si in range(0,len(silh_candidates)):
							e=silh_candidates[si]
							silh_candidates[si]=[Vector(e[0]),Vector(e[1])]
						print(len(silh_candidates))
						for e1i in range(0,len(silh_candidates)):
							e1=silh_candidates[e1i]
							for e2i in range(e1i+1,len(silh_candidates)):
								e2=silh_candidates[e2i]
								#print(e1,e2)
								if e1[0]!=e2[0] and e1[1]!=e2[0] and e1[0]!=e2[1] and e1[1]!=e2[1]:# and (e1[0][0]<e2[0][0]<e1[1][0] or e1[0][0]<e2[1][0]<e1[1][0])and(e1[0][1]<e2[0][1]<e1[1][1] or e1[0][1]<e2[1][1]<e1[1][1]):# and e1 not in toremove and e2 not in toremove:
									intersect=mathutils.geometry.intersect_line_line_2d(e1[0],e1[1],e2[0],e2[1])
									if intersect!=None:
										if intersect!=e1 and intersect!=e2:
											e1.append(intersect)
											e2.append(intersect)
										
						ndict={}# build a dictionary
						r=10000000
						startpoint=None
						minx=100000000
						for e in silh_candidates:
							#i=0
							for v in e:
								#e[i]=v.to_tuple()
								
								v1=(int(v.x*r)/r,int(v.y*r)/r)# slight rounding to avoid floating point imprecissions.
								if v1[0]<minx:
									startpoint=v1
									minx=v1[0]
								
								ndict[v1]=[]
	
								#i+=1
						#firstedge=silh_candidates[0]
						
						for e in silh_candidates:# sort intersected edges:
							if len(e)>2:
								start=e.pop(0)
								
								while len(e)>0:
									end=None
									mind=10000000000000
									endindex=-1
									i=0
									for vi in range(0,len(e)):
										v=e[vi]
										vec=v-start
										if vec.length==0:
											e.remove(v)
											vi-=1
										elif vec.length<mind:
											mind=vec.length
											end=v
											endindex=vi
										#i+=1
									if end!=None:
										v1=(int(start.x*r)/r,int(start.y*r)/r)
										v2=(int(end.x*r)/r,int(end.y*r)/r)
										#if v2 not in ndict[v1]:
										ndict[v1].append(v2)
										ndict[v2].append(v1)
										#ndict[v2].append(v1)
										start=e.pop(endindex)
							else:
								v1=(int(e[0].x*r)/r,int(e[0].y*r)/r)
								v2=(int(e[1].x*r)/r,int(e[1].y*r)/r)
								ndict[v1].append(v2)
								ndict[v2].append(v1)
						
						'''
						
						'''
						'''#some preliminary export
						edgedict={}
						silh_candidates=[]
						keys=[]
						keys.extend(ndict.keys())
						for k in keys:
							for v in ndict[k]:
								silh_candidates.append([k,v])
								
						';''
						
						#ndict.pop(ndict.keys[0)
						
						'''
						def getMinXDict(d):
							keys=[]
							keys.extend(d.keys())
							minx=100000
							mink=None
							for k in keys:
								if k[0]<minx:
									minx=k[0]
									mink=k
							return mink
							
						chunks=[]		
						first=ndict[startpoint]
						print(first)
						#left=Vector((-1,0))
						ri=getVectorRight(((startpoint[0]-0.1,startpoint[1]),startpoint),first)
							
						ch=[startpoint,first[ri]]#first and his reference
						lastv=(startpoint,first[ri])
						i=0
						print(lastv)
						
						while len(d)>0 and i<20000:# and verts!=[]:
							verts=ndict.get(ch[-1],[])
							if len(verts)<1:
								if len(ch)>2:
									chunks.append(ch)
								
								#v1=ndict.popitem()
								i=20000000
								#v=getMinXDict(ndict)
								#ch=[v] 
							else:
								print(i)
								print(len(verts))
								print(len(d))
								vi=getVectorRight(lastv,verts)
								
								v=verts[vi]
								if v[0]==ch[-2][0] and v[1]==ch[-2][1]:# and v[2]==ch[-2][2]:
									pass
								else:
									#print(v,ch[-2])
									ch.append(v)
									lastv=(ch[-2],ch[-1])
									dictRemove(ndict,ch[-2])
									#ndict.pop(ch[-2])
									done=True
									if v[0]==ch[0][0] and v[1]==ch[0][1]:# and v[2]==ch[0][2]:
										chunks.append(ch)
										dictRemove(ndict,startpoint)
										print('closed')
										#cleanUpDict(ndict)
										v=getMinXDict(ndict)
										print(v)
										ch=[ndict[v],ndict[v][0] ]
										#i=20000000
							
							i+=1
						#spoly.simplify()
						#polyToMesh(spoly,0) 
						#cand
						print('found chunks')
						print(len(chunks))
						
						#silh_candidates_vect=[]
						
						
						print(time.time()-t)
						loc=ob.location.to_2d()
						#for e in silh_candidates:
						#	ori=0
							#v1=Vector(e[0])+loc
							#v2=Vector(e[1])+loc
							
							#silh_candidates_vect.append([Vector((v1.x,v1.y)),Vector((v2.x,v2.y,0)),ori])
						cchunks=[]
						for ch in chunks:
							nchunk=camPathChunk([])
							for v in ch:
								nchunk.points.append((v[0],v[1],0))
							cchunks.append(nchunk)
						
						chunksToMesh(cchunks,operation)
						#spoly.shift(ob.location.x,ob.location.y)
						#operation.silhouete=[spoly]
		elif operation.onlycurves==True:#curve conversion to polygon format
			allchunks=[]
			for ob in operation.objects:
				chunks=curveToChunks(ob)
				allchunks.extend(chunks)
			silhouete=chunksToPolys(allchunks)
			operation.silhouete=silhouete
			print('silhouete')
			print(len(operation.silhouete))
	else:#detecting silhouete in image
		print('detecting silhouette - raster based')
		samples=renderSampleImage(operation)
		i=samples>operation.minz
		chunks=imageToChunks(operation,i)
		#chunks.pop(0)
			
		silhouete=chunksToPolys(chunks)
		operation.silhouete=silhouete
	operation.update_silhouete_tag=False
	return operation.silhouete
	
def getAmbient(o):
	if o.update_ambient_tag:
		if o.ambient_behaviour=='AROUND':
			o.ambient = getObjectOutline( o.ambient_radius , o , True)# in this method we need ambient from silhouette
		else:
			o.ambient=Polygon.Polygon(((o.min.x,o.min.y),(o.min.x,o.max.y),(o.max.x,o.max.y),(o.max.x,o.min.y)))
	o.update_ambient_tag=False
	
def getObjectOutline(radius,operation,Offset):
	
	polygons=getObjectSilhouette(operation)
	outline=Polygon.Polygon()
	i=0
	#print('offseting polygons')
	
	
	# we have to sort polygons here, because when they are added, they can overwrite smaller polygons with holes...
	#sortok=False
	#print('sizesorting')
	#print(len(polygons))
	'''#this didnt work.
	#TODO: support more levels of hierarchy with curves. - do it with the clipper library!
	while sortok==False:
		sortok=True
		for pi in range(0,len(polygons)-1):
			p1=polygons[pi]
			p2=polygons[pi+1]
			bb1=p1.boundingBox()
			bb2=p2.boundingBox()
			sx1=bb1[1]-bb1[0]
			sy1=bb1[3]-bb1[2]
			sx2=bb2[1]-bb2[0]
			sy2=bb2[3]-bb2[2]
			print(sx1*sy1,sx2*sy2)
			#if sx1*sy1<sx2*sy2:#bounding box area is bigger... not really good but works now
			if (bb1[0]<bb2[0] and bb1[1]>bb2[1]) and (bb1[2]<bb2[2] and bb1[3]>bb2[3]):
				print('swap')
				swap=polygons[pi]
				polygons[pi]=polygons[pi+1]
				polygons[pi+1]=swap
				sortok=False
		
	'''	
		
	outlines=[]
	for p in polygons:#sort by size before this???
		#if len(ch.points)>2:
		#3chp=[]
		##for v in ch.points:
		#	chp.append((v[0],v[1]))
		#p=Polygon.Polygon(chp)
		#i+=1
		#print(i)
		if radius>0:
			p=outlinePoly(p,radius,operation,Offset)
					
		if operation.dont_merge:
			for ci in range(0,len(p)):
				outline.addContour(p[ci],p.isHole(ci))
		else:
			#print(p)
			outline=outline+p
	return outline
	
def addMachineObject():
	
	s=bpy.context.scene
	ao=bpy.context.active_object
	if s.objects.get('CAM_machine')!=None:
	   o=s.objects['CAM_machine']
	else:
	    bpy.ops.mesh.primitive_cube_add(view_align=False, enter_editmode=False, location=(1, 1, -1), rotation=(0, 0, 0))
	    o=bpy.context.active_object
	    o.name='CAM_machine'
	    o.data.name='CAM_machine'
	    bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)
	    o.draw_type = 'WIRE'
	    bpy.ops.object.editmode_toggle()
	    bpy.ops.mesh.delete(type='ONLY_FACE')
	    bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE', action='TOGGLE')
	    bpy.ops.mesh.select_all(action='TOGGLE')
	    bpy.ops.mesh.subdivide(number_cuts=32, smoothness=0, quadtri=False, quadcorner='STRAIGHT_CUT', fractal=0, fractal_along_normal=0, seed=0)
	    bpy.ops.mesh.select_nth(nth=2, offset=0)
	    bpy.ops.mesh.delete(type='EDGE')
	    bpy.ops.object.editmode_toggle()
	    o.hide_render = True
	    o.hide_select = True
	    o.select=False
	#bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
       
	o.dimensions=bpy.context.scene.cam_machine[0].working_area
	activate(ao)

def addBridges(ch,o,z):
	ch.getLength()
	n=int(ch.length/o.bridges_max_distance)
	n = max(n,o.bridges_per_curve)
	dist=ch.length/n
	pos=[]
	for i in range(0,n):
		pos.append([i*dist+0.0001,i*dist+o.bridges_width+o.cutter_diameter])
	dist=0
	bridgeheight=min(0,o.min.z+o.bridges_height)
	inbridge=False
	posi=0
	insertpoints=[]
	changepoints=[]
	vi=0
	while vi<len(ch.points):
		v1=ch.points[vi]
		v2=Vector(v1)#this is for case of last point and not closed chunk..
		if ch.closed and vi==len(ch.points)-1:
			v2=Vector(ch.points[0])
		else:
			v2=Vector(ch.points[vi+1])
		v1=Vector(v1)
		v=v2-v1
		dist+=v.length
		
		wasinbridge=inbridge
		if not inbridge and posi<len(pos) and pos[posi][0]<dist:#detect start of bridge
			
			ratio=(dist-pos[posi][0])/v.length
			point1=v2-v*ratio#TODO: optimize this
			point2=v2-v*ratio
			if bridgeheight>point1.z:
				point1.z=min(point1.z,bridgeheight)
				point2.z=max(point2.z,bridgeheight)
				#ch.points.insert(vi-1,point1)
				#ch.points.insert(vi,point2)
				insertpoints.append([vi+1,point1.to_tuple()])
				insertpoints.append([vi+1,point2.to_tuple()])
			inbridge=True
			
		if wasinbridge and inbridge:#still in bridge, raise the point up.#
			changepoints.append([vi,(v1.x,v1.y,max(v1.z,bridgeheight))])
			#ch.points[vi]=(v1.x,v1.y,max(v1.z,bridgeheight))
			
		if inbridge and pos[posi][1]<dist:#detect end of bridge
			ratio=(dist-pos[posi][1])/v.length
			point1=v2-v*ratio
			point2=v2-v*ratio
			if bridgeheight>point1.z:
				point1.z=max(point1.z,bridgeheight)
				point2.z=min(point2.z,bridgeheight)
				#ch.points.insert(vi,point1)
				#ch.points.insert(vi+1,point2)
				#vi+=2
				insertpoints.append([vi+1,point1.to_tuple()])
				insertpoints.append([vi+1,point2.to_tuple()])
			inbridge=False
			posi+=1 
			vi-=1
			dist-=v.length
		vi+=1
			
		
		
		
		if posi>=len(pos):
			print('added bridges')
			break;
	for p in changepoints:
		ch.points[p[0]]=p[1]
	for pi in range(len(insertpoints)-1,-1,-1):
		ch.points.insert(insertpoints[pi][0],insertpoints[pi][1])
#this is the main function.
def getPaths(context,operation):#should do all path calculations.
	
	t=time.clock()
	s=bpy.context.scene
	o=operation
	getBounds(o)
	
	
	if o.use_limit_curve:
		if o.limit_curve!='':
			limit_curve=bpy.data.objects[o.limit_curve]
			
	
	
	###########cutout strategy is completely here:
	if o.strategy=='CUTOUT':
		#ob=bpy.context.active_object
		offset=True
		if o.cut_type=='ONLINE' and o.onlycurves==True:#is separate to allow open curves :)
			print('separe')
			chunksFromCurve=[]
			for ob in o.objects:
				chunksFromCurve.extend(curveToChunks(ob))
			
			for ch in chunksFromCurve:
				print(ch.points)
				
				if len(ch.points)>2:
					ch.poly=chunkToPoly(ch)
		else:
			if o.cut_type=='ONLINE':
				p=getObjectOutline(0,o,True)
				
			elif o.cut_type=='OUTSIDE':
				p=getObjectOutline(o.cutter_diameter/2,o,True)
			elif o.cut_type=='INSIDE':
				p=getObjectOutline(o.cutter_diameter/2,o,False)
			chunksFromCurve=polyToChunks(p,-1)
		
		#parentChildPoly(chunksFromCurve,chunksFromCurve,o)
		
		parentChildPoly(chunksFromCurve,chunksFromCurve,o)
		chunksFromCurve=sortChunks(chunksFromCurve,o)
		
		if (o.movement_type=='CLIMB' and o.spindle_rotation_direction=='CCW') or (o.movement_type=='CONVENTIONAL' and o.spindle_rotation_direction=='CW'):
			for ch in chunksFromCurve:
				ch.points.reverse()
		chunks=[]
		if o.use_layers:
			steps=[]
			n=math.ceil(-(o.min.z/o.stepdown))
			layerstart=0
			for x in range(0,n):
				layerend=max(-((x+1)*o.stepdown),o.min.z)
				steps.append([layerstart,layerend])
				layerstart=layerend
		else:
				steps=[[0,o.min.z]]
			
		if o.contour_ramp:
			for chunk in chunksFromCurve:
				if chunk.closed:
					for step in steps:
						chunks.extend(setChunksZRamp([chunk],step[0],step[1],o))
				else:
					chunks.extend(setChunksZ([chunk],step[1]))
					#o.warnings
					o.warnings=o.warnings+'Ramp in not suported for non-closed curves! \n '
					#if o.ramp_out:
				#if o.ramp_out:
				#	chunks.extend(ChunkRampOut([chunk], angle) )
		else:
			if o.first_down:
				for chunk in chunksFromCurve:
					for step in steps:
						chunks.extend(setChunksZ([chunk],step[1]))
			else:
				for step in steps:
					chunks.extend(setChunksZ(chunksFromCurve,step[1]))
		if o.use_bridges:
			for ch in chunks:
				addBridges(ch,o,0)
				
		if bpy.app.debug_value==0 or bpy.app.debug_value==1 or bpy.app.debug_value==3 or bpy.app.debug_value==2:# or bpy.app.debug_value==4:
			chunksToMesh(chunks,o)
		'''#bridge stuff from carve strategy:
					pathSamples=[]
			#for ob in o.objects:
			ob=bpy.data.objects[o.curve_object]
			pathSamples.extend(curveToChunks(ob))
			pathSamples=sortChunks(pathSamples,o)#sort before sampling
			pathSamples=chunksRefine(pathSamples,o)
		'''
	if o.strategy=='POCKET':	
		p=getObjectOutline(o.cutter_diameter/2,o,False)
		all=Polygon.Polygon(p)
		approxn=(min(o.max.x-o.min.x,o.max.y-o.min.y)/o.dist_between_paths)/2
		i=0
		chunks=[]
		chunksFromCurve=[]
		lastchunks=[]
		while len(p)>0:
			nchunks=polyToChunks(p,o.min.z)
			chunksFromCurve.extend(nchunks)
			parentChildDist(lastchunks,nchunks,o)
			lastchunks=nchunks
			
			p=outlinePoly(p,o.dist_between_paths,o,False)
			
			#for c in p:
			#	all.addContour(c)
			percent=int(i/approxn*100)
			progress('outlining polygons ',percent) 
			i+=1
		if (o.movement_type=='CLIMB' and o.spindle_rotation_direction=='CW') or (o.movement_type=='CONVENTIONAL' and o.spindle_rotation_direction=='CCW'):
			for ch in chunksFromCurve:
				ch.points.reverse()
				
		#if bpy.app.debug_value==1:
			
		chunksFromCurve=sortChunks(chunksFromCurve,o)	
			
		chunks=[]
		if o.use_layers:
			n=math.ceil(-(o.min.z/o.stepdown))
			layers=[]
			layerstart=0
			for x in range(0,n):
				layerend=max(-((x+1)*o.stepdown),o.min.z)
				layers.append([layerstart,layerend])
				layerstart=layerend
		else:
			layers=[[0,o.min.z]]

		for l in layers:
			lchunks=setChunksZ(chunksFromCurve,l[1])
			###########helix_enter first try here TODO: check if helix radius is not out of operation area.
			if o.helix_enter:
				helix_radius=o.cutter_diameter*0.5*o.helix_diameter*0.01#90 percent of cutter radius
				helix_circumference=helix_radius*pi*2
				
				revheight=helix_circumference*tan(o.helix_angle)
				for chi,ch in enumerate(lchunks):
					if chunksFromCurve[chi].children==[]:
					
						p=ch.points[0]#TODO:intercept closest next point when it should stay low 
						#first thing to do is to check if helix enter can really enter.
						checkc=Circle(helix_radius+o.cutter_diameter/2,o.circle_detail)
						checkc.shift(p[0],p[1])
						covers=False
						for poly in o.silhouete:
							if poly.covers(checkc):
								covers=True
								break;
						
						if covers:
							revolutions=(l[0]-p[2])/revheight
							#print(revolutions)
							h=Helix(helix_radius,o.circle_detail, l[0],p,revolutions)
							#invert helix if not the typical direction
							if (o.movement_type=='CONVENTIONAL' and o.spindle_rotation_direction=='CW') or (o.movement_type=='CLIMB' 	and o.spindle_rotation_direction=='CCW'):
								nhelix=[]
								for v in h:
									nhelix.append((2*p[0]-v[0],v[1],v[2]))
								h=nhelix
							ch.points=h+ch.points
						else:
							o.warnings=o.warnings+'Helix entry did not fit! \n '
			#Arc retract here first try:
			if o.retract_tangential:#TODO: check for entry and exit point before actual computing... will be much better.
									#TODO: fix this for CW and CCW!
				for chi, ch in enumerate(lchunks):
					#print(chunksFromCurve[chi])
					#print(chunksFromCurve[chi].parents)
					if chunksFromCurve[chi].parents==[] or len(chunksFromCurve[chi].parents)==1:
						
						revolutions=0.25
						v1=Vector(ch.points[-1])
						i=-2
						v2=Vector(ch.points[i])
						v=v1-v2
						while v.length==0:
							i=i-1
							v2=Vector(ch.points[i])
							v=v1-v2
						
						v.normalize()
						rotangle=Vector((v.x,v.y)).angle_signed(Vector((1,0)))
						e=Euler((0,0,pi/2.0))# TODO:#CW CLIMB!
						v.rotate(e)
						p=v1+v*o.retract_radius
						center = p
						p=(p.x,p.y,p.z)
						
						#progress(str((v1,v,p)))
						h=Helix(o.retract_radius, o.circle_detail, p[2]+o.retract_height,p, revolutions)
						
						e=Euler((0,0,rotangle+pi))#angle to rotate whole retract move
						rothelix=[]
						c=[]#polygon for outlining and checking collisions.
						for p in h:#rotate helix to go from tangent of vector
							v1=Vector(p)
							
							v=v1-center
							v.x=-v.x#flip it here first...
							v.rotate(e)
							p=center+v
							rothelix.append(p)
							c.append((p[0],p[1]))
							
						c=Polygon.Polygon(c)
						#print('çoutline')
						#print(c)
						coutline = outlinePoly(c,o.cutter_diameter/2,operation,offset = True)
						#print(h)
						#print('çoutline')
						#print(coutline)
						#polyToMesh(coutline,0)
						rothelix.reverse()
						
						covers=False
						for poly in o.silhouete:
							if poly.covers(coutline):
								covers=True
								break;
						
						if covers:
							ch.points.extend(rothelix)
			chunks.extend(lchunks)
		
		##################CUTOUT continues here
		chunksToMesh(chunks,o)
	elif o.strategy=='CRAZY':
		crazyPath(o)
	elif o.strategy=='PARALLEL' or o.strategy=='CROSS' or o.strategy=='BLOCK' or o.strategy=='SPIRAL' or o.strategy=='CIRCLES' or o.strategy=='OUTLINEFILL' or o.strategy=='CARVE'or o.strategy=='PENCIL':  
		
		
		ambient_level=0.0
		
		if o.strategy=='CARVE':
			pathSamples=[]
			#for ob in o.objects:
			ob=bpy.data.objects[o.curve_object]
			pathSamples.extend(curveToChunks(ob))
			pathSamples=sortChunks(pathSamples,o)#sort before sampling
			pathSamples=chunksRefine(pathSamples,o)
		elif o.strategy=='PENCIL':
			prepareArea(o)
			pathSamples=getImageCorners(o,o.offset_image)
			#for ch in pathSamples:
			#	for i,p in enumerate(ch.points):
			#		ch.points[i]=(p[0],p[1],0)
			pathSamples=sortChunks(pathSamples,o)#sort before sampling
		else: 
			pathSamples=getPathPattern(o)
	
		#print (minz)
		
		
		chunks=[]
		if o.use_layers:
			n=math.ceil(-(o.min.z/o.stepdown))
			layers=[]
			for x in range(0,n):
				
				layerstart=-(x*o.stepdown)
				layerend=max(-((x+1)*o.stepdown),o.min.z)
				layers.append([layerstart,layerend])
				
				
		else:
			layerstart=0#
			layerend=o.min.z#
			layers=[[layerstart,layerend]]
		
		chunks.extend(sampleChunks(o,pathSamples,layers))
		if (o.strategy=='PARALLEL' or o.strategy=='CROSS'):# and not o.parallel_step_back:
			chunks=sortChunks(chunks,o)
		#print(chunks)
		if o.strategy=='CARVE':
			for ch in chunks:
				for vi in range(0,len(ch.points)):
					ch.points[vi]=(ch.points[vi][0],ch.points[vi][1],ch.points[vi][2]-o.carve_depth)
	
		chunksToMesh(chunks,o)
		
	elif o.strategy=='WATERLINE':
		topdown=True
		tw=time.time()
		chunks=[]
		progress ('retrieving object slices')
		prepareArea(o)
		layerstep=1000000000
		if o.use_layers:
			layerstep=math.floor(o.stepdown/o.slice_detail)
			if layerstep==0:
				layerstep=1
				
		#for projection of filled areas		
		layerstart=0#
		layerend=o.min.z#
		layers=[[layerstart,layerend]]
		#######################		
		nslices=ceil(abs(o.minz/o.slice_detail))
		lastislice=numpy.array([])
		lastslice=Polygon.Polygon()#polyversion
		layerstepinc=0
		
		slicesfilled=0
		getAmbient(o)
		for h in range(0,nslices):
			layerstepinc+=1
			slicechunks=[]
			z=o.minz+h*o.slice_detail
			#print(z)
			#sliceimage=o.offset_image>z
			islice=o.offset_image>z
			slicepolys=imageToPoly(o,islice)
			
			poly=Polygon.Polygon()#polygversion
			lastchunks=[]
			#imagechunks=imageToChunks(o,islice)
			#for ch in imagechunks:
			#	slicechunks.append(camPathChunk([]))
			#	for s in ch.points:
			#		slicechunks[-1].points.append((s[0],s[1],z))
					
			
			#print('found polys',layerstepinc,len(slicepolys))
			for p in slicepolys:
				#print('polypoints',p.nPoints(0))
				poly+=p#polygversion
				#print()
				#polyToMesh(p,z)
				nchunks=polyToChunks(p,z)
				#print('chunksnum',len(nchunks))
				#if len(nchunks)>0:
				#	print('chunkpoints',len(nchunks[0].points))
				#print()
				lastchunks.extend(nchunks)
				slicechunks.extend(nchunks)
				#print('totchunks',len(slicechunks))
			if len(slicepolys)>0:
				slicesfilled+=1
				#chunks.extend(polyToChunks(slicepolys[1],z))
				#print(len(p),'slicelen')
			
			
			#
			#print(len(lastslice))
			#'''
			#print('test waterlayers')
			#print(layerstep,layerstepinc)
			if o.waterline_fill:
				layerstart=min(o.max.z,z+o.slice_detail)#
				layerend=max(o.min.z,z-o.slice_detail)#
				layers=[[layerstart,layerend]]
			
				if len(lastslice)>0 or (o.inverse and len(poly)>0 and slicesfilled==1):#fill top slice for normal and first for inverse, fill between polys
					offs=False
					if len(lastslice)>0:#between polys
						if o.inverse:
							restpoly=poly-lastslice
						else:
							restpoly=lastslice-poly#Polygon.Polygon(lastslice)
						#print('filling between')
					if (not o.inverse and len(poly)==0 and slicesfilled>0) or (o.inverse and len(poly)>0 and slicesfilled==1):#first slice fill
						restpoly=lastslice
						#print('filling first')
					
					restpoly=outlinePoly(restpoly,o.dist_between_paths,o,offs)
					fillz = z 
					i=0
					while len(restpoly)>0:
						nchunks=polyToChunks(restpoly,fillz)
						#project paths TODO: path projection during waterline is not working
						if o.waterline_project:
							nchunks=chunksRefine(nchunks,o)
							nchunks=sampleChunks(o,nchunks,layers)
						
						#########################
						slicechunks.extend(nchunks)
						parentChildDist(lastchunks,nchunks,o)
						lastchunks=nchunks
						#slicechunks.extend(polyToChunks(restpoly,z))
						restpoly=outlinePoly(restpoly,o.dist_between_paths,o,offs)
						i+=1
						#print(i)
				i=0
				if (slicesfilled>0 and layerstepinc==layerstep) or (not o.inverse and len(poly)>0 and slicesfilled==1) or (o.inverse and len(poly)==0 and slicesfilled>0):# fill layers and last slice, last slice with inverse is not working yet - inverse millings end now always on 0 so filling ambient does have no sense.
					fillz=z
					layerstepinc=0
					if o.ambient_behaviour=='AROUND':#TODO: use getAmbient
						ilim=ceil(o.ambient_radius/o.dist_between_paths)
						restpoly=poly
						if (o.inverse and len(poly)==0 and slicesfilled>0):
							restpoly=lastslice
						offs=True
					else:
						ilim=1000#TODO:this should be replaced... no limit, just check if the shape grows over limits.
						
						offs=False
						boundrect=Polygon.Polygon(((o.min.x,o.min.y),(o.min.x,o.max.y),(o.max.x,o.max.y),(o.max.x,o.min.y)))
						restpoly=boundrect-poly
						if (o.inverse and len(poly)==0 and slicesfilled>0):
							restpoly=boundrect-lastslice
					
					restpoly=outlinePoly(restpoly,o.dist_between_paths,o,offs)
					i=0
					while len(restpoly)>0 and i<ilim:
						
						nchunks=polyToChunks(restpoly,fillz)
						#########################
						slicechunks.extend(nchunks)
						parentChildDist(lastchunks,nchunks,o)
						lastchunks=nchunks
						#slicechunks.extend(polyToChunks(restpoly,z))
						restpoly=outlinePoly(restpoly,o.dist_between_paths,o,offs)
						i+=1
				
				
						
				percent=int(h/nslices*100)
				progress('waterline layers ',percent)  
				lastslice=poly
				
			#print(poly)
			#print(len(lastslice))
			'''
			if len(lastislice)>0:
				i=numpy.logical_xor(lastislice , islice)
				
				n=0
				while i.sum()>0 and n<10000:
					i=outlineImageBinary(o,o.dist_between_paths,i,False)
					polys=imageToPoly(o,i)
					for poly in polys:
						chunks.extend(polyToChunks(poly,z))
					n+=1
			
		
					#restpoly=outlinePoly(restpoly,o.dist_between_paths,o,False)
					#chunks.extend(polyToChunks(restpoly,z))
					
			lastislice=islice
			'''
			
			
			#if bpy.app.debug_value==1:
			if (o.movement_type=='CONVENTIONAL' and o.spindle_rotation_direction=='CCW') or (o.movement_type=='CLIMB' and o.		spindle_rotation_direction=='CW'):
				for chunk in slicechunks:
					chunk.points.reverse()
			slicechunks=sortChunks(slicechunks,o)
			if topdown:
				slicechunks.reverse()
			#project chunks in between
			
			chunks.extend(slicechunks)
		#chunks=sortChunks(chunks)
		if topdown:
			chunks.reverse()
			'''
			chi=0
			if len(chunks)>2:
				while chi<len(chunks)-2:
					d=dist2d((chunks[chi][-1][0],chunks[chi][-1][1]),(chunks[chi+1][0][0],chunks[chi+1][0][1]))
					if chunks[chi][0][2]>=chunks[chi+1][0][2] and d<o.dist_between_paths*2:
						chunks[chi].extend(chunks[chi+1])
						chunks.remove(chunks[chi+1])
						chi=chi-1
					chi+=1
			'''
		print(time.time()-tw)
		chunksToMesh(chunks,o)	  
		
	elif o.strategy=='DRILL':
		ob=bpy.data.objects[o.object_name]
		activate(ob)
	
		bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked":False, "mode":'TRANSLATION'}, TRANSFORM_OT_translate={"value":(0, 0, 0), "constraint_axis":(False, False, False), "constraint_orientation":'GLOBAL', "mirror":False, "proportional":'DISABLED', "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "texture_space":False, "release_confirm":False})
		bpy.ops.group.objects_remove_all()
		ob=bpy.context.active_object
		ob.data.dimensions='3D'
		try:
			bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)
			bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
			bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
			
		except:
			pass
		l=ob.location
		
		if ob.type=='CURVE':
			chunks=[]
			for c in ob.data.splines:
					maxx,minx,maxy,miny=-10000,10000,-10000,100000
					for p in c.points:
						if o.drill_type=='ALL_POINTS':
							chunks.append(camPathChunk([(p.co.x+l.x,p.co.y+l.y,o.min.z)]))
						minx=min(p.co.x,minx)
						maxx=max(p.co.x,maxx)
						miny=min(p.co.y,miny)
						maxy=max(p.co.y,maxy)
					for p in c.bezier_points:
						if o.drill_type=='ALL_POINTS':
							chunks.append(camPathChunk([(p.co.x+l.x,p.co.y+l.y,o.min.z)]))
						minx=min(p.co.x,minx)
						maxx=max(p.co.x,maxx)
						miny=min(p.co.y,miny)
						maxy=max(p.co.y,maxy)
					cx=(maxx+minx)/2
					cy=(maxy+miny)/2
					
					center=(cx,cy)
					aspect=(maxx-minx)/(maxy-miny)
					if (1.3>aspect>0.7 and o.drill_type=='MIDDLE_SYMETRIC') or o.drill_type=='MIDDLE_ALL': 
						chunks.append(camPathChunk([(center[0]+l.x,center[1]+l.y,o.min.z)]))
			chunks=sortChunks(chunks,o)
			chunksToMesh(chunks,o)
		ob=bpy.context.active_object
		bpy.context.scene.objects.unlink(ob)
	elif o.strategy=='SLICES':
		slicechunks = getSlices(o,0)
		for slicechunk in slicechunks:
			#print(slicechunk)
			pslices=chunksToPolys(slicechunk)
			#p1=outlinePoly(pslice,o.dist_between_paths,o,False)
			for pslice in pslices:
				p=pslice#-p1
			#print(p)
				polyToMesh(p,slicechunk[0][0][2])
		
	t1=time.clock()-t 
	progress('total time',t1)
	
	#progress('finished')

def reload_paths(o):
	oname = "cam_path_"+o.name
	s=bpy.context.scene
	#for o in s.objects:
	ob=None
	if oname in s.objects:
		s.objects[oname].data.name='xxx_cam_deleted_path'
		ob=s.objects[oname]
	
	picklepath=getCachePath(o)+'.pickle'
	f=open(picklepath,'rb')
	d=pickle.load(f)
	f.close()
	'''
	passed=False
	while not passed:
		try:
			f=open(picklepath,'rb')
			d=pickle.load(f)
			f.close()
			passed=True
		except:
			print('sleep')
			time.sleep(1)
	'''
	o.warnings=d['warnings']
	o.duration=d['duration']
	verts=d['path']
	
	edges=[]
	for a in range(0,len(verts)-1):
		edges.append((a,a+1))
		
	oname="cam_path_"+o.name
	mesh = bpy.data.meshes.new(oname)
	mesh.name=oname
	mesh.from_pydata(verts, edges, [])
	
	if oname in s.objects:
		s.objects[oname].data=mesh
	else: 
		ob=object_utils.object_data_add(bpy.context, mesh, operator=None)
	ob=s.objects[oname]
	ob.location=(0,0,0)
	o.path_object_name=oname
	#unpickle here:
	

	
