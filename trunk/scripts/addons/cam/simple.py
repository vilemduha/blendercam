import math,sys,os,string
import bpy
import mathutils 
from mathutils import *
from math import *

def tuple_add(t,t1):#add two tuples as Vectors
	return (t[0]+t1[0],t[1]+t1[1],t[2]+t1[2])

def tuple_sub(t,t1):#sub two tuples as Vectors
	return (t[0]-t1[0],t[1]-t1[1],t[2]-t1[2])

def tuple_mul(t,c):#multiply two tuples with a number
	return (t[0]*c,t[1]*c,t[2]*c)
	

def progress(text,n=None):
	'''function for reporting during the script, works for background operations in the header.'''
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


def activate(o):
	s=bpy.context.scene
	bpy.ops.object.select_all(action='DESELECT')
	o.select=True
	s.objects.active=o
	

def dist2d(v1,v2):
	'''distance between two points in 2d'''
	return math.sqrt((v1[0]-v2[0])*(v1[0]-v2[0])+(v1[1]-v2[1])*(v1[1]-v2[1]))

def delob(ob):
	'''object deletion for multiple uses'''
	activate(ob)
	bpy.ops.object.delete(use_global=False)

def dupliob(o,pos):
	'''helper function for visualising cutter positions'''
	activate(o)
	bpy.ops.object.duplicate()
	s=1.0/BULLET_SCALE
	bpy.ops.transform.resize(value=(s, s, s), constraint_axis=(False, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
	o=bpy.context.active_object
	bpy.ops.rigidbody.object_remove()
	o.location=pos

def compare(v1,v2,vmiddle,e):
	'''comparison for optimisation of paths'''
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
	

def isVerticalLimit(v1,v2,limit):
	'''test path segment on verticality threshold, for protect_vertical option'''
	z=abs(v1[2]-v2[2])
	#verticality=0.05 
	#this will be better.
	#
	#print(a)
	if z>0:
		v2d=Vector((0,0,-1))
		v3d=Vector((v1[0]-v2[0],v1[1]-v2[1],v1[2]-v2[2]))
		a=v3d.angle(v2d)
		if a>pi/2:
			a=abs(a-pi)
		#print(a)
		if a<limit:
			#print(abs(v1[0]-v2[0])/z)
			#print(abs(v1[1]-v2[1])/z)
			if v1[2]>v2[2]:
				v1=(v2[0],v2[1],v1[2])
				return v1,v2
			else: 
				v2=(v1[0],v1[1],v2[2])
				return v1,v2
	return v1,v2
	
def getCachePath(o):
	fn=bpy.data.filepath
	l=len(bpy.path.basename(fn))
	bn=bpy.path.basename(fn)[:-6]
	
	
	iname=fn[:-l]+'temp_cam'+os.sep+bn+'_'+o.name
	return iname

def safeFileName(name):#for export gcode
	valid_chars = "-_.()%s%s" % (string.ascii_letters, string.digits)
	filename=''.join(c for c in name if c in valid_chars)
	return filename