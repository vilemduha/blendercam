async def pencil(o):
    await prepare_area(o)
    get_ambient(o)
    pathSamples = get_offset_image_cavities(o, o.offset_image)
    pathSamples = limit_chunks(pathSamples, o)
    # sort before sampling
    pathSamples = await sort_chunks(pathSamples, o)

    chunks = []
    layers = strategy.get_layers(o, o.max_z, o.min.z)

    log.info(f"Sampling Object: {o.name}")
    chunks.extend(await sample_chunks(o, pathSamples, layers))
    log.info("Sampling Finished Successfully")

    chunks = chunks_coherency(chunks)
    log.info("Coherency Check")

    log.info("Sorting")
    chunks = await sort_chunks(chunks, o)

    if o.movement.ramp:
        for ch in chunks:
            ch.ramp_zig_zag(ch.zstart, None, o)

    if o.use_bridges:
        log.info(chunks)
        for bridge_chunk in chunks:
            use_bridges(bridge_chunk, o)

    strategy.chunks_to_mesh(chunks, o)
