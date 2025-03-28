"""Fabex 'version_utils.py' © 2012 Vilem Novak
"""


# Import OpencamLib
# Return available OpenCamLib version on success, None otherwise
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
