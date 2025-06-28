fabex.properties.material_props
===============================

.. py:module:: fabex.properties.material_props

.. autoapi-nested-parse::

   Fabex 'material_props.py'

   'CAM Material Properties'



Classes
-------

.. autoapisummary::

   fabex.properties.material_props.CAM_MATERIAL_Properties


Module Contents
---------------

.. py:class:: CAM_MATERIAL_Properties

   Bases: :py:obj:`bpy.types.PropertyGroup`


   .. py:attribute:: estimate_from_model
      :type:  BoolProperty(name='Estimate Cut Area from Model', description='Estimate cut area based on model geometry', default=True, update=update_material)


   .. py:attribute:: radius_around_model
      :type:  FloatProperty(name='Radius Around Model', description='Increase cut area around the model on X and Y by this amount', default=0.0, unit='LENGTH', precision=PRECISION, update=update_material)


   .. py:attribute:: center_x
      :type:  BoolProperty(name='Center on X Axis', description='Position model centered on X', default=False, update=update_material)


   .. py:attribute:: center_y
      :type:  BoolProperty(name='Center on Y Axis', description='Position model centered on Y', default=False, update=update_material)


   .. py:attribute:: z_position
      :type:  EnumProperty(name='Z Placement', items=(('ABOVE', 'Above', 'Place object vertically above the XY plane'), ('BELOW', 'Below', 'Place object vertically below the XY plane'), ('CENTERED', 'Centered', 'Place object vertically centered on the XY plane')), description='Position below Zero', default='BELOW', update=update_material)


   .. py:attribute:: origin
      :type:  FloatVectorProperty(name='Material Origin', default=(0, 0, 0), unit='LENGTH', precision=PRECISION, subtype='XYZ', update=update_material)


   .. py:attribute:: size
      :type:  FloatVectorProperty(name='Material Size', default=(0.2, 0.2, 0.1), min=0, unit='LENGTH', precision=PRECISION, subtype='XYZ', update=update_material)


