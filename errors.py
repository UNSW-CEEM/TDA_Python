import functools
from flask import jsonify


def parse_to_user_and_log(logger):
    def actual_decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if logger is not None:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    data = {'error': str(e)}
                    logger.exception(e)
                    return jsonify(data)
            else:
                return func(*args, **kwargs)
        return wrapper
    return actual_decorator


def log(logger):
    def actual_decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if logger is not None:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    data = {'message': str(e)}
                    logger.exception(e)
            else:
                func(*args, **kwargs)
        return wrapper
    return actual_decorator
