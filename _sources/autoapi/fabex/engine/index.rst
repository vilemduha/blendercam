fabex.engine
============

.. py:module:: fabex.engine

.. autoapi-nested-parse::

   Fabex 'engine.py'

   Engine definition, options and panels.



Classes
-------

.. autoapisummary::

   fabex.engine.FABEX_ENGINE


Functions
---------

.. autoapisummary::

   fabex.engine.get_panels


Module Contents
---------------

.. py:class:: FABEX_ENGINE(*args, **kwargs)

   Bases: :py:obj:`bpy.types.RenderEngine`


   .. py:attribute:: bl_idname
      :value: 'FABEX_RENDER'



   .. py:attribute:: bl_label
      :value: 'Fabex CNC/CAM'



   .. py:attribute:: bl_use_eevee_viewport
      :value: True



.. py:function:: get_panels()

   Retrieve a list of panels for the Blender UI.

   This function compiles a list of UI panels that are compatible with the
   Blender rendering engine. It excludes certain predefined panels that are
   not relevant for the current context. The function checks all subclasses
   of the `bpy.types.Panel` and includes those that have the
   `COMPAT_ENGINES` attribute set to include 'BLENDER_RENDER', provided
   they are not in the exclusion list.

   :returns: A list of panel classes that are compatible with the
             Blender rendering engine, excluding specified panels.
   :rtype: list


