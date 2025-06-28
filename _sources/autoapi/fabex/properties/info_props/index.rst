fabex.properties.info_props
===========================

.. py:module:: fabex.properties.info_props

.. autoapi-nested-parse::

   Fabex 'info_props.py'

   'CAM Info Properties'



Classes
-------

.. autoapisummary::

   fabex.properties.info_props.CAM_INFO_Properties


Module Contents
---------------

.. py:class:: CAM_INFO_Properties

   Bases: :py:obj:`bpy.types.PropertyGroup`


   .. py:attribute:: warnings
      :type:  StringProperty(name='Warnings', description='Warnings', default='', update=update_operation)


   .. py:attribute:: chipload
      :type:  FloatProperty(name='Chipload', description='Calculated chipload', default=0.0, unit='LENGTH', precision=CHIPLOAD_PRECISION)


   .. py:attribute:: chipload_per_tooth
      :type:  StringProperty(name='Chipload per Tooth', description='The chipload divided by the number of teeth', default='')


   .. py:attribute:: duration
      :type:  FloatProperty(name='Estimated Time', default=0.01, min=0.0, max=MAX_OPERATION_TIME, precision=PRECISION, unit='TIME')


