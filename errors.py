from flask import jsonify
import traceback


def parse_to_user(f, logger):
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            data = {}
            data['message'] = str(e) + traceback.format_exc()
            logger.exception(error)
            return jsonify(data)
    return wrapper