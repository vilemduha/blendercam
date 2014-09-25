#very simple slicing for 3d meshes, usefull for plywood cutting.
from cam import chunk, polygon_utils_cam
import bpy

def getSlices(ob,slice_distance):
	'''function for slicing a mesh. It is now not used, but can be used for e.g. lasercutting from sheets a 3d model in the future.'''
	
	layer_thickness=slice_distance
	edges=[]
	verts = []
	i=0
	slices=[]#slice format is [length, minx,miny, maxx, maxy,verts,z]
	firstslice=None
	lastslice=None
	maxzt = -100000000000000000000000000
	minzt = 1000000000000000000000000000
	#progress('slicing object')
	m=ob.to_mesh(scene=bpy.context.scene, apply_modifiers=True, settings='PREVIEW')
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
	print('sorting slices') 
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
	#print(len(slicechunks))
	return slicechunks


	
def sliceObject(ob):
	settings=bpy.context.scene.cam_slice
	
	layers = getSlices(ob, settings.slice_distance)
	#print(layers)
	sliceobjects=[]
	i=1
	for layer in layers:
		pi=1
		layerpolys=[]
		for slicechunk in layer:
			#these functions here are totally useless conversions, could generate slices more directly, just lazy to  write new functions
			#print (slicechunk)
			nchp=[]
			for p in slicechunk:
				nchp.append((p[0],p[1]))
			#print(slicechunk)
			ch = chunk.camPathChunk(nchp)

			#print(ch)
			pslices=chunk.chunksToPolys([ch])
			#p1=outlinePoly(pslice,o.dist_between_paths,o.circle_detail,o.optimize,o.optimize_threshold,False)
			#print(pslices)
			for pslice in pslices:
				p = pslice#-p1
				#print(p)
				text = '%i - %i' % (i,pi)
				bpy.ops.object.text_add()
				textob = bpy.context.active_object
				textob.data.size = 0.0035
				textob.data.body = text
				textob.data.align = 'CENTER'
				
				#print(len(ch.points))
				sliceobject = polygon_utils_cam.polyToMesh('slice',p,slicechunk[0][2])
				textob.location=(0,0,0)
				
				textob.parent=sliceobject
				
				sliceobject.data.extrude = settings.slice_distance/2
				sliceobject.data.dimensions = '2D'
				sliceobjects.append(sliceobject)
				pi+=1
		#FIXME: the polys on same layer which are hollow are not joined by now, this prevents doing hollow surfaces :(
		#for p in layerpolys:
			#for p1 in layerpolys:
				
		i+=1
	for o in sliceobjects:
		o.select=True
	bpy.ops.group.create(name='slices')