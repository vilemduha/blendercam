"""CMC CAM 'op_properties.py'

'CAM Operation Setup' panel in Properties > Render
"""

import bpy
from bpy.types import Panel

from .buttons_panel import CAMButtonsPanel


class CAM_OPERATION_PROPERTIES_Panel(CAMButtonsPanel, Panel):
    """CAM Operation Properties Panel"""

    bl_label = "CAM Operation Setup"
    bl_idname = "WORLD_PT_CAM_OPERATION"

    def draw_cutter_engagement(self):
        layout = self.layout
        if self.op is not None:
            # Cutter Engagement
            # Warns if cutter engagement is greater than 50%
            if self.op.cutter_type in ["BALLCONE"]:
                engagement = round(100 * self.op.dist_between_paths / self.op.ball_radius, 1)
            else:
                engagement = round(100 * self.op.dist_between_paths / self.op.cutter_diameter, 1)

            if engagement > 50:
                layout.label(text="Warning: High Cutter Engagement")

            layout.label(text=f"Cutter Engagement: {engagement}%")

    def draw_enable_A_B_axis(self):
        layout = self.layout

        # Enable A & B Axes
        if self.level >= 1:
            layout.prop(self.op, "enable_A")
            if self.op.enable_A:
                layout.prop(self.op, "rotation_A")
                layout.prop(self.op, "A_along_x")
                if self.op.A_along_x:
                    layout.label(text="A || X - B || Y")
                else:
                    layout.label(text="A || Y - B || X")

            layout.prop(self.op, "enable_B")
            if self.op.enable_B:
                layout.prop(self.op, "rotation_B")

    def draw_overshoot(self):
        layout = self.layout

        # Overshoot
        layout.prop(self.op, "straight")

    def draw(self, context):
        layout = self.layout
        if self.op is not None:
            # Machine Axis
            if self.level >= 2:
                layout.prop(self.op, "machine_axes")

            # Strategy
            if self.op.machine_axes == "4":
                layout.prop(self.op, "strategy4axis")
                if self.op.strategy4axis == "INDEXED":
                    layout.prop(self.op, "strategy")
                layout.prop(self.op, "rotary_axis_1")
            elif self.op.machine_axes == "5":
                layout.prop(self.op, "strategy5axis")
                if self.op.strategy5axis == "INDEXED":
                    layout.prop(self.op, "strategy")
                layout.prop(self.op, "rotary_axis_1")
                layout.prop(self.op, "rotary_axis_2")
            else:
                layout.prop(self.op, "strategy")

            # Cutout Options
            if self.op.strategy in ["CUTOUT"]:
                # Cutout Type
                layout.prop(self.op, "cut_type")
                if self.op.cut_type in ["OUTSIDE", "INSIDE"]:
                    self.draw_overshoot()
                # Startpoint
                layout.prop(self.op, "profile_start")
                # Lead In & Out
                layout.prop(self.op, "lead_in")
                layout.prop(self.op, "lead_out")

            if self.op.strategy in ["CUTOUT", "CURVE"]:
                self.draw_enable_A_B_axis()
                # Outlines
                layout.prop(self.op, "outlines_count")
                if self.op.outlines_count > 1:
                    layout.prop(self.op, "dist_between_paths")
                    self.draw_cutter_engagement()
                    layout.prop(self.op.movement, "insideout")
                # Merge
                layout.prop(self.op, "dont_merge")

            # Waterline Options
            if self.op.strategy in ["WATERLINE"]:
                layout.label(text="Ocl Doesn't Support Fill Areas")
                if not self.op.optimisation.use_opencamlib:
                    layout.prop(self.op, "slice_detail")
                    layout.prop(self.op, "waterline_fill")
                    if self.op.waterline_fill:
                        layout.prop(self.op, "dist_between_paths")
                        layout.prop(self.op, "waterline_project")
                layout.label(text="Waterline Needs a Skin Margin")

            # Carve Options
            if self.op.strategy in ["CARVE"]:
                layout.prop(self.op, "carve_depth")
                layout.prop(self.op, "dist_along_paths")

            # Medial Axis Options
            if self.op.strategy in ["MEDIAL_AXIS"]:
                layout.prop(self.op, "medial_axis_threshold")
                layout.prop(self.op, "medial_axis_subdivision")
                layout.prop(self.op, "add_pocket_for_medial")
                layout.prop(self.op, "add_mesh_for_medial")

            # Drill Options
            if self.op.strategy in ["DRILL"]:
                layout.prop(self.op, "drill_type")
                self.draw_enable_A_B_axis()

            # Pocket Options
            if self.op.strategy in ["POCKET"]:
                self.draw_overshoot()
                layout.prop(self.op, "pocketType")
                if self.op.pocketType == "PARALLEL":
                    layout.label(text="Warning:Parallel pocket Experimental", icon="ERROR")
                    layout.prop(self.op, "parallelPocketCrosshatch")
                    layout.prop(self.op, "parallelPocketContour")
                    layout.prop(self.op, "parallelPocketAngle")
                else:
                    layout.prop(self.op, "pocket_option")
                    layout.prop(self.op, "pocketToCurve")
                layout.prop(self.op, "dist_between_paths")
                self.draw_cutter_engagement()
                self.draw_enable_A_B_axis()

            # Default Options
            if self.op.strategy not in [
                "CUTOUT",
                "CURVE",
                "WATERLINE",
                "CARVE",
                "MEDIAL_AXIS",
                "DRILL",
                "POCKET",
            ]:
                layout.prop(self.op, "dist_between_paths")
                self.draw_cutter_engagement()
                layout.prop(self.op, "dist_along_paths")
                if self.op.strategy in ["PARALLEL", "CROSS"]:
                    layout.prop(self.op, "parallel_angle")
                    self.draw_enable_A_B_axis()
                layout.prop(self.op, "inverse")

            # Bridges Options
            if self.level >= 1:
                if self.op.strategy not in ["POCKET", "DRILL", "CURVE", "MEDIAL_AXIS"]:
                    layout.prop(self.op, "use_bridges")
                    if self.op.use_bridges:
                        layout.prop(self.op, "bridges_width")
                        layout.prop(self.op, "bridges_height")
                        layout.prop_search(
                            self.op, "bridges_collection_name", bpy.data, "collections"
                        )
                        layout.prop(self.op, "use_bridge_modifiers")
                    layout.operator("scene.cam_bridges_add", text="Autogenerate Bridges / Tabs")

                # Skin
                self.layout.prop(self.op, "skin")

                # Array
                if self.op.machine_axes == "3":
                    layout.prop(self.op, "array")
                    if self.op.array:
                        layout.prop(self.op, "array_x_count")
                        layout.prop(self.op, "array_x_distance")
                        layout.prop(self.op, "array_y_count")
                        layout.prop(self.op, "array_y_distance")
