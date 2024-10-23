"""CNC CAM 'optimisation.py'

'CAM Optimisation' properties and panel in Properties > Render
"""

import bpy
from bpy.props import (
    BoolProperty,
    FloatProperty,
    IntProperty,
)
from bpy.types import (
    Panel,
    PropertyGroup,
)

from .buttons_panel import CAMButtonsPanel
from ...utils import (
    opencamlib_version,
    update_exact_mode,
    update_opencamlib,
    update_operation,
    update_zbuffer_image,
)
from ...constants import PRECISION


class CAM_OPTIMISATION_Properties(PropertyGroup):

    optimize: BoolProperty(
        name="Reduce Path Points",
        description="Reduce path points",
        default=True,
        update=update_operation,
    )

    optimize_threshold: FloatProperty(
        name="Reduction Threshold in μm",
        default=0.2,
        min=0.000000001,
        max=1000,
        precision=20,
        update=update_operation,
    )

    use_exact: BoolProperty(
        name="Use Exact Mode",
        description="Exact mode allows greater precision, but is slower " "with complex meshes",
        default=True,
        update=update_exact_mode,
    )

    imgres_limit: IntProperty(
        name="Maximum Resolution in Megapixels",
        default=16,
        min=1,
        max=512,
        description="Limits total memory usage and prevents crashes. "
        "Increase it if you know what are doing",
        update=update_zbuffer_image,
    )

    pixsize: FloatProperty(
        name="Sampling Raster Detail",
        default=0.0001,
        min=0.00001,
        max=0.1,
        precision=PRECISION,
        unit="LENGTH",
        update=update_zbuffer_image,
    )

    use_opencamlib: BoolProperty(
        name="Use OpenCAMLib",
        description="Use OpenCAMLib to sample paths or get waterline shape",
        default=False,
        update=update_opencamlib,
    )

    exact_subdivide_edges: BoolProperty(
        name="Auto Subdivide Long Edges",
        description="This can avoid some collision issues when " "importing CAD models",
        default=False,
        update=update_exact_mode,
    )

    circle_detail: IntProperty(
        name="Detail of Circles Used for Curve Offsets",
        default=64,
        min=12,
        max=512,
        update=update_operation,
    )

    simulation_detail: FloatProperty(
        name="Simulation Sampling Raster Detail",
        default=0.0002,
        min=0.00001,
        max=0.01,
        precision=PRECISION,
        unit="LENGTH",
        update=update_operation,
    )


class CAM_OPTIMISATION_Panel(CAMButtonsPanel, Panel):
    """CAM Optimisation Panel"""

    bl_label = "CAM Optimisation"
    bl_idname = "WORLD_PT_CAM_OPTIMISATION"
    panel_interface_level = 2

    def draw(self, context):
        layout = self.layout

        if self.level >= 2 and self.op is not None:
            # Optimize
            layout.prop(self.op.optimisation, "optimize")
            if self.op.optimisation.optimize:
                layout.prop(self.op.optimisation, "optimize_threshold")
            layout.separator()

            # Exact Mode
            if not self.op.geometry_source == "OBJECT" or self.op.geometry_source == "COLLECTION":
                return

            self.exact_possible = self.op.strategy not in [
                "MEDIAL_AXIS",
                "POCKET",
                "CUTOUT",
                "DRILL",
                "PENCIL",
                "CURVE",
            ]

            if self.exact_possible:
                layout.prop(self.op.optimisation, "use_exact")

            if not self.exact_possible or not self.op.optimisation.use_exact:
                layout.prop(self.op.optimisation, "pixsize")
                layout.prop(self.op.optimisation, "imgres_limit")

                sx = self.op.max.x - self.op.min.x
                sy = self.op.max.y - self.op.min.y
                resx = int(sx / self.op.optimisation.pixsize)
                resy = int(sy / self.op.optimisation.pixsize)

                if resx > 0 and resy > 0:
                    resolution = "Resolution: " + str(resx) + " x " + str(resy)
                    layout.label(text=resolution)

            # Use OpenCAMLib
            if not (self.exact_possible and self.op.optimisation.use_exact):
                return

            ocl_version = opencamlib_version()

            if ocl_version is None:
                layout.label(text="OpenCAMLib is not Available ")
                layout.prop(self.op.optimisation, "exact_subdivide_edges")
            else:
                layout.prop(self.op.optimisation, "use_opencamlib")
            layout.separator()

            # Simulation Detail
            layout.prop(self.op.optimisation, "simulation_detail")
            layout.prop(self.op.optimisation, "circle_detail")

            # Simplify Gcode
            if self.op.strategy not in ["DRILL"]:
                layout.prop(self.op, "remove_redundant_points")

            if self.op.remove_redundant_points:
                layout.prop(self.op, "simplify_tol")

            # Use Modifiers
            if self.op.geometry_source in ["OBJECT", "COLLECTION"]:
                layout.prop(self.op, "use_modifiers")

            # Hide All Others
            layout.prop(self.op, "hide_all_others")

            # Parent Path to Object
            layout.prop(self.op, "parent_path_to_object")
