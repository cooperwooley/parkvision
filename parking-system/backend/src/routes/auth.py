from flask import Blueprint, request, jsonify, session
from werkzeug.security import check_password_hash
from datetime import datetime
from models.user import User
from extensions import db

auth_bp = Blueprint('auth', __name__)

"""
    Log in an admin user.

    Args:
        None (uses request data via Flask)

    Returns:
        Response: JSON response indicating success or failure,
                  with a token if successful.
"""

@auth_bp.route('/admin/login', methods=['POST'])
def admin_login():
    data = request.json
    username_or_email = data.get('username_or_email')
    password = data.get('password')

    if not username_or_email or not password:
        return jsonify({'error': 'Username/email and password required'}), 400

    user = User.query.filter(
        (User.username == username_or_email) | (User.email == username_or_email)
    ).first()

    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({'error': 'Invalid credentials'}), 401

    if not user.is_admin:
        return jsonify({'error': 'Access denied'}), 403

    # Store user info in session (or use JWT/token if applicable)
    session['user_id'] = user.id
    session['is_admin'] = True

    user.last_login = datetime.now(datetime.timezone.utc)
    db.session.commit()

    return jsonify({'message': f'Welcome admin {user.username}'}), 200
