import bpy,time
import numpy
import math
import re
from math import *
from bpy.props import *


bl_info = {
	"name": "Bas relief",
	"author": "Vilem Novak",
	"version": (0, 1, 0),
	"blender": (2, 80, 0),
	"location": "Properties > render",
	"description": "Converts zbuffer image to bas relief.",
	"warning": "there is no warranty. needs Numpy library installed in blender python directory.",
	"wiki_url": "blendercam.blogspot.com",
	"tracker_url": "",
	"category": "Scene"}

##////////////////////////////////////////////////////////////////////
#// Full Multigrid Algorithm for solving partial differential equations
#//////////////////////////////////////////////////////////////////////
#MODYF = 0 #/* 1 or 0 (1 is better) */
#MINS = 16	#/* minimum size 4 6 or 100 */


#SMOOTH_IT = 2 #/* minimum 1  */
#V_CYCLE = 10 #/* number of v-cycles  2*/
#ITERATIONS = 5

#// precision
EPS = 1.0e-32
PRECISION=5
NUMPYALG=False
#PLANAR_CONST=True

def copy_compbuf_data(inbuf, outbuf):
	outbuf[:]=inbuf[:]

def restrictbuf( inbuf, outbuf ):#scale down array....

	inx = inbuf.shape[0]
	iny = inbuf.shape[1]

	outx = outbuf.shape[0]
	outy = outbuf.shape[1]

	dx=inx/outx
	dy=iny/outy

	filterSize = 0.5
	xfiltersize=dx*filterSize

	sy=dy/2-0.5
	if dx==2 and dy==2:#much simpler method
		#if dx<2:
		#restricted=
		#num=restricted.shape[0]*restricted.shape[1]
		outbuf[:]=(inbuf[::2,::2]+inbuf[1::2,::2]+inbuf[::2,1::2]+inbuf[1::2,1::2])/4.0

	elif NUMPYALG:#numpy method
		yrange=numpy.arange(0,outy)
		xrange=numpy.arange(0,outx)

		w=0
		sx = dx/2-0.5

		sxrange=xrange*dx+sx
		syrange=yrange*dy+sy

		sxstartrange=numpy.array(numpy.ceil(sxrange-xfiltersize),dtype=int)
		sxstartrange[sxstartrange<0]=0
		sxendrange=numpy.array(numpy.floor(sxrange+xfiltersize)+1,dtype=int)
		sxendrange[sxendrange>inx]=inx

		systartrange=numpy.array(numpy.ceil(syrange-xfiltersize),dtype=int)
		systartrange[systartrange<0]=0
		syendrange=numpy.array(numpy.floor(syrange+xfiltersize)+1,dtype=int)
		syendrange[syendrange>iny]=iny
		#np.arange(8*6*3).reshape((8, 6, 3))

		indices=numpy.arange(outx*outy*2*3).reshape((2,outx*outy,3))#3is the maximum value...?pff.

		r=sxendrange-sxstartrange

		indices[0]=sxstartrange.repeat(outy)

		indices[1]=systartrange.repeat(outx).reshape(outx,outy).swapaxes(0,1).flatten()

		#systartrange=numpy.max(0,numpy.ceil(syrange-xfiltersize))
		#syendrange=numpy.min(numpy.floor(syrange+xfiltersize),iny-1)+1

		outbuf.fill(0)
		tempbuf=inbuf[indices[0],indices[1]]
		tempbuf+=inbuf[indices[0]+1,indices[1]]
		tempbuf+=inbuf[indices[0],indices[1]+1]
		tempbuf+=inbuf[indices[0]+1,indices[1]+1]
		tempbuf/=4.0
		outbuf[:]=tempbuf.reshape((outx,outy))
		#outbuf[:,:]=inbuf[]#inbuf[sxstartrange,systartrange] #+ inbuf[sxstartrange+1,systartrange] + inbuf[sxstartrange,systartrange+1] + inbuf[sxstartrange+1,systartrange+1])/4.0



	else:#old method
		for y in range(0,outy):

			sx = dx/2-0.5
			for x in range(0,outx):
				pixVal = 0
				w = 0

				#
				for ix in range(max( 0, ceil(sx-dx*filterSize)),min( floor( sx+dx*filterSize ), inx-1)+1):
					for iy in range(max( 0, ceil( sy-dx*filterSize ) ),min( floor( sy+dx*filterSize), iny-1)+1):
						pixVal += inbuf[ix,iy]
						w += 1
				outbuf[x ,y] = pixVal/w

				sx+=dx
			sy+=dy

def prolongate( inbuf, outbuf ):

	inx = inbuf.shape[0]
	iny = inbuf.shape[1]

	outx = outbuf.shape[0]
	outy = outbuf.shape[1]

	dx=inx/outx
	dy=iny/outy

	filterSize = 1
	xfiltersize=dx*filterSize
	#outx[:]=

	#outbuf.put(inbuf.repeat(4))
	if dx==0.5 and dy==0.5:
		outbuf[::2,::2]=inbuf
		outbuf[1::2,::2]=inbuf
		outbuf[::2,1::2]=inbuf
		outbuf[1::2,1::2]=inbuf
		#x=inbuf::.flatten().repeat(2)
	elif NUMPYALG:#numpy method
		sy=-dy/2
		sx=-dx/2
		xrange=numpy.arange(0,outx)
		yrange=numpy.arange(0,outy)

		sxrange=xrange*dx+sx
		syrange=yrange*dy+sy

		sxstartrange=numpy.array(numpy.ceil(sxrange-xfiltersize),dtype=int)
		sxstartrange[sxstartrange<0]=0
		sxendrange=numpy.array(numpy.floor(sxrange+xfiltersize)+1,dtype=int)
		sxendrange[sxendrange>=inx]=inx-1
		systartrange=numpy.array(numpy.ceil(syrange-xfiltersize),dtype=int)
		systartrange[systartrange<0]=0
		syendrange=numpy.array(numpy.floor(syrange+xfiltersize)+1,dtype=int)
		syendrange[syendrange>=iny]=iny-1

		indices=numpy.arange(outx*outy*2).reshape((2,outx*outy))
		indices[0]=sxstartrange.repeat(outy)
		indices[1]=systartrange.repeat(outx).reshape(outx,outy).swapaxes(0,1).flatten()

		#systartrange=numpy.max(0,numpy.ceil(syrange-xfiltersize))
		#syendrange=numpy.min(numpy.floor(syrange+xfiltersize),iny-1)+1
		#outbuf.fill(0)
		tempbuf=inbuf[indices[0],indices[1]]
		#tempbuf+=inbuf[indices[0]+1,indices[1]]
		#tempbuf+=inbuf[indices[0],indices[1]+1]
		#tempbuf+=inbuf[indices[0]+1,indices[1]+1]
		tempbuf/=4.0
		outbuf[:]=tempbuf.reshape((outx,outy))

		#outbuf.fill(0)
		#outbuf[xrange,yrange]=inbuf[sxstartrange,systartrange]# + inbuf[sxendrange,systartrange] + inbuf[sxstartrange,syendrange] + inbuf[sxendrange,syendrange])/4.0

	else:
		sy=-dy/2
		for y in range(0,outy):
			sx=-dx/2
			for x in range(0,outx):
				pixVal = 0
				weight = 0

				for ix in range(max( 0, ceil( sx-filterSize ) ),min( floor(sx+filterSize), inx-1 )+1):
					for iy in range(max( 0, ceil( sy-filterSize ) ),min( floor( sy+filterSize), iny-1 )+1):
						fx = abs( sx - ix )
						fy = abs( sy - iy )

						fval = (1-fx)*(1-fy)

						pixVal += inbuf[ix,iy] * fval
						weight += fval
				#if weight==0:
				#	print('error' )
				#	return
				outbuf[x,y]=pixVal/weight
				sx+=dx
			sy+=dy

def idx(r,c,cols):

	return r*cols+c+1


## smooth u using f at level
def smooth( U, F , linbcgiterations, planar):

	iter=0
	err=0

	rows = U.shape[1]
	cols = U.shape[0]

	n = U.size

	linbcg( n, F, U, 2, 0.001, linbcgiterations, iter, err , rows, cols, planar)



def calculate_defect( D, U, F ):


	sx = F.shape[0]
	sy = F.shape[1]

	h = 1.0/sqrt(sx*sy*1.0)
	h2i = 1.0/(h*h)

	h2i = 1
	D[1:-1,1:-1]=F[1:-1,1:-1] - U[:-2,1:-1] - U[2:,1:-1] - U[1:-1, :-2] - U[1:-1,2:] + 4*U[1:-1,1:-1]
	#sides
	D[1:-1,0]=F[1:-1,0] - U[:-2,0] - U[2:,0] - U[1:-1, 1] + 3*U[1:-1,0]
	D[1:-1,-1]=F[1:-1,-1] - U[:-2,-1] - U[2:,-1] - U[1:-1, -2] + 3*U[1:-1,-1]
	D[0,1:-1] = F[0,1:-1] - U[0,:-2] - U[0,:-2] - U[1,1:-1] + 3*U[0,1:-1]
	D[-1,1:-1] = F[-1,1:-1] - U[-1,:-2] - U[-1,:-2] - U[-1,1:-1] + 3*U[-1,1:-1]
	#coners
	D[0,0]=F[0,0] - U[0,1] - U[1,0] + 2*U[0,0]
	D[0,-1]=F[0,-1] - U[1,-1] - U[0,-2] + 2*U[0,-1]
	D[-1,0]=F[-1,0] - U[-2,0] - U[-1,1] + 2*U[-1,0]
	D[-1,-1]=F[-1,-1] - U[-2,-1] - U[-1,-2] + 2*U[-1,-1]

	# for y in range(0,sy):
	# 	for x in range(0,sx):
	#
	# 		w = max(0,x-1)
	# 		n = max(0,y-1)
	# 		e = min(sx, x+1)
	# 		s = min(sy, y+1)
	#
	#
	# 		D[x,y] = F[x,y] -( U[e,y] + U[w,y] + U[x,n]	+ U[x,s] - 4.0*U[x,y])

def add_correction( U, C ):
	U+=C

#def alloc_compbuf(xmax,ymax,pix, 1):
#	ar=numpy.array()


def solve_pde_multigrid( F, U , vcycleiterations, linbcgiterations, smoothiterations, mins, levels, useplanar, planar):

	xmax = F.shape[0]
	ymax = F.shape[1]

	#int i  # index for simple loops
	#int k  # index for iterating through levels
	#int k2 # index for iterating through levels in V-cycles

	## 1. restrict f to coarse-grid (by the way count the number of levels)
	##  k=0: fine-grid = f
	##  k=levels: coarsest-grid
	#pix = CB_VAL#what is this>???
	#int cycle
	#int sx, sy

	RHS=[]
	IU=[]
	VF=[]
	PLANAR=[]
	for a in range(0,levels+1):
		RHS.append(None)
		IU.append(None)
		VF.append(None)
		PLANAR.append(None)
	VF[0] = numpy.zeros((xmax,ymax), dtype=numpy.float)
	#numpy.fill(pix)!? TODO

	RHS[0] = F.copy()
	IU[0] = U.copy()
	PLANAR[0] = planar.copy()

	sx=xmax
	sy=ymax
	#print(planar)
	for k in range(0,levels):
		# calculate size of next level
		sx=int(sx/2)
		sy=int(sy/2)
		PLANAR[k+1] = numpy.zeros((sx,sy), dtype=numpy.float)
		RHS[k+1] = numpy.zeros((sx,sy), dtype=numpy.float)
		IU[k+1] = numpy.zeros((sx,sy), dtype=numpy.float)
		VF[k+1] = numpy.zeros((sx,sy), dtype=numpy.float)

		# restrict from level k to level k+1 (coarser-grid)
		restrictbuf(PLANAR[k], PLANAR[k+1])
		PLANAR[k+1]=PLANAR[k+1]>0
		#numpytoimage(PLANAR[k+1],'planar')
		#print(PLANAR[k+1])
		restrictbuf( RHS[k], RHS[k+1] )
		#numpytoimage(RHS[k+1],'rhs')



	# 2. find exact sollution at the coarsest-grid (k=levels)
	IU[levels].fill(0.0)#this was replaced to easify code. exact_sollution( RHS[levels], IU[levels] )

	# 3. nested iterations

	for k in range(levels-1,-1,-1):
		print('K:', str(k))

		# 4. interpolate sollution from last coarse-grid to finer-grid
		# interpolate from level k+1 to level k (finer-grid)
		prolongate( IU[k+1], IU[k] )
		#print('k',k)
		# 4.1. first target function is the equation target function
		#	(following target functions are the defect)
		copy_compbuf_data( RHS[k], VF[k] )

		#print('lanar ')

		# 5. V-cycle (twice repeated)

		for cycle in range(0,vcycleiterations):
			print('v-cycle iteration:', str(cycle))

			# 6. downward stroke of V
			for k2 in range(k,levels):
				# 7. pre-smoothing of initial sollution using target function
				#  zero for initial guess at smoothing
				#  (except for level k when iu contains prolongated result)
				if( k2!=k ):
					IU[k2].fill(0.0)

				for i in range(0,smoothiterations):
					smooth( IU[k2], VF[k2], linbcgiterations, PLANAR[k2])

				# 8. calculate defect at level
				#  d[k2] = Lh * ~u[k2] - f[k2]

				D = numpy.zeros_like(IU[k2])
				#if k2==0:
				#IU[k2][planar[k2]]=IU[k2].max()
				#print(IU[0])
				if useplanar and k2==0:
					IU[k2][PLANAR[k2]]=IU[k2].min()
				#if k2==0 :

				#	VF[k2][PLANAR[k2]]=0.0
				#	print(IU[0])
				calculate_defect( D, IU[k2], VF[k2] )

				# 9. restrict deffect as target function for next coarser-grid
				#  def -> f[k2+1]
				restrictbuf( D, VF[k2+1] )

			# 10. solve on coarsest-grid (target function is the deffect)
			#   iu[levels] should contain sollution for
			#   the f[levels] - last deffect, iu will now be the correction
			IU[levels].fill(0.0)#exact_sollution(VF[levels], IU[levels] )

			# 11. upward stroke of V
			for k2 in range(levels-1,k-1,-1):
				print('k2: ',str(k2))
				# 12. interpolate correction from last coarser-grid to finer-grid
				#   iu[k2+1] -> cor
				C = numpy.zeros_like(IU[k2])
				prolongate( IU[k2+1], C )


				# 13. add interpolated correction to initial sollution at level k2
				add_correction( IU[k2], C )

				# 14. post-smoothing of current sollution using target function
				for i in range(0, smoothiterations):

					smooth( IU[k2], VF[k2] ,linbcgiterations,PLANAR[k2])


				if useplanar and k2==0:
					IU[0][planar]=IU[0].min()
					#print(IU[0])

		#--- end of V-cycle

	#--- end of nested iteration

	# 15. final sollution
	#   IU[0] contains the final sollution

	U[:]=IU[0]


def asolve(b, x):
	x[:] = -4*b

def atimes(x, res):
	res[1:-1,1:-1]=x[:-2,1:-1]+x[2:,1:-1]+x[1:-1,:-2]+x[1:-1,2:] - 4*x[1:-1,1:-1]
	#sides
	res[1:-1,0]=x[0:-2,0]+x[2:,0]+x[1:-1,1] - 3*x[1:-1,0]
	res[1:-1,-1] = x[0:-2,-1]+x[2:,-1]+x[1:-1,-2]- 3*x[1:-1,-1]
	res[0,1:-1] = x[0, :-2] + x[0, 2:] + x[1, 1:-1] -3*x [0,1:-1]
	res[-1,1:-1] = x[-1, :-2] + x[-1, 2:] + x[-2, 1:-1] -3*x [-1,1:-1]
	#corners
	res[0,0]=x[1,0]+x[0,1]-2*x[0,0]
	res[-1,0]=x[-2,0]+x[-1,1]-2*x[-1,0]
	res[0,-1]=x[0,-2]+x[1,-1]-2*x[0,-1]
	res[-1,-1]=x[-1,-2]+x[-2,-1]-2*x[-1,-1]

def snrm(n, sx, itol):

	if (itol <= 3):
		temp=sx*sx
		ans=temp.sum()
		return sqrt(ans)
	else:
		temp=numpy.abs(sx)
		return temp.max()

#/**
# * Biconjugate Gradient Method
# * from Numerical Recipes in C
# */
def linbcg(n, b, x, itol, tol, itmax, iter, err, rows, cols, planar):

	p=numpy.zeros((cols,rows))
	pp=numpy.zeros((cols,rows))
	r=numpy.zeros((cols,rows))
	rr=numpy.zeros((cols,rows))
	z=numpy.zeros((cols,rows))
	zz=numpy.zeros((cols,rows))

	iter=0
	atimes(x,r)
	r[:]=b-r
	rr[:]=r

	atimes(r,rr)	  # minimum residual

	znrm=1.0

	if (itol == 1):
		bnrm=snrm(n,b,itol)

	elif (itol == 2):
		asolve(b,z)
		bnrm=snrm(n,z,itol)

	elif (itol == 3 or itol == 4):
		asolve(b,z)
		bnrm=snrm(n,z,itol)
		asolve(r,z)
		znrm=snrm(n,z,itol)
	else:
		print("illegal itol in linbcg")

	asolve(r,z)

	while (iter <= itmax):
		#print('linbcg iteration:', str(iter))
		iter+=1
		zm1nrm=znrm
		asolve(rr,zz)

		bknum=0.0

		temp=z*rr

		bknum=temp.sum()#-z[0]*rr[0]????

		if (iter == 1):
			p[:]=z
			pp[:]=zz

		else:
			bk=bknum/bkden
			p=bk*p+z
			pp=bk*pp+zz
		bkden=bknum
		atimes(p,z)
		temp=z*pp
		akden = temp.sum()
		ak=bknum/akden
		atimes(pp,zz)

		x+=ak*p
		r-= ak*z
		rr -= ak*zz

		asolve(r,z)

		if (itol == 1 or itol == 2):
			znrm=1.0
			err=snrm(n,r,itol)/bnrm
		elif (itol == 3 or itol == 4):
			znrm=snrm(n,z,itol)
			if (abs(zm1nrm-znrm) > EPS*znrm):
				dxnrm=abs(ak)*snrm(n,p,itol)
				err=znrm/abs(zm1nrm-znrm)*dxnrm
			else:
				err=znrm/bnrm
				continue
			xnrm=snrm(n,x,itol)

			if (err <= 0.5*xnrm):
				err /= xnrm
			else:
				err=znrm/bnrm
				continue
		if (err <= tol):
			break
	#if PLANAR_CONST and planar.shape==rr.shape:
	#	x[planar]=0.0


#--------------------------------------------------------------------


def numpysave(a,iname):
	inamebase=bpy.path.basename(iname)

	i=numpytoimage(a,inamebase)

	r=bpy.context.scene.render

	r.image_settings.file_format='OPEN_EXR'
	r.image_settings.color_mode='BW'
	r.image_settings.color_depth='32'

	i.save_render(iname)

def numpytoimage(a,iname):
	t=time.time()
	print('numpy to image - here')
	t=time.time()
	print(a.shape[0],a.shape[1])
	foundimage=False
	for image in bpy.data.images:

		if image.name[:len(iname)]==iname and image.size[0]==a.shape[0] and image.size[1]==a.shape[1]:
			i=image
			foundimage=True
	if not foundimage:
		bpy.ops.image.new(name=iname, width=a.shape[0], height=a.shape[1], color=(0, 0, 0, 1), alpha=True, generated_type='BLANK', float=True)
		for image in bpy.data.images:

			if image.name[:len(iname)]==iname and image.size[0]==a.shape[0] and image.size[1]==a.shape[1]:
				i=image

	d=a.shape[0]*a.shape[1]
	a=a.swapaxes(0,1)
	a=a.reshape(d)
	a=a.repeat(4)
	a[3::4]=1
	#i.pixels=a
	i.pixels[:]=a[:]#this gives big speedup!
	print('\ntime '+str(time.time()-t))
	return i


def imagetonumpy(i):
	t=time.time()
	inc=0

	width=i.size[0]
	height=i.size[1]
	x=0
	y=0
	count=0
	na=numpy.array((0.1),dtype=float)

	size=width*height
	na.resize(size*4)

	p=i.pixels[:]#these 2 lines are about 15% faster than na=i.pixels[:].... whyyyyyyyy!!?!?!?!?! Blender image data access is evil.
	na[:]=p
	#na=numpy.array(i.pixels[:])#this was terribly slow... at least I know why now, it probably
	na=na[::4]
	na=na.reshape(height,width)
	na=na.swapaxes(0,1)

	print('\ntime of image to numpy '+str(time.time()-t))
	return na

def tonemap(i):
	maxheight=i.max()
	minheight=i.min()
	i[:]=((i-minheight))/(maxheight-minheight)

def vert(column, row, z,XYscaling,Zscaling):
    """ Create a single vert """
    return column * XYscaling, row * XYscaling, z * Zscaling

def buildMesh(mesh_z,br):
    global rows
    global size   
    scale=1
    scalez=1
    decimateRatio= br.decimate_ratio #get variable from interactive table
    bpy.ops.object.select_all(action='DESELECT')
    for object in bpy.data.objects:
        if re.search("BasReliefMesh",str(object)):
            bpy.data.objects.remove(object)
            print("old basrelief removed")
        
  
      
    print("Building mesh")
    numY = mesh_z.shape[1]
    numX = mesh_z.shape[0]
    print(numX,numY)
    
    verts = list()
    faces = list()
    
    for i, row in enumerate(mesh_z):
        for j, col in enumerate(row):
            verts.append(vert(i, j, col,scale,scalez))

    count = 0
    for i in range (0, numY *(numX-1)):
        if count < numY-1:
            A = i  # the first vertex
            B = i+1  # the second vertex
            C = (i+numY)+1 # the third vertex
            D = (i+numY) # the fourth vertex
 
            face = (A,B,C,D)
            faces.append(face)
            count = count + 1
        else:
         count = 0

    # Create Mesh Datablock
    mesh = bpy.data.meshes.new("displacement")
    mesh.from_pydata(verts, [], faces)

    mesh.update()

    # make object from mesh
    new_object = bpy.data.objects.new('BasReliefMesh', mesh)
    scene = bpy.context.scene
    scene.collection.objects.link(new_object)

    #mesh object is made - preparing to decimate.
    ob=bpy.data.objects['BasReliefMesh']
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    bpy.context.active_object.dimensions= (br.widthmm/1000,br.heightmm/1000,br.thicknessmm/1000)
    bpy.context.active_object.location= (float(br.justifyx)*br.widthmm/1000,float(br.justifyy)*br.heightmm/1000,float(br.justifyz)*br.thicknessmm/1000)


    print("faces:" + str(len(ob.data.polygons)))
    print("vertices:" + str(len(ob.data.vertices)))
    if decimateRatio > 0.95:
        print("skipping decimate ratio > 0.95")
    else:
        m =  ob.modifiers.new(name="Foo", type='DECIMATE')
        m.ratio=decimateRatio
        print("decimating with ratio:"+str(decimateRatio))
        bpy.ops.object.modifier_apply({"object" : ob}, modifier=m.name)
        print("decimated")
        print("faces:" + str(len(ob.data.polygons)))
        print("vertices:" + str(len(ob.data.vertices)))
 
# Switches to cycles render to CYCLES to render the sceen then switches it back to BLENDERCAM_RENDER for basRelief

def renderScene(width,height,bit_diameter,passes_per_radius):
    print("rendering scene")
    bpy.context.scene.render.engine = 'CYCLES'
    scene = bpy.context.scene
    # Set render resolution
    passes=bit_diameter/(2*passes_per_radius)
    x=round(width/passes)
    y=round(height/passes)
    print(x,y,passes)
    scene.render.resolution_x = x
    scene.render.resolution_y = y
    scene.render.resolution_percentage = 100	
    bpy.ops.render.render(animation=False, write_still=False, use_viewport=True, layer="", scene="")
    bpy.context.scene.render.engine = 'BLENDERCAM_RENDER'
    print("done rendering")
    
    
def problemAreas(br):
	t=time.time()

	i=bpy.data.images[br.source_image_name]
	i=bpy.data.images["Viewer Node"]
	silh_thres=br.silhouette_threshold
	recover_silh=br.recover_silhouettes
	silh_scale=br.silhouette_scale
	MINS=br.min_gridsize
	smoothiterations=br.smooth_iterations
	vcycleiterations=br.vcycle_iterations
	linbcgiterations=br.linbcg_iterations
	useplanar=br.use_planar
	#scale down before:
	if br.gradient_scaling_mask_use:
		m=bpy.data.images[br.gradient_scaling_mask_name]
		#mask=nar=imagetonumpy(m)

	#if br.scale_down_before_use:
	#	i.scale(int(i.size[0]*br.scale_down_before),int(i.size[1]*br.scale_down_before))
	#	if br.gradient_scaling_mask_use:
	#		m.scale(int(m.size[0]*br.scale_down_before),int(m.size[1]*br.scale_down_before))

	nar=imagetonumpy(i)
	#return
	if br.gradient_scaling_mask_use:
		mask=imagetonumpy(m)
	#put image to scale
	tonemap(nar)
	nar=1-nar# reverse z buffer+ add something
	print(nar.min(),nar.max())
	gx=nar.copy()
	gx.fill(0)
	gx[:-1,:]=nar[1:,:]-nar[:-1,:]
	gy=nar.copy()
	gy.fill(0)
	gy[:,:-1]=nar[:,1:]-nar[:,:-1]

	#it' ok, we can treat neg and positive silh separately here:
	a=br.attenuation
	planar=nar<(nar.min()+0.0001)#numpy.logical_or(silhxplanar,silhyplanar)#
	#sqrt for silhouettes recovery:
	sqrarx=numpy.abs(gx)
	for iter in range(0,br.silhouette_exponent):
		sqrarx=numpy.sqrt(sqrarx)
	sqrary=numpy.abs(gy)
	for iter in range(0,br.silhouette_exponent):
		sqrary=numpy.sqrt(sqrary)


	#detect and also recover silhouettes:
	silhxpos=gx>silh_thres
	gx=gx*(-silhxpos)+recover_silh*(silhxpos*silh_thres*silh_scale)*sqrarx
	silhxneg=gx<-silh_thres
	gx=gx*(-silhxneg)-recover_silh*(silhxneg*silh_thres*silh_scale)*sqrarx
	silhx=numpy.logical_or(silhxpos,silhxneg)
	gx=gx*silhx+(1.0/a*numpy.log(1.+a*(gx)))*(-silhx)#attenuate

	#if br.fade_distant_objects:
	#	gx*=(nar)
	#	gy*=(nar)

	silhypos=gy>silh_thres
	gy=gy*(-silhypos)+recover_silh*(silhypos*silh_thres*silh_scale)*sqrary
	silhyneg=gy<-silh_thres
	gy=gy*(-silhyneg)-recover_silh*(silhyneg*silh_thres*silh_scale)*sqrary
	silhy=numpy.logical_or(silhypos,silhyneg)#both silh
	gy=gy*silhy+(1.0/a*numpy.log(1.+a*(gy)))*(-silhy)#attenuate

	#now scale slopes...
	if br.gradient_scaling_mask_use:
		gx*=mask
		gy*=mask


	divg=gx+gy
	divga=numpy.abs(divg)
	divgp= divga>silh_thres/4.0
	divgp=1-divgp
	for a in range(0,2):
		atimes(divgp,divga)
		divga=divgp

	numpytoimage(divga,'problem')


def relief(br):
	t=time.time()

	i=bpy.data.images[br.source_image_name]
	i=bpy.data.images["Viewer Node"]
	silh_thres=br.silhouette_threshold
	recover_silh=br.recover_silhouettes
	silh_scale=br.silhouette_scale
	MINS=br.min_gridsize
	smoothiterations=br.smooth_iterations
	vcycleiterations=br.vcycle_iterations
	linbcgiterations=br.linbcg_iterations
	useplanar=br.use_planar
	#scale down before:
	if br.gradient_scaling_mask_use:
		m=bpy.data.images[br.gradient_scaling_mask_name]
		#mask=nar=imagetonumpy(m)

	#if br.scale_down_before_use:
	#	i.scale(int(i.size[0]*br.scale_down_before),int(i.size[1]*br.scale_down_before))
	#	if br.gradient_scaling_mask_use:
	#		m.scale(int(m.size[0]*br.scale_down_before),int(m.size[1]*br.scale_down_before))

	nar=imagetonumpy(i)
	#return
	if br.gradient_scaling_mask_use:
		mask=imagetonumpy(m)
	#put image to scale
	tonemap(nar)
	nar=1-nar# reverse z buffer+ add something
	print(nar.min(),nar.max())
	gx=nar.copy()
	gx.fill(0)
	gx[:-1,:]=nar[1:,:]-nar[:-1,:]
	gy=nar.copy()
	gy.fill(0)
	gy[:,:-1]=nar[:,1:]-nar[:,:-1]

	#it' ok, we can treat neg and positive silh separately here:
	a=br.attenuation
	planar=nar<(nar.min()+0.0001)#numpy.logical_or(silhxplanar,silhyplanar)#
	#sqrt for silhouettes recovery:
	sqrarx=numpy.abs(gx)
	for iter in range(0,br.silhouette_exponent):
		sqrarx=numpy.sqrt(sqrarx)
	sqrary=numpy.abs(gy)
	for iter in range(0,br.silhouette_exponent):
		sqrary=numpy.sqrt(sqrary)


	#detect and also recover silhouettes:
	silhxpos=gx>silh_thres
	print("*** silhxpos is %s" %silhxpos)
	gx=gx*(~silhxpos)+recover_silh*(silhxpos*silh_thres*silh_scale)*sqrarx
	silhxneg=gx<-silh_thres
	gx=gx*(~silhxneg)-recover_silh*(silhxneg*silh_thres*silh_scale)*sqrarx
	silhx=numpy.logical_or(silhxpos,silhxneg)
	gx=gx*silhx+(1.0/a*numpy.log(1.+a*(gx)))*(~silhx)#attenuate

	#if br.fade_distant_objects:
	#	gx*=(nar)
	#	gy*=(nar)

	silhypos=gy>silh_thres
	gy=gy*(~silhypos)+recover_silh*(silhypos*silh_thres*silh_scale)*sqrary
	silhyneg=gy<-silh_thres
	gy=gy*(~silhyneg)-recover_silh*(silhyneg*silh_thres*silh_scale)*sqrary
	silhy=numpy.logical_or(silhypos,silhyneg)#both silh
	gy=gy*silhy+(1.0/a*numpy.log(1.+a*(gy)))*(~silhy)#attenuate

	#now scale slopes...
	if br.gradient_scaling_mask_use:
		gx*=mask
		gy*=mask

	#
	#print(silhx)
	#silhx=abs(gx)>silh_thres
	#gx=gx*(-silhx)
	#silhy=abs(gy)>silh_thres
	#gy=gy*(-silhy)


	divg=gx+gy
	divg[1:,:]=divg[1:,:]-gx[:-1,:] #subtract x
	divg[:,1:]=divg[:,1:]-gy[:,:-1] #subtract y

	if br.detail_enhancement_use:# fourier stuff here!disabled by now
		print("detail enhancement")
		rows,cols=gx.shape
		crow,ccol = int(rows/2), int(cols/2)
		#dist=int(br.detail_enhancement_freq*gx.shape[0]/(2))
		#bandwidth=.1
		#dist=
		divgmin=divg.min()
		divg+=divgmin
		divgf=numpy.fft.fft2(divg)
		divgfshift=numpy.fft.fftshift(divgf)
		#mspectrum = 20*numpy.log(numpy.abs(divgfshift))
		#numpytoimage(mspectrum,'mspectrum')
		mask=divg.copy()
		pos=numpy.array((crow,ccol))

		#bpy.context.scene.view_settings.curve_mapping.initialize()
		#cur=bpy.context.scene.view_settings.curve_mapping.curves[0]
		def filterwindow(x,y, cx = 0, cy = 0):#, curve=None):
			return abs((cx-x))+abs((cy-y))
			#v=(abs((cx-x)/(cx))+abs((cy-y)/(cy)))
			#return v

		mask=numpy.fromfunction(filterwindow,divg.shape, cx=crow, cy=ccol)#, curve=cur)
		mask=numpy.sqrt(mask)
		#for x in range(mask.shape[0]):
		#	for y in range(mask.shape[1]):
		#		mask[x,y]=cur.evaluate(mask[x,y])
		maskmin=mask.min()
		maskmax=mask.max()
		mask=(mask-maskmin)/(maskmax-maskmin)
		mask*=br.detail_enhancement_amount
		mask+=1-mask.max()
		#mask+=1
		mask[crow-1:crow+1,ccol-1:ccol+1]=1#to preserve basic freqencies.
		#numpytoimage(mask,'mask')
		divgfshift = divgfshift*mask
		divgfshift = numpy.fft.ifftshift(divgfshift)
		divg = numpy.abs(numpy.fft.ifft2(divgfshift))
		divg-=divgmin
		divg=-divg
		print("detail enhancement finished")

	levels=0
	mins = min(nar.shape[0],nar.shape[1])
	while (mins>=MINS):
		levels+=1
		mins = mins/2


	target=numpy.zeros_like(divg)

	solve_pde_multigrid( divg, target ,vcycleiterations, linbcgiterations, smoothiterations, mins, levels, useplanar, planar)

	tonemap(target)
	
	buildMesh(target,br)

#	ipath=bpy.path.abspath(i.filepath)[:-len(bpy.path.basename(i.filepath))]+br.output_image_name+'.exr'
#	numpysave(target,ipath)
	t=time.time()-t
	print('total time:'+ str(t)+'\n')
	#numpytoimage(target,br.output_image_name)


class BasReliefsettings(bpy.types.PropertyGroup):
	source_image_name: bpy.props.StringProperty(name='Image source', description='image source')
#	output_image_name: bpy.props.StringProperty(name='Image target', description='image output name')
	bit_diameter: FloatProperty(name="Diameter of ball end in mm", description="Diameter of bit which will be used for carving", min=0.01, max=50.0, default=3.175, precision=PRECISION)
	pass_per_radius: bpy.props.IntProperty(name="Passes per radius", description="Amount of passes per radius\n(more passes, more mesh precision)",default=2, min=1, max=10)
	widthmm: bpy.props.IntProperty(name="Desired width in mm", default=200, min=5, max=4000)
	heightmm: bpy.props.IntProperty(name="Desired height in mm", default=150, min=5, max=4000)
	thicknessmm: bpy.props.IntProperty(name="Thickness in mm", default=15, min=5, max=100)
	
	justifyx: bpy.props.EnumProperty(name="X",items=[('1', 'Left','', 0),('-0.5', 'Centered','', 1),('-1', 'Right','', 2)],default='-1')
	justifyy: bpy.props.EnumProperty(name="Y",items=[('1', 'Bottom','', 0),('-0.5', 'Centered','', 2),('-1', 'Top','', 1),],default='-1')
	justifyz: bpy.props.EnumProperty(name="Z",items=[('-1', 'Below 0','', 0),('-0.5', 'Centered','', 2),('1', 'Above 0','', 1),],default='-1')
     
	silhouette_threshold: FloatProperty(name="Silhouette threshold", description="Silhouette threshold", min=0.000001, max=1.0, default=0.003, precision=PRECISION)
	recover_silhouettes: bpy.props.BoolProperty(name="Recover silhouettes",description="", default=True)
	silhouette_scale: FloatProperty(name="Silhouette scale", description="Silhouette scale", min=0.000001, max=5.0, default=0.3, precision=PRECISION)
	silhouette_exponent: bpy.props.IntProperty(name="Silhouette square exponent", description="If lower, true depht distances between objects will be more visibe in the relief", default=3, min=0, max=5)
	attenuation: FloatProperty(name="Gradient attenuation", description="Gradient attenuation", min=0.000001, max=100.0, default=1.0, precision=PRECISION)
	min_gridsize: bpy.props.IntProperty(name="Minimum grid size", default=16, min=2, max=512)
	smooth_iterations: bpy.props.IntProperty(name="Smooth iterations", default=1, min=1, max=64)
	vcycle_iterations: bpy.props.IntProperty(name="V-cycle iterations",description="set up higher for plananr constraint", default=2, min=1, max=128)
	linbcg_iterations: bpy.props.IntProperty(name="Linbcg iterations",description="set lower for flatter relief, and when using planar constraint", default=5, min=1, max=64)
	use_planar: bpy.props.BoolProperty(name="Use planar constraint",description="", default=False)
	gradient_scaling_mask_use: bpy.props.BoolProperty(name="Scale gradients with mask",description="", default=False)
	decimate_ratio: FloatProperty(name="Decimate Ratio", description="Simplify the mesh using the Decimate modifier.  The lower the value the more simplyfied", min=0.01, max=1.0, default=0.1, precision=PRECISION)


	gradient_scaling_mask_name: bpy.props.StringProperty(name='Scaling mask name', description='mask name')
	scale_down_before_use: bpy.props.BoolProperty(name="Scale down image before processing",description="", default=False)
	scale_down_before: FloatProperty(name="Image scale", description="Image scale", min=0.025, max=1.0, default=.5, precision=PRECISION)
	detail_enhancement_use: bpy.props.BoolProperty(name="Enhance details ",description="enhance details by frequency analysis", default=False)
	#detail_enhancement_freq=FloatProperty(name="frequency limit", description="Image scale", min=0.025, max=1.0, default=.5, precision=PRECISION)
	detail_enhancement_amount: FloatProperty(name="amount", description="Image scale", min=0.025, max=1.0, default=.5, precision=PRECISION)

	advanced: bpy.props.BoolProperty(name="Advanced options",description="show advanced options", default=True)

class BASRELIEF_Panel(bpy.types.Panel):
	"""Bas relief panel"""
	bl_label = "Bas relief"
	bl_idname = "WORLD_PT_BASRELIEF"

	bl_space_type = "PROPERTIES"
	bl_region_type = "WINDOW"
	bl_context = "render"

	COMPAT_ENGINES = {'BLENDERCAM_RENDER'}

	#def draw_header(self, context):
	#   self.layout.menu("CAM_CUTTER_MT_presets", text="CAM Cutter")
	@classmethod
	def poll(cls, context):
		rd = context.scene.render
		return rd.engine in cls.COMPAT_ENGINES

	def draw(self, context):
		layout = self.layout
		#print(dir(layout))
		s=bpy.context.scene

		br=s.basreliefsettings

		#if br:
			#cutter preset
		layout.operator("scene.calculate_bas_relief", text="Calculate relief")
		layout.prop(br,'advanced')
		layout.prop_search(br,'source_image_name', bpy.data, "images")
#		layout.prop(br,'output_image_name')
		layout.label(text="Project parameters")
		layout.prop(br,'bit_diameter')
		layout.prop(br,'pass_per_radius')
		layout.prop(br,'widthmm')
		layout.prop(br,'heightmm')
		layout.prop(br,'thicknessmm')
		
		layout.label(text="Justification")
		layout.prop(br,'justifyx')
		layout.prop(br,'justifyy')
		layout.prop(br,'justifyz')
		
		layout.label(text="Silhouette")
		layout.prop(br,'silhouette_threshold')
		layout.prop(br,'recover_silhouettes')
		if br.recover_silhouettes:
			layout.prop(br,'silhouette_scale')
			if br.advanced:
				layout.prop(br,'silhouette_exponent')
		#layout.template_curve_mapping(br,'curva')
		if br.advanced:
			#layout.prop(br,'attenuation')
			layout.prop(br,'min_gridsize')
			layout.prop(br,'smooth_iterations')
		layout.prop(br,'vcycle_iterations')
		layout.prop(br,'linbcg_iterations')
		layout.prop(br,'use_planar')
		layout.prop(br,'decimate_ratio')


		layout.prop(br,'gradient_scaling_mask_use')
		if br.advanced:
			if br.gradient_scaling_mask_use:
				layout.prop_search(br,'gradient_scaling_mask_name', bpy.data, "images")
			layout.prop(br,'detail_enhancement_use')
			if br.detail_enhancement_use:
				#layout.prop(br,'detail_enhancement_freq')
				layout.prop(br,'detail_enhancement_amount')
				#print(dir(layout))
				#layout.prop(s.view_settings.curve_mapping,"curves")
				#layout.label('Frequency scaling:')
				#s.view_settings.curve_mapping.clip_max_y=2

				#layout.template_curve_mapping(s.view_settings, "curve_mapping")

		#layout.prop(br,'scale_down_before_use')
		#if br.scale_down_before_use:
		#	layout.prop(br,'scale_down_before')

class DoBasRelief(bpy.types.Operator):
	"""calculate Bas relief"""
	bl_idname = "scene.calculate_bas_relief"
	bl_label = "calculate Bas relief"
	bl_options = {'REGISTER', 'UNDO'}

	processes=[]

	#@classmethod
	#def poll(cls, context):
	#	return context.active_object is not None

	def execute(self, context):
		s=bpy.context.scene
		br=s.basreliefsettings
		
		renderScene(br.widthmm,br.heightmm,br.bit_diameter,br.pass_per_radius)
		
		relief(br)
		return {'FINISHED'}

class ProblemAreas(bpy.types.Operator):
	"""find Bas relief Problem areas"""
	bl_idname = "scene.problemareas_bas_relief"
	bl_label = "problem areas Bas relief"
	bl_options = {'REGISTER', 'UNDO'}

	processes=[]

	#@classmethod
	#def poll(cls, context):
	#	return context.active_object is not None

	def execute(self, context):
		s=bpy.context.scene
		br=s.basreliefsettings
		problemAreas(br)
		return {'FINISHED'}


def get_panels():
	return(
	BasReliefsettings,
	BASRELIEF_Panel,
	DoBasRelief,
	ProblemAreas
	)

def register():
	for p in get_panels():
		bpy.utils.register_class(p)
	s=bpy.types.Scene
	s.basreliefsettings = bpy.props.PointerProperty(type=BasReliefsettings)

def unregister():
	for p in get_panels():
		bpy.utils.unregister_class(p)
	s=bpy.types.Scene
	del s.basreliefsettings

if __name__ == "__main__":
	register()
