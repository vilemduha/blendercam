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

#here is the main functionality of Blender CAM. The functions here are called with operators defined in ops.py. All other libraries are called mostly from here.

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

import numpy
import random,sys, os
import pickle
import string
from cam import chunk
from cam.chunk import *
from cam import collision
from cam.collision import *
#import multiprocessing 
from cam import simple
from cam.simple import * 
from cam import pattern
from cam.pattern import *
from cam import polygon_utils_cam
from cam.polygon_utils_cam import *
from cam import image_utils
from cam.image_utils import *
from cam.nc import nc
from cam.nc import iso
from cam.opencamlib.opencamlib import oclSample, oclSamplePoints, oclResampleChunks, oclGetWaterline


from shapely.geometry import polygon as spolygon
from shapely import ops as sops
from shapely import geometry as sgeometry
from shapely import affinity, prepared
#from shapely.geometry import * not possible until Polygon libs gets out finally..
SHAPELY=True
	
def positionObject(operation):
	ob=bpy.data.objects[operation.object_name]
	minx,miny,minz,maxx,maxy,maxz=getBoundsWorldspace([ob], operation.use_modifiers) 
	ob.location.x-=minx
	ob.location.y-=miny
	ob.location.z-=maxz

def getBoundsWorldspace(obs, use_modifiers = False):
	#progress('getting bounds of object(s)')
	t=time.time()
		
	maxx=maxy=maxz=-10000000
	minx=miny=minz=10000000
	for ob in obs:
		#bb=ob.bound_box
		mw=ob.matrix_world
		if ob.type=='MESH':
			if use_modifiers:
				mesh = ob.to_mesh(bpy.context.scene, True, 'RENDER')
			else:
				mesh = ob.data
				
			for c in mesh.vertices:
				coord=c.co
				worldCoord = mw * Vector((coord[0], coord[1], coord[2]))
				minx=min(minx,worldCoord.x)
				miny=min(miny,worldCoord.y)
				minz=min(minz,worldCoord.z)
				maxx=max(maxx,worldCoord.x)
				maxy=max(maxy,worldCoord.y)
				maxz=max(maxz,worldCoord.z)
				
			if use_modifiers:
				bpy.data.meshes.remove(mesh)
		else:
			 
			#for coord in bb:
			for c in ob.data.splines:
				for p in c.bezier_points:
					coord=p.co
					#this can work badly with some imported curves, don't know why...
					#worldCoord = mw * Vector((coord[0]/ob.scale.x, coord[1]/ob.scale.y, coord[2]/ob.scale.z))
					worldCoord =mw * Vector((coord[0], coord[1], coord[2]))
					minx=min(minx,worldCoord.x)
					miny=min(miny,worldCoord.y)
					minz=min(minz,worldCoord.z)
					maxx=max(maxx,worldCoord.x)
					maxy=max(maxy,worldCoord.y)
					maxz=max(maxz,worldCoord.z)
				for p in c.points:
					coord=p.co
					#this can work badly with some imported curves, don't know why...
					#worldCoord = mw * Vector((coord[0]/ob.scale.x, coord[1]/ob.scale.y, coord[2]/ob.scale.z))
					worldCoord =mw * Vector((coord[0], coord[1], coord[2]))
					minx=min(minx,worldCoord.x)
					miny=min(miny,worldCoord.y)
					minz=min(minz,worldCoord.z)
					maxx=max(maxx,worldCoord.x)
					maxy=max(maxy,worldCoord.y)
					maxz=max(maxz,worldCoord.z)
	#progress(time.time()-t)
	return minx,miny,minz,maxx,maxy,maxz

def getSplineBounds(ob,curve):
	#progress('getting bounds of object(s)')
	maxx=maxy=maxz=-10000000
	minx=miny=minz=10000000
	mw=ob.matrix_world
		
	for p in curve.bezier_points:
		coord=p.co
		#this can work badly with some imported curves, don't know why...
		#worldCoord = mw * Vector((coord[0]/ob.scale.x, coord[1]/ob.scale.y, coord[2]/ob.scale.z))
		worldCoord =mw * Vector((coord[0], coord[1], coord[2]))
		minx=min(minx,worldCoord.x)
		miny=min(miny,worldCoord.y)
		minz=min(minz,worldCoord.z)
		maxx=max(maxx,worldCoord.x)
		maxy=max(maxy,worldCoord.y)
		maxz=max(maxz,worldCoord.z)
	for p in curve.points:
		coord=p.co
		#this can work badly with some imported curves, don't know why...
		#worldCoord = mw * Vector((coord[0]/ob.scale.x, coord[1]/ob.scale.y, coord[2]/ob.scale.z))
		worldCoord =mw * Vector((coord[0], coord[1], coord[2]))
		minx=min(minx,worldCoord.x)
		miny=min(miny,worldCoord.y)
		minz=min(minz,worldCoord.z)
		maxx=max(maxx,worldCoord.x)
		maxy=max(maxy,worldCoord.y)
		maxz=max(maxz,worldCoord.z)
	#progress(time.time()-t)
	return minx,miny,minz,maxx,maxy,maxz
	
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
		
	if o.geometry_source=='OBJECT' or o.geometry_source=='GROUP':
		o.onlycurves=True
		for ob in o.objects:
			if ob.type=='MESH':
				o.onlycurves=False;
	else:
		o.onlycurves=False


def checkMemoryLimit(o):
	#utils.getBounds(o)
	sx=o.max.x-o.min.x
	sy=o.max.y-o.min.y
	resx=sx/o.pixsize
	resy=sy/o.pixsize
	res=resx*resy
	limit=o.imgres_limit*1000000
	#print('co se to deje')
	if res>limit:
		ratio=(res/limit)
		o.pixsize=o.pixsize*math.sqrt(ratio)
		o.warnings=o.warnings+'sampling resolution had to be reduced!\n'
		print('changing sampling resolution to %f' % o.pixsize)
	#print('furt nevim')
	#print(ratio)
	
def getChangeData(o):
	'''this is a function to check if object props have changed, to see if image updates are needed in the image based method'''
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

		
def getBounds(o):
	#print('kolikrat sem rpijde')
	if o.geometry_source=='OBJECT' or o.geometry_source=='GROUP':
		if o.material_from_model:
			minx,miny,minz,maxx,maxy,maxz=getBoundsWorldspace(o.objects, o.use_modifiers)

			o.min.x=minx-o.material_radius_around_model
			o.min.y=miny-o.material_radius_around_model
			o.max.z=max(o.maxz,maxz)
				
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
		if o.source_image_crop:
			sx=int(i.size[0]*o.source_image_crop_start_x/100)
			ex=int(i.size[0]*o.source_image_crop_end_x/100)
			sy=int(i.size[1]*o.source_image_crop_start_y/100)
			ey=int(i.size[1]*o.source_image_crop_end_y/100)
			#operation.image.resize(ex-sx,ey-sy)
			crop=(sx,sy,ex,ey)
		else:
			sx=0
			ex=i.size[0]
			sy=0
			ey=i.size[1]
			
		o.pixsize=o.source_image_size_x/i.size[0]
		
		o.min.x=o.source_image_offset.x+(sx)*o.pixsize
		o.max.x=o.source_image_offset.x+(ex)*o.pixsize
		o.min.y=o.source_image_offset.y+(sy)*o.pixsize
		o.max.y=o.source_image_offset.y+(ey)*o.pixsize
		o.min.z=o.source_image_offset.z+o.minz
		o.max.z=o.source_image_offset.z
	s=bpy.context.scene
	m=s.cam_machine
	if o.max.x-o.min.x>m.working_area.x or o.max.y-o.min.y>m.working_area.y or o.max.z-o.min.z>m.working_area.z:
		#o.max.x=min(o.min.x+m.working_area.x,o.max.x)
		#o.max.y=min(o.min.y+m.working_area.y,o.max.y)
		#o.max.z=min(o.min.z+m.working_area.z,o.max.z)
		o.warnings+='Operation exceeds your machine limits\n'
		
	#progress (o.min.x,o.min.y,o.min.z,o.max.x,o.max.y,o.max.z)
	
def getBoundsMultiple(operations):
	"gets bounds of multiple operations, mainly for purpose of simulations or rest milling. highly suboptimal."
	maxx = maxy = maxz = -10000000
	minx = miny = minz = 10000000
	for o in operations:
		getBounds(o)
		maxx = max( maxx, o.max.x)
		maxy = max( maxy, o.max.y)
		maxz = max( maxz, o.max.z)
		minx = min( minx, o.min.x )
		miny = min( miny, o.min.y )
		minz = min( minz, o.min.z )
		
	return minx,miny,minz,maxx,maxy,maxz

def samplePathLow(o,ch1,ch2,dosample):
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
		if not (o.use_opencamlib and o.use_exact):
			if o.use_exact:
				if o.update_bullet_collision_tag:
					prepareBulletCollision(o)
					o.update_bullet_collision_tag = False
					
				cutterdepth=o.cutter_shape.dimensions.z/2
				for p in bpath.points:
					z=getSampleBullet(o.cutter_shape, p[0],p[1], cutterdepth, 1, o.minz)
					if z>p[2]:
						p[2]=z
			else:
				for p in bpath.points:
					xs=(p[0]-o.min.x)/pixsize+o.borderwidth+pixsize/2#-m
					ys=(p[1]-o.min.y)/pixsize+o.borderwidth+pixsize/2#-m
					z=getSampleImage((xs,ys),o.offset_image,o.minz)+o.skin
					if z>p[2]:
						p[2]=z
	return bpath


#def threadedSampling():#not really possible at all without running more blenders for same operation :( python!
#samples in both modes now - image and bullet collision too.
def sampleChunks(o,pathSamples,layers):
	#
	minx,miny,minz,maxx,maxy,maxz=o.min.x,o.min.y,o.min.z,o.max.x,o.max.y,o.max.z
	getAmbient(o)  

	if o.use_exact:#prepare collision world
		if o.use_opencamlib:
			oclSample(o, pathSamples)
			cutterdepth=0
		else:
			if o.update_bullet_collision_tag:
				prepareBulletCollision(o)			
				o.update_bullet_collision_tag=False
			#print (o.ambient)
			cutter=o.cutter_shape
			cutterdepth=cutter.dimensions.z/2
	else:
		if o.strategy!='WATERLINE': # or prepare offset image, but not in some strategies.
			prepareArea(o)
		
		pixsize=o.pixsize
		
		coordoffset=o.borderwidth+pixsize/2#-m
		
		res=ceil(o.cutter_diameter/o.pixsize)
		m=res/2
		
	t=time.time()
	#print('sampling paths')
	
	totlen=0;#total length of all chunks, to estimate sampling time.
	for ch in pathSamples:
		totlen+=len(ch.points)
	layerchunks=[]
	minz=o.minz-0.000001#correction for image method problems
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
	last_percent=-1
	#timing for optimisation
	samplingtime=timinginit()
	sortingtime=timinginit()
	totaltime=timinginit()
	timingstart(totaltime)
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
			if o.strategy!='WATERLINE' and int(100*n/totlen)!=last_percent:
				last_percent=int(100*n/totlen)
				progress('sampling paths ',last_percent)
			n+=1
			x=s[0]
			y=s[1]
			if not o.ambient.contains(sgeometry.Point(x,y)):
				newsample=(x,y,1)
			else:
				if o.use_opencamlib and o.use_exact:
					z=s[2]
					if minz>z:
						z=minz
					newsample=(x,y,z)
				####sampling
				elif o.use_exact and not o.use_opencamlib:
					
					if lastsample!=None:#this is an optimalization, search only for near depths to the last sample. Saves about 30% of sampling time.
						z=getSampleBullet(cutter, x,y, cutterdepth, 1, lastsample[2]-o.dist_along_paths)#first try to the last sample
						if z<minz-1:
							z=getSampleBullet(cutter, x,y, cutterdepth, lastsample[2]-o.dist_along_paths, minz)
					else:
						z=getSampleBullet(cutter, x,y, cutterdepth, 1, minz)
					
					#print(z)
					#here we have 
				else:
					timingstart(samplingtime)
					xs=(x-minx)/pixsize+coordoffset
					ys=(y-miny)/pixsize+coordoffset
					timingadd(samplingtime)
					#if o.inverse:
					#  z=layerstart
					z=getSampleImage((xs,ys),o.offset_image,minz)+o.skin
				#if minz>z and o.ambient.isInside(x,y):
				#	z=minz;
				################################
				#handling samples
				############################################
				
				if minz>z:
					z=minz
				newsample=(x,y,z)
				#z=max(minz,z)
					
				#if sampled:# and (not o.inverse or (o.inverse)):uh what was this? disabled
				#	newsample=(x,y,z)
						
				#elif o.ambient_behaviour=='ALL' and not o.inverse:#handle ambient here, this should be obsolete,
				#	newsample=(x,y,minz)
			for i,l in enumerate(layers):
				terminatechunk=False
				
				ch=layeractivechunks[i]
				#print(i,l)
				#print(l[1],l[0])
				
				if l[1]<=newsample[2]<=l[0]:
					lastlayer=None #rather the last sample here ? has to be set to None, since sometimes lastsample vs lastlayer didn't fit and did ugly ugly stuff....
					if lastsample!=None:
						for i2,l2 in enumerate(layers):
							if l2[1]<=lastsample[2]<=l2[0]:
								lastlayer=i2
					
					currentlayer=i
					if lastlayer!=None and lastlayer!=currentlayer:# and lastsample[2]!=newsample[2]:#sampling for sorted paths in layers- to go to the border of the sampled layer at least...there was a bug here, but should be fixed.
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
								v1,v2=isVerticalLimit(v1,v2,o.protect_vertical_limit)
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
								#print(v1,v2,betweensample,lastlayer,currentlayer)
								layeractivechunks[ls].points.insert(-1,betweensample.to_tuple())
								layeractivechunks[ls+1].points.insert(0,betweensample.to_tuple())
							
							li+=1
							#this chunk is terminated, and allready in layerchunks /
								
						#ch.points.append(betweensample.to_tuple())#
					ch.points.append(newsample)
				elif l[1]>newsample[2]:
					ch.points.append((newsample[0],newsample[1],l[1]))
				elif l[0]<newsample[2]:	 #terminate chunk
					terminatechunk=True

				if terminatechunk:
					if len(ch.points)>0:
						layerchunks[i].append(ch)
						thisrunchunks[i].append(ch)
						layeractivechunks[i]=camPathChunk([])
			lastsample=newsample
			
		for i,l in enumerate(layers):
			ch=layeractivechunks[i]
			if len(ch.points)>0:  
				layerchunks[i].append(ch)
				thisrunchunks[i].append(ch)
				layeractivechunks[i]=camPathChunk([])
				
			#PARENTING	
			if (o.strategy=='PARALLEL' or o.strategy=='CROSS' or o.strategy == 'OUTLINEFILL'):
				timingstart(sortingtime)
				parentChildDist(thisrunchunks[i], lastrunchunks[i],o)
				timingadd(sortingtime)

		lastrunchunks=thisrunchunks
				
			#print(len(layerchunks[i]))
	progress('checking relations between paths')
	timingstart(sortingtime)

	if (o.strategy=='PARALLEL' or o.strategy=='CROSS' or o.strategy == 'OUTLINEFILL'):
		if len(layers)>1:# sorting help so that upper layers go first always
			for i in range(0,len(layers)-1):
				parents=[]
				children=[]
				#only pick chunks that should have connectivity assigned - 'last' and 'first' ones of the layer.
				for ch in layerchunks[i+1]:
					if ch.children == []:
						parents.append(ch)
				for ch1 in layerchunks[i]:
					if ch1.parents == []:
						children.append(ch1)
				
				parentChild(parents,children,o) #parent only last and first chunk, before it did this for all.
	timingadd(sortingtime)
	chunks=[]
	
	for i,l in enumerate(layers):
		if o.ramp:
			for ch in layerchunks[i]:
				ch.zstart=layers[i][0]
				ch.zend=layers[i][1]
		chunks.extend(layerchunks[i])
	timingadd(totaltime)
	timingprint(samplingtime)
	timingprint(sortingtime)
	timingprint(totaltime)
	return chunks  
	
def sampleChunksNAxis(o,pathSamples,layers):
	#
	minx,miny,minz,maxx,maxy,maxz=o.min.x,o.min.y,o.min.z,o.max.x,o.max.y,o.max.z
	
	#prepare collision world
	if o.update_bullet_collision_tag:
		prepareBulletCollision(o)
		#print('getting ambient')
		getAmbient(o)  
		o.update_bullet_collision_tag=False
	#print (o.ambient)
	cutter=o.cutter_shape
	cutterdepth=cutter.dimensions.z/2
		
	t=time.time()
	print('sampling paths')
	
	totlen=0;#total length of all chunks, to estimate sampling time.
	for chs in pathSamples:
		totlen+=len(chs.startpoints)
	layerchunks=[]
	minz=o.minz
	layeractivechunks=[]
	lastrunchunks=[]
	
	for l in layers:
		layerchunks.append([])
		layeractivechunks.append(camPathChunk([]))
		lastrunchunks.append([])
	n=0
	
	lastz=minz
	for patternchunk in pathSamples:
		#print (patternchunk.endpoints)
		thisrunchunks=[]
		for l in layers:
			thisrunchunks.append([])
		lastlayer=None
		currentlayer=None
		lastsample=None
		#threads_count=4
		lastrotation=(0,0,0)
		#for t in range(0,threads):
		#print(len(patternchunk.startpoints),len( patternchunk.endpoints))
		spl=len(patternchunk.startpoints)
		for si in range(0,spl):#,startp in enumerate(patternchunk.startpoints):#TODO: seems we are writing into the source chunk , and that is why we need to write endpoints everywhere too?
			
			if n/200.0==int(n/200.0):
				progress('sampling paths ',int(100*n/totlen))
			n+=1
			sampled=False
			#print(si)
			
			#get the vector to sample 
			startp=Vector(patternchunk.startpoints[si])
			endp=Vector(patternchunk.endpoints[si])
			rotation=patternchunk.rotations[si]
			sweepvect=endp-startp
			sweepvect.normalize()
			####sampling
			if rotation!=lastrotation:
				
				cutter.rotation_euler=rotation
				#cutter.rotation_euler.x=-cutter.rotation_euler.x
				#print(rotation)

				if o.cutter_type=='VCARVE':# Bullet cone is always pointing Up Z in the object
					cutter.rotation_euler.x+=pi
				cutter.update_tag()
				#bpy.context.scene.frame_set(-1)
				#bpy.context.scene.update()
				#bpy.context.scene.frame_set(1)
				bpy.context.scene.frame_set(1)#this has to be :( it resets the rigidbody world. No other way to update it probably now :(
				bpy.context.scene.frame_set(2)#actually 2 frame jumps are needed.
				bpy.context.scene.frame_set(0)
				#
				#
				#bpy.context.scene.frame_set(-1)

				#bpy.context.scene.update()
				#update scene here?
				
			#print(startp,endp)
			#samplestartp=startp+sweepvect*0.3#this is correction for the sweep algorithm to work better.
			newsample=getSampleBulletNAxis(cutter, startp, endp ,rotation, cutterdepth)

			#print('totok',startp,endp,rotation,newsample)
			################################
			#handling samples
			############################################
			if newsample!=None:#this is weird, but will leave it this way now.. just prototyping here.
				sampled=True
			else:#TODO: why was this here?
				newsample=startp
				sampled=True
				#print(newsample)
				
			#elif o.ambient_behaviour=='ALL' and not o.inverse:#handle ambient here
				#newsample=(x,y,minz)
			if sampled:
				for i,l in enumerate(layers):
					terminatechunk=False
					ch=layeractivechunks[i]
					
					#print(i,l)
					#print(l[1],l[0])
					v=startp-newsample
					distance=-v.length
					
					if l[1]<=distance<=l[0]:
						lastlayer=currentlayer
						currentlayer=i
						
						if lastsample != None and lastlayer != None and currentlayer != None and lastlayer != currentlayer:#sampling for sorted paths in layers- to go to the border of the sampled layer at least...there was a bug here, but should be fixed.
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
								splitdistance=layers[ls][1]
							
								#v1=lastsample
								#v2=newsample
								#if o.protect_vertical:#different algo for N-Axis! need sto be perpendicular to or whatever.
								#	v1,v2=isVerticalLimit(v1,v2,o.protect_vertical_limit)
								#v1=Vector(v1)
								#v2=Vector(v2)
								#print(v1,v2)
								ratio=(splitdistance-lastdistance)/(distance-lastdistance)
								#print(ratio)
								betweensample=lastsample+(newsample-lastsample)*ratio
								#this probably doesn't work at all!!!! check this algoritm>
								betweenrotation=tuple_add(lastrotation,tuple_mul(tuple_sub(rotation,lastrotation),ratio))
								#startpoint = retract point, it has to be always available...
								betweenstartpoint=laststartpoint+(startp-laststartpoint)*ratio
								#here, we need to have also possible endpoints always..
								betweenendpoint = lastendpoint+(endp-lastendpoint)*ratio
								if growing:
									if li>0:
										layeractivechunks[ls].points.insert(-1,betweensample)
										layeractivechunks[ls].rotations.insert(-1,betweenrotation)
										layeractivechunks[ls].startpoints.insert(-1,betweenstartpoint)
										layeractivechunks[ls].endpoints.insert(-1,betweenendpoint)
									else:
										layeractivechunks[ls].points.append(betweensample)
										layeractivechunks[ls].rotations.append(betweenrotation)
										layeractivechunks[ls].startpoints.append(betweenstartpoint)
										layeractivechunks[ls].endpoints.append(betweenendpoint)
									layeractivechunks[ls+1].points.append(betweensample)
									layeractivechunks[ls+1].rotations.append(betweenrotation)
									layeractivechunks[ls+1].startpoints.append(betweenstartpoint)
									layeractivechunks[ls+1].endpoints.append(betweenendpoint)
								else:
									
									layeractivechunks[ls].points.insert(-1,betweensample)
									layeractivechunks[ls].rotations.insert(-1,betweenrotation)
									layeractivechunks[ls].startpoints.insert(-1,betweenstartpoint)
									layeractivechunks[ls].endpoints.insert(-1,betweenendpoint)
									
									layeractivechunks[ls+1].points.append(betweensample)
									layeractivechunks[ls+1].rotations.append(betweenrotation)
									layeractivechunks[ls+1].startpoints.append(betweenstartpoint)
									layeractivechunks[ls+1].endpoints.append(betweenendpoint)
									
									#layeractivechunks[ls+1].points.insert(0,betweensample)
								li+=1
								#this chunk is terminated, and allready in layerchunks /
							
							#ch.points.append(betweensample)#
						ch.points.append(newsample)
						ch.rotations.append(rotation)
						ch.startpoints.append(startp)
						ch.endpoints.append(endp)
						lastdistance = distance
						
					
					elif l[1]>distance:
						v=sweepvect*l[1]
						p=startp-v
						ch.points.append(p)
						ch.rotations.append(rotation)
						ch.startpoints.append(startp)
						ch.endpoints.append(endp)
					elif l[0]<distance:	 #retract to original track
						ch.points.append(startp)
						ch.rotations.append(rotation)
						ch.startpoints.append(startp)
						ch.endpoints.append(endp)
						#terminatechunk=True
					'''
					if terminatechunk:
						#print(ch.points)
						if len(ch.points)>0:
							if len(ch.points)>0: 
								layerchunks[i].append(ch)
								thisrunchunks[i].append(ch)
								layeractivechunks[i]=camPathChunk([])
					'''
			#else:
			#	terminatechunk=True
			lastsample = newsample
			lastrotation = rotation
			laststartpoint = startp
			lastendpoint = endp
			
		for i,l in enumerate(layers):
			ch=layeractivechunks[i]
			if len(ch.points)>0:  
				layerchunks[i].append(ch)
				thisrunchunks[i].append(ch)
				layeractivechunks[i]=camPathChunk([])
				
			if (o.strategy == 'PARALLEL' or o.strategy == 'CROSS' or o.strategy == 'OUTLINEFILL'):
				parentChildDist(thisrunchunks[i], lastrunchunks[i],o)
				
		lastrunchunks=thisrunchunks
				
			#print(len(layerchunks[i]))
	
	progress('checking relations between paths')
	'''#this algorithm should also work for n-axis, but now is "sleeping"
	if (o.strategy=='PARALLEL' or o.strategy=='CROSS'):
		if len(layers)>1:# sorting help so that upper layers go first always
			for i in range(0,len(layers)-1):
				#print('layerstuff parenting')
				parentChild(layerchunks[i+1],layerchunks[i],o)
	'''
	chunks=[]
	for i,l in enumerate(layers):
		chunks.extend(layerchunks[i])
	
	return chunks  

			
def createSimulationObject(name,operations,i):
	oname='csim_'+name
	
	o=operations[0]
	
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
	print(o.max.x, o.min.x)
	print(o.max.y, o.min.y)
	print('bounds')
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
	
def doSimulation(name,operations):
	'''perform simulation of operations. Currently only for 3 axis'''
	for o in operations:
		getOperationSources(o)
	limits = getBoundsMultiple(operations)#this is here because some background computed operations still didn't have bounds data
	i=image_utils.generateSimulationImage(operations,limits)
	cp=getCachePath(operations[0])[:-len(operations[0].name)]+name
	iname=cp+'_sim.exr'
	
	numpysave(i,iname)
	i=bpy.data.images.load(iname)
	createSimulationObject(name,operations,i)

def extendChunks5axis(chunks,o):

	s=bpy.context.scene
	m=s.cam_machine
	s=bpy.context.scene
	free_movement_height = o.free_movement_height# o.max.z + 
	if m.use_position_definitions:# dhull
		cutterstart=Vector((m.starting_position.x, m.starting_position.y ,max(o.max.z, m.starting_position.z)))#start point for casting
	else:
		cutterstart=Vector((0,0,max(o.max.z,free_movement_height)))#start point for casting
	cutterend=Vector((0,0,o.min.z))
	oriname=o.name+' orientation'
	ori=s.objects[oriname]
	#rotationaxes = rotTo2axes(ori.rotation_euler,'CA')#warning-here it allready is reset to 0!!
	print('rot',o.rotationaxes)
	a,b=o.rotationaxes#this is all nonsense by now.
	for chunk in chunks:
		for v in chunk.points:
			cutterstart.x=v[0]
			cutterstart.y=v[1]
			cutterend.x=v[0]
			cutterend.y=v[1]
			chunk.startpoints.append(cutterstart.to_tuple())
			chunk.endpoints.append(cutterend.to_tuple())
			chunk.rotations.append((a,b,0))#TODO: this is a placeholder. It does 99.9% probably write total nonsense.
			
			
def chunksToMesh(chunks,o):
	'''convert sampled chunks to path, optimization of paths'''
	t=time.time()
	s=bpy.context.scene
	m=s.cam_machine
	verts=[]
	
	free_movement_height =  o.free_movement_height#o.max.z +
	
	if o.machine_axes=='3':
		if m.use_position_definitions:
			origin=(m.starting_position.x, m.starting_position.y, m.starting_position.z)# dhull
		else:
			origin=(0,0,free_movement_height)	 
		
		verts = [origin]
	if o.machine_axes!='3':
		verts_rotations=[]#(0,0,0)
	if (o.machine_axes == '5' and o.strategy5axis=='INDEXED') or (o.machine_axes=='4' and o.strategy4axis=='INDEXED'):
		extendChunks5axis(chunks,o)
	
	if o.array:
		nchunks=[]
		for x in range(0,o.array_x_count):
			for y in range(0,o.array_y_count):
				print(x,y)
				for ch in chunks:
					ch=ch.copy()
					ch.shift(x*o.array_x_distance, y*o.array_y_distance,0)
					nchunks.append(ch)
		chunks = nchunks
		
	progress('building paths from chunks')
	e=0.0001
	lifted=True
	test=bpy.app.debug_value
	edges=[]	
	
	for chi in range(0,len(chunks)):
		
		#print(chi)
		
		ch=chunks[chi]
		#print(chunks)
		#print (ch)
		if len(ch.points)>0:#TODO: there is a case where parallel+layers+zigzag ramps send empty chunks here...
			#print(len(ch.points))
			nverts=[]
			if o.optimize:
				ch=optimizeChunk(ch,o)
			
			#lift and drop
			
			if lifted:#did the cutter lift before? if yes, put a new position above of the first point of next chunk. 
				if o.machine_axes=='3' or (o.machine_axes=='5' and o.strategy5axis=='INDEXED') or (o.machine_axes=='4' and o.strategy4axis=='INDEXED'):
					v=(ch.points[0][0],ch.points[0][1],free_movement_height)
				else:#otherwise, continue with the next chunk without lifting/dropping
					v=ch.startpoints[0]#startpoints=retract points
					verts_rotations.append(ch.rotations[0])
				verts.append(v)
			
			#add whole chunk
			verts.extend(ch.points)
			
			#add rotations for n-axis
			if o.machine_axes!='3':
				verts_rotations.extend(ch.rotations)
				
			lift = True
			#check if lifting should happen
			if chi<len(chunks)-1 and len(chunks[chi+1].points)>0:#TODO: remake this for n axis, and this check should be somewhere else...
				#nextch=
				last=Vector(ch.points[-1])
				first=Vector(chunks[chi+1].points[0])
				vect=first-last
				if (o.machine_axes=='3' and (o.strategy=='PARALLEL' or o.strategy=='CROSS') and vect.z==0 and vect.length<o.dist_between_paths*2.5) or (o.machine_axes =='4' and vect.length<o.dist_between_paths*2.5):#case of neighbouring paths
					lift=False
				if abs(vect.x)<e and abs(vect.y)<e:#case of stepdown by cutting.
					lift=False
				
			if lift:
				if o.machine_axes=='3' or (o.machine_axes=='5' and o.strategy5axis=='INDEXED') or (o.machine_axes=='4' and o.strategy4axis=='INDEXED'):
					v=(ch.points[-1][0],ch.points[-1][1],free_movement_height)
				else:
					v=ch.startpoints[-1]
					verts_rotations.append(ch.rotations[-1])
				verts.append(v)
			lifted=lift
			#print(verts_rotations)
	if o.use_exact and not o.use_opencamlib:
		cleanupBulletCollision(o)
	print(time.time()-t)
	t=time.time()
	
	#actual blender object generation starts here:
	edges=[]	
	for a in range(0,len(verts)-1):
		edges.append((a,a+1))
	
	oname="cam_path_"+o.name
		
	mesh = bpy.data.meshes.new(oname)
	mesh.name=oname
	mesh.from_pydata(verts, edges, [])
	
	if oname in s.objects:
		s.objects[oname].data=mesh
		ob=s.objects[oname]
	else: 
		ob=object_utils.object_data_add(bpy.context, mesh, operator=None)
		ob=ob.object
	
	if o.machine_axes!='3':
		#store rotations into shape keys, only way to store large arrays with correct floating point precision - object/mesh attributes can only store array up to 32000 intems.
		x=[]
		y=[]
		z=[]
		ob.shape_key_add()
		ob.shape_key_add()
		shapek=mesh.shape_keys.key_blocks[1]
		shapek.name='rotations'
		print(len(shapek.data))
		print(len(verts_rotations))
			
		for i,co in enumerate(verts_rotations):#TODO: optimize this. this is just rewritten too many times...
			#print(r)
			
			shapek.data[i].co=co
			

	
		
	print(time.time()-t)
	
	ob.location=(0,0,0)
	o.path_object_name=oname
	
	# parent the path object to source object if object mode
	if o.geometry_source=='OBJECT':
		activate(o.objects[0])
		ob.select = True
		bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
	else:
		ob.select = True

	
		
def exportGcodePath(filename,vertslist,operations):
	'''exports gcode with the heeks nc adopted library.'''
	
	progress('exporting gcode file')
	t=time.time()
	s=bpy.context.scene
	m=s.cam_machine
	
	#find out how many files will be done:
	
	split=False
	
	totops=0
	findex=0
	if m.eval_splitting:#detect whether splitting will happen
		for mesh in vertslist:
			totops+=len(mesh.vertices)
		print(totops)
		if totops>m.split_limit:
			split=True
			filesnum=ceil(totops/m.split_limit)
			print('file will be separated into %i files' % filesnum)
	print('1')	
	
	basefilename=bpy.data.filepath[:-len(bpy.path.basename(bpy.data.filepath))]+safeFileName(filename)
	
	
	extension='.tap'
	if m.post_processor=='ISO':
		from .nc import iso as postprocessor
	if m.post_processor=='MACH3':
		from .nc import mach3 as postprocessor
	elif m.post_processor=='EMC':
		extension = '.ngc'
		from .nc import emc2b as postprocessor
	elif m.post_processor=='GRBL':
		extension = '.ngc'
		from .nc import grbl as postprocessor
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
	elif m.post_processor=='GRAVOS':
		extension = '.nc'
		from .nc import gravos as postprocessor
	elif m.post_processor=='WIN-PC' :
		extension='.din'
		from .nc import winpc as postprocessor
	elif m.post_processor=='SHOPBOT MTC':
		extension='.sbp'
		from .nc import shopbot_mtc as postprocessor
	elif m.post_processor=='LYNX_OTTER_O':
		extension='.nc'
		from .nc import lynx_otter_o as postprocessor
	
	if s.unit_settings.system=='METRIC':
		unitcorr=1000.0
	elif s.unit_settings.system=='IMPERIAL':
		unitcorr=1/0.0254;
	else:
		unitcorr=1;
	rotcorr=180.0/pi

	use_experimental = bpy.context.user_preferences.addons['cam'].preferences.experimental
	
	
	def startNewFile():
		fileindex=''
		if split:
			fileindex='_'+str(findex)
		filename=basefilename+fileindex+extension
		c=postprocessor.Creator()

		# process user overrides for post processor settings
		
		if use_experimental and isinstance(c, iso.Creator):
			c.output_block_numbers = m.output_block_numbers
			c.start_block_number = m.start_block_number
			c.block_number_increment = m.block_number_increment
			c.output_tool_definitions = m.output_tool_definitions
			c.output_tool_change = m.output_tool_change
			c.output_g43_on_tool_change_line = m.output_g43_on_tool_change

		c.file_open(filename)
	
		#unit system correction
		###############
		if s.unit_settings.system=='METRIC':
			c.metric()
		elif s.unit_settings.system=='IMPERIAL':
			c.imperial()
		
		#start program
		c.program_begin(0,filename)
		c.flush_nc()
		c.comment('G-code generated with BlenderCAM and NC library')
		#absolute coordinates
		c.absolute()
		
		#work-plane, by now always xy, 
		c.set_plane(0)
		c.flush_nc()
		
		return c
		
	c=startNewFile()
	last_cutter=None;#[o.cutter_id,o.cutter_dameter,o.cutter_type,o.cutter_flutes]
	
	processedops=0
	last = Vector((0,0,0))
	
	for i,o in enumerate(operations):
	
		if use_experimental and o.output_header:
			lines = o.gcode_header.split(';')
			for aline in lines:
				c.write(aline + '\n')
			
		free_movement_height=o.free_movement_height#o.max.z+
		
		mesh=vertslist[i]
		verts=mesh.vertices[:]
		if o.machine_axes!='3':
			rots=mesh.shape_keys.key_blocks['rotations'].data
			
		#spindle rpm and direction
		###############
		if o.spindle_rotation_direction=='CW':
			spdir_clockwise=True
		else:
			spdir_clockwise=False
		
		#write tool, not working yet probably 
		#print (last_cutter)
		if ((not use_experimental) or m.output_tool_change) and last_cutter!=[o.cutter_id,o.cutter_diameter,o.cutter_type,o.cutter_flutes]:
			c.comment('Tool change - D = %s type %s flutes %s' % ( strInUnits(o.cutter_diameter,4),o.cutter_type, o.cutter_flutes))
			c.tool_change(o.cutter_id)
			c.flush_nc()
		
		last_cutter=[o.cutter_id,o.cutter_diameter,o.cutter_type,o.cutter_flutes]	
		

		c.spindle(o.spindle_rpm,spdir_clockwise)
		c.write_spindle()
		c.flush_nc()

		if m.spindle_start_time>0:
			c.dwell(m.spindle_start_time)
		c.flush_nc()

		
		# dhull c.feedrate(unitcorr*o.feedrate)
		
		
		
		#commands=[]
		m=bpy.context.scene.cam_machine
		
		millfeedrate=min(o.feedrate,m.feedrate_max)
		
		millfeedrate=unitcorr*max(millfeedrate,m.feedrate_min)
		plungefeedrate= millfeedrate*o.plunge_feedrate/100
		freefeedrate=m.feedrate_max*unitcorr
		fadjust=False
		if o.do_simulation_feedrate and mesh.shape_keys!= None and  mesh.shape_keys.key_blocks.find('feedrates')!=-1:
			shapek =  mesh.shape_keys.key_blocks['feedrates']
			
			fadjust=True
		
		if m.use_position_definitions:# dhull 
			last=Vector((m.starting_position.x, m.starting_position.y, m.starting_position.z))
		else:		
			if i<1:
				last=Vector((0.0,0.0,free_movement_height))#nonsense values so first step of the operation gets written for sure
		lastrot=Euler((0,0,0))
		duration=0.0
		f=0.1123456#nonsense value, so first feedrate always gets written 
		fadjustval = 1 # if simulation load data is Not present
		
		downvector= Vector((0,0,-1))
		plungelimit=(pi/2-o.plunge_angle)
		
		scale_graph=0.05 #warning this has to be same as in export in utils!!!!
		
		#print('2')
		for vi,vert in enumerate(verts):
			# skip the first vertex if this is a chained operation
			# ie: outputting more than one operation
			# otherwise the machine gets sent back to 0,0 for each operation which is unecessary
			if i>0 and vi==0:
				continue 
			v=vert.co
			if o.machine_axes!='3':
				v=v.copy()#we rotate it so we need to copy the vector
				r=Euler(rots[vi].co)
				#conversion to N-axis coordinates
				# this seems to work correctly for 4 axis.
				rcompensate=r.copy()
				rcompensate.x=-r.x
				rcompensate.y=-r.y
				rcompensate.z=-r.z
				v.rotate(rcompensate)
				
				if r.x==lastrot.x: 
					ra=None;
					#print(r.x,lastrot.x)
				else:	
					
					ra=r.x*rotcorr
					#print(ra,'RA')
				#ra=r.x*rotcorr
				if r.y==lastrot.y: rb=None;
				else:	rb=r.y*rotcorr
				#rb=r.y*rotcorr
				#print (	ra,rb)
				
				
				
			if vi>0 and v.x==last.x: vx=None; 
			else:	vx=v.x*unitcorr
			if vi>0 and v.y==last.y: vy=None; 
			else:	vy=v.y*unitcorr
			if vi>0 and v.z==last.z: vz=None; 
			else:	vz=v.z*unitcorr
			
			
			if fadjust:
				fadjustval = shapek.data[vi].co.z / scale_graph
				
				
			
			#v=(v.x*unitcorr,v.y*unitcorr,v.z*unitcorr)
			vect=v-last
			l=vect.length
			if vi>0	 and l>0 and downvector.angle(vect)<plungelimit:
				#print('plunge')
				#print(vect)
				if f!=plungefeedrate or (fadjust and fadjustval!=1):
					f=plungefeedrate * fadjustval
					c.feedrate(f)
					
				if o.machine_axes=='3':
					c.feed( x=vx, y=vy, z=vz )
				else:
					
					#print('plungef',ra,rb)
					c.feed( x=vx, y=vy, z=vz ,a = ra, b = rb)
					
			elif v.z>=free_movement_height or vi==0:#v.z==last.z==free_movement_height or vi==0
			
				if f!=freefeedrate:
					f=freefeedrate
					c.feedrate(f)
					
				if o.machine_axes=='3':
					c.rapid( x = vx , y = vy , z = vz )
				else:
					#print('rapidf',ra,rb)
					c.rapid(x=vx, y=vy, z = vz, a = ra, b = rb)
				#gcommand='{RAPID}'
				
			else:
				
				if f!=millfeedrate or (fadjust and fadjustval!=1):
					f=millfeedrate * fadjustval
					c.feedrate(f)
					
				if o.machine_axes=='3':
					c.feed(x=vx,y=vy,z=vz)
				else:
					#print('normalf',ra,rb)
					c.feed( x=vx, y=vy, z=vz ,a = ra, b = rb)

			
			duration+=vect.length/f
			#print(duration)
			last=v
			if o.machine_axes!='3':
				lastrot=r
				
			processedops+=1
			if split and processedops>m.split_limit:
				c.rapid(x=last.x*unitcorr,y=last.y*unitcorr,z=free_movement_height*unitcorr)
				#@v=(ch.points[-1][0],ch.points[-1][1],free_movement_height)
				findex+=1
				c.file_close()
				c=startNewFile()
				c.flush_nc()
				c.comment('Tool change - D = %s type %s flutes %s' % ( strInUnits(o.cutter_diameter,4),o.cutter_type, o.cutter_flutes))
				c.tool_change(o.cutter_id)
				c.spindle(o.spindle_rpm,spdir_clockwise)
				c.write_spindle()
				c.flush_nc()

				if m.spindle_start_time>0:
					c.dwell(m.spindle_start_time)
					c.flush_nc()
				
				c.feedrate(unitcorr*o.feedrate)
				c.rapid(x=last.x*unitcorr,y=last.y*unitcorr,z=free_movement_height*unitcorr)
				c.rapid(x=last.x*unitcorr,y=last.y*unitcorr,z=last.z*unitcorr)
				processedops=0
				
				
		
		c.feedrate(unitcorr*o.feedrate)
		
		if use_experimental and o.output_trailer:
			lines = o.gcode_trailer.split(';')
			for aline in lines:
				c.write(aline + '\n')
			
	o.duration=duration*unitcorr
	#print('duration')
	#print(o.duration)
	
	
	c.program_end()
	c.file_close()
	print(time.time()-t)

def curveToShapely(cob, use_modifiers = False):
	chunks=curveToChunks(cob, use_modifiers)
	polys=chunksToShapely(chunks)
	return polys
#separate function in blender, so you can offset any curve.
#FIXME: same algorithms as the cutout strategy, because that is hierarchy-respecting.
				
def silhoueteOffset(context,offset):
	bpy.context.scene.cursor_location=(0,0,0)
	ob=bpy.context.active_object
	if ob.type=='CURVE' or ob.type == 'FONT':
		silhs=curveToShapely(ob)
	else:
		silhs=getObjectSilhouete('OBJECTS',[ob])
	
	polys = []
	mp = shapely.ops.unary_union(silhs)
	mp = mp.buffer(offset, resolution = 64)
	shapelyToCurve('offset curve',mp,ob.location.z)
	
	
	return {'FINISHED'}
	
def polygonBoolean(context,boolean_type):
	bpy.context.scene.cursor_location=(0,0,0)
	ob=bpy.context.active_object
	obs=[]
	for ob1 in bpy.context.selected_objects:
		if ob1!=ob:
			obs.append(ob1)
	plist=curveToShapely(ob)
	p1 = sgeometry.asMultiPolygon(plist)
	polys=[]
	for o in obs:
		plist=curveToShapely(o)
		p2 = sgeometry.asMultiPolygon(plist)
		polys.append(p2)
	#print(polys)
	if boolean_type=='UNION':
		for p2 in polys:
			p1=p1.union(p2)
	elif boolean_type=='DIFFERENCE':
		for p2 in polys:
			p1=p1.difference(p2)
	elif boolean_type=='INTERSECT':
		for p2 in polys:
			p1=p1.intersection( p2)
		
	shapelyToCurve('boolean',p1,ob.location.z)
	#bpy.ops.object.convert(target='CURVE')
	#bpy.context.scene.cursor_location=ob.location
	#bpy.ops.object.origin_set(type='ORIGIN_CURSOR')

	return {'FINISHED'}
		

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
	

def comparezlevel(x):
	return x[5]

def overlaps(bb1,bb2):#true if bb1 is child of bb2
	ch1=bb1
	ch2=bb2
	if (ch2[1]>ch1[1]>ch1[0]>ch2[0] and ch2[3]>ch1[3]>ch1[2]>ch2[2]):
		return True


def connectChunksLow(chunks,o):	
	''' connects chunks that are close to each other without lifting, sampling them 'low' '''
	if not o.stay_low or (o.strategy=='CARVE' and o.carve_depth>0):
		return chunks
		
	connectedchunks=[]
	chunks_to_resample=[]#for OpenCAMLib sampling
	mergedist=3*o.dist_between_paths
	if o.strategy=='PENCIL':#this is bigger for pencil path since it goes on the surface to clean up the rests, and can go to close points on the surface without fear of going deep into material.
		mergedist=10*o.dist_between_paths
	
	if o.strategy=='MEDIAL_AXIS':
		mergedist= 1*o.medial_axis_subdivision
	
	if o.parallel_step_back:
		mergedist*=2
		
	if o.merge_dist>0:
		mergedist=o.merge_dist
	#mergedist=10
	lastch=None
	i=len(chunks)
	pos=(0,0,0)
	
	for ch in chunks:
		if len(ch.points)>0:
			if lastch!=None and (ch.distStart(pos,o)<mergedist):
				#CARVE should lift allways, when it goes below surface...
				#print(mergedist,ch.dist(pos,o))
				if o.strategy=='PARALLEL' or o.strategy=='CROSS' or o.strategy=='PENCIL':# for these paths sorting happens after sampling, thats why they need resample the connection
					between=samplePathLow(o,lastch,ch,True)
				else:
					#print('addbetwee')
					between=samplePathLow(o,lastch,ch,False)#other paths either dont use sampling or are sorted before it.
			
				if o.use_opencamlib and o.use_exact and (o.strategy=='PARALLEL' or o.strategy=='CROSS' or o.strategy=='PENCIL'):
					chunks_to_resample.append( (connectedchunks[-1], len(connectedchunks[-1].points), len(between.points) ) )
					
				connectedchunks[-1].points.extend(between.points)
				connectedchunks[-1].points.extend(ch.points)
			else:
				connectedchunks.append(ch)
			lastch=ch
			pos=lastch.points[-1]
			
	if o.use_opencamlib and o.use_exact:
		oclResampleChunks(o, chunks_to_resample)
		
	return connectedchunks

def getClosest(o,pos,chunks):
	#ch=-1
	mind=10000
	d=100000000000
	ch=None
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
	return ch
	
def sortChunks(chunks,o):
	if o.strategy!='WATERLINE':
		progress('sorting paths')
	sys.setrecursionlimit(100000)# the getNext() function of CamPathChunk was running out of recursion limits.
	sortedchunks=[]
	chunks_to_resample=[]
	
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
			ch = getClosest(o,pos,chunks)
		elif len(lastch.parents)>0:# looks in parents for next candidate, recursively
			#get siblings here
			#siblings=[]
			#for chs in lastch.parents:
			#	siblings.extend(chs.children)
			#ch = getClosest(o,pos,siblings)
			#if ch==None:
			#	ch = getClosest(o,pos,chunks)
			for parent in lastch.parents:
				ch=parent.getNextClosest(o,pos)
				if ch!=None:
					break
			if ch==None:
				ch = getClosest(o,pos,chunks)
			#	break
			#pass;
		if ch is not None:#found next chunk, append it to list
			#only adaptdist the chunk if it has not been sorted before
			if not ch.sorted:
				ch.adaptdist(pos, o)
				ch.sorted = True
			#print(len(ch.parents),'children')
			chunks.remove(ch)
			sortedchunks.append(ch)
			lastch = ch
			pos = lastch.points[-1]
		#print(i, len(chunks))
		# experimental fix for infinite loop problem
		#else:
			# THIS PROBLEM WASN'T HERE AT ALL. but keeping it here, it might fix the problems somwhere else:)
			# can't find chunks close enough and still some chunks left
			# to be sorted. For now just move the remaining chunks over to 
			# the sorted list.
			# This fixes an infinite loop condition that occurs sometimes.
			# This is a bandaid fix: need to find the root cause of this problem
			# suspect it has to do with the sorted flag?
			#print("no chunks found closest. Chunks not sorted: ", len(chunks))
			#sortedchunks.extend(chunks)
			#chunks[:] = []
			
		i -= 1
		
	
	sys.setrecursionlimit(1000)
	if o.strategy!='DRILL' and o.strategy != 'OUTLINEFILL': #THIS SHOULD AVOID ACTUALLY MOST STRATEGIES, THIS SHOULD BE DONE MANUALLY, BECAUSE SOME STRATEGIES GET SORTED TWICE.
		sortedchunks = connectChunksLow(sortedchunks,o)
	return sortedchunks


	

	


def getVectorRight(lastv,verts):#most right vector from a set regarding angle..
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

def getOperationSilhouete(operation):
	'''gets silhouete for the operation
		uses image thresholding for everything except curves.
	'''
	if operation.update_silhouete_tag:
		image=None
		objects=None
		if operation.geometry_source=='OBJECT' or operation.geometry_source=='GROUP':
			if operation.onlycurves==False:
				stype='OBJECTS'
			else:
				stype='CURVES'
		else:
			stype='IMAGE'
			
		totfaces=0
		if stype=='OBJECTS':
			for ob in operation.objects:
				if ob.type=='MESH':
					totfaces+=len(ob.data.polygons)
			
		
			
		if (stype == 'OBJECTS' and totfaces>200000) or stype=='IMAGE':
			print('image method')
			samples = renderSampleImage(operation)
			if stype=='OBJECTS':
				i = samples > operation.minz-0.0000001#numpy.min(operation.zbuffer_image)-0.0000001##the small number solves issue with totally flat meshes, which people tend to mill instead of proper pockets. then the minimum was also maximum, and it didn't detect contour.
			else:
				i = samples > numpy.min(operation.zbuffer_image)#this fixes another numeric imprecision.
				
			chunks=	imageToChunks(operation,i)
			operation.silhouete=chunksToShapely(chunks)
			#print(operation.silhouete)
			#this conversion happens because we need the silh to be oriented, for milling directions.
		else:
			print('object method for retrieving silhouette')#
			operation.silhouete=getObjectSilhouete(stype, objects = operation.objects)
				
		operation.update_silhouete_tag=False
	return operation.silhouete
		
def getObjectSilhouete(stype, objects=None, use_modifiers = False):
	#o=operation
	if stype=='CURVES':#curve conversion to polygon format
		allchunks=[]
		for ob in objects:
			chunks=curveToChunks(ob)
			allchunks.extend(chunks)
		silhouete=chunksToShapely(allchunks)
		
	elif stype=='OBJECTS':
		totfaces=0
		for ob in objects:
			totfaces+=len(ob.data.polygons)
			
		if totfaces<20000000:#boolean polygons method originaly was 20 000 poly limit, now limitless, it might become teribly slow, but who cares?
			t=time.time()
			print('shapely getting silhouette')
			polys=[]
			for ob in objects:
				
				if use_modifiers:
					m = ob.to_mesh(bpy.context.scene, True, 'RENDER')
				else:
					m = ob.data
				mw = ob.matrix_world
				mwi = mw.inverted()
				r=ob.rotation_euler
				m.calc_tessface()
				id=0
				e=0.000001
				scaleup=100
				for f in m.tessfaces:
					n=f.normal.copy()
					n.rotate(r)
					#verts=[]
					#for i in f.vertices:
					#	verts.append(mw*m.vertices[i].co)
					#n=mathutils.geometry.normal(verts[0],verts[1],verts[2])
					if f.area>0 and n.z!=0:#n.z>0.0 and f.area>0.0 :
						s=[]
						c=mw * f.center
						c=c.xy
						for i in f.vertices:
							v=mw* m.vertices[i].co
							s.append((v.x,v.y))
						if len(s)>2:
							#print(s)
							p=spolygon.Polygon(s)
							#print(dir(p))
							if p.is_valid:
								#polys.append(p)
								polys.append(p.buffer(e,resolution = 0))
						#if id==923:
						#	m.polygons[923].select
						id+=1
				if use_modifiers:
					bpy.data.meshes.remove(m)	
			#print(polys
			if totfaces<20000:
				p=sops.unary_union(polys)
			else:	
				print('computing in parts')
				bigshapes=[]
				i=1
				part=20000
				while i*part<totfaces:
					print(i)
					ar=polys[(i-1)*part:i*part]
					bigshapes.append(sops.unary_union(ar))
					i+=1
				if (i-1)*part<totfaces:
					last_ar = polys[(i-1)*part:]
					bigshapes.append(sops.unary_union(last_ar))
				print('joining')
				p=sops.unary_union(bigshapes)
					
			print(time.time()-t)
			
			t=time.time()
			silhouete = [p]#[polygon_utils_cam.Shapely2Polygon(p)]
		
	return silhouete
	
def getAmbient(o):
	if o.update_ambient_tag:
		if o.ambient_cutter_restrict:#cutter stays in ambient & limit curve
			m=o.cutter_diameter/2
		else: m=0

		if o.ambient_behaviour=='AROUND':
			r=o.ambient_radius - m
			o.ambient = getObjectOutline( r , o , True)# in this method we need ambient from silhouete
		else:
			o.ambient=spolygon.Polygon(((o.min.x + m ,o.min.y + m ) , (o.min.x + m ,o.max.y - m ),(o.max.x - m ,o.max.y - m ),(o.max.x - m , o.min.y + m )))
		
		if o.use_limit_curve:
			if o.limit_curve!='':
				limit_curve=bpy.data.objects[o.limit_curve]
				#polys=curveToPolys(limit_curve)
				polys = curveToShapely(limit_curve)
				o.limit_poly=shapely.ops.unary_union(polys)
				#for p in polys:
				#	o.limit_poly+=p
				if o.ambient_cutter_restrict:
					o.limit_poly = o.limit_poly.buffer(o.cutter_diameter/2,resolution = o.circle_detail)
			o.ambient = o.ambient.intersection(o.limit_poly)
	o.update_ambient_tag=False
	
def getObjectOutline(radius,o,Offset):#FIXME: make this one operation independent
#circle detail, optimize, optimize thresold.
	
	polygons=getOperationSilhouete(o)
	
	i=0
	#print('offseting polygons')
		
	if Offset:
		offset=1
	else:
		offset=-1
		
	outlines=[]
	i=0
	#print(polygons, polygons.type)
	for p1 in polygons:#sort by size before this???
		print(p1.type,len(polygons))
		i+=1
		if radius>0:
			p1 = p1.buffer(radius*offset,resolution = o.circle_detail)
		outlines.append(p1)
	
	print(outlines)
	if o.dont_merge:
		outline=sgeometry.MultiPolygon(outlines)
		#for ci in range(0,len(p)):
		#	outline.addContour(p[ci],p.isHole(ci))
	else:
		#print(p)
		outline=shapely.ops.unary_union(outlines)
		#outline = sgeometry.MultiPolygon([outline])
	#shapelyToCurve('oboutline',outline,0)
	return outline
	
def addOrientationObject(o):
	'''the orientation object should be used to set up orientations of the object for 4 and 5 axis milling.'''
	name = o.name+' orientation'
	s=bpy.context.scene
	if s.objects.find(name)==-1:
		bpy.ops.object.empty_add(type='ARROWS', view_align=False, location=(0,0,0))

		ob=bpy.context.active_object
		ob.empty_draw_size=0.05
		ob.show_name=True
		ob.name=name
	ob=s.objects[name]
	if o.machine_axes=='4':
		
		if o.rotary_axis_1=='X':
			ob.lock_rotation=[False,True,True]
			ob.rotation_euler[1]=0
			ob.rotation_euler[2]=0
		if o.rotary_axis_1=='Y':
			ob.lock_rotation=[True,False,True]
			ob.rotation_euler[0]=0
			ob.rotation_euler[2]=0
		if o.rotary_axis_1=='Z':
			ob.lock_rotation=[True,True,False]
			ob.rotation_euler[0]=0
			ob.rotation_euler[1]=0
	elif o.machine_axes=='5':
		ob.lock_rotation=[False,False,True]
		
		ob.rotation_euler[2]=0#this will be a bit hard to rotate.....
#def addCutterOrientationObject(o):
	
			
def removeOrientationObject(o):#not working
	name=o.name+' orientation'
	if bpy.context.scene.objects.find(name)>-1:
		ob=bpy.context.scene.objects[name]
		delob(ob)

def addTranspMat(ob,mname,color,alpha):	
	if mname in bpy.data.materials:
			m=bpy.data.materials[mname]
	else:
		bpy.ops.material.new()
		for m in bpy.data.materials:
			if m.name[:8] == 'Material' and m.users==0:
				m.name = mname
				break;
	ob.data.materials.append(m)
			
	ob.active_material.diffuse_color = color
	ob.active_material.use_transparency = True
	ob.active_material.alpha = alpha
	ob.show_transparent = True
	ob.draw_type = 'SOLID'
		
def addMachineAreaObject():
	
	s=bpy.context.scene
	ao=bpy.context.active_object
	if s.objects.get('CAM_machine')!=None:
	   o=s.objects['CAM_machine']
	else:
		oldunits = s.unit_settings.system
		# need to be in metric units when adding machine mesh object
		# in order for location to work properly
		s.unit_settings.system = 'METRIC'
		bpy.ops.mesh.primitive_cube_add(view_align=False, enter_editmode=False, location=(1, 1, -1), rotation=(0, 0, 0))
		o=bpy.context.active_object
		o.name='CAM_machine'
		o.data.name='CAM_machine'
		bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)
		o.draw_type = 'SOLID'
		bpy.ops.object.editmode_toggle()
		bpy.ops.mesh.delete(type='ONLY_FACE')
		bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE', action='TOGGLE')
		bpy.ops.mesh.select_all(action='TOGGLE')
		bpy.ops.mesh.subdivide(number_cuts=32, smoothness=0, quadtri=False, quadcorner='STRAIGHT_CUT', fractal=0, fractal_along_normal=0, seed=0)
		bpy.ops.mesh.select_nth(nth=2, offset=0)
		bpy.ops.mesh.delete(type='EDGE')
		bpy.ops.mesh.primitive_cube_add(view_align=False, enter_editmode=False, location=(1, 1, -1), rotation=(0, 0, 0))

		bpy.ops.object.editmode_toggle()
		addTranspMat(o,"violet_transparent",(0.800000, 0.530886, 0.725165),0.1)
		o.hide_render = True
		o.hide_select = True
		o.select=False
		s.unit_settings.system = oldunits
	#bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
	   
	o.dimensions=bpy.context.scene.cam_machine.working_area
	if ao!=None:
		activate(ao)
	else:
		bpy.context.scene.objects.active=None

			
def addMaterialAreaObject():
	s=bpy.context.scene
	operation=s.cam_operations[s.cam_active_operation]
	getOperationSources(operation)
	getBounds(operation)
	
	
	ao=bpy.context.active_object
	if s.objects.get('CAM_material')!=None:
	   o=s.objects['CAM_material']
	else:
		bpy.ops.mesh.primitive_cube_add(view_align=False, enter_editmode=False, location=(1, 1, -1), rotation=(0, 0, 0))
		o=bpy.context.active_object
		o.name='CAM_material'
		o.data.name='CAM_material'
		bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)
		
		addTranspMat(o,'blue_transparent',(0.458695, 0.794658, 0.8),0.1)
		o.hide_render = True
		o.hide_select = True
		o.select=False
	#bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
	   
	o.dimensions=bpy.context.scene.cam_machine.working_area
	
	
	o.dimensions=(operation.max.x-operation.min.x,operation.max.y-operation.min.y,operation.max.z-operation.min.z)
	o.location=(operation.min.x,operation.min.y,operation.max.z)
	if ao!=None:
		activate(ao)
	else:
		bpy.context.scene.objects.active=None		


def getContainer():
	s=bpy.context.scene
	if s.objects.get('CAM_OBJECTS')==None:
		bpy.ops.object.empty_add(type='PLAIN_AXES', view_align=False)
		container=bpy.context.active_object
		container.name='CAM_OBJECTS'
		container.location=[0,0,0]
		container.hide=True
	else:
		container=s.objects['CAM_OBJECTS']
	
	return container

def addBridge(x,y,rot,sizex, sizey):
	bpy.ops.mesh.primitive_plane_add(radius=sizey, view_align=False, enter_editmode=False, location=(0, 0, 0))
	b=bpy.context.active_object
	b.name = 'bridge'
	#b.show_name=True
	b.dimensions.x=sizex
	bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
	
	bpy.ops.object.editmode_toggle()
	bpy.ops.transform.translate(value=(0, sizey/2, 0), constraint_axis=(False, True, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
	bpy.ops.object.editmode_toggle()
	bpy.ops.object.convert(target='CURVE')

	b.location = x, y, 0
	b.rotation_euler.z=rot
	return b

def addAutoBridges(o):
	'''attempt to add auto bridges as set of curves'''
	getOperationSources(o)
	#if not o.onlycurves:
	#	o.warnings+=('not curves')
	#	return;
	bridgegroupname=o.bridges_group_name
	if bridgegroupname == '' or bpy.data.groups.get(bridgegroupname) == None:
		bridgegroupname = 'bridges_'+o.name
		bpy.data.groups.new(bridgegroupname)
	g= bpy.data.groups[bridgegroupname]
	o.bridges_group_name = bridgegroupname
	for ob in o.objects:
		
		if ob.type=='CURVE' or ob.type=='TEXT':
			curve = curveToShapely(ob)
		if ob.type == 'MESH':
			
			curve = getObjectSilhouete('OBJECTS',[ob])
		#curve = shapelyToMultipolygon(curve)
		for c in curve:
			c=c.exterior
			minx, miny, maxx, maxy = c.bounds
			d1 = c.project(sgeometry.Point(maxx+1000, (maxy+miny)/2.0))
			p = c.interpolate(d1)
			g.objects.link( addBridge(p.x,p.y,-pi/2,o.bridges_width, o.cutter_diameter*1))
			d1 = c.project(sgeometry.Point(minx-1000, (maxy+miny)/2.0))
			p = c.interpolate(d1)
			g.objects.link( addBridge(p.x,p.y,pi/2,o.bridges_width, o.cutter_diameter*1))
			d1 = c.project(sgeometry.Point((minx + maxx)/2.0, maxy + 1000))
			p = c.interpolate(d1)
			g.objects.link( addBridge(p.x,p.y,0,o.bridges_width, o.cutter_diameter*1))
			d1 = c.project(sgeometry.Point((minx + maxx) / 2.0 , miny - 1000))
			p = c.interpolate(d1)
			g.objects.link( addBridge(p.x,p.y,pi,o.bridges_width, o.cutter_diameter*1))

	
def getBridgesPoly(o):
	if not hasattr(o, 'bridgespolyorig'):
		bridgegroupname=o.bridges_group_name
		bridgegroup=bpy.data.groups[bridgegroupname]
		shapes=[]
		bpy.ops.object.select_all(action='DESELECT')

		for ob in bridgegroup.objects:
			if ob.type == 'CURVE':
				ob.select=True
		bpy.context.scene.objects.active = ob
		bpy.ops.object.duplicate();
		bpy.ops.object.join()
		ob = bpy.context.active_object
		shapes.extend(curveToShapely(ob, o.use_bridge_modifiers))
		ob.select=True
		bpy.ops.object.delete(use_global=False)
		bridgespoly=sops.unary_union(shapes)
		

		#buffer the poly, so the bridges are not actually milled...
		o.bridgespolyorig = bridgespoly.buffer(distance = o.cutter_diameter/2.0)
		o.bridgespoly_boundary = o.bridgespolyorig.boundary
		o.bridgespoly_boundary_prep = prepared.prep(o.bridgespolyorig.boundary)
		o.bridgespoly = prepared.prep(o.bridgespolyorig)
	
def useBridges(ch,o):
	'''this adds bridges to chunks, takes the bridge-objects group and uses the curves inside it as bridges.'''
	bridgegroupname=o.bridges_group_name
	bridgegroup=bpy.data.groups[bridgegroupname]
	if len(bridgegroup.objects)>0:
		

		#get bridgepoly
		getBridgesPoly(o)
		
		####
		bridgeheight=min(0,o.min.z+o.bridges_height)
		vi=0
		#shapelyToCurve('test',bridgespoly,0)
		newpoints=[]
		p1=sgeometry.Point(ch.points[0])
		startinside = o.bridgespoly.contains(p1)
		interrupted = False
		while vi<len(ch.points):
			i1=vi
			i2=vi
			chp1=ch.points[i1]
			chp2=ch.points[i1]#Vector(v1)#this is for case of last point and not closed chunk..
			if vi+1<len(ch.points):
				i2 = vi+1
				chp2=ch.points[vi+1]#Vector(ch.points[vi+1])
			v1=Vector(chp1)
			v2=Vector(chp2)
			if v1.z<bridgeheight or v2.z<bridgeheight:
				v=v2-v1
				#dist+=v.length
				p2=sgeometry.Point(chp2)
				
				if interrupted:
					p1=sgeometry.Point(chp1)
					startinside = o.bridgespoly.contains(p1)
					interrupted = False
					
					
				endinside = o.bridgespoly.contains(p2)
				l=sgeometry.LineString([chp1,chp2])
				#print(dir(bridgespoly_boundary))
				if o.bridgespoly_boundary_prep.intersects(l):
					#print('intersects')
					intersections = o.bridgespoly_boundary.intersection(l)
				else:
					intersections = sgeometry.GeometryCollection()
					
				itempty = intersections.type == 'GeometryCollection'
				itpoint = intersections.type == 'Point'
				itmpoint = intersections.type == 'MultiPoint'
				
				#print(startinside, endinside,intersections, intersections.type)
				#print(l,bridgespoly)
				if not startinside:
					#print('nothing found')
					
					newpoints.append(chp1)
				#elif startinside and endinside and itempty:
				#	newpoints.append((chp1[0],chp1[1],max(chp1[2],bridgeheight)))
				elif startinside:
					newpoints.append((chp1[0],chp1[1],max(chp1[2],bridgeheight)))
				#elif not startinside:
				#	newpoints.append(chp1)
				cpoints=[]
				if itpoint:
					cpoints= [Vector((intersections.x,intersections.y,intersections.z))]
				elif itmpoint:
					cpoints=[]
					for p in intersections:
						cpoints.append(Vector((p.x,p.y,p.z)))
				#####sort collisions here :(
				ncpoints=[]
				while len(cpoints)>0:
					mind=10000000
					mini=-1
					for i,p in enumerate(cpoints):
						if min(mind, (p-v1).length)<mind:
							mini=i
							mind= (p-v1).length
					ncpoints.append(cpoints.pop(mini))
				cpoints = ncpoints
				#endsorting
				
				
				if startinside:
					isinside=True
				else:	
					isinside=False
				for cp in cpoints:
					v3= cp
					#print(v3)
					if v.length==0:
						ratio=1
					else:
						fractvect = v3 - v1
						ratio = fractvect.length/v.length
						
					collisionz=v1.z+v.z*ratio
					np1 = (v3.x, v3.y, collisionz)
					np2	= (v3.x, v3.y, max(collisionz,bridgeheight))
					if not isinside:
						newpoints.extend((np1, np2))
					else:
						newpoints.extend((np2, np1))
					isinside = not isinside
					
				startinside = endinside
				p1=p2
				
				vi+=1
			else:
				newpoints.append(chp1)
				vi+=1
				interrupted = True
		ch.points=newpoints

def getLayers(operation, startdepth, enddepth):
	'''returns a list of layers bounded by startdepth and enddepth
	   uses operation.stepdown to determine number of layers.
	'''
	if operation.use_layers:
		layers = []
		n = math.ceil((startdepth - enddepth) / operation.stepdown)
		layerstart = operation.maxz
		for x in range(0, n):
			layerend = max(startdepth - ((x+1) * operation.stepdown), enddepth)
			if int(layerstart * 10**8) != int(layerend * 10**8):#it was possible that with precise same end of operation, last layer was done 2x on exactly same level...
				layers.append([layerstart, layerend])
			layerstart = layerend
	else:
			layers = [[startdepth, enddepth]]
	
	return layers
	
###########cutout strategy is completely here:
def strategy_cutout( o ):
	#ob=bpy.context.active_object
	print('operation: cutout')
	offset=True
	if o.cut_type=='ONLINE' and o.onlycurves==True:#is separate to allow open curves :)
		print('separate')
		chunksFromCurve=[]
		for ob in o.objects:
			chunksFromCurve.extend(curveToChunks(ob, o.use_modifiers))
		for ch in chunksFromCurve:
			#print(ch.points)
			
			if len(ch.points)>2:
				ch.poly=chunkToShapely(ch)
				#p.addContour(ch.poly)
	else:
		chunksFromCurve=[]
		if o.cut_type=='ONLINE':
			p=getObjectOutline(0,o,True)
			
		else:
			offset=True
			if o.cut_type=='INSIDE':
				offset=False
				
			p=getObjectOutline(o.cutter_diameter/2,o,offset)
			if o.outlines_count>1:
				for i in range(1,o.outlines_count):
					chunksFromCurve.extend(shapelyToChunks(p,-1))
					p = p.buffer(distance = o.dist_between_paths * offset, resolution = o.circle_detail)
			
				
		chunksFromCurve.extend(shapelyToChunks(p,-1))
		if o.outlines_count>1 and o.movement_insideout=='OUTSIDEIN':
			chunksFromCurve.reverse()
			
	#parentChildPoly(chunksFromCurve,chunksFromCurve,o)
	chunksFromCurve=limitChunks(chunksFromCurve,o)
	if not o.dont_merge:
		parentChildPoly(chunksFromCurve,chunksFromCurve,o)
	if o.outlines_count==1:
		chunksFromCurve=sortChunks(chunksFromCurve,o)
	
	#if o.outlines_count>0 and o.cut_type!='ONLINE' and o.movement_insideout=='OUTSIDEIN':#reversing just with more outlines
	#	chunksFromCurve.reverse()
					
	if (o.movement_type=='CLIMB' and o.spindle_rotation_direction=='CCW') or (o.movement_type=='CONVENTIONAL' and o.spindle_rotation_direction=='CW'):
		for ch in chunksFromCurve:
			ch.points.reverse()
		
	if o.cut_type=='INSIDE':#there would bee too many conditions above, so for now it gets reversed once again when inside cutting.
		for ch in chunksFromCurve:
			ch.points.reverse()
			
	
	layers = getLayers(o, o.maxz, o.min.z)
		
	extendorder=[]
	if o.first_down:#each shape gets either cut all the way to bottom, or every shape gets cut 1 layer, then all again. has to create copies, because same chunks are worked with on more layers usually
		for chunk in chunksFromCurve:
			for layer in layers:
				extendorder.append([chunk.copy(),layer])
	else:
		for layer in layers:
			for chunk in chunksFromCurve:
				extendorder.append([chunk.copy(),layer])
	
	for chl in extendorder:#Set Z for all chunks
		chunk=chl[0]
		layer=chl[1]
		print(layer[1])
		chunk.setZ(layer[1])
	
	chunks=[]
	
	

	if o.use_bridges:#add bridges to chunks
		#bridges=getBridges(p,o)
		print('using bridges')
		bridgeheight=min(0,o.min.z+o.bridges_height)
		for chl in extendorder:
			chunk=chl[0]
			layer=chl[1]
			if layer[1]<bridgeheight:
				useBridges(chunk,o)
				
	if o.ramp:#add ramps or simply add chunks
		for chl in extendorder:
			chunk=chl[0]
			layer=chl[1]
			if chunk.closed:
				chunk.rampContour(layer[0],layer[1],o)
				chunks.append(chunk)
			else:
				chunk.rampZigZag(layer[0],layer[1],o)
				chunks.append(chunk)
	else:
		for chl in extendorder:
			chunks.append(chl[0])
			

	chunksToMesh(chunks,o)

def strategy_curve( o ):
	print('operation: curve')
	pathSamples=[]
	getOperationSources(o)
	if not o.onlycurves:
		o.warnings+= 'at least one of assigned objects is not a curve\n'
	#ob=bpy.data.objects[o.object_name]
	for ob in o.objects:
		pathSamples.extend(curveToChunks(ob))
	pathSamples=sortChunks(pathSamples,o)#sort before sampling
	pathSamples=chunksRefine(pathSamples,o)
	
	if o.ramp:
		for ch in pathSamples:
			ch.rampZigZag(ch.zstart, ch.points[0][2],o)
			
	chunksToMesh(pathSamples,o)
	
def strategy_proj_curve( s, o ):
	print('operation: projected curve')
	pathSamples = []
	chunks = []
	ob = bpy.data.objects[o.curve_object]
	pathSamples.extend(curveToChunks(ob))
	
	targetCurve = s.objects[o.curve_object1]
	
	from cam import chunk
	if targetCurve.type != 'CURVE':
		o.warnings = o.warnings+'Projection target and source have to be curve objects!\n '
		return
	'''	#mesh method is highly unstable, I don't like itwould be there at all.... better to use curves.
	if targetCurve.type=='MESH':
		
		c=targetCurve
		for ch in pathSamples:
			ch.depth=0
			for i,s in enumerate(ch.points):
				np=c.closest_point_on_mesh(s)
				ch.startpoints.append(Vector(s))
				ch.endpoints.append(np[0])
				ch.rotations.append((0,0,0))
				vect = np[0]-Vector(s)
				
				ch.depth=min(ch.depth,-vect.length)
	else:
	'''
	if 1:
		extend_up = 0.1
		extend_down = 0.04
		tsamples = curveToChunks(targetCurve)
		for chi,ch in enumerate(pathSamples):
			cht = tsamples[chi].points
			ch.depth = 0
			for i,s in enumerate(ch.points):
				#move the points a bit
				ep = Vector(cht[i])
				sp = Vector(ch.points[i])
				#extend startpoint
				vecs = sp-ep
				vecs.normalize()
				vecs *= extend_up
				sp += vecs
				ch.startpoints.append(sp)
				
				#extend endpoint
				vece = sp - ep
				vece.normalize()
				vece *= extend_down
				ep -= vece
				ch.endpoints.append(ep)
						
				ch.rotations.append((0,0,0))
				
				vec = sp - ep
				ch.depth = min(ch.depth,-vec.length)
				ch.points[i] = sp.copy()
			
	layers = getLayers(o, 0, ch.depth)		
	
	chunks.extend(sampleChunksNAxis(o,pathSamples,layers))
	#for ch in pathSamples:
	#	ch.points=ch.endpoints
	chunksToMesh(chunks,o)

def strategy_pocket( o ):
	print('operation: pocket')
	p=getObjectOutline(o.cutter_diameter/2,o,False)
	approxn=(min(o.max.x-o.min.x,o.max.y-o.min.y)/o.dist_between_paths)/2
	i=0
	chunks=[]
	chunksFromCurve=[]
	lastchunks=[]
	centers=None
	firstoutline = p#for testing in the end.
	prest = p.buffer(-o.cutter_diameter/2, o.circle_detail)
	#shapelyToCurve('testik',p,0)
	while not p.is_empty:
		nchunks=shapelyToChunks(p,o.min.z)
		
		
		pnew=p.buffer(-o.dist_between_paths,o.circle_detail)

		if o.dist_between_paths>o.cutter_diameter/2.0:			
			prest= prest.difference(pnew.boundary.buffer(o.cutter_diameter/2, o.circle_detail))
			if not(pnew.contains(prest)):
				#shapelyToCurve('cesta',pnew,0)
				#shapelyToCurve('problemas',prest,0)
				prest = shapelyToMultipolygon(prest)
				fine=[]
				go = []
				for p1 in prest:
					if pnew.contains(p1):
						fine.append(p1)
					else:
						go.append(p1)
				if len(go)>0:
					for p1 in go:
						nchunks1=shapelyToChunks(p1,o.min.z)
						nchunks.extend(nchunks1)
						prest=sgeometry.MultiPolygon(fine)
						
		nchunks=limitChunks(nchunks,o)
		chunksFromCurve.extend(nchunks)
		print(i)
		parentChildDist(lastchunks,nchunks,o)
		#print('parented')
		lastchunks=nchunks
		
		
		percent=int(i/approxn*100)
		progress('outlining polygons ',percent) 
		p=pnew
		
		i+=1
	
	#if (o.poc)#TODO inside outside!
	if (o.movement_type=='CLIMB' and o.spindle_rotation_direction=='CW') or (o.movement_type=='CONVENTIONAL' and o.spindle_rotation_direction=='CCW'):
		for ch in chunksFromCurve:
			ch.points.reverse()
			
			
	#if bpy.app.debug_value==1:

	chunksFromCurve=sortChunks(chunksFromCurve,o)
		
	chunks=[]
	layers = getLayers(o, o.maxz, o.min.z)

	#print(layers)
	#print(chunksFromCurve)
	#print(len(chunksFromCurve))
	for l in layers:
		lchunks = setChunksZ(chunksFromCurve,l[1])
		if o.ramp:
			for ch in lchunks:
				ch.zstart = l[0]
				ch.zend = l[1]
		
		###########helix_enter first try here TODO: check if helix radius is not out of operation area.
		if o.helix_enter:
			helix_radius=o.cutter_diameter*0.5*o.helix_diameter*0.01#90 percent of cutter radius
			helix_circumference=helix_radius*pi*2
			
			revheight=helix_circumference*tan(o.ramp_in_angle)
			for chi,ch in enumerate(lchunks):
				if chunksFromCurve[chi].children==[]:
					p=ch.points[0]#TODO:intercept closest next point when it should stay low 
					#first thing to do is to check if helix enter can really enter.
					checkc=Circle(helix_radius+o.cutter_diameter/2,o.circle_detail)
					checkc = affinity.translate(checkc,p[0],p[1])
					covers=False
					for poly in o.silhouete:
						if poly.contains(checkc):
							covers=True
							break;
					
					if covers:
						revolutions=(l[0]-p[2])/revheight
						#print(revolutions)
						h=Helix(helix_radius,o.circle_detail, l[0],p,revolutions)
						#invert helix if not the typical direction
						if (o.movement_type=='CONVENTIONAL' and o.spindle_rotation_direction=='CW') or (o.movement_type=='CLIMB'	and o.spindle_rotation_direction=='CCW'):
							nhelix=[]
							for v in h:
								nhelix.append((2*p[0]-v[0],v[1],v[2]))
							h=nhelix
						ch.points=h+ch.points
					else:
						o.warnings=o.warnings+'Helix entry did not fit! \n '
						ch.closed=True
						ch.rampZigZag(l[0],l[1],o)
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
						
					c=sgeometry.Polygon(c)
					#print('çoutline')
					#print(c)
					coutline = c.buffer(o.cutter_diameter/2,o.circle_detail)
					#print(h)
					#print('çoutline')
					#print(coutline)
					#polyToMesh(coutline,0)
					rothelix.reverse()
					
					covers=False
					for poly in o.silhouete:
						if poly.contains(coutline):
							covers=True
							break;
					
					if covers:
						ch.points.extend(rothelix)
						
		chunks.extend(lchunks)

	if o.ramp:
		for ch in chunks:
			ch.rampZigZag(ch.zstart, ch.points[0][2], o)

	if o.first_down:
		chunks = sortChunks(chunks, o)

		
	chunksToMesh(chunks,o)
		
def strategy_drill( o ):
	print('operation: Drill')
	chunks=[]
	for ob in o.objects:
		activate(ob)
	
		bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked":False, "mode":'TRANSLATION'}, TRANSFORM_OT_translate={"value":(0, 0, 0), "constraint_axis":(False, False, False), "constraint_orientation":'GLOBAL', "mirror":False, "proportional":'DISABLED', "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "texture_space":False, "release_confirm":False})
		bpy.ops.group.objects_remove_all()
		bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')

		ob=bpy.context.active_object
		if ob.type=='CURVE':
			ob.data.dimensions='3D'
		try:
			bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)
			bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
			bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
			
		except:
			pass
		l=ob.location
		
		if ob.type=='CURVE':
			
			for c in ob.data.splines:
				maxx,minx,maxy,miny,maxz,minz=-10000,10000,-10000,10000,-10000,10000
				for p in c.points:
					if o.drill_type=='ALL_POINTS':
						chunks.append(camPathChunk([(p.co.x+l.x,p.co.y+l.y,p.co.z+l.z)]))
					minx=min(p.co.x,minx)
					maxx=max(p.co.x,maxx)
					miny=min(p.co.y,miny)
					maxy=max(p.co.y,maxy)
					minz=min(p.co.z,minz)
					maxz=max(p.co.z,maxz)
				for p in c.bezier_points:
					if o.drill_type=='ALL_POINTS':
						chunks.append(camPathChunk([(p.co.x+l.x,p.co.y+l.y,p.co.z+l.z)]))
					minx=min(p.co.x,minx)
					maxx=max(p.co.x,maxx)
					miny=min(p.co.y,miny)
					maxy=max(p.co.y,maxy)
					minz=min(p.co.z,minz)
					maxz=max(p.co.z,maxz)
				cx=(maxx+minx)/2
				cy=(maxy+miny)/2
				cz=(maxz+minz)/2
				
				center=(cx,cy)
				aspect=(maxx-minx)/(maxy-miny)
				if (1.3>aspect>0.7 and o.drill_type=='MIDDLE_SYMETRIC') or o.drill_type=='MIDDLE_ALL': 
					chunks.append(camPathChunk([(center[0]+l.x,center[1]+l.y,cz+l.z)]))
						
		elif ob.type=='MESH':
			for v in ob.data.vertices:
				chunks.append(camPathChunk([(v.co.x+l.x,v.co.y+l.y,v.co.z+l.z)]))
		delob(ob)#delete temporary object with applied transforms

	layers = getLayers(o, o.maxz, o.min.z)

	chunklayers = []
	for layer in layers:
		for chunk in chunks:
			# If using object for minz then use z from points in object
			if o.minz_from_ob:
				z = chunk.points[0][2]
			else: # using operation minz 
				z = o.minz
			# only add a chunk layer if the chunk z point is in or lower than the layer 
			if z <= layer[0]:
				if z <= layer[1]:
					z = layer[1]
				# perform peck drill
				newchunk = chunk.copy()
				newchunk.setZ(z)
				chunklayers.append(newchunk)
				# retract tool to maxz (operation depth start in ui)
				newchunk = chunk.copy()
				newchunk.setZ(o.maxz)
				chunklayers.append(newchunk)
					
	
	chunklayers = sortChunks( chunklayers, o)
	chunksToMesh( chunklayers, o)

def strategy_medial_axis( o ):
	print('operation: Medial Axis')	
	print('doing highly experimental stuff')
	
	from cam.voronoi import Site, computeVoronoiDiagram
	
	chunks=[]
	
	gpoly=spolygon.Polygon()
	angle=o.cutter_tip_angle
	slope=math.tan(math.pi*(90-angle/2)/180)
	if o.cutter_type=='VCARVE':
		angle = o.cutter_tip_angle
		#start the max depth calc from the "start depth" of the operation.
		maxdepth = o.maxz - math.tan(math.pi*(90-angle/2)/180) * o.cutter_diameter/2
		#don't cut any deeper than the "end depth" of the operation.
		if maxdepth<o.minz:
			maxdepth=o.minz
			#the effective cutter diameter can be reduced from it's max since we will be cutting shallower than the original maxdepth
			#without this, the curve is calculated as if the diameter was at the original maxdepth and we get the bit 
			#pulling away from the desired cut surface
			o.cutter_diameter = (maxdepth - o.maxz) / ( - math.tan(math.pi*(90-angle/2)/180) ) * 2
	elif o.cutter_type=='BALLNOSE' or o.cutter_type=='BALL':
		#angle = o.cutter_tip_angle
		maxdepth = o.cutter_diameter/2
	else:
		o.warnings+='Only Ballnose, Ball and V-carve cutters\n are supported'
		return
	#remember resolutions of curves, to refine them, 
	#otherwise medial axis computation yields too many branches in curved parts
	resolutions_before=[]
	for ob in o.objects:
		if ob.type == 'CURVE' or ob.type == 'FONT':
			resolutions_before.append(ob.data.resolution_u)
			if ob.data.resolution_u < 64:
				ob.data.resolution_u=64
				
				
	polys=getOperationSilhouete(o)
	mpoly = sgeometry.asMultiPolygon(polys)
	mpoly_boundary = mpoly.boundary
	for poly in polys:
		schunks=shapelyToChunks(poly,-1)
		schunks = chunksRefineThreshold(schunks,o.medial_axis_subdivision, o.medial_axis_threshold)#chunksRefine(schunks,o)
		
		verts=[]
		for ch in schunks:		
			for pt in ch.points:
				#pvoro = Site(pt[0], pt[1])
				verts.append(pt)#(pt[0], pt[1]), pt[2])
		#verts= points#[[vert.x, vert.y, vert.z] for vert in vertsPts]
		nDupli,nZcolinear = unique(verts)
		nVerts=len(verts)
		print(str(nDupli)+" duplicates points ignored")
		print(str(nZcolinear)+" z colinear points excluded")
		if nVerts < 3:
			self.report({'ERROR'}, "Not enough points")
			return {'FINISHED'}
		#Check colinear
		xValues=[pt[0] for pt in verts]
		yValues=[pt[1] for pt in verts]
		if checkEqual(xValues) or checkEqual(yValues):
			self.report({'ERROR'}, "Points are colinear")
			return {'FINISHED'}
		#Create diagram
		print("Tesselation... ("+str(nVerts)+" points)")
		xbuff, ybuff = 5, 5 # %
		zPosition=0
		vertsPts= [Point(vert[0], vert[1], vert[2]) for vert in verts]
		#vertsPts= [Point(vert[0], vert[1]) for vert in verts]
		
		pts, edgesIdx = computeVoronoiDiagram(vertsPts, xbuff, ybuff, polygonsOutput=False, formatOutput=True)
		
		#
		#pts=[[pt[0], pt[1], zPosition] for pt in pts]
		newIdx=0
		vertr=[]
		filteredPts=[]
		print('filter points')
		for p in pts:
			if not poly.contains(sgeometry.Point(p)):
				vertr.append((True,-1))
			else:
				vertr.append((False,newIdx))
				if o.cutter_type == 'VCARVE':
					#start the z depth calc from the "start depth" of the operation.
					z = o.maxz - mpoly.boundary.distance(sgeometry.Point(p))*slope
					if z<maxdepth:
						z=maxdepth
				elif o.cutter_type == 'BALL' or o.cutter_type == 'BALLNOSE':
					d = mpoly_boundary.distance(sgeometry.Point(p))
					r = o.cutter_diameter/2.0
					if d>=r:
						z=-r
					else:
						#print(r, d)
						z = -r+sqrt(r*r - d*d )
				else:
					z=0#
				#print(mpoly.distance(sgeometry.Point(0,0)))
				#if(z!=0):print(z)
				filteredPts.append((p[0],p[1],z))
				newIdx+=1
				
		print('filter edges')		
		filteredEdgs=[]
		ledges=[]
		for e in edgesIdx:
			
			do=True
			p1=pts[e[0]]
			p2=pts[e[1]]
			#print(p1,p2,len(vertr))
			if vertr[e[0]][0]: # exclude edges with allready excluded points
				do=False
			elif vertr[e[1]][0]:
				do=False
			if do:
				filteredEdgs.append(((vertr[e[0]][1],vertr[e[1]][1])))
				ledges.append(sgeometry.LineString((filteredPts[vertr[e[0]][1]],filteredPts[vertr[e[1]][1]])))
				#print(ledges[-1].has_z)
		
			
		bufpoly = poly.buffer(-o.cutter_diameter/2, resolution = 64)

		lines = shapely.ops.linemerge(ledges)
		#print(lines.type)
		
		if bufpoly.type=='Polygon' or bufpoly.type=='MultiPolygon':
			lines=lines.difference(bufpoly)
			chunks.extend(shapelyToChunks(bufpoly,maxdepth))
		chunks.extend( shapelyToChunks(lines,0))
		
		#segments=[]
		#processEdges=filteredEdgs.copy()
		#chunk=camPathChunk([])
		#chunk.points.append(filteredEdgs.pop())
		#while len(filteredEdgs)>0:
			
		#Create new mesh structure
		'''
		print("Create mesh...")
		voronoiDiagram = bpy.data.meshes.new("VoronoiDiagram") #create a new mesh
		
		
				
		voronoiDiagram.from_pydata(filteredPts, filteredEdgs, []) #Fill the mesh with triangles
		
		voronoiDiagram.update(calc_edges=True) #Update mesh with new data
		#create an object with that mesh
		voronoiObj = bpy.data.objects.new("VoronoiDiagram", voronoiDiagram)
		#place object
		#bpy.ops.view3d.snap_cursor_to_selected()#move 3d-cursor
		
		#update scene
		bpy.context.scene.objects.link(voronoiObj) #Link object to scene
		bpy.context.scene.objects.active = voronoiObj
		voronoiObj.select = True
		
		'''
		#bpy.ops.object.convert(target='CURVE')
	oi=0
	for ob in o.objects:
		if ob.type == 'CURVE' or ob.type == 'FONT':
			ob.data.resolution_u=resolutions_before[oi]
			oi+=1
		
	#bpy.ops.object.join()
	chunks = sortChunks(chunks, o )

	layers = getLayers(o, o.maxz, o.min.z)
		
	chunklayers = []

	for layer in layers:
		for chunk in chunks:
			if chunk.isbelowZ(layer[0]):
				newchunk = chunk.copy()
				newchunk.clampZ(layer[1])
				chunklayers.append(newchunk)

	if o.first_down:
		chunklayers = sortChunks(chunklayers, o)

	chunksToMesh(chunklayers, o )

	
#this is the main function.
#FIXME: split strategies into separate file!
def getPath3axis(context, operation):
	s=bpy.context.scene
	o=operation
	getBounds(o)
	
	
	if o.strategy=='CUTOUT':
		strategy_cutout( o )
		
	elif o.strategy=='CURVE':
		strategy_curve( o )
				
	elif o.strategy=='PROJECTED_CURVE':
		strategy_proj_curve(s, o)
		
	elif o.strategy=='POCKET':
		strategy_pocket( o )
	
		
	elif o.strategy in ['PARALLEL', 'CROSS', 'BLOCK', 'SPIRAL', 'CIRCLES', 'OUTLINEFILL', 'CARVE', 'PENCIL', 'CRAZY']:
		
		if o.strategy=='CARVE':
			pathSamples=[]
			#for ob in o.objects:
			ob=bpy.data.objects[o.curve_object]
			pathSamples.extend(curveToChunks(ob))
			pathSamples=sortChunks(pathSamples,o)#sort before sampling
			pathSamples=chunksRefine(pathSamples,o)
		elif o.strategy=='PENCIL':
			prepareArea(o)
			getAmbient(o)
			pathSamples=getOffsetImageCavities(o,o.offset_image)
			#for ch in pathSamples:
			#	for i,p in enumerate(ch.points):
			#	 ch.points[i]=(p[0],p[1],0)
			pathSamples=limitChunks(pathSamples,o)
			pathSamples=sortChunks(pathSamples,o)#sort before sampling
		elif o.strategy=='CRAZY':
			prepareArea(o)
			
			#pathSamples = crazyStrokeImage(o)
			#####this kind of worked and should work:
			millarea=o.zbuffer_image<o.minz+0.000001
			avoidarea = o.offset_image>o.minz+0.000001
			
			pathSamples = crazyStrokeImageBinary(o,millarea,avoidarea)
			#####
			pathSamples=sortChunks(pathSamples,o)
			pathSamples=chunksRefine(pathSamples,o)
			
		else: 
			if o.strategy=='OUTLINEFILL':
				getOperationSilhouete(o)
			pathSamples=getPathPattern(o)
			if o.strategy=='OUTLINEFILL':
				pathSamples = sortChunks(pathSamples,o)#have to be sorted once before, because of the parenting inside of samplechunks
			#chunksToMesh(pathSamples,o)#for testing pattern script
			#return
			if o.strategy in ['BLOCK', 'SPIRAL', 'CIRCLES']:
				pathSamples=connectChunksLow(pathSamples,o)
		
		#print (minz)
		
		
		chunks=[]
		layers = getLayers(o, o.maxz, o.min.z)		
		
		chunks.extend(sampleChunks(o,pathSamples,layers))
		if (o.strategy=='PENCIL'):# and bpy.app.debug_value==-3:
			chunks=chunksCoherency(chunks)
			print('coherency check')
			
		if o.strategy in ['PARALLEL', 'CROSS', 'PENCIL', 'OUTLINEFILL']:# and not o.parallel_step_back:
			print('sorting')
			chunks=sortChunks(chunks,o)
			if o.strategy == 'OUTLINEFILL':
				chunks = connectChunksLow(chunks,o)
		if o.ramp:
			for ch in chunks:
				ch.rampZigZag(ch.zstart, ch.points[0][2],o)
		#print(chunks)
		if o.strategy=='CARVE':
			for ch in chunks:
				for vi in range(0,len(ch.points)):
					ch.points[vi]=(ch.points[vi][0],ch.points[vi][1],ch.points[vi][2]-o.carve_depth)
		if o.use_bridges:
			for chunk in chunks:
				useBridges(chunk,o)
		chunksToMesh(chunks,o)
		
		
	elif o.strategy=='WATERLINE' and o.use_opencamlib:
		getAmbient(o)
		chunks=[]
		oclGetWaterline(o, chunks)
		chunks=limitChunks(chunks,o)
		if (o.movement_type=='CLIMB' and o.spindle_rotation_direction=='CW') or (o.movement_type=='CONVENTIONAL' and o.spindle_rotation_direction=='CCW'):
			for ch in chunks:
				ch.points.reverse()
		chunksToMesh(chunks,o)
		
		
	elif o.strategy=='WATERLINE' and not o.use_opencamlib:
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
		lastslice=spolygon.Polygon()#polyversion
		layerstepinc=0
		
		slicesfilled=0
		getAmbient(o)
		#polyToMesh(o.ambient,0)
		for h in range(0,nslices):
			layerstepinc+=1
			slicechunks=[]
			z=o.minz+h*o.slice_detail
			if h==0:
				z+=0.0000001# if people do mill flat areas, this helps to reach those... otherwise first layer would actually be one slicelevel above min z.
			#print(z)
			#sliceimage=o.offset_image>z
			islice=o.offset_image>z
			slicepolys=imageToShapely(o,islice,with_border=True)
			#for pviz in slicepolys:
			#	polyToMesh('slice',pviz,z)
			poly=spolygon.Polygon()#polygversion
			lastchunks=[]
			#imagechunks=imageToChunks(o,islice)
			#for ch in imagechunks:
			#	slicechunks.append(camPathChunk([]))
			#	for s in ch.points:
			#	 slicechunks[-1].points.append((s[0],s[1],z))
					
			
			#print('found polys',layerstepinc,len(slicepolys))
			for p in slicepolys:
				#print('polypoints',p.nPoints(0))
				poly=poly.union(p)#polygversion TODO: why is this added?
				#print()
				#polyToMesh(p,z)
				nchunks=shapelyToChunks(p,z)
				nchunks=limitChunks(nchunks,o, force=True)
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
			if o.waterline_fill:
				layerstart=min(o.maxz,z+o.slice_detail)#
				layerend=max(o.min.z,z-o.slice_detail)#
				layers=[[layerstart,layerend]]
				#####################################
				#fill top slice for normal and first for inverse, fill between polys
				if not lastslice.is_empty or (o.inverse and not poly.is_empty and slicesfilled==1):
					#offs=False
					if not lastslice.is_empty:#between polys
						if o.inverse:
							restpoly=poly.difference(lastslice)
						else:
							restpoly=lastslice.difference(poly)
						#print('filling between')
					if (not o.inverse and poly.is_empty and slicesfilled>0) or (o.inverse and not poly.is_empty and slicesfilled==1):#first slice fill
						restpoly=lastslice
						#print('filling first')
					
					#print(len(restpoly))
					#polyToMesh('fillrest',restpoly,z)
						
					restpoly=restpoly.buffer(-o.dist_between_paths, resolution = o.circle_detail)
					
					fillz = z 
					i=0
					while not restpoly.is_empty:
						nchunks=shapelyToChunks(restpoly,fillz)
						#project paths TODO: path projection during waterline is not working
						if o.waterline_project:
							nchunks=chunksRefine(nchunks,o)
							nchunks=sampleChunks(o,nchunks,layers)
							
						nchunks=limitChunks(nchunks,o, force=True)
						#########################
						slicechunks.extend(nchunks)
						parentChildDist(lastchunks,nchunks,o)
						lastchunks=nchunks
						#slicechunks.extend(polyToChunks(restpoly,z))
						restpoly=restpoly.buffer(-o.dist_between_paths, resolution = o.circle_detail)
						
						i+=1
						#print(i)
				i=0
				#'''
				#####################################
				# fill layers and last slice, last slice with inverse is not working yet - inverse millings end now always on 0 so filling ambient does have no sense.
				if (slicesfilled>0 and layerstepinc==layerstep) or (not o.inverse and not poly.is_empty and slicesfilled==1) or (o.inverse and poly.is_empty and slicesfilled>0):
					fillz=z
					layerstepinc=0
					
					#ilim=1000#TODO:this should be replaced... no limit, just check if the shape grows over limits.
					
					#offs=False
					boundrect=o.ambient
					restpoly=boundrect.difference(poly)
					if (o.inverse and poly.is_empty and slicesfilled>0):
						restpoly=boundrect.difference(lastslice)
					
					restpoly=restpoly.buffer(-o.dist_between_paths, resolution = o.circle_detail)
					
					i=0
					while not restpoly.is_empty: #'GeometryCollection':#len(restpoly.boundary.coords)>0:
						#print(i)
						nchunks=shapelyToChunks(restpoly,fillz)
						#########################
						nchunks=limitChunks(nchunks,o, force=True)
						slicechunks.extend(nchunks)
						parentChildDist(lastchunks,nchunks,o)
						lastchunks=nchunks
						#slicechunks.extend(polyToChunks(restpoly,z))
						restpoly=restpoly.buffer(-o.dist_between_paths, resolution = o.circle_detail)
						i+=1
				
				
				#'''
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
					polys=imageToShapely(o,i)
					for poly in polys:
						chunks.extend(polyToChunks(poly,z))
					n+=1
			
		
					#restpoly=outlinePoly(restpoly,o.dist_between_paths,oo.circle_detail,o.optimize,o.optimize_threshold,,False)
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
		#chunks=sortChunks(chunks,o)
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
		strategy_drill( o )
			
	elif o.strategy=='MEDIAL_AXIS':
		strategy_medial_axis( o )
		
	#progress('finished')
	
#tools for voroni graphs all copied from the delaunayVoronoi addon:
class Point:
	def __init__(self, x, y, z):
		self.x, self.y, self.z= x, y, z

def unique(L):
	"""Return a list of unhashable elements in s, but without duplicates.
	[[1, 2], [2, 3], [1, 2]] >>> [[1, 2], [2, 3]]"""
	#For unhashable objects, you can sort the sequence and then scan from the end of the list, deleting duplicates as you go
	nDupli=0
	nZcolinear=0
	L.sort()#sort() brings the equal elements together; then duplicates are easy to weed out in a single pass.
	last = L[-1]
	for i in range(len(L)-2, -1, -1):
		if last[:2] == L[i][:2]:#XY coordinates compararison
			if last[2] == L[i][2]:#Z coordinates compararison
				nDupli+=1#duplicates vertices
			else:#Z colinear
				nZcolinear+=1
			del L[i]
		else:
			last = L[i]
	return (nDupli,nZcolinear)#list data type is mutable, input list will automatically update and doesn't need to be returned

def checkEqual(lst):
	return lst[1:] == lst[:-1]	
	
def getPath4axis(context,operation):
	t=time.clock()
	s=bpy.context.scene
	o=operation
	getBounds(o)
	if o.strategy4axis in ['PARALLELR', 'PARALLEL', 'HELIX', 'CROSS']:  
		pathSamples=getPathPattern4axis(o)
		
		depth=pathSamples[0].depth
		chunks=[]
		
		layers = getLayers(o, 0, depth)
		
		chunks.extend(sampleChunksNAxis(o,pathSamples,layers))
		chunksToMesh(chunks,o)
	
		
def prepareIndexed(o):
	s=bpy.context.scene
	#first store objects positions/rotations
	o.matrices=[]
	o.parents=[]
	for ob in o.objects:
		o.matrices.append(ob.matrix_world.copy())
		o.parents.append(ob.parent)
		
	#then rotate them
	for ob in o.objects:
		ob.select=True
	s.objects.active=ob	
	bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
	
	s.cursor_location=(0,0,0)
	oriname=o.name+' orientation'
	ori=s.objects[oriname]
	o.orientation_matrix=ori.matrix_world.copy()
	o.rotationaxes= rotTo2axes(ori.rotation_euler,'CA')
	ori.select=True
	s.objects.active=ori
	# we parent all objects to the orientation object
	bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
	for ob in o.objects:
		ob.select=False
	#then we move the orientation object to 0,0
	bpy.ops.object.location_clear()
	bpy.ops.object.rotation_clear()
	ori.select=False
	for ob in o.objects:
		activate(ob)
		
		bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
	'''
	rot=ori.matrix_world.inverted()
	#rot.x=-rot.x
	#rot.y=-rot.y
	#rot.z=-rot.z
	rotationaxes = rotTo2axes(ori.rotation_euler,'CA')
	
	#bpy.context.space_data.pivot_point = 'CURSOR'
	#bpy.context.space_data.pivot_point = 'CURSOR'

	for ob in o.objects:
		ob.rotation_euler.rotate(rot)
	'''
	

def cleanupIndexed(operation):
	s=bpy.context.scene
	oriname=operation.name+' orientation'
	
	ori=s.objects[oriname]
	path=s.objects[operation.path_object_name]
	
	ori.matrix_world=operation.orientation_matrix
	#set correct path location
	path.location = ori.location
	path.rotation_euler = ori.rotation_euler
	
	print(ori.matrix_world,operation.orientation_matrix)
	for i,ob in enumerate(operation.objects):#TODO: fix this here wrong order can cause objects out of place
		ob.parent=operation.parents[i]
	for i,ob in enumerate(operation.objects):
	
		ob.matrix_world=operation.matrices[i]
		
		
def rotTo2axes(e,axescombination):
	'''converts an orientation object rotation to rotation defined by 2 rotational axes on the machine - for indexed machining.
	attempting to do this for all axes combinations.
	'''
	v=Vector((0,0,1))
	v.rotate(e)
	#if axes
	if axescombination=='CA':
		v2d=Vector((v.x,v.y))
		a1base=Vector((0,-1))#?is this right?It should be vector defining 0 rotation
		if v2d.length>0:
			cangle=a1base.angle_signed(v2d)
		else:
			return(0,0)
		v2d=Vector((v2d.length,v.z))
		a2base=Vector((0,1))
		aangle=a2base.angle_signed(v2d)
		print('angles',cangle,aangle)
		return (cangle, aangle)
		
	elif axescombination=='CB':
		v2d=Vector((v.x,v.y))
		a1base=Vector((1,0))#?is this right?It should be vector defining 0 rotation
		if v2d.length>0:
			cangle=a1base.angle_signed(v2d)
		else:
			return(0,0)
		v2d=Vector((v2d.length,v.z))
		a2base=Vector((0,1))
		
		bangle=a2base.angle_signed(v2d)
		
		
		print('angles',cangle,bangle)
		
		return (cangle,bangle)
	'''
	v2d=((v[a[0]],v[a[1]]))
	angle1=a1base.angle(v2d)#C for ca
	print(angle1)
	if axescombination[0]=='C':
		e1=Vector((0,0,-angle1))
	elif axescombination[0]=='A':#TODO: finish this after prototyping stage
		pass;
	v.rotate(e1)
	vbase=Vector(0,1,0)
	bangle=v.angle(vzbase)
	print(v)
	print(bangle)
	'''
	return(angle1,angle2)
	
def getPath(context,operation):#should do all path calculations.
	t=time.clock()
	#print('ahoj0')
	if shapely.speedups.available:
		shapely.speedups.enable()
	
	#these tags are for caching of some of the results. Not working well still - although it can save a lot of time during calculation...
	chd=getChangeData(operation)
	#print(chd)
	#print(o.changedata)
	if operation.changedata!=chd:# or 1:
		operation.update_offsetimage_tag=True
		operation.update_zbufferimage_tag=True
		operation.changedata=chd
	
	operation.update_silhouete_tag=True
	operation.update_ambient_tag=True
	operation.update_bullet_collision_tag=True
	

	getOperationSources(operation)

	operation.warnings=''
	checkMemoryLimit(operation)
	
	

	if operation.machine_axes=='3':
		getPath3axis(context,operation)
	
	elif (operation.machine_axes=='5' and operation.strategy5axis=='INDEXED') or (operation.machine_axes=='4' and operation.strategy4axis=='INDEXED'):#5 axis operations are now only 3 axis operations that get rotated...
		operation.orientation = prepareIndexed(operation)#TODO RENAME THIS
		
		getPath3axis(context,operation)#TODO RENAME THIS
		
		cleanupIndexed(operation)#TODO RENAME THIS
		#transform5axisIndexed
	elif operation.machine_axes=='4':
		getPath4axis(context,operation)
	
	
	#export gcode if automatic.
	if operation.auto_export:
		if bpy.data.objects.get(operation.path_object_name)==None:
			return;
		p=bpy.data.objects[operation.path_object_name]
		exportGcodePath(operation.filename,[p.data],[operation])

	operation.changed=False
	t1=time.clock()-t 
	progress('total time',t1)

def reload_paths(o):
	oname = "cam_path_"+o.name
	s=bpy.context.scene
	#for o in s.objects:
	ob=None
	old_pathmesh=None
	if oname in s.objects:
		old_pathmesh=s.objects[oname].data
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
		object_utils.object_data_add(bpy.context, mesh, operator=None)
		ob=bpy.context.active_object
		ob.name=oname
	ob=s.objects[oname]
	ob.location=(0,0,0)
	o.path_object_name=oname
	o.changed=False
	
	if old_pathmesh != None:
		bpy.data.meshes.remove(old_pathmesh)
