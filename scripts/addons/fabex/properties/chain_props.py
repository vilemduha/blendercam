"""Fabex 'chain.py'

All properties of a CAM Chain (a series of Operations), and the Chain's Operation reference.
"""

from bpy.props import (
    BoolProperty,
    CollectionProperty,
    IntProperty,
    StringProperty,
)
from bpy.types import PropertyGroup

from ..utilities.operation_utils import chain_valid


# this type is defined just to hold reference to operations for chains
class CAM_OP_REFERENCE_Properties(PropertyGroup):
    name: StringProperty(
        name="Operation Name",
        default="Operation",
    )
    computing = False  # for UiList display


# chain is just a set of operations which get connected on export into 1 file.
class CAM_CHAIN_Properties(PropertyGroup):
    index: IntProperty(
        name="Index",
        description="Index in the hard-defined camChains",
        default=-1,
    )
    active_operation: IntProperty(
        name="Active Operation",
        description="Active operation in chain",
        default=-1,
    )
    name: StringProperty(
        name="Chain Name",
        default="Chain",
    )
    filename: StringProperty(
        name="File Name",
        default="Chain",
    )  # filename of
    valid: BoolProperty(
        name="Valid",
        description="True if whole Chain is OK for calculation",
        default=True,
    )
    invalid_reason: StringProperty(
        name="Chain Error",
        default="",
        update=chain_valid,
    )
    computing: BoolProperty(
        name="Computing Right Now",
        description="",
        default=False,
    )
    # this is to hold just operation names.
    operations: CollectionProperty(
        type=CAM_OP_REFERENCE_Properties,
    )
