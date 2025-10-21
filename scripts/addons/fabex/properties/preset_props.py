"""Fabex 'properties.preset_props.py' © 2012 Vilem Novak

Preset Properties
"""

from os import listdir, sep

import bpy

from ..utilities.logging_utils import log

##################
# Operation Presets #
##################
operation_preset_path = bpy.utils.preset_paths("cam_operations")[0]
operation_presets = sorted(listdir(operation_preset_path))
operation_presets = [
    operation.replace("_", " ").replace(".py", "") for operation in operation_presets
]


def operation_by_op_type(op_type):
    return [operation for operation in operation_presets if operation.startswith(op_type)]


finishing_operations = operation_by_op_type("Fin")
roughing_operations = operation_by_op_type("Rou")

operation_types = [
    finishing_operations,
    roughing_operations,
]

user_operations = [
    operation for operation in operation_presets if not operation.startswith("  pycache")
]

for operation_list in operation_types:
    for operation in operation_list:
        user_operations.remove(operation)


def get_operation_list(op_type, op_types):
    operation_list = []
    for operation in op_types:
        operation = operation.replace(op_type, "")
        operation_list.append((operation, operation, ""))
    return operation_list


finishing_presets = get_operation_list("Fin", finishing_operations)
roughing_presets = get_operation_list("Rou", roughing_operations)

user_operation_presets = get_operation_list("User", user_operations)


def update_operation_preset(self, context):
    operation_preset = context.scene.operation_preset
    filepath = f"{operation_preset_path}{sep}{operation_preset}.py"
    log.info(f"Operation Preset Filepath: {filepath}")
    bpy.ops.script.execute_preset(
        filepath=filepath,
        menu_idname="CAM_OPERATION_MT_presets",
    )


def update_finishing(self, context):
    context.scene.operation_preset = f"Fin{context.scene.finishing.replace(' ', '_')}"
    update_operation_preset(self, context)


def update_roughing(self, context):
    context.scene.operation_preset = f"Rou{context.scene.roughing.replace(' ', '_')}"
    update_operation_preset(self, context)


def update_user_operation(self, context):
    context.scene.operation_preset = f"{context.scene.user_operation.replace(' ', '_')}"
    update_operation_preset(self, context)


##################
# Cutter Presets #
##################
cutter_preset_path = bpy.utils.preset_paths("cam_cutters")[0]
cutter_presets = sorted(listdir(cutter_preset_path))
cutter_presets = [cutter.replace("_", " ").replace(".py", "") for cutter in cutter_presets]


def cutter_by_make(make):
    return [cutter for cutter in cutter_presets if cutter.startswith(make)]


idcwoodcraft_cutters = cutter_by_make("IDC")
cadence_cutters = cutter_by_make("Cadence")

brand_cutters = [
    idcwoodcraft_cutters,
    cadence_cutters,
]

user_cutters = [cutter for cutter in cutter_presets if not cutter.startswith("  pycache")]

for cutter_list in brand_cutters:
    for cutter in cutter_list:
        user_cutters.remove(cutter)


def get_cutter_list(make, models):
    cutter_list = []
    for cutter in models:
        cutter = cutter.replace(make, "")
        cutter_list.append((cutter, cutter, ""))
    return cutter_list


idcwoodcraft_presets = get_cutter_list("IDC", idcwoodcraft_cutters)
cadence_presets = get_cutter_list("Cadence", cadence_cutters)

user_cutter_presets = get_cutter_list("User", user_cutters)


def update_cutter_preset(self, context):
    active_op = context.scene.cam_operations[context.scene.cam_active_operation]
    cutter = active_op.cutter_object_name.replace(" ", "_")
    filepath = f"{cutter_preset_path}{sep}{cutter}.py"
    log.info(f"Cutter Preset Filepath: {filepath}")
    bpy.ops.script.execute_preset(
        filepath=filepath,
        menu_idname="CAM_CUTTER_MT_presets",
    )


def update_idcwoodcraft(self, context):
    active_op = context.scene.cam_operations[context.scene.cam_active_operation]
    active_op.cutter_object_name = f"IDC{context.scene.idcwoodcraft.replace(' ', '_')}"
    update_cutter_preset(self, context)


def update_cadence(self, context):
    active_op = context.scene.cam_operations[context.scene.cam_active_operation]
    active_op.cutter_object_name = f"Cadence{context.scene.cadence.replace(' ', '_')}"
    update_cutter_preset(self, context)


def update_user_cutter(self, context):
    active_op = context.scene.cam_operations[context.scene.cam_active_operation]
    active_op.cutter_object_name = f"{context.scene.user_cutter.replace(' ', '_')}"
    update_cutter_preset(self, context)


###################
# Machine Presets #
###################
machine_preset_path = bpy.utils.preset_paths("cam_machines")[0]
machine_presets = sorted(listdir(machine_preset_path))
machine_presets = [machine.replace("_", " ").replace(".py", "") for machine in machine_presets]


def machine_by_make(make):
    return [machine for machine in machine_presets if machine.startswith(make)]


avidcnc_machines = machine_by_make("AvidCNC")
carbide3d_machines = machine_by_make("Carbide3D")
cnc4all_machines = machine_by_make("CNC4ALL")
inventables_machines = machine_by_make("Inventables")
millright_machines = machine_by_make("MillRight")
onefinity_machines = machine_by_make("Onefinity")
ooznest_machines = machine_by_make("Ooznest")
sienci_machines = machine_by_make("Sienci")

brand_machines = [
    avidcnc_machines,
    carbide3d_machines,
    cnc4all_machines,
    inventables_machines,
    millright_machines,
    onefinity_machines,
    ooznest_machines,
    sienci_machines,
]

user_machines = [machine for machine in machine_presets if not machine.startswith("  pycache")]

for machine_list in brand_machines:
    for machine in machine_list:
        user_machines.remove(machine)


def get_machine_list(make, models):
    machine_list = []
    for machine in models:
        machine = machine.replace(make, "")
        machine_list.append((machine, machine, ""))
    return machine_list


avidcnc_presets = get_machine_list("AvidCNC", avidcnc_machines)
carbide3d_presets = get_machine_list("Carbide3D", carbide3d_machines)
cnc4all_presets = get_machine_list("CNC4ALL", cnc4all_machines)
inventables_presets = get_machine_list("Inventables", inventables_machines)
millright_presets = get_machine_list("MillRight", millright_machines)
onefinity_presets = get_machine_list("Onefinity", onefinity_machines)
ooznest_presets = get_machine_list("Ooznest", ooznest_machines)
sienci_presets = get_machine_list("Sienci", sienci_machines)

user_machine_presets = get_machine_list("User", user_machines)


def update_machine_preset(self, context):
    machine = context.scene.cam_machine.name
    bpy.ops.script.execute_preset(
        filepath=f"{machine_preset_path}{sep}{machine}.py",
        menu_idname="CAM_MACHINE_MT_presets",
    )


def update_avidcnc(self, context):
    context.scene.cam_machine.name = f"AvidCNC{context.scene.avidcnc.replace(' ', '_')}"
    update_machine_preset(self, context)


def update_carbide3d(self, context):
    context.scene.cam_machine.name = f"Carbide3D{context.scene.carbide3d.replace(' ', '_')}"
    update_machine_preset(self, context)


def update_cnc4all(self, context):
    context.scene.cam_machine.name = f"CNC4ALL{context.scene.cnc4all.replace(' ', '_')}"
    update_machine_preset(self, context)


def update_inventables(self, context):
    context.scene.cam_machine.name = f"Inventables{context.scene.inventables.replace(' ', '_')}"
    update_machine_preset(self, context)


def update_millright(self, context):
    context.scene.cam_machine.name = f"MillRight{context.scene.millright.replace(' ', '_')}"
    update_machine_preset(self, context)


def update_onefinity(self, context):
    context.scene.cam_machine.name = f"Onefinity{context.scene.onefinity.replace(' ', '_')}"
    update_machine_preset(self, context)


def update_ooznest(self, context):
    context.scene.cam_machine.name = f"Ooznest{context.scene.ooznest.replace(' ', '_')}"
    update_machine_preset(self, context)


def update_sienci(self, context):
    context.scene.cam_machine.name = f"Sienci{context.scene.sienci.replace(' ', '_')}"
    update_machine_preset(self, context)


def update_user_machine(self, context):
    context.scene.cam_machine.name = f"{context.scene.user_machine.replace(' ', '_')}"
    update_machine_preset(self, context)
