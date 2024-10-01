cam.chain
=========

.. py:module:: cam.chain

.. autoapi-nested-parse::

   BlenderCAM 'chain.py'

   All properties of a CAM Chain (a series of Operations), and the Chain's Operation reference.



Classes
-------

.. autoapisummary::

   cam.chain.opReference
   cam.chain.camChain


Module Contents
---------------

.. py:class:: opReference

   Bases: :py:obj:`bpy.types.PropertyGroup`


   .. py:attribute:: name
      :type:  StringProperty(name='Operation Name', default='Operation')


   .. py:attribute:: computing
      :value: False



.. py:class:: camChain

   Bases: :py:obj:`bpy.types.PropertyGroup`


   .. py:attribute:: index
      :type:  IntProperty(name='Index', description='Index in the hard-defined camChains', default=-1)


   .. py:attribute:: active_operation
      :type:  IntProperty(name='Active Operation', description='Active operation in chain', default=-1)


   .. py:attribute:: name
      :type:  StringProperty(name='Chain Name', default='Chain')


   .. py:attribute:: filename
      :type:  StringProperty(name='File Name', default='Chain')


   .. py:attribute:: valid
      :type:  BoolProperty(name='Valid', description='True if whole chain is ok for calculation', default=True)


   .. py:attribute:: computing
      :type:  BoolProperty(name='Computing Right Now', description='', default=False)


   .. py:attribute:: operations
      :type:  CollectionProperty(type=opReference)


