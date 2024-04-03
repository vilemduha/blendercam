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
        name="Have the Operation Presets been Updated",
        default=False,
    )

    experimental: BoolProperty(
        name="Show experimental features",
        default=False,
    )

    update_source: StringProperty(
        name="Source of updates for the addon",
        description="This can be either a github repo link in which case "
        "it will download the latest release on there, "
        "or an api link like "
        "https://api.github.com/repos/<author>/blendercam/commits"
        " to get from a github repository",
        default="https://github.com/pppalain/blendercam",
    )

    last_update_check: IntProperty(
        name="Last update time",
        default=0,
    )

    last_commit_hash: StringProperty(
        name="Hash of last commit from updater",
        default="",
    )

    just_updated: BoolProperty(
        name="Set to true on update or initial install",
        default=True,
    )

    new_version_available: StringProperty(
        name="Set to new version name if one is found",
        default="",
    )

    default_interface_level: EnumProperty(
        name="Interface level in new file",
        description="Choose visible options",
        items=[
            ("0", "Basic", "Only show essential options"),
            ("1", "Advanced", "Show advanced options"),
            ("2", "Complete", "Show all options"),
            ("3", "Experimental", "Show experimental options"),
        ],
        default="3",
    )

    default_machine_preset: StringProperty(
        name="Machine preset in new file",
        description="So that machine preset choice persists between files",
        default="",
    )

    def draw(self, context):
        layout = self.layout
        layout.label(
            text="Use experimental features when you want to help development of Blender CAM:"
        )
        layout.prop(self, "experimental")
        layout.prop(self, "update_source")
        layout.label(text="Choose a preset update source")

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
