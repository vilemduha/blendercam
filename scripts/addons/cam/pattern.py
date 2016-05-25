# blender CAM pattern.py (c) 2012 Vilem Novak
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

import time
import mathutils
from mathutils import *


from cam import simple, chunk
from cam.simple import * 
from cam.chunk import * 
from cam import polygon_utils_cam
from cam.polygon_utils_cam import *
import shapely
from shapely import geometry as sgeometry
import numpy

def getPathPatternParallel(o,angle):
	#minx,miny,minz,maxx,maxy,maxz=o.min.x,o.min.y,o.min.z,o.max.x,o.max.y,o.max.z
	#ob=o.object
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
	#defaultar=numpy.arange(int(-dim/pathd), int(dim/pathd)).tolist()
	if bpy.app.debug_value==0:# by default off
		#this is the original pattern method, slower, but well tested:
		dirvect=Vector((0,1,0))
		dirvect.rotate(e)
		dirvect.normalize()
		dirvect*=pathstep
		for a in range(int(-dim/pathd), int(dim/pathd)):#this is highly ineffective, computes path2x the area needed...
			chunk=camPathChunk([])
			#chunk=camPathChunk(defaultar.copy())
			v=Vector((a*pathd,int(-dim/pathstep)*pathstep,0))
			v.rotate(e)
			v+=vm#shifting for the rotation, so pattern rotates around middle...
			for b in range(int(-dim/pathstep),int(dim/pathstep)):
				v+=dirvect
				
				if v.x>o.min.x and v.x<o.max.x and v.y>o.min.y and v.y<o.max.y:
					chunk.points.append((v.x,v.y,zlevel))
					#chunk.points[a]=(v.x,v.y,zlevel)
			if (reverse and o.movement_type=='MEANDER') or (o.movement_type=='CONVENTIONAL' and o.spindle_rotation_direction=='CW') or (o.movement_type=='CLIMB' and o.spindle_rotation_direction=='CCW') :
				chunk.points.reverse()
				
					
			#elif   
			if len(chunk.points)>0:
				pathchunks.append(chunk)
			if len(pathchunks)>1 and reverse and o.parallel_step_back and not o.use_layers:
				#parallel step back - for finishing, best with climb movement, saves cutter life by going into material with climb, while using move back on the surface to improve finish(which would otherwise be a conventional move in the material)
					
				if o.movement_type=='CONVENTIONAL' or o.movement_type=='CLIMB':
					pathchunks[-2].points.reverse()
				changechunk=pathchunks[-1]
				pathchunks[-1]=pathchunks[-2]
				pathchunks[-2]=changechunk
						
			reverse = not reverse
			#print (chunk.points)
	else:#alternative algorithm with numpy, didn't work as should so blocked now...
		
		v=Vector((0,1,0))
		#e.z=-e.z
		v.rotate(e)
		e1=Euler((0,0,-math.pi/2))
		v1=v.copy()
		v1.rotate(e1)
		a1res=int(dim/pathd)-int(-dim/pathd)
		a2res=int(dim/pathstep)-int(-dim/pathstep)
		
		axis_across_paths=numpy.array((numpy.arange(int(-dim/pathd), int(dim/pathd))*pathd*v1.x+xm,
													numpy.arange(int(-dim/pathd), int(dim/pathd))*pathd*v1.y+ym,
													numpy.arange(int(-dim/pathd), int(dim/pathd))*0))
		#axis_across_paths=axis_across_paths.swapaxes(0,1)
		#progress(axis_across_paths)
		
		axis_along_paths=numpy.array((numpy.arange(int(-dim/pathstep),int(dim/pathstep))*pathstep*v.x,
												numpy.arange(int(-dim/pathstep),int(dim/pathstep))*pathstep*v.y,
												numpy.arange(int(-dim/pathstep),int(dim/pathstep))*0+zlevel))#rotate this first
		progress(axis_along_paths)
		#axis_along_paths = axis_along_paths.swapaxes(0,1)
		#progress(axis_along_paths)
		
		#chunks=numpy.array((1.0))
		#chunks.resize(3,a1res,a2res)
		chunks=[]
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
			#if v.x>o.min.x and v.x<o.max.x and v.y>o.min.y and v.y<o.max.y:
			
			xfitmin=nax[0]>o.min.x
			xfitmax=nax[0]<o.max.x
			xfit=xfitmin & xfitmax
			#print(xfit,nax)
			nax=numpy.array([nax[0][xfit],nax[1][xfit],nax[2][xfit]])
			yfitmin=nax[1]>o.min.y
			yfitmax=nax[1]<o.max.y
			yfit=yfitmin & yfitmax
			nax=numpy.array([nax[0][yfit],nax[1][yfit],nax[2][yfit]])
			chunks.append(nax.swapaxes(0,1))
		#chunks
		
		
		#print(chunks)
		#chunks=chunks.swapaxes(0,1)
		#chunks=chunks.swapaxes(1,2)
		#print(chunks)
		pathchunks=[]
		for ch in chunks:
			ch=ch.tolist()
			pathchunks.append(camPathChunk(ch)) 
			#print (ch)
		
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
						chunk.closed=False
						pathchunks.append(chunk)
						
						chunk=camPathChunk([])
				v.rotate(e)
			
			
			if len(chunk.points)>0:
				chunk.points.append(firstchunk.points[0])
				if chunk==firstchunk:
					chunk.closed=True
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
		
		
		polys=operation.silhouete
		pathchunks=[]
		chunks=[]
		for p in polys:
			p=p.buffer(-o.dist_between_paths/10,o.circle_detail)#first, move a bit inside, because otherwise the border samples go crazy very often changin between hit/non hit and making too many jumps in the path.
			chunks.extend(shapelyToChunks(p,0))
		
		pathchunks.extend(chunks)
		lastchunks=chunks
		firstchunks=chunks
		
		#for ch in chunks:
		#   if len(ch.points)>2:
		#	 polys.extend()
				
		approxn=(min(maxx-minx,maxy-miny)/o.dist_between_paths)/2
		i=0
		
		for porig in polys:
			p=porig
			while not p.is_empty:#:p.nPoints()>0:
				p=p.buffer(-o.dist_between_paths,o.circle_detail)
				if not p.is_empty:
					nchunks=shapelyToChunks(p,zlevel)
					
					if o.movement_insideout=='INSIDEOUT':
						parentChildDist(lastchunks,nchunks,o)
					else:
						parentChildDist(nchunks,lastchunks,o)
					pathchunks.extend(nchunks)
					lastchunks=nchunks
				percent=int(i/approxn*100)
				progress('outlining polygons ',percent) 
				i+=1
		pathchunks.reverse()
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
					p=p.buffer(dist,o.circle_detail)
					if not p.is_empty:
						nchunks=shapelyToChunks(p,zlevel)
						if o.movement_insideout=='INSIDEOUT':
							parentChildDist(nchunks,lastchunks,o)
						else:
							parentChildDist(lastchunks,nchunks,o)
						pathchunks.extend(nchunks)
						lastchunks=nchunks
		
		if o.movement_insideout == 'OUTSIDEIN':
			pathchunks.reverse()
		
		for chunk in pathchunks:
			if o.movement_insideout=='OUTSIDEIN':
				chunk.points.reverse()
			if (o.movement_type=='CLIMB' and o.spindle_rotation_direction=='CW') or (o.movement_type=='CONVENTIONAL' and o.spindle_rotation_direction=='CCW'):
				chunk.points.reverse()
		
		#parentChildPoly(pathchunks,pathchunks,o)	
		chunksRefine(pathchunks,o)
	progress(time.time()-t)
	return pathchunks
	
def getPathPattern4axis(operation):
	o=operation
	t=time.time()
	progress('building path pattern')
	minx,miny,minz,maxx,maxy,maxz=o.min.x,o.min.y,o.min.z,o.max.x,o.max.y,o.max.z
	pathchunks=[]
	zlevel=1#minz#this should do layers...
	

	#set axes for various options, Z option is obvious nonsense now.
	if o.rotary_axis_1=='X':
		a1=0
		a2=1
		a3=2
	if o.rotary_axis_1=='Y':
		a1=1
		a2=0
		a3=2
	if o.rotary_axis_1=='Z':
		a1=2
		a2=0
		a3=1
	
	o.max.z=o.maxz
	#set radius for all types of operation
	m1=max(abs(o.min[a2]),abs(o.max[a2]))
	m2=max(abs(o.min[a3]),abs(o.max[a3]))
	
	radius=max(o.max.z,0.0001)#math.sqrt(m1*m1+m2*m2)+operation.cutter_diameter*2#max radius estimation, but the minimum is object 
	radiusend=o.min.z
	
	mradius=max(radius,radiusend)
	circlesteps=(mradius*pi*2)/o.dist_along_paths
	circlesteps = max(4,circlesteps)
	anglestep = 2*pi/circlesteps
	#generalized rotation
	e=Euler((0,0,0))
	e[a1]=anglestep
	
	#generalized length of the operation
	maxl=o.max[a1]
	minl=o.min[a1]
	steps=(maxl-minl)/o.dist_between_paths
	
	#set starting positions for cutter e.t.c.
	cutterstart=Vector((0,0,0))
	cutterend=Vector((0,0,0))#end point for casting


	
	if o.strategy4axis=='PARALLELR':
		
		for a in range(0,floor(steps)+1):
			chunk=camPathChunk([])

			cutterstart[a1]=o.min[a1]+a*o.dist_between_paths
			cutterend[a1]=cutterstart[a1]
			
			cutterstart[a2]=0#radius
			cutterend[a2]=0#radiusend
			
			cutterstart[a3]=radius
			cutterend[a3]=radiusend
			
			for b in range(0,floor(circlesteps)+1):
				#print(cutterstart,cutterend)
				chunk.startpoints.append(cutterstart.to_tuple())
				chunk.endpoints.append(cutterend.to_tuple())
				rot=[0,0,0]
				rot[a1]=a*2*pi+b*anglestep
				
				chunk.rotations.append(rot)
				cutterstart.rotate(e)
				cutterend.rotate(e)

			chunk.depth=radiusend-radius
			#last point = first
			chunk.startpoints.append(chunk.startpoints[0])
			chunk.endpoints.append(chunk.endpoints[0])
			chunk.rotations.append(chunk.rotations[0])
			
			pathchunks.append(chunk)
			
	if o.strategy4axis=='PARALLEL':
		circlesteps=(mradius*pi*2)/o.dist_between_paths
		steps=(maxl-minl)/o.dist_along_paths
		
		anglestep = 2*pi/circlesteps
		#generalized rotation
		e=Euler((0,0,0))
		e[a1]=anglestep
		
		reverse=False
		
		for b in range(0,floor(circlesteps)+1):
			chunk=camPathChunk([])
			cutterstart[a2]=0
			cutterstart[a3]=radius
			
			cutterend[a2]=0
			cutterend[a3]=radiusend
			
			e[a1]=anglestep*b
			
			cutterstart.rotate(e)
			cutterend.rotate(e)
			
			for a in range(0,floor(steps)+1):
				cutterstart[a1]=o.min[a1]+a*o.dist_along_paths
				cutterend[a1]=cutterstart[a1]
				chunk.startpoints.append(cutterstart.to_tuple())
				chunk.endpoints.append(cutterend.to_tuple())
				rot=[0,0,0]
				rot[a1]=b*anglestep
				chunk.rotations.append(rot)
				
			chunk.depth=radiusend-radius
			#last point = first

			pathchunks.append(chunk)
			
			if (reverse and o.movement_type=='MEANDER') or (o.movement_type=='CONVENTIONAL' and o.spindle_rotation_direction=='CW') or (o.movement_type=='CLIMB' and o.spindle_rotation_direction=='CCW') :
				chunk.reverse()
				
			reverse=not reverse
			
	if o.strategy4axis=='HELIX':
		print('helix')
		
		a1step=o.dist_between_paths / circlesteps
		
		chunk=camPathChunk([])#only one chunk, init here
		
		for a in range(0,floor(steps)+1):
			
			cutterstart[a1]=o.min[a1]+a*o.dist_between_paths
			cutterend[a1]=cutterstart[a1]
			cutterstart[a2]=0
			cutterstart[a3]=radius
			cutterend[a3]=radiusend
			
			for b in range(0,floor(circlesteps)+1):
				#print(cutterstart,cutterend)
				cutterstart[a1]+=a1step
				cutterend[a1]+=a1step
				chunk.startpoints.append(cutterstart.to_tuple())
				chunk.endpoints.append(cutterend.to_tuple())
				
				rot=[0,0,0]
				rot[a1]=a*2*pi+b*anglestep
				chunk.rotations.append(rot)
				
				cutterstart.rotate(e)
				cutterend.rotate(e)

			chunk.depth=radiusend-radius
			#last point = first
			
	
	
		pathchunks.append(chunk)
	#print(chunk.startpoints)
	#print(pathchunks)	
	#sprint(len(pathchunks))
	#print(o.strategy4axis)
	return pathchunks 
