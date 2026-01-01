fabex.operators.curve_equation_ops
==================================

.. py:module:: fabex.operators.curve_equation_ops

.. autoapi-nested-parse::

   Fabex 'curve_cam_equation.py' © 2021, 2022 Alain Pelletier

   Operators to create a number of geometric shapes with curves.



Classes
-------

.. autoapisummary::

   fabex.operators.curve_equation_ops.CamSineCurve
   fabex.operators.curve_equation_ops.CamLissajousCurve
   fabex.operators.curve_equation_ops.CamHypotrochoidCurve
   fabex.operators.curve_equation_ops.CamCustomCurve


Module Contents
---------------

.. py:class:: CamSineCurve

   Bases: :py:obj:`bpy.types.Operator`


   Create a Sine Wave Curve


   .. py:attribute:: bl_idname
      :value: 'object.sine'



   .. py:attribute:: bl_label
      :value: 'Periodic Wave'



   .. py:attribute:: bl_options


   .. py:attribute:: axis
      :type:  EnumProperty(name='Displacement Axis', items=(('XY', 'Y to displace X axis', 'Y constant; X sine displacement'), ('YX', 'X to displace Y axis', 'X constant; Y sine displacement'), ('ZX', 'X to displace Z axis', 'X constant; Y sine displacement'), ('ZY', 'Y to displace Z axis', 'X constant; Y sine displacement')), default='ZX')


   .. py:attribute:: wave
      :type:  EnumProperty(name='Wave', items=(('sine', 'Sine Wave', 'Sine Wave'), ('triangle', 'Triangle Wave', 'triangle wave'), ('cycloid', 'Cycloid', 'Sine wave rectification'), ('invcycloid', 'Inverse Cycloid', 'Sine wave rectification')), default='sine')


   .. py:attribute:: amplitude
      :type:  FloatProperty(name='Amplitude', default=0.01, min=0, max=10, precision=4, unit='LENGTH')


   .. py:attribute:: period
      :type:  FloatProperty(name='Period', default=0.5, min=0.001, max=100, precision=4, unit='LENGTH')


   .. py:attribute:: beat_period
      :type:  FloatProperty(name='Beat Period Offset', default=0.0, min=0.0, max=100, precision=4, unit='LENGTH')


   .. py:attribute:: shift
      :type:  FloatProperty(name='Phase Shift', default=0, min=-360, max=360, precision=4, step=100, unit='ROTATION')


   .. py:attribute:: offset
      :type:  FloatProperty(name='Offset', default=0, min=-1.0, max=1, precision=4, unit='LENGTH')


   .. py:attribute:: iteration
      :type:  IntProperty(name='Iteration', default=100, min=50, max=2000)


   .. py:attribute:: max_t
      :type:  FloatProperty(name='Wave Ends at X', default=0.5, min=-3.0, max=3, precision=4, unit='LENGTH')


   .. py:attribute:: min_t
      :type:  FloatProperty(name='Wave Starts at X', default=0, min=-3.0, max=3, precision=4, unit='LENGTH')


   .. py:attribute:: wave_distance
      :type:  FloatProperty(name='Distance Between Multiple Waves', default=0.0, min=0.0, max=100, precision=4, unit='LENGTH')


   .. py:attribute:: wave_angle_offset
      :type:  FloatProperty(name='Angle Offset for Multiple Waves', default=pi / 2, min=-200 * pi, max=200 * pi, precision=4, step=100, unit='ROTATION')


   .. py:attribute:: wave_amount
      :type:  IntProperty(name='Amount of Multiple Waves', default=1, min=1, max=2000)


   .. py:method:: execute(context)


.. py:class:: CamLissajousCurve

   Bases: :py:obj:`bpy.types.Operator`


   Create a Lissajous Curve (Knot / Weave Pattern)


   .. py:attribute:: bl_idname
      :value: 'object.lissajous'



   .. py:attribute:: bl_label
      :value: 'Lissajous Figure'



   .. py:attribute:: bl_options


   .. py:attribute:: amplitude_a
      :type:  FloatProperty(name='Amplitude A', default=0.1, min=0, max=100, precision=4, unit='LENGTH')


   .. py:attribute:: wave_a
      :type:  EnumProperty(name='Wave X', items=(('sine', 'Sine Wave', 'Sine Wave'), ('triangle', 'Triangle Wave', 'triangle wave')), default='sine')


   .. py:attribute:: amplitude_b
      :type:  FloatProperty(name='Amplitude B', default=0.1, min=0, max=100, precision=4, unit='LENGTH')


   .. py:attribute:: wave_b
      :type:  EnumProperty(name='Wave Y', items=(('sine', 'Sine Wave', 'Sine Wave'), ('triangle', 'Triangle Wave', 'triangle wave')), default='sine')


   .. py:attribute:: period_a
      :type:  FloatProperty(name='Period A', default=1.1, min=0.001, max=100, precision=4, unit='LENGTH')


   .. py:attribute:: period_b
      :type:  FloatProperty(name='Period B', default=1.0, min=0.001, max=100, precision=4, unit='LENGTH')


   .. py:attribute:: period_z
      :type:  FloatProperty(name='Period Z', default=1.0, min=0.001, max=100, precision=4, unit='LENGTH')


   .. py:attribute:: amplitude_z
      :type:  FloatProperty(name='Amplitude Z', default=0.0, min=0, max=100, precision=4, unit='LENGTH')


   .. py:attribute:: shift
      :type:  FloatProperty(name='Phase Shift', default=0, min=-360, max=360, precision=4, step=100, unit='ROTATION')


   .. py:attribute:: iteration
      :type:  IntProperty(name='Iteration', default=500, min=50, max=10000)


   .. py:attribute:: max_t
      :type:  FloatProperty(name='Wave Ends at X', default=11, min=-3.0, max=1000000, precision=4, unit='LENGTH')


   .. py:attribute:: min_t
      :type:  FloatProperty(name='Wave Starts at X', default=0, min=-10.0, max=3, precision=4, unit='LENGTH')


   .. py:method:: execute(context)


.. py:class:: CamHypotrochoidCurve

   Bases: :py:obj:`bpy.types.Operator`


   Create a Hypotrochoid Curve (Spirograph-type Pattern)


   .. py:attribute:: bl_idname
      :value: 'object.hypotrochoid'



   .. py:attribute:: bl_label
      :value: 'Spirograph Type Figure'



   .. py:attribute:: bl_options


   .. py:attribute:: typecurve
      :type:  EnumProperty(name='Type of Curve', items=(('hypo', 'Hypotrochoid', 'Inside ring'), ('epi', 'Epicycloid', 'Outside inner ring')))


   .. py:attribute:: R
      :type:  FloatProperty(name='Big Circle Radius', default=0.25, min=0.001, max=100, precision=4, unit='LENGTH')


   .. py:attribute:: r
      :type:  FloatProperty(name='Small Circle Radius', default=0.18, min=0.0001, max=100, precision=4, unit='LENGTH')


   .. py:attribute:: d
      :type:  FloatProperty(name='Distance from Center of Interior Circle', default=0.05, min=0, max=100, precision=4, unit='LENGTH')


   .. py:attribute:: dip
      :type:  FloatProperty(name='Variable Depth from Center', default=0.0, min=-100, max=100, precision=4)


   .. py:method:: execute(context)


.. py:class:: CamCustomCurve

   Bases: :py:obj:`bpy.types.Operator`


   Create a Curve based on User Defined Variables


   .. py:attribute:: bl_idname
      :value: 'object.customcurve'



   .. py:attribute:: bl_label
      :value: 'Custom Curve'



   .. py:attribute:: bl_options


   .. py:attribute:: x_string
      :type:  StringProperty(name='X Equation', description='Equation x=F(t)', default='t')


   .. py:attribute:: y_string
      :type:  StringProperty(name='Y Equation', description='Equation y=F(t)', default='0')


   .. py:attribute:: z_string
      :type:  StringProperty(name='Z Equation', description='Equation z=F(t)', default='0.05*sin(2*pi*4*t)')


   .. py:attribute:: iteration
      :type:  IntProperty(name='Iteration', default=100, min=50, max=2000)


   .. py:attribute:: max_t
      :type:  FloatProperty(name='Wave Ends at X', default=0.5, min=-3.0, max=10, precision=4, unit='LENGTH')


   .. py:attribute:: min_t
      :type:  FloatProperty(name='Wave Starts at X', default=0, min=-3.0, max=3, precision=4, unit='LENGTH')


   .. py:method:: execute(context)


