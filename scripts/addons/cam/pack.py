import bpy
from cam import utils, simple,polygon_utils_cam
import Polygon
import random
#this algorithm takes all selected curves, 
#converts them to polygons,
# offsets them by the pre-set margin
#then chooses a starting location possibly inside the allready occupied area and moves and rotates the polygon out of the occupied area
#if one or more positions are found where the poly doesn't overlap, it is placed and added to the occupied area - allpoly
#this algorithm is very slow and STUPID, a collision algorithm would be much much faster...

def packCurves():
	packsettings=bpy.context.scene.cam_pack
	
	sheetsizex=packsettings.sheet_x
	sheetsizey=packsettings.sheet_y
	direction=packsettings.sheet_fill_direction
	distance=packsettings.distance
	rotate = packsettings.rotate
	
	polyfield=[]#in this, position, rotation, and actual poly will be stored.
	for ob in bpy.context.selected_objects:
		allchunks=[]
		simple.activate(ob)
		bpy.ops.object.make_single_user(type='SELECTED_OBJECTS')
		bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
		z=ob.location.z
		bpy.ops.object.location_clear()
		bpy.ops.object.rotation_clear()

		chunks=utils.curveToChunks(ob)
		npolys=utils.chunksToPolys(chunks)
		#add all polys in silh to one poly
		poly=Polygon.Polygon()
		for p in npolys:
			poly+=p
		poly.simplify()
		poly=polygon_utils_cam.outlinePoly(poly,distance/1.5,8,True,.003,offset = True)
		polyfield.append([[0,0],0.0,poly,ob,z])
	random.shuffle(polyfield)
	#primitive layout here:
	allpoly=Polygon.Polygon()#main collision poly.
	
	
	shift=0.0015#one milimeter by now.
	rotchange=.3123456#in radians
	
	xmin,xmax,ymin,ymax=polyfield[0][2].boundingBox()
	if direction=='X':
		mindist=-xmin
	else:
		mindist=-ymin
	i=0
	for pf in polyfield:
		print(i)
		rot=0
		porig=pf[2]
		placed=False
		xmin,xmax,ymin,ymax=p.boundingBox()
		#p.shift(-xmin,-ymin)
		if direction=='X':
			x=mindist
			y=-ymin
		if direction=='Y':
			x=-xmin
			y=mindist
		
		iter=0
		best=None
		hits=0
		besthit=None
		while not placed:
			
			#swap x and y, and add to x
			#print(x,y)
			#p=Polygon.Polygon(porig)
			p=porig
			p.rotate(rot,0,0)
			p.shift(x,y)
			
			xmin,xmax,ymin,ymax=p.boundingBox()
			if xmin>0 and ymin>0 and ((direction=='Y' and xmax<sheetsizex) or (direction=='X' and ymax<sheetsizey)) and not p.overlaps(allpoly):
				#we do more good solutions, choose best out of them:
				hits+=1
				if best==None:
					best=[x,y,rot,xmax,ymax]
					besthit=hits
				if direction=='X':
					if xmax<best[3]:
						best=[x,y,rot,xmax,ymax]
						besthit=hits
				elif ymax<best[4]:
					best=[x,y,rot,xmax,ymax]
					besthit=hits
					


					
			p.shift(-x,-y)
			p.rotate(-rot,0,0)
			
			if hits>=15 or (iter>10000 and hits>0):#here was originally more, but 90% of best solutions are still 1
				placed=True
				pf[3].location.x=best[0]
				pf[3].location.y=best[1]
				pf[3].location.z=pf[4]
				pf[3].rotation_euler.z=best[2]
				
				
				pf[3].select=True
				
				#print(mindist)
				mindist=mindist-0.5*(xmax-xmin)
				#print(mindist)
				#print(iter)
				
				#reset polygon to best position here:
				p.rotate(best[2],0,0)
				p.shift(best[0],best[1])
				
				#polygon_utils_cam.polyToMesh(p,0.1)#debug visualisation
				keep=[]
				
				npoly=Polygon.Polygon()
				for ci in range(0,len(allpoly)):
					cminx,cmaxx,cminy,cmaxy=allpoly.boundingBox(ci)
					if direction=='X' and cmaxx>mindist-.1:
							npoly.addContour(allpoly[ci])
					if direction=='Y' and cmaxy>mindist-.1:
							npoly.addContour(allpoly[ci])
							
				allpoly=npoly
				#polygon_utils_cam.polyToMesh(allpoly,0.1)#debug visualisation
				
				for c in p:
					allpoly.addContour(c)
				#cleanup allpoly
				print(iter,hits,besthit)
			if not placed:
				if direction=='Y':
					x+=shift
					mindist=y
					if (xmax+shift>sheetsizex):
						x=x-xmin
						y+=shift
				if direction=='X':
					y+=shift
					mindist=x
					if (ymax+shift>sheetsizey):
						y=y-ymin
						x+=shift
				if rotate: rot+=rotchange
			iter+=1
		i+=1

