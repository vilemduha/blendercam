import math
from math import *
import mathutils
from mathutils import *
import curve_simplify

import Polygon

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

def nRect(l,r):
	s=((-l/2.0,-r/10.0),(l/2.0,-r/10.0),(l/2.0,r),(-l/2,r))
	r= Polygon.Polygon(s)
	return r

def getLength(p,i=None):#i is contour index
	if i==None:
		contours=p
	else:
		contours=[p[i]]
	length=0.0
	for c in contours:
		for vi,v1 in enumerate(c):
			#print(len(self.points),vi)
			v2=Vector(v1)#this is for case of last point and not closed chunk..
			if vi==len(c)-1:
				v2=Vector(c[0])
			else:
				v2=Vector(c[vi+1])
			v1=Vector(v1)
			v=v2-v1
			length+=v.length
	return length
	
def polyRemoveDoubles(p,optimize_threshold):
	
	#vecs=[]
	pnew=Polygon.Polygon()
	soptions=['distance','distance',0.0,5,optimize_threshold,5,optimize_threshold]
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
	
	
def outlinePoly(p,r,circle_detail,optimize,optimize_threshold,offset = True):
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
		
		pr = Polygon.Polygon(p)#try a copy instead pr+p#TODO fix this. this probably ruins depth in outlines! should add contours instead, or do a copy
		
		circle=Circle(r,circle_detail)
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
			
			if optimize:
				pr=polyRemoveDoubles(pr,optimize_threshold)
		p=pr
	return p

def polyToMesh(p,z):
	import bpy,bmesh
	from bpy_extras import object_utils
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
