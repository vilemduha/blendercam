fabex.preferences
=================

.. py:module:: fabex.preferences

.. autoapi-nested-parse::

   Fabex 'preferences.py'

   Class to store all Addon preferences.



Classes
-------

.. autoapisummary::

   fabex.preferences.CamAddonPreferences


Module Contents
---------------

.. py:class:: CamAddonPreferences

   Bases: :py:obj:`bpy.types.AddonPreferences`


   .. py:attribute:: bl_idname


   .. py:attribute:: op_preset_update
      :type:  BoolProperty(name='Have the Operation Presets Been Updated', default=False)


   .. py:attribute:: wireframe_color
      :type:  EnumProperty(name='Wire Color Source', description='Wireframe color comes from Object, Theme or a Random color', items=[('OBJECT', 'Object', 'Show object color on wireframe'), ('THEME', 'Theme', "Show Scene wireframes with the theme's wire color"), ('RANDOM', 'Random', 'Show random object color on wireframe')], default='OBJECT')


   .. py:attribute:: default_interface_level
      :type:  EnumProperty(name='Interface Level in New File', description='Choose visible options', items=[('0', 'Basic', 'Only show Essential Options'), ('1', 'Advanced', 'Show Advanced Options'), ('2', 'Complete', 'Show All Options'), ('3', 'Experimental', 'Show Experimental Options')], default='3')


   .. py:attribute:: default_shading
      :type:  EnumProperty(name='Viewport Shading in New File', description='Choose viewport shading preset', items=[('DEFAULT', 'Default', 'Standard viewport shading'), ('DELUXE', 'Deluxe', 'Cavity, Curvature, Depth of Field, Shadows & Object Colors'), ('CLEAN_DEFAULT', 'Clean Default', 'Standard viewport shading with no overlays'), ('CLEAN_DELUXE', 'Clean Deluxe', 'Deluxe shading with no overlays'), ('PREVIEW', 'Preview', 'HDRI Lighting Preview')], default='DEFAULT')


   .. py:attribute:: default_layout
      :type:  EnumProperty(name='Panel Layout', description='Presets for all panel locations', items=[('CLASSIC', 'Classic', 'Properties Area holds most panels, Tools holds the rest'), ('MODERN', 'Modern', 'Properties holds Main panels, Sidebar holds Operation panels, Tools holds Tools'), ('USER', 'User', 'Define your own locations for panels')], default='MODERN')


   .. py:attribute:: default_main_location
      :type:  EnumProperty(name='Main Panels', description='Location for Chains, Operations, Material, Machine, Pack, Slice Panels', items=[('PROPERTIES', 'Properties', 'Default panel location is the Render tab of the Properties Area'), ('SIDEBAR', 'Sidebar (N-Panel)', 'Common location for addon UI, press N to show/hide'), ('TOOLS', 'Tools (T-Panel)', "Blender's Tool area, press T to show/hide")], default='PROPERTIES')


   .. py:attribute:: default_operation_location
      :type:  EnumProperty(name='Operation Panels', description='Location for Setup, Area, Cutter, Feedrate, Optimisation, Movement, G-code', items=[('PROPERTIES', 'Properties', 'Default panel location is the Render tab of the Properties Area'), ('SIDEBAR', 'Sidebar (N-Panel)', 'Common location for addon UI, press N to show/hide'), ('TOOLS', 'Tools (T-Panel)', "Blender's Tool area, press T to show/hide")], default='SIDEBAR')


   .. py:attribute:: default_tools_location
      :type:  EnumProperty(name='Tools Panels', description='Location for Curve Tools, Curve Creators, Info', items=[('PROPERTIES', 'Properties', 'Default panel location is the Render tab of the Properties Area'), ('SIDEBAR', 'Sidebar (N-Panel)', 'Common location for addon UI, press N to show/hide'), ('TOOLS', 'Tools (T-Panel)', "Blender's Tool area, press T to show/hide")], default='TOOLS')


   .. py:attribute:: user_main_location
      :type:  EnumProperty(name='Main Panels', items=[('PROPERTIES', 'Properties', 'Default panel location is the Render tab of the Properties Area'), ('SIDEBAR', 'Sidebar (N-Panel)', 'Common location for addon UI, press N to show/hide'), ('TOOLS', 'Tools (T-Panel)', "Blender's Tool area, press T to show/hide")], default='PROPERTIES')


   .. py:attribute:: user_operation_location
      :type:  EnumProperty(name='Operation Panels', items=[('PROPERTIES', 'Properties', 'Default panel location is the Render tab of the Properties Area'), ('SIDEBAR', 'Sidebar (N-Panel)', 'Common location for addon UI, press N to show/hide'), ('TOOLS', 'Tools (T-Panel)', "Blender's Tool area, press T to show/hide")], default='SIDEBAR')


   .. py:attribute:: user_tools_location
      :type:  EnumProperty(name='Tools Panels', items=[('PROPERTIES', 'Properties', 'Default panel location is the Render tab of the Properties Area'), ('SIDEBAR', 'Sidebar (N-Panel)', 'Common location for addon UI, press N to show/hide'), ('TOOLS', 'Tools (T-Panel)', "Blender's Tool area, press T to show/hide")], default='TOOLS')


   .. py:attribute:: default_machine_preset
      :type:  StringProperty(name='Machine Preset in New File', description='So that machine preset choice persists between files', default='')


   .. py:attribute:: default_simulation_material
      :type:  EnumProperty(name='Simulation Shader', items=[('GLASS', 'Glass', 'Glass or Clear Acrylic-type Material'), ('METAL', 'Metal', 'Metallic Material'), ('PLASTIC', 'Plastic', 'Plastic-type Material'), ('WOOD', 'Wood', 'Wood Grain-type Material')], default='WOOD')


   .. py:attribute:: show_popups
      :type:  BoolProperty(name='Show Warning Popups', description='Shows a Popup window when there is a warning', default=True)


   .. py:method:: draw(context)


