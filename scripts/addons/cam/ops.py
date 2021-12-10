# blender CAM ops.py (c) 2012 Vilem Novak
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ***** END GPL LICENCE BLOCK *****

# blender operators definitions are in this file. They mostly call the functions from utils.py


import bpy
from bpy.props import *
from bpy_extras.io_utils import ImportHelper

import subprocess, os, threading
from cam import utils, pack, polygon_utils_cam, simple,gcodepath,bridges, simulation
import shapely
import mathutils
import math
import cam




class threadCom:  # object passed to threads to read background process stdout info
    def __init__(self, o, proc):
        self.opname = o.name
        self.outtext = ''
        self.proc = proc
        self.lasttext = ''


def threadread(tcom):
    """reads stdout of background process, done this way to have it non-blocking"""
    inline = tcom.proc.stdout.readline()
    inline = str(inline)
    s = inline.find('progress{')
    if s > -1:
        e = inline.find('}')
        tcom.outtext = inline[s + 9:e]


class CAMPositionObject(bpy.types.Operator):
    """position object for CAM operation. Tests object bounds and places them so the object is aligned to be positive from x and y and negative from z."""
    bl_idname = "object.cam_position"
    bl_label = "position object for CAM operation"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        s = bpy.context.scene
        operation = s.cam_operations[s.cam_active_operation]
        if operation.object_name in bpy.data.objects:
            utils.positionObject(operation)
        else:
            print('no object assigned')
            return {'FINISHED'}
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        layout.prop_search(self, "operation", bpy.context.scene, "cam_operations")


@bpy.app.handlers.persistent
def timer_update(context):
    """monitoring of background processes"""
    text = ''
    s = bpy.context.scene
    if hasattr(bpy.ops.object.calculate_cam_paths_background.__class__, 'cam_processes'):
        processes = bpy.ops.object.calculate_cam_paths_background.__class__.cam_processes
        for p in processes:
            # proc=p[1].proc
            readthread = p[0]
            tcom = p[1]
            if not readthread.is_alive():
                readthread.join()
                # readthread.
                tcom.lasttext = tcom.outtext
                if tcom.outtext != '':
                    print(tcom.opname, tcom.outtext)
                    tcom.outtext = ''

                if 'finished' in tcom.lasttext:
                    processes.remove(p)

                    o = s.cam_operations[tcom.opname]
                    o.computing = False;
                    utils.reload_paths(o)
                    update_zbufferimage_tag = False
                    update_offsetimage_tag = False
                else:
                    readthread = threading.Thread(target=threadread, args=([tcom]), daemon=True)
                    readthread.start()
                    p[0] = readthread
            o = s.cam_operations[tcom.opname]  # changes
            o.outtext = tcom.lasttext  # changes
    # text=text+('# %s %s #' % (tcom.opname,tcom.lasttext))#CHANGES


# s.cam_text=text#changes

# commented out by NFZ: asking every property area to redraw
# causes my netbook to come to a crawl and cpu overheats
# need to find a better way of doing this
# doesn't effect normal path calculation when commented out
# maybe this should only be enabled when when background calc selected
# if bpy.context.screen!=None:
#	for area in bpy.context.screen.areas:
#		if area.type == 'PROPERTIES':
#			area.tag_redraw()

class PathsBackground(bpy.types.Operator):
    """calculate CAM paths in background. File has to be saved before."""
    bl_idname = "object.calculate_cam_paths_background"
    bl_label = "Calculate CAM paths in background"
    bl_options = {'REGISTER', 'UNDO'}

    # processes=[]

    # @classmethod
    # def poll(cls, context):
    #	return context.active_object is not None

    def execute(self, context):
        s = bpy.context.scene
        o = s.cam_operations[s.cam_active_operation]
        self.operation = o
        o.computing = True
        # if bpy.data.is_dirty:
        # bpy.ops.wm.save_mainfile()#this has to be replaced with passing argument or pickle stuff..
        # picklepath=getCachePath(o)+'init.pickle'

        bpath = bpy.app.binary_path
        fpath = bpy.data.filepath

        for p in bpy.utils.script_paths():
            scriptpath = p + os.sep + 'addons' + os.sep + 'cam' + os.sep + 'backgroundop.py'
            print(scriptpath)
            if os.path.isfile(scriptpath):
                break
        proc = subprocess.Popen([bpath, '-b', fpath, '-P', scriptpath, '--', '-o=' + str(s.cam_active_operation)],
                                bufsize=1, stdout=subprocess.PIPE, stdin=subprocess.PIPE)

        tcom = threadCom(o, proc)
        readthread = threading.Thread(target=threadread, args=([tcom]), daemon=True)
        readthread.start()
        # self.__class__.cam_processes=[]
        if not hasattr(bpy.ops.object.calculate_cam_paths_background.__class__, 'cam_processes'):
            bpy.ops.object.calculate_cam_paths_background.__class__.cam_processes = []
        bpy.ops.object.calculate_cam_paths_background.__class__.cam_processes.append([readthread, tcom])
        return {'FINISHED'}


class KillPathsBackground(bpy.types.Operator):
    """Remove CAM path processes in background."""
    bl_idname = "object.kill_calculate_cam_paths_background"
    bl_label = "Kill background computation of an operation"
    bl_options = {'REGISTER', 'UNDO'}

    # processes=[]

    # @classmethod
    # def poll(cls, context):
    #     return context.active_object is not None

    def execute(self, context):
        s = bpy.context.scene
        o = s.cam_operations[s.cam_active_operation]
        self.operation = o

        if hasattr(bpy.ops.object.calculate_cam_paths_background.__class__, 'cam_processes'):
            processes = bpy.ops.object.calculate_cam_paths_background.__class__.cam_processes
            for p in processes:
                # proc=p[1].proc
                # readthread=p[0]
                tcom = p[1]
                if tcom.opname == o.name:
                    processes.remove(p)
                    tcom.proc.kill()
                    o.computing = False

        return {'FINISHED'}


class CalculatePath(bpy.types.Operator):
    """calculate CAM paths"""
    bl_idname = "object.calculate_cam_path"
    bl_label = "Calculate CAM paths"
    bl_options = {'REGISTER', 'UNDO'}

    # this property was actually ignored, so removing it in 0.3
    # operation= StringProperty(name="Operation", description="Specify the operation to calculate",default='Operation')

    def execute(self, context):
        print("CALCULATE")
        # getIslands(context.object)
        s = bpy.context.scene
        o = s.cam_operations[s.cam_active_operation]
        if o.geometry_source=='OBJECT':
            ob = bpy.data.objects[o.object_name]
            ob.hide_set(False)
        if o.geometry_source=='COLLECTION':
            obc = bpy.data.collections[o.collection_name]
            for ob in obc.objects:
                ob.hide_set(False)
        if o.strategy=="CARVE":
            curvob=bpy.data.objects[o.curve_object]
            curvob.hide_set(False)
        print(bpy.context.mode)
        if bpy.context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode = 'OBJECT')	#force object mode
        bpy.ops.object.select_all(action='DESELECT')
        path = bpy.data.objects.get('cam_path_{}'.format(o.name))
        if path:
            path.select_set(state=True)
            bpy.ops.object.delete()

        if not o.valid:
            self.report({'ERROR_INVALID_INPUT'}, "Operation can't be performed, see warnings for info")
            print("Operation can't be performed, see warnings for info")
            return {'FINISHED'}

        if o.computing:
            return {'FINISHED'}

        o.operator = self

        if o.use_layers:
            o.parallel_step_back = False

        gcodepath.getPath(context, o)
        coll = bpy.data.collections.get('RigidBodyWorld')
        if coll:
            bpy.data.collections.remove(coll)

        return {'FINISHED'}


class PathsAll(bpy.types.Operator):
    """calculate all CAM paths"""
    bl_idname = "object.calculate_cam_paths_all"
    bl_label = "Calculate all CAM paths"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        i = 0
        for o in bpy.context.scene.cam_operations:
            bpy.context.scene.cam_active_operation = i
            print('\nCalculating path :' + o.name)
            print('\n')
            bpy.ops.object.calculate_cam_paths_background()
            i += 1

        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        layout.prop_search(self, "operation", bpy.context.scene, "cam_operations")


class CamPackObjects(bpy.types.Operator):
    """calculate all CAM paths"""
    bl_idname = "object.cam_pack_objects"
    bl_label = "Pack curves on sheet"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.ops.object.mode_set(mode = 'OBJECT')	#force object mode		
        obs = bpy.context.selected_objects
        pack.packCurves()
        # layout.
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout


class CamSliceObjects(bpy.types.Operator):
    """Slice a mesh object horizontally"""
    # warning, this is a separate and neglected feature, it's a mess - by now it just slices up the object.
    bl_idname = "object.cam_slice_objects"
    bl_label = "Slice object - usefull for lasercut puzzles e.t.c."
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        from cam import slice
        ob = bpy.context.active_object
        slice.sliceObject(ob)
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout


def getChainOperations(chain):
    """return chain operations, currently chain object can't store operations directly due to blender limitations"""
    chop = []
    for cho in chain.operations:
        for so in bpy.context.scene.cam_operations:
            if so.name == cho.name:
                chop.append(so)
    return chop


class PathsChain(bpy.types.Operator):
    """calculate a chain and export the gcode alltogether. """
    bl_idname = "object.calculate_cam_paths_chain"
    bl_label = "Calculate CAM paths in current chain and export chain gcode"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        s = bpy.context.scene
        bpy.ops.object.mode_set(mode = 'OBJECT')	#force object mode
        chain = s.cam_chains[s.cam_active_chain]
        chainops = getChainOperations(chain)
        meshes = []

        # if len(chainops)<4:
        for i in range(0, len(chainops)):
            s.cam_active_operation = s.cam_operations.find(chainops[i].name)
            bpy.ops.object.calculate_cam_path()

        for o in chainops:
            # bpy.ops.object.calculate_cam_paths_background()
            meshes.append(bpy.data.objects["cam_path_{}".format(o.name)].data)
        gcodepath.exportGcodePath(chain.filename, meshes, chainops)
        return {'FINISHED'}


class PathExportChain(bpy.types.Operator):
    """calculate a chain and export the gcode alltogether. """
    bl_idname = "object.cam_export_paths_chain"
    bl_label = "Export CAM paths in current chain as gcode"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        s = bpy.context.scene

        chain = s.cam_chains[s.cam_active_chain]
        chainops = getChainOperations(chain)
        meshes = []

        # if len(chainops)<4:

        for o in chainops:
            # bpy.ops.object.calculate_cam_paths_background()
            meshes.append(bpy.data.objects["cam_path_{}".format(o.name)].data)
        gcodepath.exportGcodePath(chain.filename, meshes, chainops)
        return {'FINISHED'}


class PathExport(bpy.types.Operator):
    """Export gcode. Can be used only when the path object is present"""
    bl_idname = "object.cam_export"
    bl_label = "Export operation gcode"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        s = bpy.context.scene
        operation = s.cam_operations[s.cam_active_operation]

        print("EXPORING", operation.filename, bpy.data.objects["cam_path_{}".format(operation.name)].data, operation)

        gcodepath.exportGcodePath(operation.filename, [bpy.data.objects["cam_path_{}".format(operation.name)].data], [operation])
        return {'FINISHED'}


class CAMSimulate(bpy.types.Operator):
    """simulate CAM operation
    this is performed by: creating an image, painting Z depth of the brush substractively. Works only for some operations, can not be used for 4-5 axis."""
    bl_idname = "object.cam_simulate"
    bl_label = "CAM simulation"
    bl_options = {'REGISTER', 'UNDO'}

    operation: StringProperty(name="Operation",
                               description="Specify the operation to calculate", default='Operation')

    def execute(self, context):
        s = bpy.context.scene
        operation = s.cam_operations[s.cam_active_operation]

        # if operation.geometry_source=='OBJECT' and operation.object_name in bpy.data.objects and #bpy.data.objects[operation.object_name].type=='CURVE':
        #	print('simulation of curve operations is not available')
        #	return {'FINISHED'}

        operation_name = "cam_path_{}".format(operation.name)

        if operation_name in bpy.data.objects:
            simulation.doSimulation(operation_name, [operation])
        else:
            print('no computed path to simulate')
            return {'FINISHED'}
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        layout.prop_search(self, "operation", bpy.context.scene, "cam_operations")


class CAMSimulateChain(bpy.types.Operator):
    """simulate CAM chain, compared to single op simulation just writes into one image and thus enables to see how ops work together."""
    bl_idname = "object.cam_simulate_chain"
    bl_label = "CAM simulation"
    bl_options = {'REGISTER', 'UNDO'}

    operation: StringProperty(name="Operation",
                               description="Specify the operation to calculate", default='Operation')

    def execute(self, context):
        s = bpy.context.scene
        chain = s.cam_chains[s.cam_active_chain]
        chainops = getChainOperations(chain)

        canSimulate = True
        for operation in chainops:
            if not operation.name in bpy.data.objects:
                canSimulate = True  #force true
            print("operation name " + str(operation.name))
        if canSimulate:
            simulation.doSimulation(chain.name, chainops)
        else:
            print('no computed path to simulate')
            return {'FINISHED'}
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        layout.prop_search(self, "operation", bpy.context.scene, "cam_operations")


class CamChainAdd(bpy.types.Operator):
    """Add new CAM chain"""
    bl_idname = "scene.cam_chain_add"
    bl_label = "Add new CAM chain"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.scene is not None

    def execute(self, context):
        # main(context)
        s = bpy.context.scene
        s.cam_chains.add()
        chain = s.cam_chains[-1]
        s.cam_active_chain = len(s.cam_chains) - 1
        chain.name = 'Chain_' + str(s.cam_active_chain + 1)
        chain.filename = chain.name
        chain.index = s.cam_active_chain

        return {'FINISHED'}


class CamChainRemove(bpy.types.Operator):
    """Remove  CAM chain"""
    bl_idname = "scene.cam_chain_remove"
    bl_label = "Remove CAM chain"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.scene is not None

    def execute(self, context):
        bpy.context.scene.cam_chains.remove(bpy.context.scene.cam_active_chain)
        if bpy.context.scene.cam_active_chain > 0:
            bpy.context.scene.cam_active_chain -= 1

        return {'FINISHED'}


class CamChainOperationAdd(bpy.types.Operator):
    """Add operation to chain"""
    bl_idname = "scene.cam_chain_operation_add"
    bl_label = "Add operation to chain"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.scene is not None

    def execute(self, context):
        s = bpy.context.scene
        chain = s.cam_chains[s.cam_active_chain]
        s = bpy.context.scene
        # s.chaindata[chain.index].remove(chain.active_operation+1,s.cam_operations[s.cam_active_operation])
        chain.operations.add()
        chain.active_operation += 1
        chain.operations[-1].name = s.cam_operations[s.cam_active_operation].name
        return {'FINISHED'}


class CamChainOperationUp(bpy.types.Operator):
    """Add operation to chain"""
    bl_idname = "scene.cam_chain_operation_up"
    bl_label = "Add operation to chain"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.scene is not None

    def execute(self, context):
        s = bpy.context.scene
        chain = s.cam_chains[s.cam_active_chain]
        a = chain.active_operation
        if a > 0:
            chain.operations.move(a, a - 1)
            chain.active_operation -= 1
        return {'FINISHED'}


class CamChainOperationDown(bpy.types.Operator):
    """Add operation to chain"""
    bl_idname = "scene.cam_chain_operation_down"
    bl_label = "Add operation to chain"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.scene is not None

    def execute(self, context):
        s = bpy.context.scene
        chain = s.cam_chains[s.cam_active_chain]
        a = chain.active_operation
        if a < len(chain.operations) - 1:
            chain.operations.move(a, a + 1)
            chain.active_operation += 1
        return {'FINISHED'}


class CamChainOperationRemove(bpy.types.Operator):
    """Remove operation from chain"""
    bl_idname = "scene.cam_chain_operation_remove"
    bl_label = "Remove operation from chain"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.scene is not None

    def execute(self, context):
        # main(context)
        s = bpy.context.scene
        chain = s.cam_chains[s.cam_active_chain]
        s = bpy.context.scene
        # s.chaindata[chain.index].append(s.cam_operations[s.cam_active_operation])
        chain.operations.remove(chain.active_operation)
        chain.active_operation -= 1
        if chain.active_operation < 0:
            chain.active_operation = 0
        return {'FINISHED'}


def fixUnits():
    """Sets up units for blender CAM"""
    s = bpy.context.scene
    # dhull: leave unit settings alone - may also need to comment out scale_length below
    # if s.unit_settings.system=='NONE':#metric is hereby default
    #	s.unit_settings.system='METRIC'

    s.unit_settings.system_rotation = 'DEGREES'

    s.unit_settings.scale_length = 1.0  # Blender CAM doesn't respect this property and there were users reporting problems, not seeing this was changed.


# add pocket op for medial axis and profile cut inside to clean unremoved material
def Add_Pocket(self, maxdepth, sname, new_cutter_diameter):
    bpy.ops.object.select_all(action='DESELECT')
    s = bpy.context.scene
    mpocket_exists = False
    for ob in s.objects:  # delete old medial pocket
        if ob.name.startswith("medial_poc"):
            ob.select_set(True)
            bpy.ops.object.delete()

    for op in s.cam_operations:  # verify medial pocket operation exists
        if op.name == "MedialPocket":
            mpocket_exists = True



    ob=bpy.data.objects[sname]
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    utils.silhoueteOffset(ob, -new_cutter_diameter/2,1,0.3)
    bpy.context.active_object.name = 'medial_pocket'

    if not mpocket_exists:     # create a pocket operation if it does not exist already
        s.cam_operations.add()
        o = s.cam_operations[-1]
        o.object_name = 'medial_pocket'
        s.cam_active_operation = len(s.cam_operations) - 1
        o.name = 'MedialPocket' # + str(s.cam_active_operation + 1)
        o.filename = o.name
        o.strategy = 'POCKET'
        o.use_layers = False
        o.material_from_model =False
        o.material_size[2] = -maxdepth
        o.minz_from_ob = False
        o.minz_from_material = True
        
       
class CamOperationAdd(bpy.types.Operator):
    """Add new CAM operation"""
    bl_idname = "scene.cam_operation_add"
    bl_label = "Add new CAM operation"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.scene is not None

    def execute(self, context):
        # main(context)
        s = bpy.context.scene

        fixUnits()

        if s.objects.get('CAM_machine') is None:
             utils.addMachineAreaObject()
        # if len(s.cam_material)==0:
        #     s.cam_material.add()

        s.cam_operations.add()
        o = s.cam_operations[-1]
        s.cam_active_operation = len(s.cam_operations) - 1
        o.name = 'Operation_' + str(s.cam_active_operation + 1)
        o.filename = o.name
        ob = bpy.context.active_object
        if ob is not None:
            o.object_name = ob.name
            minx, miny, minz, maxx, maxy, maxz = utils.getBoundsWorldspace([ob])
            o.minz = minz

        return {'FINISHED'}


class CamOperationCopy(bpy.types.Operator):
    """Copy CAM operation"""
    bl_idname = "scene.cam_operation_copy"
    bl_label = "Copy active CAM operation"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.scene is not None

    def execute(self, context):
        # main(context)
        s = bpy.context.scene

        fixUnits()

        s = bpy.context.scene
        s.cam_operations.add()
        copyop = s.cam_operations[s.cam_active_operation]
        s.cam_active_operation += 1
        l = len(s.cam_operations) - 1
        s.cam_operations.move(l, s.cam_active_operation)
        o = s.cam_operations[s.cam_active_operation]

        for k in copyop.keys():
            o[k] = copyop[k]
        o.computing = False

        ####get digits in the end

        isdigit = True
        numdigits = 0
        num = 0
        if o.name[-1].isdigit():
            numdigits = 1
            while isdigit:
                numdigits += 1
                isdigit = o.name[-numdigits].isdigit()
            numdigits -= 1
            o.name = o.name[:-numdigits] + str(int(o.name[-numdigits:]) + 1).zfill(numdigits)
            o.filename = o.name
        else:
            o.name = o.name + '_copy'
            o.filename = o.filename + '_copy'

        return {'FINISHED'}


class CamOperationRemove(bpy.types.Operator):
    """Remove CAM operation"""
    bl_idname = "scene.cam_operation_remove"
    bl_label = "Remove CAM operation"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.scene is not None

    def execute(self, context):
        scene = context.scene
        try:
            ao = scene.cam_operations[scene.cam_active_operation]
            ob = bpy.data.objects[ao.name]
            scene.objects.active = ob
            bpy.ops.object.delete(True)
        except:
            pass

        ao = scene.cam_operations[scene.cam_active_operation]
        print(cam.was_hidden_dict)
        if ao.name in cam.was_hidden_dict:
            del cam.was_hidden_dict[ao.name]

        scene.cam_operations.remove(scene.cam_active_operation)
        if scene.cam_active_operation > 0:
            scene.cam_active_operation -= 1

        return {'FINISHED'}


# move cam operation in the list up or down
class CamOperationMove(bpy.types.Operator):
    """Move CAM operation"""
    bl_idname = "scene.cam_operation_move"
    bl_label = "Move CAM operation in list"
    bl_options = {'REGISTER', 'UNDO'}

    direction: EnumProperty(name='direction',
                             items=(('UP', 'Up', ''), ('DOWN', 'Down', '')),
                             description='direction',
                             default='DOWN')

    @classmethod
    def poll(cls, context):
        return context.scene is not None

    def execute(self, context):
        # main(context)
        a = bpy.context.scene.cam_active_operation
        cops = bpy.context.scene.cam_operations
        if self.direction == 'UP':
            if a > 0:
                cops.move(a, a - 1)
                bpy.context.scene.cam_active_operation -= 1

        else:
            if a < len(cops) - 1:
                cops.move(a, a + 1)
                bpy.context.scene.cam_active_operation += 1

        return {'FINISHED'}


class CamOrientationAdd(bpy.types.Operator):
    """Add orientation to cam operation, for multiaxis operations"""
    bl_idname = "scene.cam_orientation_add"
    bl_label = "Add orientation"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.scene is not None

    def execute(self, context):
        # main(context)
        s = bpy.context.scene
        a = s.cam_active_operation
        o = s.cam_operations[a]
        gname = o.name + '_orientations'
        bpy.ops.object.empty_add(type='ARROWS')

        oriob = bpy.context.active_object
        oriob.empty_draw_size = 0.02  # 2 cm

        simple.addToGroup(oriob, gname)
        oriob.name = 'ori_' + o.name + '.' + str(len(bpy.data.collections[gname].objects)).zfill(3)

        return {'FINISHED'}


class CamBridgesAdd(bpy.types.Operator):
    """Add bridge objects to curve"""
    bl_idname = "scene.cam_bridges_add"
    bl_label = "Add bridges"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.scene is not None

    def execute(self, context):
        # main(context)
        s = bpy.context.scene
        a = s.cam_active_operation
        o = s.cam_operations[a]
        bridges.addAutoBridges(o)
        return {'FINISHED'}

