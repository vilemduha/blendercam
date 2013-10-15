import Polygon
from cam import simple
from cam.simple import * 

class camPathChunk:
	#parents=[]
	#children=[]
	#sorted=False
	
	#progressIndex=-1# for e.g. parallel strategy, when trying to save time..
	def __init__(self,inpoints ,startpoints = [], endpoints = [], rotations = []):
		if len(inpoints)>2:
			self.poly=Polygon.Polygon(inpoints)
		else:
			self.poly=Polygon.Polygon()
		self.points=inpoints#for 3 axes, this is only storage of points. For N axes, here go the sampled points
		self.startpoints = []#from where the sweep test begins, but also retract point for given path
		self.endpoints = []#where sweep test ends
		self.rotations = []#rotation of the machine axes
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
				#   ch.points.reverse()
				return min(d1,d2)
			else:
				return dist2d(pos,self.points[0])
	def distStart(self,pos,o):
		return dist2d(pos,self.points[0])
		
	def adaptdist(self,pos,o):
		#reorders chunk so that it starts at the closest point to pos.
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
				if d2<d1:
					self.points.reverse()
		
	def getNext(self):
		for child in self.children:
			if child.sorted==False:
				#unsortedchildren=True
				return child.getNext()  
		#self.unsortedchildren=False		
		return self
	
	def getLength(self):
		#computes length of the chunk - in 3d
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
	
	def reverse(self):
		self.points.reverse()
		self.startpoints.reverse()
		self.endpoints.reverse()
		self.rotations.reverse()
	def pop(self, index):
		self.points.pop(index)
		if len(self.startpoints)>0:
			self.startpoints.pop(index)
			self.endpoints.pop(index)
			self.rotations.pop(index)
#def appendChunk(sorted,ch,o,pos) 

def chunksCoherency(chunks):
	#checks chunks for their stability, for pencil path. it checks if the vectors direction doesn't jump too much too quickly, if this happens it splits the chunk on such places, too much jumps = deletion of the chunk. this is because otherwise the router has to slow down too often, but also means that some parts detected by cavity algorithm won't be milled 
	nchunks=[]
	for chunk in chunks:
		if len(chunk.points)>2:
			nchunk=camPathChunk([])
			
			#doesn't check for 1 point chunks here, they shouldn't get here at all.
			lastvec=Vector(chunk.points[1])-Vector(chunk.points[0])
			for i in range(0,len(chunk.points)-1):
				nchunk.points.append(chunk.points[i])
				vec=Vector(chunk.points[i+1])-Vector(chunk.points[i])
				angle=vec.angle(lastvec,vec)
				#print(angle,i)
				if angle>1.07:#60 degrees is maximum toleration for pencil paths. 
					if len(nchunk.points)>4:#this is a testing threshold
						nchunks.append(nchunk)
					nchunk=camPathChunk([])
				lastvec=vec
			if len(nchunk.points)>4:#this is a testing threshold
				nchunks.append(nchunk)
	return nchunks  

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

def optimizeChunk(chunk,operation):
	
	for vi in range(len(chunk.points)-2,0,-1):
		#vmiddle=Vector()
		#v1=Vector()
		#v2=Vector()
		if compare(chunk.points[vi-1],chunk.points[vi+1],chunk.points[vi],operation.optimize_threshold):

			chunk.pop(vi)
			
			#vi-=1
	#protect_vertical=True
	if operation.protect_vertical and operation.axes=='3':#protect vertical surfaces so far only for 3 axes..doesn't have now much logic for n axes, right?
		#print('verticality test')
		
		
		for vi in range(len(chunk.points)-1,0,-1):
			v1=chunk.points[vi]
			v2=chunk.points[vi-1]
			v1c,v2c=isVerticalLimit(v1,v2,operation.protect_vertical_limit)
			if v1c!=v1:
				chunk.points[vi]=v1c
			elif v2c!=v2:
				chunk.points[vi-1]=v2c
			
			
		#print(vcorrected)
	return chunk			
	
def limitChunks(chunks,o):
	if o.use_limit_curve:
		nchunks=[]
		for ch in chunks:
			nch=camPathChunk([])
			nch1=nch
			closed=True
			for s in ch.points:
				sampled=o.limit_poly.isInside(s[0],s[1])
				if not sampled and len(nch.points)>0:
					nch.closed=False
					closed=False
					nchunks.append(nch)
					nch=camPathChunk([])
				elif sampled:
					nch.points.append(s)
					
			if len(nch.points)>1 and closed and ch.closed and ch.points[0]==ch.points[1]:
				nch.closed=True
			elif ch.closed and nch!=nch1 and nch.points[-1]==nch1.points[0]:#here adds beginning of closed chunk to the end, if the chunks were split during limiting
				nch.points.extend(nch1.points)
				nchunks.remove(nch1)
				print('joining stuff')
			if len(nch.points)>0:
				nchunks.append(nch)
		return nchunks
	else:
		return chunks

def parentChildPoly(parents,children,o):
	#hierarchy based on polygons - a polygon inside another is his child.
	#hierarchy works like this: - children get milled first. 
	
	for parent in parents:
		#print(parent.poly)
		for child in children:
			#print(child.poly)
			if child!=parent and len(child.poly)>0:
				if parent.poly.isInside(child.poly[0][0][0],child.poly[0][0][1]):
					parent.children.append(child)
					child.parents.append(parent)

def parentChildDist(parents, children,o):
	#parenting based on distance between chunks
	#hierarchy works like this: - children get milled first. 
	dlim=o.dist_between_paths*2
	if (o.strategy=='PARALLEL' or o.strategy=='CROSS') and o.parallel_step_back:
		dlim=dlim*2
		
	for child in children:
		for parent in parents:
			isrelation=False
			if parent!=child:
				for v in child.points:
					for v1 in parent.points:
						
						if dist2d(v,v1)<dlim:
							isrelation=True
							break
					if isrelation:
						break
				if isrelation:
					parent.children.append(child)
					child.parents.append(parent)
						
def parentChild(parents, children, o):
	#connect all children to all parents. Useful for any type of defining hierarchy.
	#hierarchy works like this: - children get milled first. 

	for child in children:
		for parent in parents:
				if parent!=child:
					parent.children.append(child)
					child.parents.append(parent)	

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
				
			if ppart!=ptest and len(ptest.poly)>0 and len(ppart.poly)>0 and ptest.poly.nPoints(0)>0 and ppart.poly.nPoints(0)>0:
				if ptest.poly.isInside(ppart.poly[0][0][0],ppart.poly[0][0][1]):
					#hierarchy works like this: - children get milled first. 
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
		