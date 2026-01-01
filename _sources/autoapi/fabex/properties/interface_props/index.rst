fabex.properties.interface_props
================================

.. py:module:: fabex.properties.interface_props

.. autoapi-nested-parse::

   Fabex 'interface.py'

   'Interface' properties and panel in Properties > Render



Classes
-------

.. autoapisummary::

   fabex.properties.interface_props.CAM_INTERFACE_Properties


Functions
---------

.. autoapisummary::

   fabex.properties.interface_props.update_interface
   fabex.properties.interface_props.update_shading
   fabex.properties.interface_props.update_layout
   fabex.properties.interface_props.update_user_layout
   fabex.properties.interface_props.draw_interface


Module Contents
---------------

.. py:function:: update_interface(self, context)

.. py:function:: update_shading(self, context)

.. py:function:: update_layout(self, context)

.. py:function:: update_user_layout(self, context)

.. py:class:: CAM_INTERFACE_Properties

   Bases: :py:obj:`bpy.types.PropertyGroup`


   .. py:attribute:: level
      :type:  EnumProperty(name='Interface', description='Choose visible options', items=[('0', 'Basic', 'Only show essential options', '', 0), ('1', 'Advanced', 'Show advanced options', '', 1), ('2', 'Complete', 'Show all options', '', 2), ('3', 'Experimental', 'Show experimental options', 'EXPERIMENTAL', 3)], default='0', update=update_interface)


   .. py:attribute:: shading
      :type:  EnumProperty(name='Shading', description='Choose viewport shading preset', items=[('DEFAULT', 'Default', 'Standard viewport shading'), ('DELUXE', 'Deluxe', 'Cavity, Curvature, Depth of Field, Shadows & Object Colors'), ('CLEAN_DEFAULT', 'Clean Default', 'Standard viewport shading with no overlays'), ('CLEAN_DELUXE', 'Clean Deluxe', 'Deluxe shading with no overlays'), ('PREVIEW', 'Preview', 'HDRI Lighting Preview')], default='DEFAULT', update=update_shading)


   .. py:attribute:: layout
      :type:  EnumProperty(name='Layout', description='Presets for all panel locations', items=[('CLASSIC', 'Classic', 'Properties Area holds most panels, Tools holds the rest'), ('MODERN', 'Modern', 'Properties holds Main panels, Sidebar holds Operation panels, Tools holds Tools'), ('USER', 'User', 'Define your own locations for panels')], default='MODERN', update=update_layout)


   .. py:attribute:: main_location
      :type:  EnumProperty(name='Main Panels', description='Location for Chains, Operations, Material, Machine, Pack, Slice Panels', items=[('PROPERTIES', 'Properties', 'Default panel location is the Render tab of the Properties Area'), ('SIDEBAR', 'Sidebar (N-Panel)', 'Common location for addon UI, press N to show/hide'), ('TOOLS', 'Tools (T-Panel)', "Blender's Tool area, press T to show/hide")], default='PROPERTIES', update=update_user_layout)


   .. py:attribute:: operation_location
      :type:  EnumProperty(name='Operation Panels', description='Location for Setup, Area, Cutter, Feedrate, Optimisation, Movement, G-code', items=[('PROPERTIES', 'Properties', 'Default panel location is the Render tab of the Properties Area'), ('SIDEBAR', 'Sidebar (N-Panel)', 'Common location for addon UI, press N to show/hide'), ('TOOLS', 'Tools (T-Panel)', "Blender's Tool area, press T to show/hide")], default='SIDEBAR', update=update_user_layout)


   .. py:attribute:: tools_location
      :type:  EnumProperty(name='Tools Panels', description='Location for Curve Tools, Curve Creators, Info', items=[('PROPERTIES', 'Properties', 'Default panel location is the Render tab of the Properties Area'), ('SIDEBAR', 'Sidebar (N-Panel)', 'Common location for addon UI, press N to show/hide'), ('TOOLS', 'Tools (T-Panel)', "Blender's Tool area, press T to show/hide")], default='TOOLS', update=update_user_layout)


.. py:function:: draw_interface(self, context)

