"""Fabex 'numba_utils.py'

Patch to ensure functions will run if numba is unavailable.
"""

try:
    from numba import jit, prange

    print("Numba library is available.")
except:
    print("Numba library is not installed.")

    def jit(f=None, *args, **kwargs):
        def decorator(func):
            return func

        if callable(f):
            return f
        else:
            return decorator

    prange = range
