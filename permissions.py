"""
Module to handle user permissions.
"""
from flask import Blueprint, request, jsonify
from models import db, Permission
from flask_login import login_required, current_user

permissions_bp = Blueprint('permissions', __name__)

@permissions_bp.route('/files/<file_id>/users/<user_id>', methods=['POST'])
# @login_required
def grant_permission(file_id, user_id):
    data = request.json
    permission = Permission(
        file_id=file_id,
        user_id=user_id,
        can_read=data.get('can_read', True),
        can_write=data.get('can_write', False),
        can_delete=data.get('can_delete', False),
        can_share=data.get('can_share', False)
    )
    db.session.add(permission)
    db.session.commit()
    return jsonify({'message': 'Permission granted'}), 201

@permissions_bp.route('/files/<file_id>/users/<user_id>', methods=['DELETE'])
# @login_required
def revoke_permission(file_id, user_id):
    permission = Permission.query.filter_by(file_id=file_id, user_id=user_id).first()
    if permission:
        db.session.delete(permission)
        db.session.commit()
        return jsonify({'message': 'Permission revoked'}), 200
    return jsonify({'error': 'Permission not found'}), 404

def check_permission(user_id, file_id, permission_type):
    permission = Permission.query.filter_by(user_id=user_id, file_id=file_id).first()
    if not permission:
        return False
    return getattr(permission, permission_type, False)
