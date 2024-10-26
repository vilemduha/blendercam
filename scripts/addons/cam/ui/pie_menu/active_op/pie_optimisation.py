"""Fabex 'pie_optimisation.py'

'Operation Optimisation' Pie Menu
"""

import bpy
from bpy.types import Menu


class VIEW3D_MT_PIE_Optimisation(Menu):
    # label is displayed at the center of the pie menu.
    bl_label = "∴    Operation Optimisation    ∴"

    def draw(self, context):
        scene = context.scene
        operation = scene.cam_operations[scene.cam_active_operation]
        material = operation.material

        layout = self.layout
        # layout.use_property_split = True
        layout.use_property_decorate = False

        pie = layout.menu_pie()

        # Left
        box = pie.box()
        column = box.column(align=True)
        if not operation.geometry_source == "OBJECT" or operation.geometry_source == "COLLECTION":
            return

        self.exact_possible = operation.strategy not in [
            "MEDIAL_AXIS",
            "POCKET",
            "CUTOUT",
            "DRILL",
            "PENCIL",
            "CURVE",
        ]

        if self.exact_possible:
            column.prop(operation.optimisation, "use_exact")

        if not self.exact_possible or not operation.optimisation.use_exact:
            column.prop(operation.optimisation, "pixsize")
            column.prop(operation.optimisation, "imgres_limit")

            sx = operation.max.x - operation.min.x
            sy = operation.max.y - operation.min.y
            resx = int(sx / operation.optimisation.pixsize)
            resy = int(sy / operation.optimisation.pixsize)

            if resx > 0 and resy > 0:
                resolution = "Resolution: " + str(resx) + " x " + str(resy)
                column.label(text=resolution)

        # if not operation.optimisation.use_exact:
        #     return
        #
        # ocl_version = opencamlib_version()
        #
        # if ocl_version is None:
        #     column.label(text="OpenCAMLib Is Not Available")
        #     column.prop(operation.optimisation, 'exact_subdivide_edges')
        # else:
        #     column.prop(operation.optimisation, 'use_opencamlib')

        column.prop(operation.optimisation, "simulation_detail")
        column.prop(operation.optimisation, "circle_detail")

        # Right
        box = pie.box()
        column = box.column(align=True)
        if operation.strategy not in ["DRILL"]:
            column.prop(operation, "remove_redundant_points")
        if operation.remove_redundant_points:
            column.prop(operation, "simplify_tol")
        if operation.geometry_source in ["OBJECT", "COLLECTION"]:
            column.prop(operation, "use_modifiers")
        column.prop(operation, "hide_all_others")
        column.prop(operation, "parent_path_to_object")

        # Bottom
        box = pie.box()
        column = box.column(align=True)
        column.prop(operation.optimisation, "optimize")
        if operation.optimisation.optimize:
            column.prop(operation.optimisation, "optimize_threshold")

        # Top
        column = pie.column()
        box = column.box()
        box.scale_y = 2
        box.scale_x = 2
        box.emboss = "NONE"
        box.operator("wm.call_menu_pie", text="", icon="BACK").name = "VIEW3D_MT_PIE_Operation"
