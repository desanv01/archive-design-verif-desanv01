"""Task 6: a decorator that wraps a function."""

from functools import wraps


def trace_call(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"Starting {func.__name__}")
        result = func(*args, **kwargs)
        print(f"Finished {func.__name__} with result={result}")
        return result

    return wrapper


@trace_call
def bitwise_xor(a, b):
    return a ^ b


bitwise_xor(0b1100, 0b1010)
