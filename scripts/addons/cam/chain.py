from bpy.props import (
    BoolProperty,
    CollectionProperty,
    IntProperty,
    StringProperty,
)
from bpy.types import PropertyGroup


# this type is defined just to hold reference to operations for chains
class opReference(PropertyGroup):
    name: StringProperty(
        name="Operation name",
        default="Operation",
    )
    computing = False  # for UiList display


# chain is just a set of operations which get connected on export into 1 file.
class camChain(PropertyGroup):
    index: IntProperty(
        name="index",
        description="index in the hard-defined camChains",
        default=-1,
    )
    active_operation: IntProperty(
        name="active operation",
        description="active operation in chain",
        default=-1,
    )
    name: StringProperty(
        name="Chain Name",
        default="Chain",
    )
    filename: StringProperty(
        name="File name",
        default="Chain",
    )  # filename of
    valid: BoolProperty(
        name="Valid",
        description="True if whole chain is ok for calculation",
        default=True,
    )
    computing: BoolProperty(
        name="Computing right now",
        description="",
        default=False,
    )
    # this is to hold just operation names.
    operations: CollectionProperty(
        type=opReference,
    )
