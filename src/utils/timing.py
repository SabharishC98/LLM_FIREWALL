"""
Utility: Timing helpers.
"""

import time
from contextlib import contextmanager


@contextmanager
def timer():
    """
    Context manager that tracks elapsed time.
    
    Usage:
        with timer() as t:
            do_something()
        print(f"Took {t.elapsed_ms}ms")
    """
    t = Timer()
    t.start()
    try:
        yield t
    finally:
        t.stop()


class Timer:
    """Simple high-resolution timer."""
    
    def __init__(self):
        self._start: float = 0
        self._end: float = 0

    def start(self):
        self._start = time.perf_counter()

    def stop(self):
        self._end = time.perf_counter()

    @property
    def elapsed_ms(self) -> float:
        end = self._end if self._end else time.perf_counter()
        return round((end - self._start) * 1000, 2)
