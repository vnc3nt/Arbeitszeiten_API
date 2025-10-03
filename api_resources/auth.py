from flask import request
from flask_restful import Resource, reqparse
from models import db, users, token, update_expire_time
from time import time
import hashlib
import secrets
from functools import wraps
from constants import USERNAME_REGEX
from sqlalchemy import func

def hash_pw(password: str) -> str:
    """Hash password using SHA512"""
    return hashlib.sha512(bytes(password, encoding="utf-8")).hexdigest()

def token_required(f):
    """Decorator to require valid token for API endpoints"""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return {'message': 'Token fehlt'}, 401
        
        try:
            # Expected format: "Bearer <token>"
            token_string = auth_header.split(' ')[1] if ' ' in auth_header else auth_header
        except IndexError:
            return {'message': 'Ungültiges Token-Format'}, 401
        
        # Check if token exists and is valid
        user_token = db.session.query(token).filter(token.token == token_string).first()
        
        if not user_token:
            return {'message': 'Ungültiges Token'}, 401
        
        # Check if token is expired
        if user_token.expiretime < time():
            db.session.delete(user_token)
            db.session.commit()
            return {'message': 'Token abgelaufen'}, 401
        
        # Update token expiration time
        user_token.expiretime = update_expire_time()
        db.session.commit()
        
        # Pass user_id to the decorated function
        return f(user_id=user_token.userid, *args, **kwargs)
    
    return decorated


class AuthRegister(Resource):
    """User registration endpoint"""
    
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str, required=True, help='Benutzername ist erforderlich')
        parser.add_argument('password', type=str, required=True, help='Passwort ist erforderlich')
        args = parser.parse_args()
        
        username = args['username']
        password = args['password']
        
        # Validate username format
        if USERNAME_REGEX.fullmatch(username) is not None:
            return {'message': 'Benutzername darf keine Leerzeichen enthalten'}, 400
        
        # Check if username already exists
        existing_user = db.session.query(users).filter(users.username == username).first()
        if existing_user:
            return {'message': 'Benutzername existiert bereits'}, 409
        
        # Validate password length
        if len(password) < 8:
            return {'message': 'Passwort muss mindestens 8 Zeichen lang sein'}, 400
        
        # Create new user
        last_id = db.session.query(func.max(users.id)).scalar()
        new_user_id = (last_id or 0) + 1
        
        new_user = users(
            id=new_user_id,
            username=username,
            password=hash_pw(password)
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        return {
            'message': 'Benutzer erfolgreich registriert',
            'user_id': new_user_id,
            'username': username
        }, 201


class AuthLogin(Resource):
    """User login endpoint"""
    
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str, required=True, help='Benutzername ist erforderlich')
        parser.add_argument('password', type=str, required=True, help='Passwort ist erforderlich')
        args = parser.parse_args()
        
        username = args['username']
        password = args['password']
        
        # Find user
        user = db.session.query(users).filter(users.username == username).first()
        
        if not user:
            return {'message': 'Ungültige Anmeldedaten'}, 401
        
        # Check password
        if user.password != hash_pw(password):
            return {'message': 'Ungültige Anmeldedaten'}, 401
        
        # Clean up expired tokens
        db.session.query(token).filter(token.expiretime < time()).delete()
        
        # Create new token
        new_token = token(
            userid=user.id,
            token=secrets.token_urlsafe(96)
        )
        
        db.session.add(new_token)
        db.session.commit()
        
        return {
            'message': 'Erfolgreich angemeldet',
            'token': new_token.token,
            'user_id': user.id,
            'username': user.username
        }, 200


class AuthLogout(Resource):
    """User logout endpoint"""
    
    @token_required
    def post(self, user_id):
        auth_header = request.headers.get('Authorization')
        token_string = auth_header.split(' ')[1] if ' ' in auth_header else auth_header
        
        # Delete token
        user_token = db.session.query(token).filter(token.token == token_string).first()
        if user_token:
            db.session.delete(user_token)
            db.session.commit()
        
        return {'message': 'Erfolgreich abgemeldet'}, 200


class AuthUser(Resource):
    """Get current user information"""
    
    @token_required
    def get(self, user_id):
        user = db.session.query(users).filter(users.id == user_id).first()
        
        if not user:
            return {'message': 'Benutzer nicht gefunden'}, 404
        
        return {
            'user_id': user.id,
            'username': user.username
        }, 200


class AuthChangePassword(Resource):
    """Change user password"""
    
    @token_required
    def post(self, user_id):
        parser = reqparse.RequestParser()
        parser.add_argument('current_password', type=str, required=True, help='Aktuelles Passwort ist erforderlich')
        parser.add_argument('new_password', type=str, required=True, help='Neues Passwort ist erforderlich')
        args = parser.parse_args()
        
        current_password = args['current_password']
        new_password = args['new_password']
        
        # Get user
        user = db.session.query(users).filter(users.id == user_id).first()
        
        if not user:
            return {'message': 'Benutzer nicht gefunden'}, 404
        
        # Verify current password
        if user.password != hash_pw(current_password):
            return {'message': 'Aktuelles Passwort ist falsch'}, 401
        
        # Validate new password
        if len(new_password) < 8:
            return {'message': 'Neues Passwort muss mindestens 8 Zeichen lang sein'}, 400
        
        # Update password
        user.password = hash_pw(new_password)
        
        # Delete all user tokens (force re-login)
        db.session.query(token).filter(token.userid == user_id).delete()
        
        db.session.commit()
        
        return {'message': 'Passwort erfolgreich geändert'}, 200


class AuthChangeUsername(Resource):
    """Change username"""
    
    @token_required
    def post(self, user_id):
        parser = reqparse.RequestParser()
        parser.add_argument('new_username', type=str, required=True, help='Neuer Benutzername ist erforderlich')
        args = parser.parse_args()
        
        new_username = args['new_username']
        
        # Validate username format
        if USERNAME_REGEX.fullmatch(new_username) is not None:
            return {'message': 'Benutzername darf keine Leerzeichen enthalten'}, 400
        
        # Check if username already exists
        existing_user = db.session.query(users).filter(users.username == new_username).first()
        if existing_user and existing_user.id != user_id:
            return {'message': 'Benutzername existiert bereits'}, 409
        
        # Update username
        user = db.session.query(users).filter(users.id == user_id).first()
        if not user:
            return {'message': 'Benutzer nicht gefunden'}, 404
        
        user.username = new_username
        db.session.commit()
        
        return {
            'message': 'Benutzername erfolgreich geändert',
            'username': new_username
        }, 200


class AuthDeleteAccount(Resource):
    """Delete user account"""
    
    @token_required
    def delete(self, user_id):
        parser = reqparse.RequestParser()
        parser.add_argument('password', type=str, required=True, help='Passwort ist erforderlich')
        args = parser.parse_args()
        
        password = args['password']
        
        # Get user
        user = db.session.query(users).filter(users.id == user_id).first()
        
        if not user:
            return {'message': 'Benutzer nicht gefunden'}, 404
        
        # Verify password
        if user.password != hash_pw(password):
            return {'message': 'Falsches Passwort'}, 401
        
        # Delete all user data
        from models import data, category
        
        db.session.query(data).filter(data.userid == user_id).delete()
        db.session.query(token).filter(token.userid == user_id).delete()
        db.session.query(category).filter(category.userid == user_id).delete()
        db.session.query(users).filter(users.id == user_id).delete()
        
        db.session.commit()
        
        return {'message': 'Account erfolgreich gelöscht'}, 200
