"""Fabex 'async_utils.py' © 2012 Vilem Novak
"""

import types


@types.coroutine
def progress_async(text, n=None, value_type="%"):
    """Report progress during script execution for background operations.

    This function is designed to provide progress updates while a script is
    running, particularly for background operations. It yields a dictionary
    containing the progress information, which includes the text description
    of the progress, an optional numeric value, and the type of value being
    reported. If an exception is thrown during the operation, it will be
    raised for handling.

    Args:
        text (str): A message indicating the current progress.
        n (optional): An optional numeric value representing the progress.
        value_type (str?): A string indicating the type of value being reported (default is '%').

    Raises:
        Exception: If an exception is thrown during the operation.
    """
    # (f"Progress:{text} {n}{value_type}\n")

    throw_exception = yield ("Progress:", {"text": text, "n": n, "value_type": value_type})
    if throw_exception is not None:
        raise throw_exception
