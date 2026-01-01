fabex.operators.log_ops
=======================

.. py:module:: fabex.operators.log_ops

.. autoapi-nested-parse::

   Fabex 'log_ops.py' © 2012 Vilem Novak

   Blender Operator definitions are in this file.
   They mostly call the functions from 'utils.py'



Attributes
----------

.. autoapisummary::

   fabex.operators.log_ops.log_folder


Classes
-------

.. autoapisummary::

   fabex.operators.log_ops.CamOpenLogFolder
   fabex.operators.log_ops.CamPurgeLogs


Module Contents
---------------

.. py:data:: log_folder
   :value: ''


.. py:class:: CamOpenLogFolder

   Bases: :py:obj:`bpy.types.Operator`


   Open the CAM Log Folder


   .. py:attribute:: bl_idname
      :value: 'scene.cam_open_log_folder'



   .. py:attribute:: bl_label
      :value: 'Open Log Folder'



   .. py:attribute:: bl_options


   .. py:method:: poll(context)
      :classmethod:



   .. py:method:: execute(context)

      Opens the folder where CAM logs are stored.

      :param context: The context in which the operation is executed.

      :returns:

                A dictionary indicating the operation's completion status,
                    specifically returning {'FINISHED'} upon successful execution.
      :rtype: dict



.. py:class:: CamPurgeLogs

   Bases: :py:obj:`bpy.types.Operator`


   Delete CAM Logs


   .. py:attribute:: bl_idname
      :value: 'scene.cam_purge_logs'



   .. py:attribute:: bl_label
      :value: 'Purge CAM Logs'



   .. py:attribute:: bl_options


   .. py:method:: poll(context)
      :classmethod:



   .. py:method:: execute(context)

      Execute the CAM log removal process.

      This function removes the files from the CAM logs folder

      :param context: The context in which the function is executed.

      :returns:

                A dictionary indicating the status of the operation,
                    specifically {'FINISHED'} upon successful execution.
      :rtype: dict



