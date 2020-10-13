# blender CAM __init__.py (c) 2012 Vilem Novak
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

bl_info = {
	"name": "Send to 3d printer",
	"author": "Vilem Novak",
	"version": (0, 1, 0),
	"blender": (2, 7, 0),
	"location": "Render > Engine > 3d printer",
	"description": "Send 3d model to printer. Needs Cura to be installed on your system.",
	"warning": "",
	"wiki_url": "blendercam.blogspot.com",
	"tracker_url": "",
	"category": "Scene"}

import bpy
from bpy.props import *
import subprocess, os
import threading
import bgl, blf
PRECISION=7

class PrintSettings(bpy.types.PropertyGroup):
	"""stores all data for machines"""
	#name = bpy.props.StringProperty(name="Machine Name", default="Machine")
	slicer = EnumProperty(name='System',
		items=(('CURA','Cura','the default slicer'),('INTERNAL','Internal (not existing)','experimental code')),
		description='System to use',
		default='CURA')

	printers=[]
	for p in bpy.utils.script_paths():
		try:
			directory=p+'\\addons\\print_3d\\machine_profiles\\'
			list=os.listdir(directory)
			for profile in list:
				if profile[-4:]=='.ini':
					profile=profile
					printers.append((profile[:-4],profile[:-4],profile+' config file'))
		except:
			pass;

	printer = EnumProperty(name='printer',
		items=printers,
		description='Printer')
		#default='PEACHY')

	presets=[]
	for p in bpy.utils.script_paths():
		try:
			directory=p+'\\addons\\print_3d\\ini\\'
			list=os.listdir(directory)
			for preset in list:
				if preset[-4:]=='.ini':
					#preset=preset[:-4]
					presets.append((directory+preset,preset[:-4],preset+' config file'))
		except:
			pass;

	preset = EnumProperty(name='preset',
		items=presets,
		description='Preset')
		#default='PEACHY')
	filepath_engine = StringProperty(
				name="Cura binary location",
				description="Path to engine executable",
				subtype='FILE_PATH',
				)
	dirpath_engine = StringProperty(
				name="Cura directory",
				description="Path to cura top directory",
				subtype='DIR_PATH',
				)
	interface = EnumProperty(name='interface',
		items=(('STANDARD','Standard user',"Everybody, if you really don't want to mess with how things work"),('DEVELOPER','Developer','If you want to improve how things work and understand what you are doing')),
		description='Interface type',
		default='DEVELOPER')
	mm = 0.001

	# layerThickness=bpy.props.FloatProperty(name="layerThickness", description="layerThickness", default=0.1 * mm, min=0.00001, max=320000,precision=PRECISION)
	# initialLayerThickness=bpy.props.FloatProperty(name="initialLayerThickness", description="initialLayerThickness", default=0.15 * mm, min=0.00001, max=320000,precision=PRECISION)
	# filamentDiameter=bpy.props.FloatProperty(name="filamentDiameter", description="filamentDiameter", default=0.4 * mm, min=0.00001, max=320000,precision=PRECISION)
	# filamentFlow=bpy.props.FloatProperty(name="filamentFlow", description="filamentFlow", default=0.4 * mm, min=0.00001, max=320000,precision=PRECISION)
	# extrusionWidth=bpy.props.FloatProperty(name="extrusionWidth", description="extrusionWidth", default=0.4 * mm, min=0.00001, max=320000,precision=PRECISION)
	# insetCount=bpy.props.IntProperty(name="insetCount", description="insetCount", default=1, min=0, max=1000)
	# downSkinCount=bpy.props.FloatProperty(name="downSkinCount", description="downSkinCount", default=1, min=0.00001, max=320000,precision=PRECISION)
	# upSkinCount=bpy.props.FloatProperty(name="upSkinCount", description="upSkinCount", default=1, min=0.00001, max=320000,precision=PRECISION)
	# infillOverlap=bpy.props.FloatProperty(name="infillOverlap", description="infillOverlap", default=0.4 * mm, min=0.00001, max=320000,precision=PRECISION)
	# initialSpeedupLayers=bpy.props.FloatProperty(name="initialSpeedupLayers", description="initialSpeedupLayers", default=0.4 * mm, min=0.00001, max=320000,precision=PRECISION)
	# initialLayerSpeed=bpy.props.FloatProperty(name="initialLayerSpeed", description="initialLayerSpeed", default=0.4 * mm, min=0.00001, max=320000,precision=PRECISION)
	# printSpeed=bpy.props.FloatProperty(name="printSpeed", description="printSpeed", default=0.4 * mm, min=0.00001, max=320000,precision=PRECISION)
	# infillSpeed=bpy.props.FloatProperty(name="infillSpeed", description="infillSpeed", default=0.4 * mm, min=0.00001, max=320000,precision=PRECISION)
	# moveSpeed=bpy.props.FloatProperty(name="moveSpeed", description="moveSpeed", default=0.4 * mm, min=0.00001, max=320000,precision=PRECISION)
	# fanSpeedMin=bpy.props.FloatProperty(name="fanSpeedMin", description="fanSpeedMin", default=0.4 * mm, min=0.00001, max=320000,precision=PRECISION)
	# fanSpeedMax=bpy.props.FloatProperty(name="fanSpeedMax", description="fanSpeedMax", default=0.4 * mm, min=0.00001, max=320000,precision=PRECISION)
	# supportAngle=bpy.props.FloatProperty(name="supportAngle", description="supportAngle", default=0.4 , min=0.00000, max=3.141926,precision=PRECISION,subtype="ANGLE",)
	# supportEverywhere=bpy.props.BoolProperty(name="supportEverywhere", description="supportEverywhere", default=0)
	# supportLineDistance=bpy.props.FloatProperty(name="supportLineDistance", description="supportLineDistance", default=0.4 * mm, min=0.00001, max=320000,precision=PRECISION)
	# supportXYDistance=bpy.props.FloatProperty(name="supportXYDistance", description="supportXYDistance", default=0.4 * mm, min=0.00001, max=320000,precision=PRECISION)
	# supportZDistance=bpy.props.FloatProperty(name="supportZDistance", description="supportZDistance", default=0.4 * mm, min=0.00001, max=320000,precision=PRECISION)
	# supportExtruder=bpy.props.FloatProperty(name="supportExtruder", description="supportExtruder", default=0.4 * mm, min=0.00001, max=320000,precision=PRECISION)
	# retractionAmount=bpy.props.FloatProperty(name="retractionAmount", description="retractionAmount", default=0.4 * mm, min=0.00001, max=320000,precision=PRECISION)
	# retractionSpeed=bpy.props.FloatProperty(name="retractionSpeed", description="retractionSpeed", default=0.4 * mm, min=0.00001, max=320000,precision=PRECISION)
	# retractionMinimalDistance=bpy.props.FloatProperty(name="retractionMinimalDistance", description="retractionMinimalDistance", default=0.4 * mm, min=0.00001, max=320000,precision=PRECISION)
	# retractionAmountExtruderSwitch=bpy.props.FloatProperty(name="retractionAmountExtruderSwitch", description="retractionAmountExtruderSwitch", default=0.4 * mm, min=0.00001, max=320000,precision=PRECISION)
	# minimalExtrusionBeforeRetraction=bpy.props.FloatProperty(name="minimalExtrusionBeforeRetraction", description="minimalExtrusionBeforeRetraction", default=0.4 * mm, min=0.00001, max=320000,precision=PRECISION)
	# enableCombing=bpy.props.BoolProperty(name="enableCombing", description="enableCombing", default=0)
	# multiVolumeOverlap=bpy.props.FloatProperty(name="multiVolumeOverlap", description="multiVolumeOverlap", default=0.4 * mm, min=0.00001, max=320000,precision=PRECISION)
	# objectSink=bpy.props.FloatProperty(name="objectSink", description="objectSink", default=0.4 * mm, min=0.00001, max=320000,precision=PRECISION)
	# minimalLayerTime=bpy.props.FloatProperty(name="minimalLayerTime", description="minimalLayerTime", default=0.4 * mm, min=0.00001, max=320000,precision=PRECISION)
	# minimalFeedrate=bpy.props.FloatProperty(name="minimalFeedrate", description="minimalFeedrate", default=0.4 * mm, min=0.00001, max=320000,precision=PRECISION)
	# coolHeadLift=bpy.props.BoolProperty(name="coolHeadLift", description="coolHeadLift", default=0)
	#
	# startCode=	 bpy.props.StringProperty(name='LimitstartCodecurve', description='startCode')
	# endCode=   bpy.props.StringProperty(name='endCode', description='endCode')
	#
	# fixHorrible=bpy.props.BoolProperty(name="fixHorrible", description="fixHorrible", default=0)
	#
	# propnames = ["layerThickness","initialLayerThickness","filamentDiameter","filamentFlow","extrusionWidth","insetCount","downSkinCount","upSkinCount","infillOverlap","initialSpeedupLayers","initialLayerSpeed","printSpeed","infillSpeed","printSpeed","moveSpeed","fanSpeedMin","fanSpeedMax","supportAngle","supportEverywhere","supportLineDistance","supportXYDistance","supportZDistance","supportExtruder","retractionAmount","retractionSpeed","retractionMinimalDistance","retractionAmountExtruderSwitch","minimalExtrusionBeforeRetraction","enableCombing","multiVolumeOverlap","objectSink","minimalLayerTime","minimalFeedrate","coolHeadLift","startCode","endCode","fixHorrible"]


class threadComPrint3d:#object passed to threads to read background process stdout info
	def __init__(self,ob,proc):
		self.obname=ob.name
		self.outtext=''
		self.proc=proc
		self.lasttext=''
		self.progress=0

def threadread_print3d( tcom):
	"""reads stdout of background process, done this way to have it non-blocking"""
	#print(tcom.proc)
	#if tcom.proc!=None:
	inline = tcom.proc.stdout.readline()
	inline=str(inline)
	s=inline.find('Preparing: ')
	if s>-1:
		perc=inline[ s+11 :s+14]
		tcom.outtext=''.join(c for c in perc if c.isdigit())
		tcom.progress = min(100,int(tcom.outtext))
	else:
		#print(inline)
		s=inline.find('GCode')
		#print(s)
		if s>-1:
			tcom.outtext='finished'#inline[s:]




# def header_info_print3d(self, context):
# 	"""writes background operations data to header"""
# 	s=bpy.context.scene
# 	self.layout.label(s.print3d_text)

@bpy.app.handlers.persistent
def timer_update_print3d(context):
	"""monitoring of background processes"""
	text=''
	s=bpy.context.scene

	if hasattr(bpy.ops.object.print3d.__class__,'print3d_processes'):
		processes=bpy.ops.object.print3d.__class__.print3d_processes
		for p in processes:
			#proc=p[1].proc
			readthread=p[0]
			tcom=p[1]
			if not readthread.is_alive():
				readthread.join()
				#readthread.
				tcom.lasttext=tcom.outtext
				if tcom.outtext!='':
					#print(tcom.obname,tcom.outtext)
					tcom.outtext=''

				if 'finished'in tcom.lasttext:#'GCode file saved'
					processes.remove(p)

				else:
					readthread=threading.Thread(target=threadread_print3d, args = ([tcom]), daemon=True)
					readthread.start()
					p[0]=readthread

			if tcom.lasttext!=tcom.outtext:
				tcom.lasttext=tcom.outtext
				for area in bpy.context.screen.areas:
					#print(area.type)
					if area.type == 'VIEW_3D':
						area.tag_redraw()


def draw_callback_px_box(self, context):
	wm = context.window_manager
	sc = context.scene
	pos_x, pos_y = 0,0 #getDisplayLocation(context)

	# get text-width/height to resize the box

	# Got the size right, now draw box using proper colors
	box_color_r, box_color_g, box_color_b, box_color_alpha = .2,.6,.2,.1#sc.screencast_keys_box_color
	if hasattr(bpy.ops.object.print3d.__class__,'print3d_processes'):
		processes=bpy.ops.object.print3d.__class__.print3d_processes
		i=0
		for p in processes:

			#proc=p[1].proc
			readthread=p[0]
			tcom=p[1]
			progress=tcom.progress*.01
			box_width = context.region.width * progress
			offset_y = 80
			bar_height = 30
			x0 = 0# max(0, pos_x - padding_x)
			y0 = context.region.height-offset_y-bar_height*i# max(0, pos_y - padding_y)
			x1 = box_width
			y1 = bar_height+y0
			positions = [[x0, y0], [x0, y1], [x1, y1], [x1, y0]]
			settings = [[bgl.GL_QUADS, min(0.0, box_color_alpha)], [bgl.GL_LINE_LOOP, min(0.0, box_color_alpha)]]
			#print('boxie')
			for mode, box_alpha in settings:
				bgl.glEnable(bgl.GL_BLEND)
				bgl.glBegin(mode)
				bgl.glColor4f(box_color_r, box_color_g, box_color_b, box_color_alpha)
				for v1, v2 in positions:
					bgl.glVertex2f(v1, v2)
				bgl.glEnd()

			#TEXT HERE
			#calculate overall time

			timer_color_r, timer_color_g, timer_color_b, timer_color_alpha = .9,.9,.9,.5
			pos_x = 20
			pos_y = context.region.height-offset_y-bar_height*i+int(bar_height*.3)

			#draw time
			blf.size(0, int(bar_height*.45) , 72)
			blf.position(0, pos_x, pos_y, 0)
			bgl.glColor4f(timer_color_r, timer_color_g, timer_color_b, timer_color_alpha)
			blf.draw(0, "Slicing %s : %s %%" % (tcom.obname,tcom.outtext))
			i+=1
def draw_callback_px(self, context):
	draw_callback_px_box(self, context)

def addLine(text,line):
	text+=line+'\n'

def tweakCuraPreferences(enginepath,printer):
	filepath=enginepath+'\\Cura\preferences.ini'

	for p in bpy.utils.script_paths():
		directory=p+'\\addons\\print_3d\\machine_profiles\\'
		flist=os.listdir(directory)
		n=printer+'.ini'

		if n in flist:
			presetfilepath=directory+n

	f=open(filepath,'r')
	text=f.read()
	f.close()
	machineblocks=[]
	machinesnum=0
	found=0
	while found>-1:
		found=text.find('[machine_',found+1)
		if found>-1:
			machineblocks.append(found)
			machinesnum+=1
	#print(machinesnum)

	idx=text.find(printer)
	printerindex=0

	if idx==-1:
		#print('Selected printer not in Cura settings, adding it')
		#print(presetfilepath)
		printerindex=machinesnum
		pf=open(presetfilepath,'r')
		printerpreset = pf.read()
		#print(printerpreset)
		pf.close()
		text+=('\n\n[machine_%i]\n' % (machinesnum))
		text+=printerpreset
		#print(text)
	else:
		for i,m in enumerate(machineblocks):
			if m<idx<m+40:
				printerindex=i
				break;
	#set active machine to the printerindex
	lines=text.split('\n')
	#print(lines)
	for i,l in enumerate(lines):
		prop=l.split(' = ')
		tweakprops={'active_machine':printerindex}
		if tweakprops.get(prop[0])!=None:
			lines[i]='%s = %s' %( prop[0],str(tweakprops[prop[0]]))
	text=''
	for l in lines:
		addLine(text,l)

	f=open(filepath,'w')
	f.write(text)
	f.close()
	return printerindex

class Print3d(bpy.types.Operator):
	"""send object to 3d printer"""
	bl_idname = "object.print3d"
	bl_label = "Print object in 3d"
	bl_options = {'REGISTER', 'UNDO'}
	#processes=[]


	@classmethod
	def poll(cls, context):
		return context.active_object is not None

	@staticmethod
	def handle_add(self, context):
		if not(hasattr(PrintSettings,'handle')) or PrintSettings.handle == None:
			PrintSettings.handle = bpy.types.SpaceView3D.draw_handler_add(draw_callback_px, (self, context), 'WINDOW', 'POST_PIXEL')
		#bpy.app.handlers.scene_update_pre.append(timer_update_print3d)
		#ScreencastKeysStatus._handle = bpy.types.SpaceView3D.draw_handler_add(draw_callback_px, (self, context), 'WINDOW', 'POST_PIXEL')
		#ScreencastKeysStatus._timer = context.window_manager.event_timer_add(0.075, context.window)

	@staticmethod
	def handle_remove(context):
		if ScreencastKeysStatus._handle is not None:
			#context.window_manager.event_timer_remove(ScreencastKeysStatus._timer)
			bpy.types.SpaceView3D.draw_handler_remove(PrintSettings._handle, 'WINDOW')
		PrintSettings._handle = None
		#PrintSettings._timer = None

	def execute(self, context):
		Print3d.handle_add(self,context)


		s=bpy.context.scene
		settings=s.print3d_settings
		ob=bpy.context.active_object


		"""
		#this was first try - using the slicer directly.
		if settings.slicer=='CURA':
			fpath=bpy.data.filepath+'_'+ob.name+'.stl'
			gcodepath=bpy.data.filepath+'_'+ob.name+'.gcode'
			enginepath=settings.filepath_engine

			#Export stl, with a scale correcting blenders and Cura size interpretation in stl:
			bpy.ops.export_mesh.stl(check_existing=False, filepath=fpath, filter_glob="*.stl", ascii=False, use_mesh_modifiers=True, axis_forward='Y', axis_up='Z', global_scale=1000)

			#this is Cura help line:
			#CuraEngine [-h] [-v] [-m 3x3matrix] [-s <settingkey>=<value>] -o <output.gcode> <model.stl>

			#we build the command line here:
			commands=[enginepath]

			#add the properties, here add whatever you want exported from cura props, so far it doesn't work. Going with .ini files will be probably better in future:
			unit=1000000#conversion between blender mm unit(0.001 of basic unit) and slicer unit (0.001 mm)




			for name in settings.propnames:
				#print(s)
				commands.append('-s')
				commands.append(name+'='+str(eval('settings.'+name)))
				#commands.extend([key,str(propsdict[key])])

			commands.extend(['-o', gcodepath,fpath])

			print(commands)
			#run cura in background:
			proc = subprocess.Popen(commands,bufsize=1, stdout=subprocess.PIPE,stdin=subprocess.PIPE)

			s=''
			for command in commands:
				s+=(command)+' '
			print(s)
			print('gcode file exported:')
			print(gcodepath)
		"""
		#second try - use cura command line options, with .ini files.
		if settings.slicer=='CURA':

			opath=bpy.data.filepath[:-6]
			fpath=opath+'_'+ob.name+'.stl'
			gcodepath=opath+'_'+ob.name+'.gcode'
			enginepath=settings.dirpath_engine
			inipath=settings.preset
			tweakCuraPreferences(enginepath,settings.printer)
			#return {'FINISHED'}
			#Export stl, with a scale correcting blenders and Cura size interpretation in stl:
			bpy.ops.export_mesh.stl(check_existing=False, filepath=fpath, filter_glob="*.stl", ascii=False, use_mesh_modifiers=True, axis_forward='Y', axis_up='Z', global_scale=1000)

			#this is Cura help line:
			#CuraEngine [-h] [-v] [-m 3x3matrix] [-s <settingkey>=<value>] -o <output.gcode> <model.stl>

			#we build the command line here:
			#commands=[enginepath+'python\python.exe,']#,'-m', 'Cura.cura', '%*']
			os.chdir(settings.dirpath_engine)
			#print('\n\n\n')

			#print(os.listdir())
			commands=['python\\python.exe','-m', 'Cura.cura','-i',inipath, '-s', fpath]
			#commands=[enginepath+'cura.bat', '-s', fpath]

			#commands.extend()#'-o', gcodepath,

			#print(commands)
			#print('\n\n\n')

			s=''
			for command in commands:
				s+=(command)+' '
			#print(s)


			#run cura in background:
			#proc = subprocess.call(commands,bufsize=1, stdout=subprocess.PIPE,stdin=subprocess.PIPE)
			#print(proc)
			proc= subprocess.Popen(commands,bufsize=1, stdout=subprocess.PIPE,stdin=subprocess.PIPE)#,env={"PATH": enginepath})
			#print(proc)
			tcom=threadComPrint3d(ob,proc)
			readthread=threading.Thread(target=threadread_print3d, args = ([tcom]), daemon=True)
			readthread.start()
			#self.__class__.print3d_processes=[]
			if not hasattr(bpy.ops.object.print3d.__class__,'print3d_processes'):
				bpy.ops.object.print3d.__class__.print3d_processes=[]
			bpy.ops.object.print3d.__class__.print3d_processes.append([readthread,tcom])

			#print('gcode file exported:')
			#print(gcodepath)

		return {'FINISHED'}

class PRINT3D_SETTINGS_Panel(bpy.types.Panel):
	"""CAM feedrate panel"""
	bl_label = "3d print settings"
	bl_space_type = 'PROPERTIES'
	bl_region_type = 'WINDOW'
	bl_context = "render"
	COMPAT_ENGINES = {'PRINT3D'}

	@classmethod
	def poll(cls, context):
		rd = context.scene.render
		return rd.engine in cls.COMPAT_ENGINES

	def draw(self, context):
		layout = self.layout
		scene=bpy.context.scene

		settings=scene.print3d_settings

		#layout.prop(settings,'slicer')
		layout.prop(settings,'printer')
		layout.prop(settings,'preset')

		#layout.prop(settings,'filepath_engine')
		layout.prop(settings,'dirpath_engine')
		layout.operator("object.print3d")

		layout.separator()
		#reporting code in the property window got moved to view_3d
		#texts = scene.print3d_text.split('\n')
		#for t in texts:
		#	layout.label(text=t)

		#layout.prop(settings,'interface')

		#if settings.interface=='DEVELOPER':
			#for prop in settings.propnames:
			#	layout.prop(settings,prop)

		#else:
			#layout.label('here will be settings for casual users after we tune them.')
			#layout.label('also, Cura binary should be found automagically,')
			#layout.label('so you really set up which printer you have.')

class PRINT3D_ENGINE(bpy.types.RenderEngine):
	bl_idname = 'PRINT3D'
	bl_label = "Print 3d"

def register():
	s=bpy.types.Scene
	s.print3d_text= bpy.props.StringProperty()
	bpy.utils.register_module(__name__)

	bpy.types.Scene.print3d_settings=PointerProperty(type=PrintSettings)

	# bpy.app.handlers.scene_update_pre.append(timer_update_print3d)


	#bpy.types.INFO_HT_header.append(header_info_print3d)

def unregister():
	bpy.utils.unregister_module(__name__)
	del bpy.types.Scene.print3d_settings

	# bpy.app.handlers.scene_update_pre.remove(timer_update_print3d)
	#bpy.types.INFO_HT_header.remove(header_info_print3d)

#if __name__ == "__main__":
#	register()
