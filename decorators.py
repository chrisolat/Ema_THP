"""
custom decorator to check permissions
"""
from functools import wraps
from flask import jsonify
from flask_login import current_user
from permissions import check_permission

def permission_required(permission_type):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            file_id = kwargs.get('file_id')
            if not check_permission(current_user.user_id, file_id, permission_type):
                return jsonify({'error': 'Access denied'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator
