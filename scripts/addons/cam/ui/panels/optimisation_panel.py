"""Fabex 'optimisation.py'

'CAM Optimisation' properties and panel in Properties > Render
"""

import bpy

from bpy.types import Panel

from .parent_panel import CAMParentPanel

from ...utilities.version_utils import opencamlib_version


class CAM_OPTIMISATION_Panel(CAMParentPanel, Panel):
    """CAM Optimisation Panel"""

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "CNC"

    bl_label = "[ Optimisation ]"
    bl_idname = "FABEX_PT_CAM_OPTIMISATION"
    panel_interface_level = 2

    def draw(self, context):
        if self.level >= 2 and self.op is not None:
            layout = self.layout
            layout.use_property_split = True
            layout.use_property_decorate = False

            self.exact_possible = self.op.strategy not in [
                "MEDIAL_AXIS",
                "POCKET",
                "CUTOUT",
                "DRILL",
                "PENCIL",
                "CURVE",
            ]

            # Exact Mode
            if not self.op.geometry_source == "OBJECT" or self.op.geometry_source == "COLLECTION":
                self.exact_possible = False

            if not self.exact_possible or not self.op.optimisation.use_exact:
                col = layout.column(align=True)
                col.prop(self.op.optimisation, "pixsize", text="Detail Size")
                col.prop(self.op.optimisation, "imgres_limit", text="Max Res (MP)")

                sx = self.op.max.x - self.op.min.x
                sy = self.op.max.y - self.op.min.y
                resx = int(sx / self.op.optimisation.pixsize)
                resy = int(sy / self.op.optimisation.pixsize)

                if resx > 0 and resy > 0:
                    resolution = "Resolution: " + str(resx) + " x " + str(resy)
                    layout.label(text=resolution)

            if self.exact_possible:
                if self.op.optimisation.use_exact:
                    # Simulation Detail
                    col = layout.column(align=True)
                    col.prop(self.op.optimisation, "simulation_detail", text="Sim Detail")
                    col.prop(self.op.optimisation, "circle_detail", text="Offset Detail")

                layout.use_property_split = False
                header, panel = layout.panel("exact", default_closed=True)
                header.prop(self.op.optimisation, "use_exact", text="Exact Mode")
                if panel:
                    panel.enabled = self.op.optimisation.use_exact
                    col = panel.column(align=True)

                    # Use OpenCAMLib
                    ocl_version = opencamlib_version()

                    if ocl_version is None:
                        # col = layout.column(align=True)
                        col.label(text="OpenCAMLib is not Available ")
                        col.prop(self.op.optimisation, "exact_subdivide_edges")
                    else:
                        # col = layout.column(align=True)
                        col.prop(self.op.optimisation, "use_opencamlib")

                    # Simplify Gcode
                    if self.op.strategy not in ["DRILL"]:
                        col.prop(self.op, "remove_redundant_points")

                    if self.op.remove_redundant_points:
                        row = col.row()
                        row.use_property_split = True
                        row.prop(self.op, "simplify_tolerance")

                    # Use Modifiers
                    if self.op.geometry_source in ["OBJECT", "COLLECTION"]:
                        col.prop(self.op, "use_modifiers")

                    # Hide All Others
                    col.prop(self.op, "hide_all_others")

                    # Parent Path to Object
                    col.prop(self.op, "parent_path_to_object")

            # Optimize
            layout.use_property_split = False
            header, panel = layout.panel("reduce_points", default_closed=False)
            header.prop(self.op.optimisation, "optimize", text="Reduce Path Points")
            if panel:
                col = panel.column(align=True)
                col.use_property_split = True
                col.enabled = self.op.optimisation.optimize
                col.prop(self.op.optimisation, "optimize_threshold", text="Threshold (μm)")
