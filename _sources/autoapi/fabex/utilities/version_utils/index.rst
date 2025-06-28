fabex.utilities.version_utils
=============================

.. py:module:: fabex.utilities.version_utils

.. autoapi-nested-parse::

   Fabex 'version_utils.py' © 2012 Vilem Novak



Functions
---------

.. autoapisummary::

   fabex.utilities.version_utils.opencamlib_version
   fabex.utilities.version_utils.shapely_version


Module Contents
---------------

.. py:function:: opencamlib_version()

   Return the version of the OpenCamLib library.

   This function attempts to import the OpenCamLib library and returns its
   version. If the library is not available, it will return None. The
   function first tries to import the library using the name 'ocl', and if
   that fails, it attempts to import it using 'opencamlib' as an alias. If
   both imports fail, it returns None.

   :returns: The version of OpenCamLib if available, None otherwise.
   :rtype: str or None


.. py:function:: shapely_version()

   Return the version of the Shapely library.

   This function attempts to import the Shapely library and returns its
   version. If the library is not available, it will return None.

   :returns: The version of Shapely if available, None otherwise.
   :rtype: str or None


