"""BlenderCAM 'pie_info.py'

'Info' Pie Menu
"""

import bpy
from bpy.types import Menu


class VIEW3D_MT_PIE_Info(Menu):
    bl_label = "∴    Info    ∴"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        preferences = context.preferences.addons['cam'].preferences
        no_operation = len(scene.cam_operations) < 1
        if not no_operation:
            operation = scene.cam_operations[scene.cam_active_operation]

        pie = layout.menu_pie()

        if no_operation:
            pie.separator()
            pie.separator()
            pie.separator()

        else:
            # Left
            box = pie.box()
            column = box.column(align=True)
    #        column.label(text=f'BlenderCAM v{".".join([str(x) for x in cam_version])}')
            if len(preferences.new_version_available) > 0:
                column.label(text=f"New Version Available:")
                column.label(
                    text=f"  {preferences.new_version_available}")
                column.operator("render.cam_update_now")

    #        ocl_version = opencamlib_version()
    #        if ocl_version is None:
    #            column.label(text="OpenCAMLib is not installed")
    #        else:
    #            column.label(text=f"OpenCAMLib v{ocl_version}")

            if int(operation.info.duration * 60) > 0:
                # Right
                box = pie.box()
                column = box.column(align=True)

                time_estimate = f"Operation Duration: {int(operation.info.duration*60)}s "
                if operation.info.duration > 60:
                    time_estimate += f" ({int(operation.info.duration / 60)}h"
                    time_estimate += f" {round(operation.info.duration % 60)}min)"
                elif operation.info.duration > 1:
                    time_estimate += f" ({round(operation.info.duration % 60)}min)"

                column.label(text=time_estimate)
            else:
                pass

    #        if not operation.info.chipload > 0:
    #            return

    #        chipload = f"Chipload: {strInUnits(operation.info.chipload, 4)}/tooth"
    #        column.label(text=chipload)

            if int(operation.info.duration * 60) > 0:
                row = column.row()
                row.label(text='Hourly Rate')
                row.prop(scene.cam_machine, 'hourly_rate', text='')

                if float(scene.cam_machine.hourly_rate) < 0.01:
                    return

                cost_per_second = context.scene.cam_machine.hourly_rate / 3600
                total_cost = operation.info.duration * 60 * cost_per_second
                op_cost = f"Operation Cost: ${total_cost:.2f} (${cost_per_second:.2f}/s)"
                column.label(text=op_cost)
            else:
                pie.separator()

            if len(operation.info.warnings) > 1:
                # Bottom
                box = pie.box()
                box.alert = True
                column = box.column(align=True)
                # column.alert = True
                column.label(text='Errors')
                for line in operation.info.warnings.rstrip("\n").split("\n"):
                    if len(line) > 0:
                        column.label(text=line, icon='ERROR')
            else:
                pie.separator()

        # Top
        column = pie.column()
        box = column.box()
        box.scale_y = 2
        box.scale_x = 2
        box.emboss = 'NONE'
        box.operator(
            "wm.call_menu_pie",
            text='',
            icon='HOME'
        ).name = 'VIEW3D_MT_PIE_CAM'
