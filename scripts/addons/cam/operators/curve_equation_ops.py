"""Fabex 'curve_cam_equation.py' © 2021, 2022 Alain Pelletier

Operators to create a number of geometric shapes with curves.
"""

from math import pi, sin, cos, sqrt

import numpy as np

import bpy
from bpy.props import (
    EnumProperty,
    FloatProperty,
    IntProperty,
    StringProperty,
)
from bpy.types import Operator

from .. import parametric

from ..utilities.geom_utils import triangle, s_sine


class CamSineCurve(Operator):
    """Create a Sine Wave Curve"""  # by Alain Pelletier april 2021

    bl_idname = "object.sine"
    bl_label = "Periodic Wave"
    bl_options = {"REGISTER", "UNDO", "PRESET"}

    # zstring: StringProperty(name="Z equation", description="Equation for z=F(u,v)", default="0.05*sin(2*pi*4*t)" )
    axis: EnumProperty(
        name="Displacement Axis",
        items=(
            ("XY", "Y to displace X axis", "Y constant; X sine displacement"),
            ("YX", "X to displace Y axis", "X constant; Y sine displacement"),
            ("ZX", "X to displace Z axis", "X constant; Y sine displacement"),
            ("ZY", "Y to displace Z axis", "X constant; Y sine displacement"),
        ),
        default="ZX",
    )
    wave: EnumProperty(
        name="Wave",
        items=(
            ("sine", "Sine Wave", "Sine Wave"),
            ("triangle", "Triangle Wave", "triangle wave"),
            ("cycloid", "Cycloid", "Sine wave rectification"),
            ("invcycloid", "Inverse Cycloid", "Sine wave rectification"),
        ),
        default="sine",
    )
    amplitude: FloatProperty(
        name="Amplitude",
        default=0.01,
        min=0,
        max=10,
        precision=4,
        unit="LENGTH",
    )
    period: FloatProperty(
        name="Period",
        default=0.5,
        min=0.001,
        max=100,
        precision=4,
        unit="LENGTH",
    )
    beat_period: FloatProperty(
        name="Beat Period Offset",
        default=0.0,
        min=0.0,
        max=100,
        precision=4,
        unit="LENGTH",
    )
    shift: FloatProperty(
        name="Phase Shift",
        default=0,
        min=-360,
        max=360,
        precision=4,
        step=100,
        unit="ROTATION",
    )
    offset: FloatProperty(
        name="Offset",
        default=0,
        min=-1.0,
        max=1,
        precision=4,
        unit="LENGTH",
    )
    iteration: IntProperty(
        name="Iteration",
        default=100,
        min=50,
        max=2000,
    )
    max_t: FloatProperty(
        name="Wave Ends at X",
        default=0.5,
        min=-3.0,
        max=3,
        precision=4,
        unit="LENGTH",
    )
    min_t: FloatProperty(
        name="Wave Starts at X",
        default=0,
        min=-3.0,
        max=3,
        precision=4,
        unit="LENGTH",
    )
    wave_distance: FloatProperty(
        name="Distance Between Multiple Waves",
        default=0.0,
        min=0.0,
        max=100,
        precision=4,
        unit="LENGTH",
    )
    wave_angle_offset: FloatProperty(
        name="Angle Offset for Multiple Waves",
        default=pi / 2,
        min=-200 * pi,
        max=200 * pi,
        precision=4,
        step=100,
        unit="ROTATION",
    )
    wave_amount: IntProperty(
        name="Amount of Multiple Waves",
        default=1,
        min=1,
        max=2000,
    )

    def execute(self, context):
        amp = self.amplitude
        period = self.period
        beatperiod = self.beat_period
        offset = self.offset
        shift = self.shift

        # z=Asin(B(x+C))+D
        if self.wave == "sine":
            zstring = s_sine(amp, period, dc_offset=offset, phase_shift=shift)
            if self.beat_period != 0:
                zstring += (
                    f"+ {s_sine(amp, period+beatperiod, dc_offset=offset, phase_shift=shift)}"
                )

        # build triangle wave from fourier series
        elif self.wave == "triangle":
            zstring = f"{round(offset, 6)} + {triangle(80, period, amp)}"
            if self.beat_period != 0:
                zstring += f"+ {triangle(80, period+beatperiod, amp)}"

        elif self.wave == "cycloid":
            zstring = f"abs({s_sine(amp, period, dc_offset=offset, phase_shift=shift)})"

        elif self.wave == "invcycloid":
            zstring = f"-1 * abs({s_sine(amp, period, dc_offset=offset, phase_shift=shift)})"

        print(zstring)
        # make equation from string

        def e(t):
            return eval(zstring)

        # build function to be passed to create parametric curve ()
        def f(t, offset: float = 0.0, angle_offset: float = 0.0):
            if self.axis == "XY":
                c = (e(t + angle_offset) + offset, t, 0)
            elif self.axis == "YX":
                c = (t, e(t + angle_offset) + offset, 0)
            elif self.axis == "ZX":
                c = (t, offset, e(t + angle_offset))
            elif self.axis == "ZY":
                c = (offset, t, e(t + angle_offset))
            return c

        for i in range(self.wave_amount):
            angle_off = self.wave_angle_offset * period * i / (2 * pi)
            parametric.create_parametric_curve(
                f,
                offset=self.wave_distance * i,
                min=self.min_t,
                max=self.max_t,
                use_cubic=True,
                iterations=self.iteration,
                angle_offset=angle_off,
            )

        return {"FINISHED"}


class CamLissajousCurve(Operator):
    """Create a Lissajous Curve (Knot / Weave Pattern)"""  # by Alain Pelletier april 2021

    bl_idname = "object.lissajous"
    bl_label = "Lissajous Figure"
    bl_options = {"REGISTER", "UNDO", "PRESET"}

    amplitude_a: FloatProperty(
        name="Amplitude A",
        default=0.1,
        min=0,
        max=100,
        precision=4,
        unit="LENGTH",
    )
    wave_a: EnumProperty(
        name="Wave X",
        items=(("sine", "Sine Wave", "Sine Wave"), ("triangle", "Triangle Wave", "triangle wave")),
        default="sine",
    )

    amplitude_b: FloatProperty(
        name="Amplitude B",
        default=0.1,
        min=0,
        max=100,
        precision=4,
        unit="LENGTH",
    )
    wave_b: EnumProperty(
        name="Wave Y",
        items=(("sine", "Sine Wave", "Sine Wave"), ("triangle", "Triangle Wave", "triangle wave")),
        default="sine",
    )
    period_a: FloatProperty(
        name="Period A",
        default=1.1,
        min=0.001,
        max=100,
        precision=4,
        unit="LENGTH",
    )
    period_b: FloatProperty(
        name="Period B",
        default=1.0,
        min=0.001,
        max=100,
        precision=4,
        unit="LENGTH",
    )
    period_z: FloatProperty(
        name="Period Z",
        default=1.0,
        min=0.001,
        max=100,
        precision=4,
        unit="LENGTH",
    )
    amplitude_z: FloatProperty(
        name="Amplitude Z",
        default=0.0,
        min=0,
        max=100,
        precision=4,
        unit="LENGTH",
    )
    shift: FloatProperty(
        name="Phase Shift",
        default=0,
        min=-360,
        max=360,
        precision=4,
        step=100,
        unit="ROTATION",
    )

    iteration: IntProperty(
        name="Iteration",
        default=500,
        min=50,
        max=10000,
    )
    max_t: FloatProperty(
        name="Wave Ends at X",
        default=11,
        min=-3.0,
        max=1000000,
        precision=4,
        unit="LENGTH",
    )
    min_t: FloatProperty(
        name="Wave Starts at X",
        default=0,
        min=-10.0,
        max=3,
        precision=4,
        unit="LENGTH",
    )

    def execute(self, context):
        # x=Asin(at+delta ),y=Bsin(bt)

        if self.wave_a == "sine":
            xstring = s_sine(self.amplitude_a, self.period_a, phase_shift=self.shift)
        elif self.wave_a == "triangle":
            xstring = f"{triangle(100, self.period_a, self.amplitude_a)}"

        if self.wave_b == "sine":
            ystring = s_sine(self.amplitude_b, self.period_b)
        elif self.wave_b == "triangle":
            ystring = f"{triangle(100, self.period_b, self.amplitude_b)}"

        zstring = s_sine(self.amplitude_z, self.period_z)

        # make equation from string
        def x(t):
            return eval(xstring)

        def y(t):
            return eval(ystring)

        def z(t):
            return eval(zstring)

        print(f"x= {xstring}")
        print(f"y= {ystring}")

        # build function to be passed to create parametric curve ()
        def f(t, offset: float = 0.0):
            c = (x(t), y(t), z(t))
            return c

        parametric.create_parametric_curve(
            f, offset=0.0, min=self.min_t, max=self.max_t, use_cubic=True, iterations=self.iteration
        )

        return {"FINISHED"}


class CamHypotrochoidCurve(Operator):
    """Create a Hypotrochoid Curve (Spirograph-type Pattern)"""  # by Alain Pelletier april 2021

    bl_idname = "object.hypotrochoid"
    bl_label = "Spirograph Type Figure"
    bl_options = {"REGISTER", "UNDO", "PRESET"}

    typecurve: EnumProperty(
        name="Type of Curve",
        items=(
            ("hypo", "Hypotrochoid", "Inside ring"),
            ("epi", "Epicycloid", "Outside inner ring"),
        ),
    )
    R: FloatProperty(
        name="Big Circle Radius",
        default=0.25,
        min=0.001,
        max=100,
        precision=4,
        unit="LENGTH",
    )
    r: FloatProperty(
        name="Small Circle Radius",
        default=0.18,
        min=0.0001,
        max=100,
        precision=4,
        unit="LENGTH",
    )
    d: FloatProperty(
        name="Distance from Center of Interior Circle",
        default=0.050,
        min=0,
        max=100,
        precision=4,
        unit="LENGTH",
    )
    dip: FloatProperty(
        name="Variable Depth from Center",
        default=0.00,
        min=-100,
        max=100,
        precision=4,
    )

    def execute(self, context):
        r = round(self.r, 6)
        R = round(self.R, 6)
        d = round(self.d, 6)
        Rmr = round(R - r, 6)  # R-r
        Rpr = round(R + r, 6)  # R +r
        Rpror = round(Rpr / r, 6)  # (R+r)/r
        Rmror = round(Rmr / r, 6)  # (R-r)/r
        maxangle = 2 * pi * ((np.lcm(round(self.R * 1000), round(self.r * 1000)) / (R * 1000)))

        if self.typecurve == "hypo":
            xstring = f"{Rmr} * cos(t) + {d} * cos({Rmror} * t)"
            ystring = f"{Rmr} * sin(t) - {d} * sin({Rmror} * t)"
        else:
            xstring = f"{Rpr} * cos(t) - {d} * cos({Rpror} * t)"
            ystring = f"{Rpr} * sin(t) - {d} * sin({Rpror} * t)"

        zstring = f"({round(self.dip, 6)} * (sqrt((({xstring})**2) + (({ystring})**2))))"

        # make equation from string
        def x(t):
            return eval(xstring)

        def y(t):
            return eval(ystring)

        def z(t):
            return eval(zstring)

        print(f"x= {xstring}")
        print(f"y= {ystring}")
        print(f"z= {zstring}")
        print(f"maxangle {maxangle}")

        # build function to be passed to create parametric curve ()
        def f(t, offset: float = 0.0):
            c = (x(t), y(t), z(t))
            return c

        iter = int(maxangle * 10)
        if iter > 10000:  # do not calculate more than 10000 points
            print("limiting calculations to 10000 points")
            iter = 10000
        parametric.create_parametric_curve(
            f, offset=0.0, min=0, max=maxangle, use_cubic=True, iterations=iter
        )

        return {"FINISHED"}


class CamCustomCurve(Operator):
    """Create a Curve based on User Defined Variables"""  # by Alain Pelletier april 2021

    bl_idname = "object.customcurve"
    bl_label = "Custom Curve"
    bl_options = {"REGISTER", "UNDO", "PRESET"}

    x_string: StringProperty(
        name="X Equation",
        description="Equation x=F(t)",
        default="t",
    )
    y_string: StringProperty(
        name="Y Equation",
        description="Equation y=F(t)",
        default="0",
    )
    z_string: StringProperty(
        name="Z Equation",
        description="Equation z=F(t)",
        default="0.05*sin(2*pi*4*t)",
    )

    iteration: IntProperty(
        name="Iteration",
        default=100,
        min=50,
        max=2000,
    )
    max_t: FloatProperty(
        name="Wave Ends at X",
        default=0.5,
        min=-3.0,
        max=10,
        precision=4,
        unit="LENGTH",
    )
    min_t: FloatProperty(
        name="Wave Starts at X",
        default=0,
        min=-3.0,
        max=3,
        precision=4,
        unit="LENGTH",
    )

    def execute(self, context):
        print("x= " + self.x_string)
        print("y= " + self.y_string)
        print("z= " + self.z_string)

        # make equation from string
        def ex(t):
            return eval(self.x_string)

        def ey(t):
            return eval(self.y_string)

        def ez(t):
            return eval(self.z_string)

        # build function to be passed to create parametric curve ()
        def f(t, offset: float = 0.0):
            c = (ex(t), ey(t), ez(t))
            return c

        parametric.create_parametric_curve(
            f, offset=0.0, min=self.min_t, max=self.max_t, use_cubic=True, iterations=self.iteration
        )

        return {"FINISHED"}
