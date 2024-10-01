cam.autoupdate
==============

.. py:module:: cam.autoupdate

.. autoapi-nested-parse::

   BlenderCAM 'autoupdate.py'

   Classes to check for, download and install BlenderCAM updates.



Classes
-------

.. autoapisummary::

   cam.autoupdate.UpdateChecker
   cam.autoupdate.Updater
   cam.autoupdate.UpdateSourceOperator


Module Contents
---------------

.. py:class:: UpdateChecker

   Bases: :py:obj:`bpy.types.Operator`


   Check for Updates


   .. py:attribute:: bl_idname
      :value: 'render.cam_check_updates'



   .. py:attribute:: bl_label
      :value: 'Check for Updates in BlenderCAM Plugin'



   .. py:attribute:: bl_options


   .. py:method:: execute(context)


.. py:class:: Updater

   Bases: :py:obj:`bpy.types.Operator`


   Update to Newer Version if Possible


   .. py:attribute:: bl_idname
      :value: 'render.cam_update_now'



   .. py:attribute:: bl_label
      :value: 'Update'



   .. py:attribute:: bl_options


   .. py:method:: execute(context)


   .. py:method:: install_zip_from_url(zip_url)


.. py:class:: UpdateSourceOperator

   Bases: :py:obj:`bpy.types.Operator`


   .. py:attribute:: bl_idname
      :value: 'render.cam_set_update_source'



   .. py:attribute:: bl_label
      :value: 'Set BlenderCAM Update Source'



   .. py:attribute:: new_source
      :type:  StringProperty(default='')


   .. py:method:: execute(context)


