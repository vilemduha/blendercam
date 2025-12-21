"""Fabex 'version_utils.py' © 2012 Vilem Novak"""

from .. import __package__ as base_package


def get_fabex_version():
    """Return the version of the Fabex Extension.

    This function checks for fabex in the module list and reads and
    returns the number found in the 'version' file.

    Returns:
        str or None: The version of Fabex if available, None otherwise.
    """
    import addon_utils

    for module in addon_utils.modules():
        if module.__name__ == base_package:
            version = str(module.bl_info.get("version", (-1, -1, -1)))
            version = version.replace(", ", ".")
            version = version[1 : len(version) - 1]
            return version


def get_numba_version():
    """Return the version of the numba library.

    This function attempts to import the numba library and returns its
    version. If the library is not available, it will return None.

    Returns:
        str or None: The version of numba if available, None otherwise.
    """
    try:
        import numba
    except ImportError:
        return
    version = str(numba.version_info.full)
    version = version.replace(", ", ".")
    version = version[1 : len(version) - 1]
    return version


def get_llvmlite_version():
    """Return the version of the llvmlite library.

    This function attempts to import the llvmlite library and returns its
    version. If the library is not available, it will return None.

    Returns:
        str or None: The version of llvmlite if available, None otherwise.
    """
    try:
        import llvmlite
    except ImportError:
        return
    version = str(llvmlite.binding.llvm_version_info)
    version = version.replace(", ", ".")
    version = version[1 : len(version) - 1]
    return version


def opencamlib_version():
    """Return the version of the OpenCamLib library.

    This function attempts to import the OpenCamLib library and returns its
    version. If the library is not available, it will return None. The
    function first tries to import the library using the name 'ocl', and if
    that fails, it attempts to import it using 'opencamlib' as an alias. If
    both imports fail, it returns None.

    Returns:
        str or None: The version of OpenCamLib if available, None otherwise.
    """

    try:
        import ocl
    except ImportError:
        try:
            import opencamlib as ocl
        except ImportError as e:
            return
    return ocl.version()


# Import Shapely
# Return available OpenCamLib version on success, None otherwise
def shapely_version():
    """Return the version of the Shapely library.

    This function attempts to import the Shapely library and returns its
    version. If the library is not available, it will return None.

    Returns:
        str or None: The version of Shapely if available, None otherwise.
    """

    try:
        import shapely
    except ImportError:
        return
    return shapely.__version__
