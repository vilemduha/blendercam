async def drill(o):
    """Perform a drilling operation on the specified objects.

    This function iterates through the objects in the provided context,
    activating each object and applying transformations. It duplicates the
    objects and processes them based on their type (CURVE or MESH). For
    CURVE objects, it calculates the bounding box and center points of the
    splines and bezier points, and generates chunks based on the specified
    drill type. For MESH objects, it generates chunks from the vertices. The
    function also manages layers and chunk depths for the drilling
    operation.

    Args:
        o (object): An object containing properties and methods required
            for the drilling operation, including a list of
            objects to drill, drill type, and depth parameters.

    Returns:
        None: This function does not return a value but performs operations
            that modify the state of the Blender context.
    """

    log.info("Strategy: Drill")

    chunks = []

    for ob in o.objects:
        activate(ob)
        bpy.ops.object.duplicate_move(
            OBJECT_OT_duplicate={
                "linked": False,
                "mode": "TRANSLATION",
            },
            TRANSFORM_OT_translate={
                "value": (0, 0, 0),
                "constraint_axis": (False, False, False),
                "orient_type": "GLOBAL",
                "mirror": False,
                "use_proportional_edit": False,
                "proportional_edit_falloff": "SMOOTH",
                "proportional_size": 1,
                "snap": False,
                "snap_target": "CLOSEST",
                "snap_point": (0, 0, 0),
                "snap_align": False,
                "snap_normal": (0, 0, 0),
                "texture_space": False,
                "release_confirm": False,
            },
        )
        bpy.ops.object.parent_clear(type="CLEAR_KEEP_TRANSFORM")
        ob = bpy.context.active_object

        if ob.type == "CURVE":
            ob.data.dimensions = "3D"

        try:
            bpy.ops.object.transform_apply(
                location=True,
                rotation=False,
                scale=False,
            )
            bpy.ops.object.transform_apply(
                location=False,
                rotation=True,
                scale=False,
            )
            bpy.ops.object.transform_apply(
                location=False,
                rotation=False,
                scale=True,
            )
        except:
            pass

        object_location = ob.location

        if ob.type == "CURVE":
            for curve in ob.data.splines:
                max_x, min_x, max_y, min_y, max_z, min_z = (
                    -10000,
                    10000,
                    -10000,
                    10000,
                    -10000,
                    10000,
                )
                # If Curve Points has points use them, otherwise use Bezier Points
                points = curve.points if len(curve.points) > 0 else curve.bezier_points

                for point in points:
                    if o.drill_type == "ALL_POINTS":
                        chunks.append(
                            CamPathChunk(
                                [
                                    (
                                        point.co.x + object_location.x,
                                        point.co.y + object_location.y,
                                        point.co.z + object_location.z,
                                    )
                                ]
                            )
                        )
                    min_x = min(point.co.x, min_x)
                    max_x = max(point.co.x, max_x)
                    min_y = min(point.co.y, min_y)
                    max_y = max(point.co.y, max_y)
                    min_z = min(point.co.z, min_z)
                    max_z = max(point.co.z, max_z)

                center_x = (max_x + min_x) / 2
                center_y = (max_y + min_y) / 2
                center_z = (max_z + min_z) / 2
                center = (center_x, center_y)
                aspect = (max_x - min_x) / (max_y - min_y)

                aspect_check = 1.3 > aspect > 0.7
                mid_sym = o.drill_type == "MIDDLE_SYMETRIC"
                mid_all = o.drill_type == "MIDDLE_ALL"

                if (aspect_check and mid_sym) or mid_all:
                    chunks.append(
                        CamPathChunk(
                            [
                                (
                                    center[0] + object_location.x,
                                    center[1] + object_location.y,
                                    center_z + object_location.z,
                                )
                            ]
                        )
                    )

        elif ob.type == "MESH":
            for vertex in ob.data.vertices:
                chunks.append(
                    CamPathChunk(
                        [
                            (
                                vertex.co.x + object_location.x,
                                vertex.co.y + object_location.y,
                                vertex.co.z + object_location.z,
                            )
                        ]
                    )
                )
        # Delete temporary Object with applied transforms
        delete_object(ob)

    layers = get_layers(
        o,
        o.max_z,
        check_min_z(o),
    )

    chunk_layers = []
    for layer in layers:
        for chunk in chunks:
            # If using Object for minz then use Z from Points in Object
            if o.min_z_from == "OBJECT":
                z = chunk.get_point(0)[2]
            else:  # using operation minz
                z = o.min_z
            # only add a chunk layer if the chunk z point is in or lower than the layer
            if z <= layer[0]:
                if z <= layer[1]:
                    z = layer[1]
                # perform peck drill
                new_chunk = chunk.copy()
                new_chunk.set_z(z)
                chunk_layers.append(new_chunk)
                # retract tool to maxz (operation depth start in ui)
                new_chunk = chunk.copy()
                new_chunk.set_z(o.max_z)
                chunk_layers.append(new_chunk)

    chunk_layers = await sort_chunks(chunk_layers, o)
    chunks_to_mesh(chunk_layers, o)
