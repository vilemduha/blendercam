cam.cam_chunk
=============

.. py:module:: cam.cam_chunk

.. autoapi-nested-parse::

   BlenderCAM 'chunk.py' © 2012 Vilem Novak

   Classes and Functions to build, store and optimize CAM path chunks.



Classes
-------

.. autoapisummary::

   cam.cam_chunk.camPathChunkBuilder
   cam.cam_chunk.camPathChunk


Functions
---------

.. autoapisummary::

   cam.cam_chunk.Rotate_pbyp
   cam.cam_chunk._internalXyDistanceTo
   cam.cam_chunk.chunksCoherency
   cam.cam_chunk.setChunksZ
   cam.cam_chunk._optimize_internal
   cam.cam_chunk.optimizeChunk
   cam.cam_chunk.limitChunks
   cam.cam_chunk.parentChildPoly
   cam.cam_chunk.parentChildDist
   cam.cam_chunk.parentChild
   cam.cam_chunk.chunksToShapely
   cam.cam_chunk.meshFromCurveToChunk
   cam.cam_chunk.makeVisible
   cam.cam_chunk.restoreVisibility
   cam.cam_chunk.meshFromCurve
   cam.cam_chunk.curveToChunks
   cam.cam_chunk.shapelyToChunks
   cam.cam_chunk.chunkToShapely
   cam.cam_chunk.chunksRefine
   cam.cam_chunk.chunksRefineThreshold


Module Contents
---------------

.. py:function:: Rotate_pbyp(originp, p, ang)

.. py:function:: _internalXyDistanceTo(ourpoints, theirpoints, cutoff)

.. py:class:: camPathChunkBuilder(inpoints=None, startpoints=None, endpoints=None, rotations=None)

   .. py:attribute:: points


   .. py:attribute:: startpoints


   .. py:attribute:: endpoints


   .. py:attribute:: rotations


   .. py:attribute:: depth
      :value: None



   .. py:method:: to_chunk()


.. py:class:: camPathChunk(inpoints, startpoints=None, endpoints=None, rotations=None)

   .. py:attribute:: poly
      :value: None



   .. py:attribute:: simppoly
      :value: None



   .. py:attribute:: closed
      :value: False



   .. py:attribute:: children
      :value: []



   .. py:attribute:: parents
      :value: []



   .. py:attribute:: sorted
      :value: False



   .. py:attribute:: length
      :value: 0



   .. py:attribute:: zstart
      :value: 0



   .. py:attribute:: zend
      :value: 0



   .. py:method:: update_poly()


   .. py:method:: get_point(n)


   .. py:method:: get_points()


   .. py:method:: get_points_np()


   .. py:method:: set_points(points)


   .. py:method:: count()


   .. py:method:: copy()


   .. py:method:: shift(x, y, z)


   .. py:method:: setZ(z, if_bigger=False)


   .. py:method:: offsetZ(z)


   .. py:method:: flipX(x_centre)


   .. py:method:: isbelowZ(z)


   .. py:method:: clampZ(z)


   .. py:method:: clampmaxZ(z)


   .. py:method:: dist(pos, o)


   .. py:method:: distStart(pos, o)


   .. py:method:: xyDistanceWithin(other, cutoff)


   .. py:method:: xyDistanceTo(other, cutoff=0)


   .. py:method:: adaptdist(pos, o)


   .. py:method:: getNextClosest(o, pos)


   .. py:method:: getLength()


   .. py:method:: reverse()


   .. py:method:: pop(index)


   .. py:method:: dedupePoints()


   .. py:method:: insert(at_index, point, startpoint=None, endpoint=None, rotation=None)


   .. py:method:: append(point, startpoint=None, endpoint=None, rotation=None, at_index=None)


   .. py:method:: extend(points, startpoints=None, endpoints=None, rotations=None, at_index=None)


   .. py:method:: clip_points(minx, maxx, miny, maxy)

      Remove Any Points Outside This Range



   .. py:method:: rampContour(zstart, zend, o)


   .. py:method:: rampZigZag(zstart, zend, o)


   .. py:method:: changePathStart(o)


   .. py:method:: breakPathForLeadinLeadout(o)


   .. py:method:: leadContour(o)


.. py:function:: chunksCoherency(chunks)

.. py:function:: setChunksZ(chunks, z)

.. py:function:: _optimize_internal(points, keep_points, e, protect_vertical, protect_vertical_limit)

.. py:function:: optimizeChunk(chunk, operation)

.. py:function:: limitChunks(chunks, o, force=False)

.. py:function:: parentChildPoly(parents, children, o)

.. py:function:: parentChildDist(parents, children, o, distance=None)

.. py:function:: parentChild(parents, children, o)

.. py:function:: chunksToShapely(chunks)

.. py:function:: meshFromCurveToChunk(object)

.. py:function:: makeVisible(o)

.. py:function:: restoreVisibility(o, storage)

.. py:function:: meshFromCurve(o, use_modifiers=False)

.. py:function:: curveToChunks(o, use_modifiers=False)

.. py:function:: shapelyToChunks(p, zlevel)

.. py:function:: chunkToShapely(chunk)

.. py:function:: chunksRefine(chunks, o)

   Add Extra Points in Between for Chunks


.. py:function:: chunksRefineThreshold(chunks, distance, limitdistance)

   Add Extra Points in Between for Chunks. for Medial Axis Strategy only!


