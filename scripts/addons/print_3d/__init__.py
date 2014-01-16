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

PRECISION=7

class PrintSettings(bpy.types.PropertyGroup):
	'''stores all data for machines'''
	#name = bpy.props.StringProperty(name="Machine Name", default="Machine")
	slicer = EnumProperty(name='System',
		items=(('CURA','Cura','the default slicer'),('INTERNAL','Internal (not existing)','experimental code')),
		description='System to use',
		default='CURA')
	printer = EnumProperty(name='printer',
		items=(('PEACHY','Peachy','Peachy printer'),('OTHER','Other, but no other supported now.','no other supported now,just a stub')),
		description='Printer',
		default='PEACHY')
	filepath_engine = StringProperty(
                name="Cura binary location",
                description="Path to engine executable",
                subtype='FILE_PATH',
                )
	interface = EnumProperty(name='interface',
		items=(('STANDARD','Standard user',"Everybody, if you really don't want to mess with how things work"),('DEVELOPER','Developer','If you want to improve how things work and understand what you are doing')),
		description='Interface type',
		default='DEVELOPER')
	mm=0.001
	
	
	
	layerThickness=bpy.props.FloatProperty(name="layerThickness", description="layerThickness", default=0.1 * mm, min=0.00001, max=320000,precision=PRECISION)
	initialLayerThickness=bpy.props.FloatProperty(name="initialLayerThickness", description="initialLayerThickness", default=0.15 * mm, min=0.00001, max=320000,precision=PRECISION)
	filamentDiameter=bpy.props.FloatProperty(name="filamentDiameter", description="filamentDiameter", default=0.4 * mm, min=0.00001, max=320000,precision=PRECISION)
	filamentFlow=bpy.props.FloatProperty(name="filamentFlow", description="filamentFlow", default=0.4 * mm, min=0.00001, max=320000,precision=PRECISION)
	extrusionWidth=bpy.props.FloatProperty(name="extrusionWidth", description="extrusionWidth", default=0.4 * mm, min=0.00001, max=320000,precision=PRECISION)
	insetCount=bpy.props.IntProperty(name="insetCount", description="insetCount", default=1, min=0, max=1000)
	downSkinCount=bpy.props.FloatProperty(name="downSkinCount", description="downSkinCount", default=1, min=0.00001, max=320000,precision=PRECISION)
	upSkinCount=bpy.props.FloatProperty(name="upSkinCount", description="upSkinCount", default=1, min=0.00001, max=320000,precision=PRECISION)
	infillOverlap=bpy.props.FloatProperty(name="infillOverlap", description="infillOverlap", default=0.4 * mm, min=0.00001, max=320000,precision=PRECISION)
	initialSpeedupLayers=bpy.props.FloatProperty(name="initialSpeedupLayers", description="initialSpeedupLayers", default=0.4 * mm, min=0.00001, max=320000,precision=PRECISION)
	initialLayerSpeed=bpy.props.FloatProperty(name="initialLayerSpeed", description="initialLayerSpeed", default=0.4 * mm, min=0.00001, max=320000,precision=PRECISION)
	printSpeed=bpy.props.FloatProperty(name="printSpeed", description="printSpeed", default=0.4 * mm, min=0.00001, max=320000,precision=PRECISION)
	infillSpeed=bpy.props.FloatProperty(name="infillSpeed", description="infillSpeed", default=0.4 * mm, min=0.00001, max=320000,precision=PRECISION)
	moveSpeed=bpy.props.FloatProperty(name="moveSpeed", description="moveSpeed", default=0.4 * mm, min=0.00001, max=320000,precision=PRECISION)
	fanSpeedMin=bpy.props.FloatProperty(name="fanSpeedMin", description="fanSpeedMin", default=0.4 * mm, min=0.00001, max=320000,precision=PRECISION)
	fanSpeedMax=bpy.props.FloatProperty(name="fanSpeedMax", description="fanSpeedMax", default=0.4 * mm, min=0.00001, max=320000,precision=PRECISION)
	supportAngle=bpy.props.FloatProperty(name="supportAngle", description="supportAngle", default=0.4 , min=0.00000, max=3.141926,precision=PRECISION,subtype="ANGLE",)
	supportEverywhere=bpy.props.BoolProperty(name="supportEverywhere", description="supportEverywhere", default=0)
	supportLineDistance=bpy.props.FloatProperty(name="supportLineDistance", description="supportLineDistance", default=0.4 * mm, min=0.00001, max=320000,precision=PRECISION)
	supportXYDistance=bpy.props.FloatProperty(name="supportXYDistance", description="supportXYDistance", default=0.4 * mm, min=0.00001, max=320000,precision=PRECISION)
	supportZDistance=bpy.props.FloatProperty(name="supportZDistance", description="supportZDistance", default=0.4 * mm, min=0.00001, max=320000,precision=PRECISION)
	supportExtruder=bpy.props.FloatProperty(name="supportExtruder", description="supportExtruder", default=0.4 * mm, min=0.00001, max=320000,precision=PRECISION)
	retractionAmount=bpy.props.FloatProperty(name="retractionAmount", description="retractionAmount", default=0.4 * mm, min=0.00001, max=320000,precision=PRECISION)
	retractionSpeed=bpy.props.FloatProperty(name="retractionSpeed", description="retractionSpeed", default=0.4 * mm, min=0.00001, max=320000,precision=PRECISION)
	retractionMinimalDistance=bpy.props.FloatProperty(name="retractionMinimalDistance", description="retractionMinimalDistance", default=0.4 * mm, min=0.00001, max=320000,precision=PRECISION)
	retractionAmountExtruderSwitch=bpy.props.FloatProperty(name="retractionAmountExtruderSwitch", description="retractionAmountExtruderSwitch", default=0.4 * mm, min=0.00001, max=320000,precision=PRECISION)
	minimalExtrusionBeforeRetraction=bpy.props.FloatProperty(name="minimalExtrusionBeforeRetraction", description="minimalExtrusionBeforeRetraction", default=0.4 * mm, min=0.00001, max=320000,precision=PRECISION)
	enableCombing=bpy.props.BoolProperty(name="enableCombing", description="enableCombing", default=0)
	multiVolumeOverlap=bpy.props.FloatProperty(name="multiVolumeOverlap", description="multiVolumeOverlap", default=0.4 * mm, min=0.00001, max=320000,precision=PRECISION)
	objectSink=bpy.props.FloatProperty(name="objectSink", description="objectSink", default=0.4 * mm, min=0.00001, max=320000,precision=PRECISION)
	minimalLayerTime=bpy.props.FloatProperty(name="minimalLayerTime", description="minimalLayerTime", default=0.4 * mm, min=0.00001, max=320000,precision=PRECISION)
	minimalFeedrate=bpy.props.FloatProperty(name="minimalFeedrate", description="minimalFeedrate", default=0.4 * mm, min=0.00001, max=320000,precision=PRECISION)
	coolHeadLift=bpy.props.BoolProperty(name="coolHeadLift", description="coolHeadLift", default=0)
	
	startCode=   bpy.props.StringProperty(name='LimitstartCodecurve', description='startCode')
	endCode=   bpy.props.StringProperty(name='endCode', description='endCode')
	
	fixHorrible=bpy.props.BoolProperty(name="fixHorrible", description="fixHorrible", default=0)
	
	propnames = ["layerThickness","initialLayerThickness","filamentDiameter","filamentFlow","extrusionWidth","insetCount","downSkinCount","upSkinCount","infillOverlap","initialSpeedupLayers","initialLayerSpeed","printSpeed","infillSpeed","printSpeed","moveSpeed","fanSpeedMin","fanSpeedMax","supportAngle","supportEverywhere","supportLineDistance","supportXYDistance","supportZDistance","supportExtruder","retractionAmount","retractionSpeed","retractionMinimalDistance","retractionAmountExtruderSwitch","minimalExtrusionBeforeRetraction","enableCombing","multiVolumeOverlap","objectSink","minimalLayerTime","minimalFeedrate","coolHeadLift","startCode","endCode","fixHorrible"]
'''
	
			'retractionMinimalDistance': int(profile.getProfileSettingFloat('retraction_min_travel') * 1000),
			'retractionAmountExtruderSwitch': int(profile.getProfileSettingFloat('retraction_dual_amount') * 1000),
			'minimalExtrusionBeforeRetraction': int(profile.getProfileSettingFloat('retraction_minimal_extrusion') * 1000),
			'enableCombing': 1 if profile.getProfileSetting('retraction_combing') == 'True' else 0,
			'multiVolumeOverlap': int(profile.getProfileSettingFloat('overlap_dual') * 1000),
			'objectSink': int(profile.getProfileSettingFloat('object_sink') * 1000),
			'minimalLayerTime': int(profile.getProfileSettingFloat('cool_min_layer_time')),
			'minimalFeedrate': int(profile.getProfileSettingFloat('cool_min_feedrate')),
			'coolHeadLift': 1 if profile.getProfileSetting('cool_head_lift') == 'True' else 0,
			'startCode': profile.getAlterationFileContents('start.gcode', extruderCount),
			'endCode': profile.getAlterationFileContents('end.gcode', extruderCount),

			'extruderOffset[1].X': int(profile.getMachineSettingFloat('extruder_offset_x1') * 1000),
			'extruderOffset[1].Y': int(profile.getMachineSettingFloat('extruder_offset_y1') * 1000),
			'extruderOffset[2].X': int(profile.getMachineSettingFloat('extruder_offset_x2') * 1000),
			'extruderOffset[2].Y': int(profile.getMachineSettingFloat('extruder_offset_y2') * 1000),
			'extruderOffset[3].X': int(profile.getMachineSettingFloat('extruder_offset_x3') * 1000),
			'extruderOffset[3].Y': int(profile.getMachineSettingFloat('extruder_offset_y3') * 1000),
			'fixHorrible': 0,
			'''

class Print3d(bpy.types.Operator):
	'''send object to 3d printer'''
	bl_idname = "object.print3d"
	bl_label = "Print object in 3d"
	bl_options = {'REGISTER', 'UNDO'}
	processes=[]
	
	#@classmethod
	#def poll(cls, context):
	#	return context.active_object is not None
	
	def execute(self, context):
		
		
		
		s=bpy.context.scene
		settings=s.print3d_settings
		ob=bpy.context.active_object

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
		
		layout.prop(settings,'filepath_engine')
		layout.operator("object.print3d")
		
		layout.separator()
		
		layout.prop(settings,'interface')

		if settings.interface=='DEVELOPER':
			for prop in settings.propnames:
				layout.prop(settings,prop)
			
		else:
			layout.label('here will be settings for casual users after we tune them.')
			layout.label('also, Cura binary should be found automagically,')
			layout.label('so you really set up which printer you have.')
		
class PRINT3D_ENGINE(bpy.types.RenderEngine):
	bl_idname = 'PRINT3D'
	bl_label = "Print 3d"
		
def register():
	bpy.utils.register_module(__name__)
	
	bpy.types.Scene.print3d_settings=PointerProperty(type=PrintSettings)
	
def unregister():
	bpy.utils.unregister_module(__name__)
	del bpy.types.Scene.print3d_settings
	
#if __name__ == "__main__":
#	register()
