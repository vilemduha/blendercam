# blender CAM curvecamequation.py (c) 2021 Alain Pelletier
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ***** END GPL LICENCE BLOCK *****



import bpy
from bpy.props import *

from cam import utils, parametric
import math
from Equation import Expression
import numpy as np


class CamSineCurve(bpy.types.Operator):
    """Object sine """  # by Alain Pelletier april 2021
    bl_idname = "object.sine"
    bl_label = "Create Periodic wave"
    bl_options = {'REGISTER', 'UNDO', 'PRESET'}

    #    zstring: StringProperty(name="Z equation", description="Equation for z=F(u,v)", default="0.05*sin(2*pi*4*t)" )
    axis: bpy.props.EnumProperty(name="displacement axis", items=(
        ('XY', 'Y to displace X axis', 'Y constant; X sine displacement'),
        ('YX', 'X to displace Y axis', 'X constant; Y sine displacement'),
        ('ZX', 'X to displace Z axis', 'X constant; Y sine displacement'),
        ('ZY', 'Y to displace Z axis', 'X constant; Y sine displacement')),default='ZX')
    wave: bpy.props.EnumProperty(name="Wave", items=(
        ('sine', 'Sine Wave', 'Sine Wave'),
        ('triangle', 'Triangle Wave', 'triangle wave'),
        ('cycloid', 'Cycloid', 'Sine wave rectification')),default='sine')
    amplitude: bpy.props.FloatProperty(name="Amplitude", default=.01, min=0, max=10, precision=4, unit="LENGTH")
    period: bpy.props.FloatProperty(name="Period", default=.5, min=0.001, max=100, precision=4, unit="LENGTH")
    beatperiod: bpy.props.FloatProperty(name="Beat Period offset", default=0.0, min=0.0, max=100, precision=4, unit="LENGTH")
    shift: bpy.props.FloatProperty(name="phase shift", default=0, min=-360, max=360, precision=4, unit="ROTATION")
    offset: bpy.props.FloatProperty(name="offset", default=0, min=-1.0, max=1, precision=4, unit="LENGTH")
    iteration: bpy.props.IntProperty(name="iteration", default=100, min=50, max=2000)
    maxt: bpy.props.FloatProperty(name="Wave ends at x", default=0.5, min=-3.0, max=3, precision=4, unit="LENGTH")
    mint: bpy.props.FloatProperty(name="Wave starts at x", default=0, min=-3.0, max=3, precision=4, unit="LENGTH")
    wave_distance: bpy.props.FloatProperty(name="distance between multiple waves", default=0.0, min=0.0, max=100, precision=4, unit="LENGTH")
    wave_angle_offset: bpy.props.FloatProperty(name="angle offset for multiple waves", default=math.pi/2, min=-200*math.pi, max=200*math.pi, precision=4, unit="ROTATION")
    wave_amount: bpy.props.IntProperty(name="amount of multiple waves", default=1, min=1, max=2000)

    def execute(self, context):

        # z=Asin(B(x+C))+D
        if self.wave=='sine':
            zstring = str(round(self.offset, 6)) + "+" + str(round(self.amplitude, 6)) + "*sin((2*pi/" + str(
                round(self.period, 6)) + ")*(t+" + str(round(self.shift, 6)) + "))"
            if self.beatperiod !=0:
                zstring+= "+" + str(round(self.offset, 6)) + "+" + str(round(self.amplitude, 6)) + "*sin((2*pi/" + str(
                    round(self.period+self.beatperiod, 6)) + ")*(t+" + str(round(self.shift, 6)) + "))"
        elif self.wave=='triangle':  #build triangle wave from fourier series
            m=self.amplitude*8/(math.pi**2)
            zstring = str(round(self.offset, 6)) + "+" + str(m) + '*(' + triangle(50,self.period) +")"
            if self.beatperiod !=0:
                zstring += "+"+str(round(self.offset, 6)) + "+" + str(m) + '*(' + triangle(50, self.period+self.beatperiod) + ")"
        elif self.wave == 'cycloid':
            zstring = "abs("+str(round(self.offset, 6)) + "+" + str(round(self.amplitude, 6)) + "*sin((2*pi/" + str(
                round(self.period, 6)) + ")*(t+" + str(round(self.shift, 6)) + ")))"
            if self.beatperiod !=0:
                zstring += "+ (" + str(round(self.offset, 6)) + "+" + str(
                    round(self.amplitude, 6)) + "*sin((2*pi/" + str(
                    round(self.period+self.beatperiod, 6)) + ")*(t+" + str(round(self.shift, 6)) + ")))"

        print(zstring)
        e = Expression(zstring, ["t"])  # make equation from string

        # build function to be passed to create parametric curve ()
        def f(t, offset: float = 0.0, angle_offset: float = 0.0):
            if self.axis == "XY":
                c = (e(t+angle_offset), t, offset)
            elif self.axis == "YX":
                c = (t, e(t+angle_offset), offset)
            elif self.axis == "ZX":
                c = (t, offset, e(t+angle_offset))
            elif self.axis == "ZY":
                c = (offset, t, e(t+angle_offset))
            return c

        for i in range(self.wave_amount):
            angle_off=self.wave_angle_offset*self.period*i/(2*math.pi)
            parametric.create_parametric_curve(f, offset=self.wave_distance*i, min=self.mint, max=self.maxt, use_cubic=True,
                                           iterations=self.iteration, angle_offset=angle_off)

        return {'FINISHED'}


class CamLissajousCurve(bpy.types.Operator):
    """Lissajous """  # by Alain Pelletier april 2021
    bl_idname = "object.lissajous"
    bl_label = "Create Lissajous figure"
    bl_options = {'REGISTER', 'UNDO', 'PRESET'}

    amplitude_A: bpy.props.FloatProperty(name="Amplitude A", default=.1, min=0, max=100, precision=4, unit="LENGTH")
    amplitude_B: bpy.props.FloatProperty(name="Amplitude B", default=.1, min=0, max=100, precision=4, unit="LENGTH")
    period_A: bpy.props.FloatProperty(name="Period A", default=1.1, min=0.001, max=100, precision=4, unit="LENGTH")
    period_B: bpy.props.FloatProperty(name="Period B", default=1.0, min=0.001, max=100, precision=4, unit="LENGTH")
    shift: bpy.props.FloatProperty(name="phase shift", default=0, min=-360, max=360, precision=4, unit="ROTATION")

    iteration: bpy.props.IntProperty(name="iteration", default=500, min=50, max=10000)
    maxt: bpy.props.FloatProperty(name="Wave ends at x", default=11, min=-3.0, max=1000000, precision=4, unit="LENGTH")
    mint: bpy.props.FloatProperty(name="Wave starts at x", default=0, min=-10.0, max=3, precision=4, unit="LENGTH")

    def execute(self, context):
        # x=Asin(at+delta ),y=Bsin(bt)

        xstring = str(round(self.amplitude_A, 6)) + "*sin((2*pi/" + str(round(self.period_A, 6)) + ")*(t+" + str(
            round(self.shift, 6)) + "))"
        ystring = str(round(self.amplitude_B, 6)) + "*sin((2*pi/" + str(round(self.period_B, 6)) + ")*(t))"
        print("x= " + str(xstring))
        print("y= " + str(ystring))
        x = Expression(xstring, ["t"])  # make equation from string
        y = Expression(ystring, ["t"])  # make equation from string

        # build function to be passed to create parametric curve ()
        def f(t, offset: float = 0.0):
            c = (x(t), y(t), 0)
            return c

        parametric.create_parametric_curve(f, offset=0.0, min=self.mint, max=self.maxt, use_cubic=True,
                                           iterations=self.iteration)

        return {'FINISHED'}


class CamHypotrochoidCurve(bpy.types.Operator):
    """hypotrochoid """  # by Alain Pelletier april 2021
    bl_idname = "object.hypotrochoid"
    bl_label = "Create Spirograph type figure"
    bl_options = {'REGISTER', 'UNDO', 'PRESET'}

    typecurve: bpy.props.EnumProperty(name="type of curve", items=(
        ('hypo', 'Hypotrochoid', 'inside ring'), ('epi', 'Epicycloid', 'outside inner ring')))
    R: bpy.props.FloatProperty(name="Big circle radius", default=0.25, min=0.001, max=100, precision=4, unit="LENGTH")
    r: bpy.props.FloatProperty(name="Small circle radius", default=0.18, min=0.0001, max=100, precision=4,
                               unit="LENGTH")
    d: bpy.props.FloatProperty(name="distance from center of interior circle", default=0.050, min=0, max=100,
                               precision=4, unit="LENGTH")

    def execute(self, context):
        r = round(self.r, 6)
        R = round(self.R, 6)
        d = round(self.d, 6)
        Rmr = round(R - r, 6)  # R-r
        Rpr = round(R + r, 6)  # R +r
        Rpror = round(Rpr / r, 6)  # (R+r)/r
        Rmror = round(Rmr / r, 6)  # (R-r)/r
        maxangle = 2 * math.pi * np.lcm(round(self.R * 1000), round(self.r * 1000)) / (R * 1000)

        if self.typecurve == "hypo":
            xstring = str(Rmr) + "*cos(t)+" + str(d) + "*cos(" + str(Rmror) + "*t)"
            ystring = str(Rmr) + "*sin(t)-" + str(d) + "*sin(" + str(Rmror) + "*t)"
        else:
            xstring = str(Rpr) + "*cos(t)-" + str(d) + "*cos(" + str(Rpror) + "*t)"
            ystring = str(Rpr) + "*sin(t)-" + str(d) + "*sin(" + str(Rpror) + "*t)"

        print("x= " + str(xstring))
        print("y= " + str(ystring))
        print("maxangle " + str(maxangle))

        x = Expression(xstring, ["t"])  # make equation from string
        y = Expression(ystring, ["t"])  # make equation from string

        # build function to be passed to create parametric curve ()
        def f(t, offset: float = 0.0):
            c = (x(t), y(t), 0)
            return c

        iter = int(maxangle * 10)
        if iter > 10000:  # do not calculate more than 10000 points
            print("limiting calculatons to 10000 points")
            iter = 10000
        parametric.create_parametric_curve(f, offset=0.0, min=0, max=maxangle, use_cubic=True, iterations=iter)

        return {'FINISHED'}


class CamCustomCurve(bpy.types.Operator):
    """Object customCurve """  # by Alain Pelletier april 2021
    bl_idname = "object.customcurve"
    bl_label = "Create custom curve"
    bl_options = {'REGISTER', 'UNDO', 'PRESET'}

    xstring: StringProperty(name="X equation", description="Equation x=F(t)", default="t")
    ystring: StringProperty(name="Y equation", description="Equation y=F(t)", default="0")
    zstring: StringProperty(name="Z equation", description="Equation z=F(t)", default="0.05*sin(2*pi*4*t)")

    iteration: bpy.props.IntProperty(name="iteration", default=100, min=50, max=2000)
    maxt: bpy.props.FloatProperty(name="Wave ends at x", default=0.5, min=-3.0, max=3, precision=4, unit="LENGTH")
    mint: bpy.props.FloatProperty(name="Wave starts at x", default=0, min=-3.0, max=3, precision=4, unit="LENGTH")

    def execute(self, context):
        print("x= " + self.xstring)
        print("y= " + self.ystring)
        print("z= " + self.zstring)
        ex = Expression(self.xstring, ["t"])  # make equation from string
        ey = Expression(self.ystring, ["t"])  # make equation from string
        ez = Expression(self.zstring, ["t"])  # make equation from string

        # build function to be passed to create parametric curve ()
        def f(t, offset: float = 0.0):
            c = (ex(t), ey(t), ez(t))
            return c

        parametric.create_parametric_curve(f, offset=0.0, min=self.mint, max=self.maxt, use_cubic=True,
                                           iterations=self.iteration)

        return {'FINISHED'}

def triangle(i,T):
    s=""
    for n in range(i):
        if n % 2 != 0:
            e = (n-1)/2
            a = round(((-1)**e)/(n**2), 8)
            b = round(n*math.pi/(T/2), 8)
            if n > 1:
                s += '+'
            s += str(a)+"*sin("+str(b)+"*t) "
    return s
