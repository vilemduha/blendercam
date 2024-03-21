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

import subprocess
import os
import threading
from cam import utils, pack, polygon_utils_cam, simple, gcodepath, bridges, simulation
from cam.async_op import AsyncOperatorMixin, AsyncCancelledException
import shapely
import mathutils
import math
import textwrap
import traceback

import cam
from cam.exception import *


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
                    o.computing = False
                    utils.reload_paths(o)
                    update_zbufferimage_tag = False
                    update_offsetimage_tag = False
                else:
                    readthread = threading.Thread(
                        target=threadread, args=([tcom]), daemon=True)
                    readthread.start()
                    p[0] = readthread
            o = s.cam_operations[tcom.opname]  # changes
            o.outtext = tcom.lasttext  # changes


class PathsBackground(bpy.types.Operator):
    """calculate CAM paths in background. File has to be saved before."""
    bl_idname = "object.calculate_cam_paths_background"
    bl_label = "Calculate CAM paths in background"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        s = bpy.context.scene
        o = s.cam_operations[s.cam_active_operation]
        self.operation = o
        o.computing = True

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
        readthread = threading.Thread(
            target=threadread, args=([tcom]), daemon=True)
        readthread.start()
        # self.__class__.cam_processes=[]
        if not hasattr(bpy.ops.object.calculate_cam_paths_background.__class__, 'cam_processes'):
            bpy.ops.object.calculate_cam_paths_background.__class__.cam_processes = []
        bpy.ops.object.calculate_cam_paths_background.__class__.cam_processes.append([
                                                                                     readthread, tcom])
        return {'FINISHED'}


class KillPathsBackground(bpy.types.Operator):
    """Remove CAM path processes in background."""
    bl_idname = "object.kill_calculate_cam_paths_background"
    bl_label = "Kill background computation of an operation"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        s = bpy.context.scene
        o = s.cam_operations[s.cam_active_operation]
        self.operation = o

        if hasattr(bpy.ops.object.calculate_cam_paths_background.__class__, 'cam_processes'):
            processes = bpy.ops.object.calculate_cam_paths_background.__class__.cam_processes
            for p in processes:
                tcom = p[1]
                if tcom.opname == o.name:
                    processes.remove(p)
                    tcom.proc.kill()
                    o.computing = False

        return {'FINISHED'}


async def _calc_path(operator, context):
    s = bpy.context.scene
    o = s.cam_operations[s.cam_active_operation]
    if o.geometry_source == 'OBJECT':
        ob = bpy.data.objects[o.object_name]
        ob.hide_set(False)
    if o.geometry_source == 'COLLECTION':
        obc = bpy.data.collections[o.collection_name]
        for ob in obc.objects:
            ob.hide_set(False)
    if o.strategy == "CARVE":
        curvob = bpy.data.objects[o.curve_object]
        curvob.hide_set(False)
    '''if o.strategy == 'WATERLINE':
        ob = bpy.data.objects[o.object_name]
        ob.select_set(True)
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)'''
    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')	    # force object mode
    bpy.ops.object.select_all(action='DESELECT')
    path = bpy.data.objects.get('cam_path_{}'.format(o.name))
    if path:
        path.select_set(state=True)
        bpy.ops.object.delete()

    if not o.valid:
        operator.report({'ERROR_INVALID_INPUT'},
                        "Operation can't be performed, see warnings for info")
        progress_async("Operation can't be performed, see warnings for info")
        return {'FINISHED', False}

    # check for free movement height < maxz and return with error
    if(o.movement.free_height < o.maxz):
        operator.report({'ERROR_INVALID_INPUT'},
                        "Free movement height is less than Operation depth start \n correct and try again.")
        progress_async("Operation can't be performed, see warnings for info")
        return {'FINISHED', False}

    if o.computing:
        return {'FINISHED', False}

    o.operator = operator

    if o.use_layers:
        o.movement.parallel_step_back = False
    try:
        await gcodepath.getPath(context, o)
        print("Got path okay")
    except CamException as e:
        traceback.print_tb(e.__traceback__)
        error_str = "\n".join(textwrap.wrap(str(e), width=80))
        operator.report({'ERROR'}, error_str)
        return {'FINISHED', False}
    except AsyncCancelledException as e:
        return {'CANCELLED', False}
    except Exception as e:
        print("FAIL", e)
        traceback.print_tb(e.__traceback__)
        operator.report({'ERROR'}, str(e))
        return {'FINISHED', False}
    coll = bpy.data.collections.get('RigidBodyWorld')
    if coll:
        bpy.data.collections.remove(coll)

    return {'FINISHED', True}


class CalculatePath(bpy.types.Operator, AsyncOperatorMixin):
    """calculate CAM paths"""
    bl_idname = "object.calculate_cam_path"
    bl_label = "Calculate CAM paths"
    bl_options = {'REGISTER', 'UNDO', 'BLOCKING'}

    @classmethod
    def poll(cls, context):
        s = context.scene
        o = s.cam_operations[s.cam_active_operation]
        if o is not None:
            if cam.isValid(o, context):
                return True
        return False

    async def execute_async(self, context):
        (retval, success) = await _calc_path(self, context)
        print(f"CALCULATED PATH (success={success},retval={retval}")
        return retval


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
        layout.prop_search(self, "operation",
                           bpy.context.scene, "cam_operations")


class CamPackObjects(bpy.types.Operator):
    """calculate all CAM paths"""
    bl_idname = "object.cam_pack_objects"
    bl_label = "Pack curves on sheet"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.ops.object.mode_set(mode='OBJECT')	    # force object mode
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


class PathsChain(bpy.types.Operator, AsyncOperatorMixin):
    """calculate a chain and export the gcode alltogether. """
    bl_idname = "object.calculate_cam_paths_chain"
    bl_label = "Calculate CAM paths in current chain and export chain gcode"
    bl_options = {'REGISTER', 'UNDO', 'BLOCKING'}

    @classmethod
    def poll(cls, context):
        s = context.scene
        chain = s.cam_chains[s.cam_active_chain]
        return cam.isChainValid(chain, context)[0]

    async def execute_async(self, context):
        s = context.scene
        bpy.ops.object.mode_set(mode='OBJECT')	    # force object mode
        chain = s.cam_chains[s.cam_active_chain]
        chainops = getChainOperations(chain)
        meshes = []
        try:
            for i in range(0, len(chainops)):
                s.cam_active_operation = s.cam_operations.find(
                    chainops[i].name)
                self.report({'INFO'}, f"Calculating path: {chainops[i].name}")
                result, success = await _calc_path(self, context)
                if not success and 'FINISHED' in result:
                    self.report(
                        {'ERROR'}, f"Couldn't calculate path: {chainops[i].name}")
        except Exception as e:
            print("FAIL", e)
            traceback.print_tb(e.__traceback__)
            operator.report({'ERROR'}, str(e))
            return {'FINISHED'}

        for o in chainops:
            meshes.append(bpy.data.objects["cam_path_{}".format(o.name)].data)
        gcodepath.exportGcodePath(chain.filename, meshes, chainops)
        return {'FINISHED'}


class PathExportChain(bpy.types.Operator):
    """calculate a chain and export the gcode alltogether. """
    bl_idname = "object.cam_export_paths_chain"
    bl_label = "Export CAM paths in current chain as gcode"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        s = context.scene
        chain = s.cam_chains[s.cam_active_chain]
        return cam.isChainValid(chain, context)[0]

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

        print("EXPORTING", operation.filename,
              bpy.data.objects["cam_path_{}".format(operation.name)].data, operation)

        gcodepath.exportGcodePath(operation.filename, [bpy.data.objects["cam_path_{}".format(operation.name)].data],
                                  [operation])
        return {'FINISHED'}


class CAMSimulate(bpy.types.Operator, AsyncOperatorMixin):
    """simulate CAM operation
    this is performed by: creating an image, painting Z depth of the brush substractively.
    Works only for some operations, can not be used for 4-5 axis."""
    bl_idname = "object.cam_simulate"
    bl_label = "CAM simulation"
    bl_options = {'REGISTER', 'UNDO', 'BLOCKING'}

    operation: StringProperty(
        name="Operation",
        description="Specify the operation to calculate",
        default='Operation',
    )

    async def execute_async(self, context):
        s = bpy.context.scene
        operation = s.cam_operations[s.cam_active_operation]

        operation_name = "cam_path_{}".format(operation.name)

        if operation_name in bpy.data.objects:
            try:
                await simulation.doSimulation(operation_name, [operation])
            except AsyncCancelledException as e:
                return {'CANCELLED'}
        else:
            self.report({'ERROR'}, 'no computed path to simulate')
            return {'FINISHED'}
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        layout.prop_search(self, "operation",
                           bpy.context.scene, "cam_operations")


class CAMSimulateChain(bpy.types.Operator, AsyncOperatorMixin):
    """simulate CAM chain, compared to single op simulation just writes into one image and thus enables
    to see how ops work together."""
    bl_idname = "object.cam_simulate_chain"
    bl_label = "CAM simulation"
    bl_options = {'REGISTER', 'UNDO', 'BLOCKING'}

    @classmethod
    def poll(cls, context):
        s = context.scene
        chain = s.cam_chains[s.cam_active_chain]
        return cam.isChainValid(chain, context)[0]

    operation: StringProperty(
        name="Operation",
        description="Specify the operation to calculate",
        default='Operation',
    )

    async def execute_async(self, context):
        s = bpy.context.scene
        chain = s.cam_chains[s.cam_active_chain]
        chainops = getChainOperations(chain)

        canSimulate = True
        for operation in chainops:
            if operation.name not in bpy.data.objects:
                canSimulate = True  # force true
            print("operation name " + str(operation.name))
        if canSimulate:
            try:
                await simulation.doSimulation(chain.name, chainops)
            except AsyncCancelledException as e:
                return {'CANCELLED'}
        else:
            print('no computed path to simulate')
            return {'FINISHED'}
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        layout.prop_search(self, "operation",
                           bpy.context.scene, "cam_operations")


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
        s = bpy.context.scene
        chain = s.cam_chains[s.cam_active_chain]
        chain.operations.remove(chain.active_operation)
        chain.active_operation -= 1
        if chain.active_operation < 0:
            chain.active_operation = 0
        return {'FINISHED'}


def fixUnits():
    """Sets up units for blender CAM"""
    s = bpy.context.scene

    s.unit_settings.system_rotation = 'DEGREES'

    s.unit_settings.scale_length = 1.0
    # Blender CAM doesn't respect this property and there were users reporting problems, not seeing this was changed.


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

    ob = bpy.data.objects[sname]
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    utils.silhoueteOffset(ob, -new_cutter_diameter/2, 1, 0.3)
    bpy.context.active_object.name = 'medial_pocket'

    if not mpocket_exists:     # create a pocket operation if it does not exist already
        s.cam_operations.add()
        o = s.cam_operations[-1]
        o.object_name = 'medial_pocket'
        s.cam_active_operation = len(s.cam_operations) - 1
        o.name = 'MedialPocket'
        o.filename = o.name
        o.strategy = 'POCKET'
        o.use_layers = False
        o.material.estimate_from_model = False
        o.material.size[2] = -maxdepth
        o.minz_from = 'MATERIAL'


class CamOperationAdd(bpy.types.Operator):
    """Add new CAM operation"""
    bl_idname = "scene.cam_operation_add"
    bl_label = "Add new CAM operation"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.scene is not None

    def execute(self, context):
        s = bpy.context.scene
        fixUnits()

        ob = bpy.context.active_object
        if ob is None:
            self.report({'ERROR_INVALID_INPUT'},
                        "Please add an object to base the operation on.")
            return {'CANCELLED'}

        minx, miny, minz, maxx, maxy, maxz = utils.getBoundsWorldspace([ob])
        s.cam_operations.add()
        o = s.cam_operations[-1]
        o.object_name = ob.name
        o.minz = minz

        s.cam_active_operation = len(s.cam_operations) - 1

        o.name = f"Op_{ob.name}_{s.cam_active_operation + 1}"
        o.filename = o.name

        if s.objects.get('CAM_machine') is None:
            utils.addMachineAreaObject()

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
        scene = bpy.context.scene

        fixUnits()

        scene = bpy.context.scene
        if len(scene.cam_operations) == 0:
            return {'CANCELLED'}
        copyop = scene.cam_operations[scene.cam_active_operation]
        scene.cam_operations.add()
        scene.cam_active_operation += 1
        l = len(scene.cam_operations) - 1
        scene.cam_operations.move(l, scene.cam_active_operation)
        o = scene.cam_operations[scene.cam_active_operation]

        for k in copyop.keys():
            o[k] = copyop[k]
        o.computing = False

        # ###get digits in the end

        isdigit = True
        numdigits = 0
        num = 0
        if o.name[-1].isdigit():
            numdigits = 1
            while isdigit:
                numdigits += 1
                isdigit = o.name[-numdigits].isdigit()
            numdigits -= 1
            o.name = o.name[:-numdigits] + \
                str(int(o.name[-numdigits:]) + 1).zfill(numdigits)
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
            if len(scene.cam_operations) == 0:
                return {'CANCELLED'}
            active_op = scene.cam_operations[scene.cam_active_operation]
            active_op_object = bpy.data.objects[active_op.name]
            scene.objects.active = active_op_object
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

    direction: EnumProperty(
        name='direction',
        items=(
            ('UP', 'Up', ''),
            ('DOWN', 'Down', '')
        ),
        description='direction',
        default='DOWN',
    )

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
        s = bpy.context.scene
        a = s.cam_active_operation
        o = s.cam_operations[a]
        gname = o.name + '_orientations'
        bpy.ops.object.empty_add(type='ARROWS')

        oriob = bpy.context.active_object
        oriob.empty_draw_size = 0.02  # 2 cm

        simple.addToGroup(oriob, gname)
        oriob.name = 'ori_' + o.name + '.' + \
            str(len(bpy.data.collections[gname].objects)).zfill(3)

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
        s = bpy.context.scene
        a = s.cam_active_operation
        o = s.cam_operations[a]
        bridges.addAutoBridges(o)
        return {'FINISHED'}
