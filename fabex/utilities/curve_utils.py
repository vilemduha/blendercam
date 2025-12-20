import bpy


from ..chunk_builder import (
    CamPathChunkBuilder,
)
from .logging_utils import log
from .shapely_utils import chunks_to_shapely
from .simple_utils import (
    activate,
    progress,
)

from ..exception import CamException


def curve_to_shapely(cob, use_modifiers=False):
    """Convert a curve object to Shapely polygons.

    This function takes a curve object and converts it into a list of
    Shapely polygons. It first breaks the curve into chunks and then
    transforms those chunks into Shapely-compatible polygon representations.
    The `use_modifiers` parameter allows for additional processing of the
    curve before conversion, depending on the specific requirements of the
    application.

    Args:
        cob: The curve object to be converted.
        use_modifiers (bool): A flag indicating whether to apply modifiers
            during the conversion process. Defaults to False.

    Returns:
        list: A list of Shapely polygons created from the curve object.
    """

    chunks = curve_to_chunks(cob, use_modifiers)
    polys = chunks_to_shapely(chunks)
    return polys


def mesh_from_curve(o, use_modifiers=False):
    activate(o)
    bpy.ops.object.duplicate()

    bpy.ops.object.parent_clear(type="CLEAR_KEEP_TRANSFORM")

    co = bpy.context.active_object

    # support for text objects is only and only here, just convert them to curves.
    if co.type == "FONT":
        bpy.ops.object.convert(target="CURVE", keep_original=False)
    elif co.type != "CURVE":  # curve must be a curve...
        bpy.ops.object.delete()  # delete temporary object
        raise CamException("Source Curve Object Must Be of Type Curve")

    co.data.dimensions = "3D"
    co.data.bevel_depth = 0
    co.data.extrude = 0
    co.data.resolution_u = 100

    # first, convert to mesh to avoid parenting issues with hooks, then apply locrotscale.
    bpy.ops.object.convert(target="MESH", keep_original=False)

    if use_modifiers:
        eval_object = co.evaluated_get(bpy.context.evaluated_depsgraph_get())
        newmesh = bpy.data.meshes.new_from_object(eval_object)
        oldmesh = co.data
        co.modifiers.clear()
        co.data = newmesh
        bpy.data.meshes.remove(oldmesh)

    try:
        bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    except:
        pass

    return bpy.context.active_object


def mesh_from_curve_to_chunk(object):
    object = mesh_from_curve(object) if object.type == "CURVE" else object
    mesh = object.data

    chunks = []
    chunk = CamPathChunkBuilder()
    ek = mesh.edge_keys
    d = {}

    for e in ek:
        d[e] = 1

    dk = d.keys()
    x = object.location.x
    y = object.location.y
    z = object.location.z
    lastvi = 0
    vtotal = len(mesh.vertices)
    perc = 0

    log.info("-")
    progress(f"Processing Curve - START")
    log.info(f"Vertices: {vtotal}")

    for vi in range(0, len(mesh.vertices) - 1):
        co = (mesh.vertices[vi].co + object.location).to_tuple()

        if not dk.isdisjoint([(vi, vi + 1)]) and d[(vi, vi + 1)] == 1:
            chunk.points.append(co)
        else:
            chunk.points.append(co)

            # this was looping chunks of length of only 2 points...
            if len(chunk.points) > 2 and (
                not (dk.isdisjoint([(vi, lastvi)])) or not (dk.isdisjoint([(lastvi, vi)]))
            ):
                chunk.closed = True
                chunk.points.append((mesh.vertices[lastvi].co + object.location).to_tuple())

            # add first point to end#originally the z was mesh.vertices[lastvi].co.z+z
            lastvi = vi + 1
            chunk = chunk.to_chunk()
            chunk.dedupe_points()

            if chunk.count() >= 1:
                # dump single point chunks
                chunks.append(chunk)

            chunk = CamPathChunkBuilder()

    progress("Processing Curve - FINISHED")

    vi = len(mesh.vertices) - 1
    chunk.points.append(
        (
            mesh.vertices[vi].co.x + x,
            mesh.vertices[vi].co.y + y,
            mesh.vertices[vi].co.z + z,
        )
    )
    if not (dk.isdisjoint([(vi, lastvi)])) or not (dk.isdisjoint([(lastvi, vi)])):
        chunk.closed = True
        chunk.points.append(
            (
                mesh.vertices[lastvi].co.x + x,
                mesh.vertices[lastvi].co.y + y,
                mesh.vertices[lastvi].co.z + z,
            )
        )
    chunk = chunk.to_chunk()
    chunk.dedupe_points()
    if chunk.count() >= 1:
        # dump single point chunks
        chunks.append(chunk)
    return chunks


def curve_to_chunks(o, use_modifiers=False):
    co = mesh_from_curve(o, use_modifiers)
    chunks = mesh_from_curve_to_chunk(co)

    co = bpy.context.active_object

    bpy.ops.object.select_all(action="DESELECT")
    bpy.data.objects[co.name].select_set(True)
    bpy.ops.object.delete()

    return chunks
