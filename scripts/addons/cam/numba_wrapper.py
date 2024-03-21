try:
    from numba import jit, prange
    print("numba: yes")
except:
    print("numba: no")

    def jit(f=None, *args, **kwargs):
        def decorator(func):
            return func

        if callable(f):
            return f
        else:
            return decorator
    prange = range
