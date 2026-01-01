fabex.operators.compatibility_op
================================

.. py:module:: fabex.operators.compatibility_op


Classes
-------

.. autoapisummary::

   fabex.operators.compatibility_op.Fabex_Compatibility_Panel


Module Contents
---------------

.. py:class:: Fabex_Compatibility_Panel

   Bases: :py:obj:`bpy.types.Operator`


   .. py:attribute:: bl_idname
      :value: 'fabex.compatibility'



   .. py:attribute:: bl_label
      :value: ''



   .. py:attribute:: os


   .. py:attribute:: architecture


   .. py:attribute:: python_version


   .. py:attribute:: python_executable
      :value: '/opt/hostedtoolcache/Python/3.11.14/x64/bin/python'



   .. py:attribute:: correct_python_version
      :value: '3.11.13'



   .. py:attribute:: string_1
      :value: Multiline-String

      .. raw:: html

         <details><summary>Show Value</summary>

      .. code-block:: python

         """Hello and welcome to Fabex!
         This popup will check your system for compatibility and assist with issues in the installation process."""

      .. raw:: html

         </details>




   .. py:attribute:: string_2
      :value: Multiline-String

      .. raw:: html

         <details><summary>Show Value</summary>

      .. code-block:: python

         """Fabex officially supports Blender 4.2+ using Python 3.11.13.
         We recommend downloading Blender from blender.org so it comes with the correct version of Python."""

      .. raw:: html

         </details>




   .. py:attribute:: string_3
      :value: Multiline-String

      .. raw:: html

         <details><summary>Show Value</summary>

      .. code-block:: python

         """Linux users may install Blender with a Package Manager then find that Fabex will not install / work correctly.
         apt, dnf, pacman, zypper etc. will provide copies of Blender that use your system's Python install.
         If your Python version is not ⚠️⚠️⚠️ EXACTLY 3.11.13 ⚠️⚠️⚠️ then Fabex will not install / work correctly.
             """

      .. raw:: html

         </details>




   .. py:attribute:: string_4
      :value: Multiline-String

      .. raw:: html

         <details><summary>Show Value</summary>

      .. code-block:: python

         """                OS: Uninferable
         Architecture: Uninferable
                 Blender: Uninferable
                  Python: Uninferable
               Location: /opt/hostedtoolcache/Python/3.11.14/x64/bin/python"""

      .. raw:: html

         </details>




   .. py:attribute:: compatible


   .. py:attribute:: title
      :type:  StringProperty(default='Fabex Compatibility Check')


   .. py:attribute:: text_1
      :type:  StringProperty(default=string_1)


   .. py:attribute:: text_2
      :type:  StringProperty(default=string_2)


   .. py:attribute:: text_3
      :type:  StringProperty(default=string_3)


   .. py:attribute:: text_4
      :type:  StringProperty(default=string_4)


   .. py:method:: execute(context)


   .. py:method:: invoke(context, event)


   .. py:method:: draw(context)


