fabex.properties.chain_props
============================

.. py:module:: fabex.properties.chain_props

.. autoapi-nested-parse::

   Fabex 'chain.py'

   All properties of a CAM Chain (a series of Operations), and the Chain's Operation reference.



Classes
-------

.. autoapisummary::

   fabex.properties.chain_props.CAM_OP_REFERENCE_Properties
   fabex.properties.chain_props.CAM_CHAIN_Properties


Module Contents
---------------

.. py:class:: CAM_OP_REFERENCE_Properties

   Bases: :py:obj:`bpy.types.PropertyGroup`


   .. py:attribute:: name
      :type:  StringProperty(name='Operation Name', default='Operation')


   .. py:attribute:: computing
      :value: False



.. py:class:: CAM_CHAIN_Properties

   Bases: :py:obj:`bpy.types.PropertyGroup`


   .. py:attribute:: index
      :type:  IntProperty(name='Index', description='Index in the hard-defined camChains', default=-1)


   .. py:attribute:: active_operation
      :type:  IntProperty(name='Active Operation', description='Active operation in chain', default=-1)


   .. py:attribute:: name
      :type:  StringProperty(name='Chain Name', default='Chain')


   .. py:attribute:: filename
      :type:  StringProperty(name='File Name', default='Chain')


   .. py:attribute:: link_chain_file_names
      :type:  BoolProperty(name='Link Chain & File Name', description='Auto-assign the Chain Name to the Chain Gcode File', default=False)


   .. py:attribute:: valid
      :type:  BoolProperty(name='Valid', description='True if whole Chain is OK for calculation', default=True)


   .. py:attribute:: invalid_reason
      :type:  StringProperty(name='Chain Error', default='', update=chain_valid)


   .. py:attribute:: computing
      :type:  BoolProperty(name='Computing Right Now', description='', default=False)


   .. py:attribute:: operations
      :type:  CollectionProperty(type=CAM_OP_REFERENCE_Properties)


