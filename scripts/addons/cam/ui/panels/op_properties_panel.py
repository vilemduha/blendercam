"""CMC CAM 'op_properties.py'

'CAM Operation Setup' panel in Properties > Render
"""

import bpy
from bpy.types import Panel

from .parent_panel import CAMParentPanel


class CAM_OPERATION_PROPERTIES_Panel(CAMParentPanel, Panel):
    """CAM Operation Properties Panel"""

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "CNC"

    bl_label = "[ Operation Setup ]"
    bl_idname = "FABEX_PT_CAM_OPERATION"
    panel_interface_level = 0

    def draw_overshoot(self, col):
        # Overshoot
        row = col.row()
        row.use_property_split = False
        row.prop(self.op, "straight", text="Overshoot")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        col = layout.column(align=True)
        col.scale_y = 1.2

        # Machine Axis Count
        if self.level >= 2:
            col.prop(self.op, "machine_axes", text="Axis Count")

        # Strategy
        if self.op.machine_axes == "4":
            col.prop(self.op, "strategy_4_axis")
            if self.op.strategy_4_axis == "INDEXED":
                col.prop(self.op, "strategy")
            col.prop(self.op, "rotary_axis_1")
        elif self.op.machine_axes == "5":
            col.prop(self.op, "strategy_5_axis")
            if self.op.strategy_5_axis == "INDEXED":
                col.prop(self.op, "strategy")
            col.prop(self.op, "rotary_axis_1")
            col.prop(self.op, "rotary_axis_2")
        else:
            col.prop(self.op, "strategy")

        # Individual Strategy Settings
        box = layout.box()
        box.label(text=self.op.strategy.title(), icon="SETTINGS")

        # Cutout Options
        if self.op.strategy in ["CUTOUT"]:
            col = box.column(align=True)
            # Cutout Type
            col.prop(self.op, "cut_type")
            # Startpoint
            col.prop(self.op, "profile_start")
            # Skin
            col.prop(self.op, "skin")
            if self.op.cut_type in ["OUTSIDE", "INSIDE"]:
                self.draw_overshoot(col=col)
            # Lead In & Out
            box = col.box()
            sub = box.column(align=True)
            sub.label(text="Radius")
            sub.prop(self.op, "lead_in", text="Lead-in")
            sub.prop(self.op, "lead_out", text="Lead-out")

        if self.op.strategy in ["CUTOUT", "CURVE"]:
            if self.op.strategy == "CURVE":
                col = box.column(align=True)
            # Outlines Box
            box = col.box()
            subcol = box.column(align=True)
            subcol.label(text="Outlines")
            # Outlines
            subcol.prop(self.op, "outlines_count", text="Count")
            # Merge
            row = subcol.row()
            row.use_property_split = False
            row.prop(self.op, "dont_merge", text="Don't Merge")
            if self.op.outlines_count > 1:
                subcol.prop(self.op.movement, "insideout")
                box = subcol.box()
                sub = box.column(align=True)
                sub.label(text="Toolpath Distance")
                sub.prop(self.op, "distance_between_paths", text="Between")

        # Waterline Options
        if self.op.strategy in ["WATERLINE"]:
            col = box.column(align=True)
            if self.op.optimisation.use_opencamlib:
                box = col.box()
                box.alert = True
                box.label(text="Ocl Doesn't Support Fill Areas", icon="ERROR")
            else:
                col.prop(self.op, "slice_detail", text="Slice Detail")
                col.prop(self.op, "skin")
                if self.op.skin == 0:
                    box = col.box()
                    box.alert = True
                    box.label(text="Waterline Needs a Skin Margin", icon="ERROR")
                row = col.row()
                row.use_property_split = False
                row.prop(self.op, "waterline_project")
                row = col.row()
                row.use_property_split = False
                row.prop(self.op, "waterline_fill", text="Fill Between Slices")
                if self.op.waterline_fill:
                    box = col.box()
                    sub = box.column(align=True)
                    sub.label(text="Toolpath Distance")
                    sub.prop(self.op, "distance_between_paths", text="Between")

        # Carve Options
        if self.op.strategy in ["CARVE"]:
            col = box.column(align=True)
            col.prop(self.op, "carve_depth", text="Depth")
            col.prop(self.op, "skin")
            box = col.box()
            sub = box.column(align=True)
            sub.label(text="Toolpath Distance")
            sub.prop(self.op, "distance_along_paths", text="Along")

        # Medial Axis Options
        if self.op.strategy in ["MEDIAL_AXIS"]:
            col = box.column(align=True)
            col.prop(self.op, "medial_axis_threshold", text="Threshold")
            col.prop(self.op, "medial_axis_subdivision", text="Detail Size")
            row = col.row()
            row.use_property_split = False
            row.prop(self.op, "add_pocket_for_medial", text="Add Pocket")
            row = col.row()
            row.use_property_split = False
            row.prop(self.op, "add_mesh_for_medial", text="Add Medial Mesh")

        # Drill Options
        if self.op.strategy in ["DRILL"]:
            col = box.column(align=True)
            col.prop(self.op, "drill_type")
            # self.draw_enable_A_B_axis(col=col)

        # Pocket Options
        if self.op.strategy in ["POCKET"]:
            col = box.column(align=True)
            if self.op.pocket_type == "PARALLEL":
                warnbox = col.box()
                warnbox.alert = True
                warnbox.label(text="! Warning ! Experimental !", icon="ERROR")
            col.prop(self.op, "pocket_type", text="Type")
            if self.op.pocket_type == "PARALLEL":
                col.prop(self.op, "parallel_pocket_angle", text="Angle")
                col.prop(self.op, "skin")
                subcol = col.column(align=True)
                subcol.use_property_split = False
                subcol.prop(self.op, "parallel_pocket_crosshatch", text="Crosshatch")
                subcol.prop(self.op, "parallel_pocket_contour")

            else:
                col.prop(self.op, "pocket_option")
                col.prop(self.op, "skin")
                self.draw_overshoot(col=col)
                row = col.row()
                row.use_property_split = False
                row.prop(self.op, "pocket_to_curve")
            box = col.box()
            sub = box.column(align=True)
            sub.label(text="Toolpath Distance")
            sub.prop(self.op, "distance_between_paths", text="Between")

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
            # box = layout.box()
            col = box.column(align=True)
            row = col.row()
            row.use_property_split = False
            row.prop(self.op, "inverse")
            if self.op.strategy in ["PARALLEL", "CROSS"]:
                col.prop(self.op, "skin")
                col.prop(self.op, "parallel_angle")
            box = col.box()
            col = box.column(align=True)
            col.label(text="Toolpath Distance")
            col.prop(self.op, "distance_between_paths", text="Between")
            col.prop(self.op, "distance_along_paths", text="Along")

        # A & B, Array, Bridges Options
        if self.level >= 1:
            #  A & B Axes
            if self.op.strategy in [
                "CUTOUT",
                "CURVE",
                "DRILL",
                "PROFILE",
                "POCKET",
                "PARALLEL",
                "CROSS",
            ]:
                layout.use_property_split = False
                header, panel = layout.panel("ab_axes", default_closed=True)
                header.label(text="A & B Axes")
                if panel:
                    subheader, subpanel = panel.panel("a_axis", default_closed=True)
                    subheader.prop(self.op, "enable_a_axis", text="A Axis")
                    if subpanel:
                        subpanel.enabled = self.op.enable_a_axis
                        col = subpanel.column(align=True)
                        row = col.row()
                        row.use_property_split = True
                        row.prop(self.op, "rotation_a")
                        col.prop(self.op, "a_along_x")
                        if self.op.a_along_x:
                            col.label(text="Ⓐ || Ⓧ  -  Ⓑ || Ⓨ")
                        else:
                            col.label(text="Ⓐ || Ⓨ  -  Ⓑ || Ⓧ")
                    subheader, subpanel = panel.panel("b_axis", default_closed=True)
                    subheader.prop(self.op, "enable_b_axis", text="B Axis")
                    if subpanel:
                        subpanel.enabled = self.op.enable_b_axis
                        col = subpanel.column(align=True)
                        col.use_property_split = True
                        col.prop(self.op, "rotation_b")

            # Array
            if self.op.machine_axes == "3":
                layout.use_property_split = False
                header, panel = layout.panel("use_array", default_closed=True)
                header.prop(self.op, "array", text="Array")
                if panel:
                    panel.enabled = self.op.array
                    panel.use_property_split = True
                    col = panel.column(align=True)
                    col.prop(self.op, "array_x_count")
                    col.prop(self.op, "array_x_distance")
                    col.prop(self.op, "array_y_count")
                    col.prop(self.op, "array_y_distance")

            # Bridges
            if self.op.strategy not in ["POCKET", "DRILL", "CURVE", "MEDIAL_AXIS"]:
                layout.use_property_split = False
                header, panel = layout.panel("bridges", default_closed=True)
                header.prop(self.op, "use_bridges", text="Bridges (Tabs)")
                if panel:
                    panel.enabled = self.op.use_bridges
                    col = panel.column(align=True)
                    col.use_property_split = True
                    col.prop(self.op, "bridges_width", text="Width")
                    col.prop(self.op, "bridges_height", text="Height")
                    col.prop_search(
                        self.op,
                        "bridges_collection_name",
                        bpy.data,
                        "collections",
                        text="Collection",
                    )
                    col.prop(self.op, "use_bridge_modifiers", text="Use Modifiers")
                    col.operator("scene.cam_bridges_add", text="Autogenerate")
