import asyncio
import inspect
import threading
import time
from functools import wraps


def rate_limit(seconds: int = 1):
    """
    Return a decorator that enforces at least `seconds` between consecutive calls.

    Args:
        seconds (int): Minimum number of seconds between calls. Default is 1 second.
    """

    def decorator(func):
        last_time = 0.0

        if inspect.iscoroutinefunction(func):
            lock = asyncio.Lock()

            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                nonlocal last_time

                async with lock:
                    elapsed = time.monotonic() - last_time

                    if elapsed < seconds:
                        await asyncio.sleep(seconds - elapsed)

                    result = await func(*args, **kwargs)
                    last_time = time.monotonic()

                    return result

            return async_wrapper

        else:
            lock = threading.Lock()

            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                nonlocal last_time

                with lock:
                    elapsed = time.monotonic() - last_time

                    if elapsed < seconds:
                        time.sleep(seconds - elapsed)

                    result = func(*args, **kwargs)
                    last_time = time.monotonic()

                    return result

            return sync_wrapper

    return decorator
