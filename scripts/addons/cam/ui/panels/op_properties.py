"""CMC CAM 'op_properties.py'

'CAM Operation Setup' panel in Properties > Render
"""

import bpy
from bpy.types import Panel

from .buttons_panel import CAMButtonsPanel


class CAM_OPERATION_PROPERTIES_Panel(CAMButtonsPanel, Panel):
    """CAM Operation Properties Panel"""

    bl_label = "Operation Setup"
    bl_idname = "WORLD_PT_CAM_OPERATION"
    panel_interface_level = 0

    def draw_cutter_engagement(self, col):
        if self.op is not None:
            # layout = self.layout
            # Cutter Engagement
            # Warns if cutter engagement is greater than 50%
            if self.op.cutter_type in ["BALLCONE"]:
                engagement = round(100 * self.op.dist_between_paths / self.op.ball_radius, 1)
            else:
                engagement = round(100 * self.op.dist_between_paths / self.op.cutter_diameter, 1)

            if engagement > 50:
                col.alert = True
                col.label(text="Warning: High Cutter Engagement")

            col.label(text=f"Cutter Engagement: {engagement}%")

    def draw_enable_A_B_axis(self, col):
        # Enable A & B Axes
        if self.level >= 1:
            # layout = self.layout
            col.prop(self.op, "enable_A")
            if self.op.enable_A:
                col.prop(self.op, "rotation_A")
                col.prop(self.op, "A_along_x")
                if self.op.A_along_x:
                    col.label(text="A || X - B || Y")
                else:
                    col.label(text="A || Y - B || X")

            col.prop(self.op, "enable_B")
            if self.op.enable_B:
                col.prop(self.op, "rotation_B")

    def draw_overshoot(self, col):
        # layout = self.layout
        # Overshoot
        col.prop(self.op, "straight")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        col = layout.column(align=True)
        # Machine Axis
        if self.level >= 2:
            col.prop(self.op, "machine_axes")

        # Strategy
        if self.op.machine_axes == "4":
            col.prop(self.op, "strategy4axis")
            if self.op.strategy4axis == "INDEXED":
                col.prop(self.op, "strategy")
            col.prop(self.op, "rotary_axis_1")
        elif self.op.machine_axes == "5":
            col.prop(self.op, "strategy5axis")
            if self.op.strategy5axis == "INDEXED":
                col.prop(self.op, "strategy")
            col.prop(self.op, "rotary_axis_1")
            col.prop(self.op, "rotary_axis_2")
        else:
            col.prop(self.op, "strategy")

        layout.label(text=self.op.strategy.title(), icon="SETTINGS")

        # Cutout Options
        if self.op.strategy in ["CUTOUT"]:
            box = layout.box()
            col = box.column(align=True)
            # Cutout Type
            col.prop(self.op, "cut_type")
            if self.op.cut_type in ["OUTSIDE", "INSIDE"]:
                self.draw_overshoot(col=col)
            # Startpoint
            col.prop(self.op, "profile_start")
            # Lead In & Out
            col.prop(self.op, "lead_in")
            col.prop(self.op, "lead_out")

        if self.op.strategy in ["CUTOUT", "CURVE"]:
            if self.op.strategy == "CURVE":
                box = layout.box()
                col = box.column(align=True)
            self.draw_enable_A_B_axis(col=col)
            # Outlines
            col.prop(self.op, "outlines_count")
            if self.op.outlines_count > 1:
                col.prop(self.op, "dist_between_paths")
                self.draw_cutter_engagement(col=col)
                col.prop(self.op.movement, "insideout")
            # Merge
            col.prop(self.op, "dont_merge")

        # Waterline Options
        if self.op.strategy in ["WATERLINE"]:
            box = layout.box()
            col = box.column(align=True)
            col.label(text="Ocl Doesn't Support Fill Areas")
            if not self.op.optimisation.use_opencamlib:
                col.prop(self.op, "slice_detail")
                col.prop(self.op, "waterline_fill")
                if self.op.waterline_fill:
                    col.prop(self.op, "dist_between_paths")
                    col.prop(self.op, "waterline_project")
            col.label(text="Waterline Needs a Skin Margin")

        # Carve Options
        if self.op.strategy in ["CARVE"]:
            box = layout.box()
            col = box.column(align=True)
            col.prop(self.op, "carve_depth")
            col.prop(self.op, "dist_along_paths")

        # Medial Axis Options
        if self.op.strategy in ["MEDIAL_AXIS"]:
            box = layout.box()
            col = box.column(align=True)
            col.prop(self.op, "medial_axis_threshold")
            col.prop(self.op, "medial_axis_subdivision")
            col.prop(self.op, "add_pocket_for_medial")
            col.prop(self.op, "add_mesh_for_medial")

        # Drill Options
        if self.op.strategy in ["DRILL"]:
            box = layout.box()
            col = box.column(align=True)
            col.prop(self.op, "drill_type")
            self.draw_enable_A_B_axis(col=col)

        # Pocket Options
        if self.op.strategy in ["POCKET"]:
            box = layout.box()
            col = box.column(align=True)
            self.draw_overshoot(col=col)
            col.prop(self.op, "pocketType", text="Type")
            if self.op.pocketType == "PARALLEL":
                col.label(text="Warning:Parallel pocket Experimental", icon="ERROR")
                col.prop(self.op, "parallelPocketCrosshatch")
                col.prop(self.op, "parallelPocketContour")
                col.prop(self.op, "parallelPocketAngle")
            else:
                col.prop(self.op, "pocket_option")
                col.prop(self.op, "pocketToCurve")
            col.prop(self.op, "dist_between_paths")
            self.draw_cutter_engagement(col=col)
            self.draw_enable_A_B_axis(col=col)

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
            box = layout.box()
            col = box.column(align=True)
            col.prop(self.op, "dist_between_paths")
            self.draw_cutter_engagement(col=col)
            col.prop(self.op, "dist_along_paths")
            if self.op.strategy in ["PARALLEL", "CROSS"]:
                col.prop(self.op, "parallel_angle")
                self.draw_enable_A_B_axis(col=col)
            col.prop(self.op, "inverse")

        # Skin
        if self.op.strategy not in ["POCKET", "DRILL", "CURVE", "MEDIAL_AXIS"]:
            col.prop(self.op, "skin")

        # Bridges Options
        if self.level >= 1:
            if self.op.strategy not in ["POCKET", "DRILL", "CURVE", "MEDIAL_AXIS"]:
                header, panel = layout.panel_prop(self.op, "use_bridges")
                header.label(text="Bridges / Tabs")
                if panel:
                    col = panel.column(align=True)
                    col.prop(self.op, "bridges_width", text="Width")
                    col.prop(self.op, "bridges_height", text="Height")
                    col.prop_search(self.op, "bridges_collection_name", bpy.data, "collections")
                    col.prop(self.op, "use_bridge_modifiers")
                    col.operator("scene.cam_bridges_add", text="Autogenerate")

            # Array
            if self.op.machine_axes == "3":
                header, panel = layout.panel_prop(self.op, "array")
                header.label(text="Array")
                if panel:
                    col = panel.column(align=True)
                    col.prop(self.op, "array_x_count")
                    col.prop(self.op, "array_x_distance")
                    col.prop(self.op, "array_y_count")
                    col.prop(self.op, "array_y_distance")
