import functools
import types


def clean_output(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        output = func(*args, **kwargs)
        cleaned = output.filter(regex="^((?!Unnamed|level|index).)*$")
        return cleaned
    return wrapper
