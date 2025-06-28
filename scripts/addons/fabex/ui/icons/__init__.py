import os
from pathlib import Path

import bpy
import bpy.utils.previews

preview_collections = {}


def register():
    icon_images = [
        "EndMillIcon",
        "BallnoseIcon",
        "VCarveIcon",
        "CylinderConeIcon",
        "LaserPlasmaIcon",
        "BullnoseIcon",
        "BallconeIcon",
        "FabexCNC_Logo",
    ]

    fabex_icons = bpy.utils.previews.new()
    icons_dir = Path(__file__).parent
    for image in icon_images:
        fabex_icons.load(image, os.path.join(icons_dir, f"{image}.png"), "IMAGE")
    preview_collections["FABEX"] = fabex_icons


def unregister():
    for fabex_icons in preview_collections.values():
        bpy.utils.previews.remove(fabex_icons)
    preview_collections.clear()
