from unittest import TestCase

import bpy

from .utils import (
    activate_dependencies,
    activate_engine,
    get_modules,
    install_extension,
    zip_extension,
)


class AddonDependencyTest(TestCase):
    """Test Addon Dependencies - Curve Tools, Simplify Curves+, STL Format (Legacy), Extra Curve Objectes
    Sets Online Access to True and downloads the required addons.
    Individual test functions check for each addon in Preferences.
    """

    @classmethod
    def setUpClass(self):
        activate_dependencies(self)
        get_modules(self)

    def test_curve_tools(self):
        """Check for Curve Tools addon"""
        self.assertIn(
            "bl_ext.blender_org.curve_tools",
            self.modules,
        )

    def test_simplify_curves_plus(self):
        """Check for Simplify Curves Plus addon"""
        self.assertIn(
            "bl_ext.blender_org.simplify_curves_plus",
            self.modules,
        )

    def test_stl_format_legacy(self):
        """Check for STL Format Legacy addon"""
        self.assertIn(
            "bl_ext.blender_org.stl_format_legacy",
            self.modules,
        )

    def test_extra_curve_objectes(self):
        self.assertIn(
            "bl_ext.blender_org.extra_curve_objectes",
            self.modules,
        )


class FabexInstallTest(TestCase):
    """Test Installation of addon, uses the zip created in the __init__"""

    @classmethod
    def setUpClass(self):
        zip_extension()
        install_extension()
        get_modules(self)

    def test_install(self):
        self.assertIn(
            "bl_ext.user_default.fabex",
            self.modules,
        )

    def test_disable(self):
        bpy.ops.preferences.addon_disable(module="bl_ext.user_default.fabex")
        get_modules(self)
        self.assertNotIn(
            "bl_ext.user_default.fabex",
            self.modules,
        )

    def test_enable(self):
        bpy.ops.preferences.addon_enable(module="bl_ext.user_default.fabex")
        get_modules(self)
        self.assertIn(
            "bl_ext.user_default.fabex",
            self.modules,
        )

    def test_engine(self):
        activate_engine(self)
        self.assertTrue(self.engine == "FABEX_RENDER")
