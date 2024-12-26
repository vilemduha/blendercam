"""Fabex 'collision.py' © 2012 Vilem Novak

Functions for Bullet and Cutter collision checks.
"""

from math import (
    cos,
    pi,
    radians,
    sin,
    tan,
)
import time

import bpy
from mathutils import (
    Euler,
    Vector,
)

from .constants import (
    BULLET_SCALE,
    CUTTER_OFFSET,
)
from .utilities.simple_utils import (
    activate,
    delete_object,
    progress,
)


def get_cutter_bullet(o):
    """Create a cutter for Rigidbody simulation collisions.

    This function generates a 3D cutter object based on the specified cutter
    type and parameters. It supports various cutter types including 'END',
    'BALLNOSE', 'VCARVE', 'CYLCONE', 'BALLCONE', and 'CUSTOM'. The function
    also applies rigid body physics to the created cutter for realistic
    simulation in Blender.

    Args:
        o (object): An object containing properties such as cutter_type, cutter_diameter,
            cutter_tip_angle, ball_radius, and cutter_object_name.

    Returns:
        bpy.types.Object: The created cutter object with rigid body properties applied.
    """

    s = bpy.context.scene
    if s.objects.get("cutter") is not None:
        c = s.objects["cutter"]
        activate(c)

    type = o.cutter_type
    if type == "END":
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=32,
            radius=o.cutter_diameter / 2,
            depth=o.cutter_diameter,
            end_fill_type="NGON",
            align="WORLD",
            enter_editmode=False,
            location=CUTTER_OFFSET,
            rotation=(0, 0, 0),
        )
        cutter = bpy.context.active_object
        cutter.scale *= BULLET_SCALE
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bpy.ops.object.origin_set(type="GEOMETRY_ORIGIN", center="BOUNDS")
        bpy.ops.rigidbody.object_add(type="ACTIVE")
        cutter = bpy.context.active_object
        cutter.rigid_body.collision_shape = "CYLINDER"
    elif type == "BALLNOSE":
        # ballnose ending used mainly when projecting from sides.
        # the actual collision shape is capsule in this case.
        bpy.ops.mesh.primitive_ico_sphere_add(
            subdivisions=3,
            radius=o.cutter_diameter / 2,
            align="WORLD",
            enter_editmode=False,
            location=CUTTER_OFFSET,
            rotation=(0, 0, 0),
        )
        cutter = bpy.context.active_object
        cutter.scale *= BULLET_SCALE
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bpy.ops.object.origin_set(type="GEOMETRY_ORIGIN", center="BOUNDS")
        bpy.ops.rigidbody.object_add(type="ACTIVE")
        cutter = bpy.context.active_object
        # cutter.dimensions.z = 0.2 * BULLET_SCALE  # should be sufficient for now... 20 cm.
        cutter.rigid_body.collision_shape = "CAPSULE"
        # bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    elif type == "VCARVE":
        angle = o.cutter_tip_angle
        s = tan(pi * (90 - angle / 2) / 180) / 2  # angles in degrees
        cone_d = o.cutter_diameter * s
        bpy.ops.mesh.primitive_cone_add(
            vertices=32,
            radius1=o.cutter_diameter / 2,
            radius2=0,
            depth=cone_d,
            end_fill_type="NGON",
            align="WORLD",
            enter_editmode=False,
            location=CUTTER_OFFSET,
            rotation=(pi, 0, 0),
        )
        cutter = bpy.context.active_object
        cutter.scale *= BULLET_SCALE
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bpy.ops.object.origin_set(type="GEOMETRY_ORIGIN", center="BOUNDS")
        bpy.ops.rigidbody.object_add(type="ACTIVE")
        cutter = bpy.context.active_object
        cutter.rigid_body.collision_shape = "CONE"
    elif type == "CYLCONE":
        angle = o.cutter_tip_angle
        s = tan(pi * (90 - angle / 2) / 180) / 2  # angles in degrees
        cylcone_d = (o.cutter_diameter - o.cylcone_diameter) * s
        bpy.ops.mesh.primitive_cone_add(
            vertices=32,
            radius1=o.cutter_diameter / 2,
            radius2=o.cylcone_diameter / 2,
            depth=cylcone_d,
            end_fill_type="NGON",
            align="WORLD",
            enter_editmode=False,
            location=CUTTER_OFFSET,
            rotation=(pi, 0, 0),
        )
        cutter = bpy.context.active_object
        cutter.scale *= BULLET_SCALE
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bpy.ops.object.origin_set(type="GEOMETRY_ORIGIN", center="BOUNDS")
        bpy.ops.rigidbody.object_add(type="ACTIVE")
        cutter = bpy.context.active_object
        cutter.rigid_body.collision_shape = "CONVEX_HULL"
        cutter.location = CUTTER_OFFSET
    elif type == "BALLCONE":
        angle = radians(o.cutter_tip_angle) / 2
        cutter_R = o.cutter_diameter / 2
        Ball_R = o.ball_radius / cos(angle)
        conedepth = (cutter_R - o.ball_radius) / tan(angle)
        bpy.ops.curve.simple(
            align="WORLD",
            location=(0, 0, 0),
            rotation=(0, 0, 0),
            Simple_Type="Point",
            use_cyclic_u=False,
        )
        oy = Ball_R
        for i in range(1, 10):
            ang = -i * (pi / 2 - angle) / 9
            qx = sin(ang) * oy
            qy = oy - cos(ang) * oy
            bpy.ops.curve.vertex_add(location=(qx, qy, 0))
        conedepth += qy
        bpy.ops.curve.vertex_add(location=(-cutter_R, conedepth, 0))
        # bpy.ops.curve.vertex_add(location=(0 , conedepth , 0))
        bpy.ops.object.editmode_toggle()
        bpy.ops.object.convert(target="MESH")
        bpy.ops.transform.rotate(value=-pi / 2, orient_axis="X")
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        ob = bpy.context.active_object
        ob.name = "BallConeTool"
        ob_scr = ob.modifiers.new(type="SCREW", name="scr")
        ob_scr.angle = radians(-360)
        ob_scr.steps = 32
        ob_scr.merge_threshold = 0
        ob_scr.use_merge_vertices = True
        bpy.ops.object.modifier_apply(modifier="scr")
        bpy.data.objects["BallConeTool"].select_set(True)
        cutter = bpy.context.active_object
        cutter.scale *= BULLET_SCALE
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bpy.ops.object.origin_set(type="GEOMETRY_ORIGIN", center="BOUNDS")
        bpy.ops.rigidbody.object_add(type="ACTIVE")
        cutter.location = CUTTER_OFFSET
        cutter.rigid_body.collision_shape = "CONVEX_HULL"
        cutter.location = CUTTER_OFFSET
    elif type == "CUSTOM":
        cutob = bpy.data.objects[o.cutter_object_name]
        activate(cutob)
        bpy.ops.object.duplicate()
        bpy.ops.rigidbody.object_add(type="ACTIVE")
        cutter = bpy.context.active_object
        scale = o.cutter_diameter / cutob.dimensions.x
        cutter.scale *= BULLET_SCALE * scale
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bpy.ops.object.origin_set(type="GEOMETRY_ORIGIN", center="BOUNDS")

        # print(cutter.dimensions,scale)
        bpy.ops.rigidbody.object_add(type="ACTIVE")
        cutter.rigid_body.collision_shape = "CONVEX_HULL"
        cutter.location = CUTTER_OFFSET

    cutter.name = "cam_cutter"
    o.cutter_shape = cutter
    return cutter


def subdivide_long_edges(ob, threshold):
    """Subdivide edges of a mesh object that exceed a specified length.

    This function iteratively checks the edges of a given mesh object and
    subdivides those that are longer than a specified threshold. The process
    involves toggling the edit mode of the object, selecting the long edges,
    and applying a subdivision operation. The function continues to
    subdivide until no edges exceed the threshold.

    Args:
        ob (bpy.types.Object): The Blender object containing the mesh to be
            subdivided.
        threshold (float): The length threshold above which edges will be
            subdivided.
    """

    print("Subdividing Long Edges")
    m = ob.data
    scale = (ob.scale.x + ob.scale.y + ob.scale.z) / 3
    subdivides = []
    n = 1
    iter = 0
    while n > 0:
        n = 0
        for i, e in enumerate(m.edges):
            v1 = m.vertices[e.vertices[0]].co
            v2 = m.vertices[e.vertices[1]].co
            vec = v2 - v1
            l = vec.length
            if l * scale > threshold:
                n += 1
                subdivides.append(i)
        if n > 0:
            print(len(subdivides))
            bpy.ops.object.editmode_toggle()

            # bpy.ops.mesh.quads_convert_to_tris(quad_method='BEAUTY', ngon_method='BEAUTY')
            # bpy.ops.mesh.tris_convert_to_quads()

            bpy.ops.mesh.select_all(action="DESELECT")
            bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type="EDGE")
            bpy.ops.object.editmode_toggle()
            for i in subdivides:
                m.edges[i].select = True
            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.subdivide(smoothness=0)
            if iter == 0:
                bpy.ops.mesh.select_all(action="SELECT")
                bpy.ops.mesh.quads_convert_to_tris(
                    quad_method="SHORTEST_DIAGONAL", ngon_method="BEAUTY"
                )
            bpy.ops.mesh.select_all(action="DESELECT")
            bpy.ops.object.editmode_toggle()
            ob.update_from_editmode()
        iter += 1


def prepare_bullet_collision(o):
    """Prepares all objects needed for sampling with Bullet collision.

    This function sets up the Bullet physics simulation by preparing the
    specified objects for collision detection. It begins by cleaning up any
    existing rigid bodies that are not part of the 'machine' object. Then,
    it duplicates the collision objects, converts them to mesh if they are
    curves or fonts, and applies necessary modifiers. The function also
    handles the subdivision of long edges and configures the rigid body
    properties for each object. Finally, it scales the 'machine' objects to
    the simulation scale and steps through the simulation frames to ensure
    that all objects are up to date.

    Args:
        o (Object): An object containing properties and settings for
    """
    progress("Preparing Collisions")

    print(o.name)
    active_collection = bpy.context.view_layer.active_layer_collection.collection
    t = time.time()
    s = bpy.context.scene
    s.gravity = (0, 0, 0)
    # cleanup rigidbodies wrongly placed somewhere in the scene
    for ob in bpy.context.scene.objects:
        if ob.rigid_body is not None and (
            bpy.data.objects.find("machine") > -1
            and ob.name not in bpy.data.objects["machine"].objects
        ):
            activate(ob)
            bpy.ops.rigidbody.object_remove()

    for collisionob in o.objects:
        bpy.context.view_layer.objects.active = collisionob
        collisionob.select_set(state=True)
        bpy.ops.object.duplicate(linked=False)
        collisionob = bpy.context.active_object
        if (
            collisionob.type == "CURVE" or collisionob.type == "FONT"
        ):  # support for curve objects collision
            if collisionob.type == "CURVE":
                odata = collisionob.data.dimensions
                collisionob.data.dimensions = "2D"
            bpy.ops.object.convert(target="MESH", keep_original=False)

        if o.use_modifiers:
            depsgraph = bpy.context.evaluated_depsgraph_get()
            mesh_owner = collisionob.evaluated_get(depsgraph)
            newmesh = mesh_owner.to_mesh()

            oldmesh = collisionob.data
            collisionob.modifiers.clear()
            collisionob.data = bpy.data.meshes.new_from_object(
                mesh_owner.evaluated_get(depsgraph),
                preserve_all_data_layers=True,
                depsgraph=depsgraph,
            )
            bpy.data.meshes.remove(oldmesh)

        # subdivide long edges here:
        if o.optimisation.exact_subdivide_edges:
            subdivide_long_edges(collisionob, o.cutter_diameter * 2)

        bpy.ops.rigidbody.object_add(type="ACTIVE")
        # using active instead of passive because of performance.TODO: check if this works also with 4axis...
        collisionob.rigid_body.collision_shape = "MESH"
        collisionob.rigid_body.kinematic = True
        # this fixed a serious bug and gave big speedup, rbs could move since they are now active...
        collisionob.rigid_body.collision_margin = o.skin * BULLET_SCALE
        bpy.ops.transform.resize(
            value=(BULLET_SCALE, BULLET_SCALE, BULLET_SCALE),
            constraint_axis=(False, False, False),
            orient_type="GLOBAL",
            mirror=False,
            use_proportional_edit=False,
            proportional_edit_falloff="SMOOTH",
            proportional_size=1,
            texture_space=False,
            release_confirm=False,
        )
        collisionob.location = collisionob.location * BULLET_SCALE
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        bpy.context.view_layer.objects.active = collisionob
        if active_collection in collisionob.users_collection:
            active_collection.objects.unlink(collisionob)

    get_cutter_bullet(o)

    # machine objects scaling up to simulation scale
    if bpy.data.objects.find("machine") > -1:
        for ob in bpy.data.objects["machine"].objects:
            activate(ob)
            bpy.ops.transform.resize(
                value=(BULLET_SCALE, BULLET_SCALE, BULLET_SCALE),
                constraint_axis=(False, False, False),
                orient_type="GLOBAL",
                mirror=False,
                use_proportional_edit=False,
                proportional_edit_falloff="SMOOTH",
                proportional_size=1,
                texture_space=False,
                release_confirm=False,
            )
            ob.location = ob.location * BULLET_SCALE
    # stepping simulation so that objects are up to date
    bpy.context.scene.frame_set(0)
    bpy.context.scene.frame_set(1)
    bpy.context.scene.frame_set(2)
    progress(time.time() - t)


def cleanup_bullet_collision(o):
    """Clean up bullet collision objects in the scene.

    This function checks for the presence of a 'machine' object in the
    Blender scene and removes any rigid body objects that are not part of
    the 'machine'. If the 'machine' object is present, it scales the machine
    objects up to the simulation scale and adjusts their locations
    accordingly.

    Args:
        o: An object that may be used in the cleanup process (specific usage not
            detailed).

    Returns:
        None: This function does not return a value.
    """

    if bpy.data.objects.find("machine") > -1:
        machinepresent = True
    else:
        machinepresent = False
    for ob in bpy.context.scene.objects:
        if ob.rigid_body is not None and not (
            machinepresent and ob.name in bpy.data.objects["machine"].objects
        ):
            delete_object(ob)
    # machine objects scaling up to simulation scale
    if machinepresent:
        for ob in bpy.data.objects["machine"].objects:
            activate(ob)
            bpy.ops.transform.resize(
                value=(1.0 / BULLET_SCALE, 1.0 / BULLET_SCALE, 1.0 / BULLET_SCALE),
                constraint_axis=(False, False, False),
                orient_type="GLOBAL",
                mirror=False,
                use_proportional_edit=False,
                proportional_edit_falloff="SMOOTH",
                proportional_size=1,
                texture_space=False,
                release_confirm=False,
            )
            ob.location = ob.location / BULLET_SCALE


def get_sample_bullet(cutter, x, y, radius, startz, endz):
    """Perform a collision test for a 3-axis milling cutter.

    This function simplifies the collision detection process compared to a
    full 3D test. It utilizes the Blender Python API to perform a convex
    sweep test on the cutter's position within a specified 3D space. The
    function checks for collisions between the cutter and other objects in
    the scene, adjusting for the cutter's radius to determine the effective
    position of the cutter tip.

    Args:
        cutter (object): The milling cutter object used for the collision test.
        x (float): The x-coordinate of the cutter's position.
        y (float): The y-coordinate of the cutter's position.
        radius (float): The radius of the cutter, used to adjust the collision detection.
        startz (float): The starting z-coordinate for the collision test.
        endz (float): The ending z-coordinate for the collision test.

    Returns:
        float: The adjusted z-coordinate of the cutter tip if a collision is detected;
            otherwise, returns a value 10 units below the specified endz.
    """
    scene = bpy.context.scene
    pos = scene.rigidbody_world.convex_sweep_test(
        cutter,
        (x * BULLET_SCALE, y * BULLET_SCALE, startz * BULLET_SCALE),
        (x * BULLET_SCALE, y * BULLET_SCALE, endz * BULLET_SCALE),
    )

    # radius is subtracted because we are interested in cutter tip position, this gets collision object center

    if pos[3] == 1:
        return (pos[0][2] - radius) / BULLET_SCALE
    else:
        return endz - 10


def get_sample_bullet_n_axis(cutter, startpoint, endpoint, rotation, cutter_compensation):
    """Perform a fully 3D collision test for N-Axis milling.

    This function computes the collision detection between a cutter and a
    specified path in a 3D space. It takes into account the cutter's
    rotation and compensation to accurately determine if a collision occurs
    during the milling process. The function uses Bullet physics for the
    collision detection and returns the adjusted position of the cutter if a
    collision is detected.

    Args:
        cutter (object): The cutter object used in the milling operation.
        startpoint (Vector): The starting point of the milling path.
        endpoint (Vector): The ending point of the milling path.
        rotation (Euler): The rotation applied to the cutter.
        cutter_compensation (float): The compensation factor for the cutter's position.

    Returns:
        Vector or None: The adjusted position of the cutter if a collision is
            detected;
            otherwise, returns None.
    """
    cutterVec = Vector((0, 0, 1)) * cutter_compensation
    # cutter compensation vector - cutter physics object has center in the middle, while cam needs the tip position.
    cutterVec.rotate(Euler(rotation))
    start = (startpoint * BULLET_SCALE + cutterVec).to_tuple()
    end = (endpoint * BULLET_SCALE + cutterVec).to_tuple()
    pos = bpy.context.scene.rigidbody_world.convex_sweep_test(cutter, start, end)

    if pos[3] == 1:
        pos = Vector(pos[0])
        # rescale and compensate from center to tip.
        res = pos / BULLET_SCALE - cutterVec / BULLET_SCALE

        return res
    else:
        return None
