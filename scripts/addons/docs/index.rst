.. BlenderCAM documentation master file, created by
   sphinx-quickstart on Sun Sep  8 08:23:06 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Fabex's Documentation!
==========================================

This site serves as an introduction to Fabex, a free and open source extension for Blender, the free and open-source 3D app.

Fabex allows you to generate toolpaths and gcode files based on 3D objects or 2D Images within Blender.

These files can then be sent to a CNC machine to cut your designs!

User Guide
*****************

.. toctree::
   :maxdepth: 1

   fun

This section is for new users, containing basic info on how to install and use the extension.

Developer Guide
******************

.. toctree::
   :maxdepth: 1

   overview
   styleguide
   testing
   workflows

This section is for people who want to contribute code to BlenderCAM, people who want to modify the addon for their needs, or anyone who simply want to better understand what is happening 'under the hood'.

:doc:`overview` offers a guide to the addon files and how they relate to one another.

:doc:`styleguide` gives tips on editors, linting, formatting etc.

:doc:`testing` has information on how to run and contribute to the Test Suite.

:doc:`workflows` contains an explanation of how the addon, testing and documentation are automated via Github Actions.

:doc: `fun` is fun