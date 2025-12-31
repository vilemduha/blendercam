"""Fabex 'numba_utils.py'

Patch to ensure functions will run if numba is unavailable.
"""

from .logging_utils import log

try:
    from numba import jit, prange

    log.info("Numba library is available.")
except:
    log.info("Numba library is not installed.")

    def jit(f=None, *args, **kwargs):
        def decorator(func):
            return func

        if callable(f):
            return f
        else:
            return decorator

    prange = range
