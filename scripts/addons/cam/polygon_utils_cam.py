import math
from math import *
import mathutils
from mathutils import *
import curve_simplify

import Polygon

import shapely
from shapely.geometry import polygon as spolygon
from shapely import ops
from shapely import geometry
SHAPELY=True
#except:
#	SHAPELY=False
	

def Polygon2Shapely(p):
	conts=[]
	sp=geometry.Polygon()
	holes=[]
	contours=[]
	#print(len(p))
	#print(p)
	for ci,c in enumerate(p):
		#print(ci)
		shapely_p=spolygon.Polygon(c)
		if p.nPoints(ci)>2 and shapely_p.is_valid:
		
			if p.isHole(ci):
				#print('ishole')
				holes.append(shapely_p)
			else:
				contours.append(shapely_p)
			
	#for c in contours:
		#sp=sp.union(spolygon.Polygon(c)
	sp=shapely.ops.unary_union(contours)
	for h in holes:
		sp=sp.difference(h)
		
	#sp=geometry.asMultiPolygon(conts)
	#sp=ops.cascaded_union(sp)
	return sp
	
def Shapely2Polygon(sp):
	gt=sp.geometryType()
	p=Polygon.Polygon()
	if gt=='Polygon':
		if sp.exterior!=None:
			p.addContour(sp.exterior.coords,False)
			for sc in sp.interiors:
				p.addContour(sc.coords,True)
	else:
		p=Polygon.Polygon()
		for spsub in sp:
			p.addContour(spsub.exterior.coords,False)
			for sc in spsub.interiors:
				p.addContour(sc.coords,True)
		
	return p
	
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
	optimize_threshold*=0.000001
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
	optimize_threshold*=0.000001
	#t=Polygon.getTolerance()
	#e=0.0001
	#Polygon.setTolerance(e)
	vref=mathutils.Vector((1,0))
	#p.simplify()
	#print(p)
	if p.nPoints()>2:
		if SHAPELY:
			sp=Polygon2Shapely(p)
			if not offset:
				r=-r
			sp=sp.buffer(r,circle_detail)
			pr=Shapely2Polygon(sp)
			'''
			sp=spolygon.Polygon()
			for ci,c in enumerate(p):
				hole=p.isHole(ci)
				nsp=Polygon2Shapely(Polygon.Polygon(c))
				if not offset:
					r=-r
				if hole:
					r=-r
				nsp=nsp.buffer(r)	
				if hole:
					sp=sp.difference(nsp)
				else:
					sp=sp.union(nsp)
			pr=Shapely2Polygon(sp)
			'''	
		else:
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

def polyToMesh(name,p,z):
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
		for vii in range(0,clen-1):#TODO CHECK IF THIS WORKS, IS THERE ALWAYS ONE EXTRA POINT THAT COMES OUT OF NOWHERE?
			v=c[vii]#same as vi...?
			verts.append((v[0],v[1],z))
			if ei>0:
				edges.append((vi-1,vi))
			if ei==clen-2:#check here too...
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
	
	ob=bpy.context.active_object
	ob.name=name
	ob.location=(0,0,0)
	bpy.ops.object.convert(target='CURVE')
	bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')

	
	return bpy.context.active_object

def shapelyToMesh(name,p,z):
	p = Shapely2Polygon(p)
	ob = polyToMesh(name,p,z)
	return ob
	
	
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