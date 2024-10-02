"""CNC CAM 'preferences.py'

Class to store all Addon preferences.
"""

from bpy.props import (
    BoolProperty,
    EnumProperty,
    IntProperty,
    StringProperty,
)
from bpy.types import (
    AddonPreferences,
)


class CamAddonPreferences(AddonPreferences):
    # this must match the addon name, use '__package__'
    # when defining this in a submodule of a python package.
    bl_idname = __package__

    op_preset_update: BoolProperty(
        name="Have the Operation Presets Been Updated",
        default=False,
    )

    experimental: BoolProperty(
        name="Show Experimental Features",
        default=False,
    )

    update_source: StringProperty(
        name="Source of Updates for the Addon",
        description="This can be either a github repo link in which case "
        "it will download the latest release on there, "
        "or an api link like "
        "https://api.github.com/repos/<author>/blendercam/commits"
        " to get from a github repository",
        default="https://github.com/pppalain/blendercam",
    )

    last_update_check: IntProperty(
        name="Last Update Time",
        default=0,
    )

    last_commit_hash: StringProperty(
        name="Hash of Last Commit from Updater",
        default="",
    )

    just_updated: BoolProperty(
        name="Set to True on Update or Initial Install",
        default=True,
    )

    new_version_available: StringProperty(
        name="Set to New Version Name if One Is Found",
        default="",
    )

    default_interface_level: EnumProperty(
        name="Interface Level in New File",
        description="Choose visible options",
        items=[
            ("0", "Basic", "Only show Essential Options"),
            ("1", "Advanced", "Show Advanced Options"),
            ("2", "Complete", "Show All Options"),
            ("3", "Experimental", "Show Experimental Options"),
        ],
        default="3",
    )

    default_machine_preset: StringProperty(
        name="Machine Preset in New File",
        description="So that machine preset choice persists between files",
        default="",
    )

    def draw(self, context):
        layout = self.layout
        layout.label(
            text="Use Experimental Features when you want to help development of CNC CAM:"
        )
        layout.prop(self, "experimental")
        layout.prop(self, "update_source")
        layout.label(text="Choose a Preset Update Source")

        UPDATE_SOURCES = [
            (
                "https://github.com/vilemduha/blendercam",
                "Stable",
                "Stable releases (github.com/vilemduja/blendercam)",
            ),
            (
                "https://github.com/pppalain/blendercam",
                "Unstable",
                "Unstable releases (github.com/pppalain/blendercam)",
            ),
            # comments for searching in github actions release script to
            # automatically set this repo if required
            # REPO ON NEXT LINE
            (
                "https://api.github.com/repos/pppalain/blendercam/commits",
                "Direct from git (may not work)",
                "Get from git commits directly",
            ),
            # REPO ON PREV LINE
            ("", "None", "Don't do auto update"),
        ]
        grid = layout.grid_flow(align=True)
        for url, short, long in UPDATE_SOURCES:
            op = grid.operator("render.cam_set_update_source", text=short)
            op.new_source = url
