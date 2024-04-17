from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt, jwt_required, get_jwt_identity, verify_jwt_in_request
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import db, User, RevokedToken, Role
from app.extensions import jwt
from functools import wraps
from sqlalchemy.exc import SQLAlchemyError


auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['POST'])
# @cross_origin(origins="*", support_credentials=True)
def register():
    email = request.json.get('email', None)
    password = request.json.get('password', None)
    
    if email is None or password is None:
        return jsonify({"msg": "Missing email or password"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"msg": "Email already registered"}), 400
    
    # Pobranie roli 'user'
    user_role = Role.query.filter_by(name='user').first()
    if not user_role:
        # Jeśli rola nie istnieje, można ją utworzyć (zależy od polityki aplikacji)
        user_role = Role(name='user')
        db.session.add(user_role)
        # nie zatwierdzamy jeszcze sesji, zrobimy to później

    hashed_password = generate_password_hash(password)
    new_user = User(email=email, hashed_password=hashed_password, roles=[user_role])

    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"msg": "User created successfully"}), 201
    except SQLAlchemyError as e:
        db.session.rollback()  # cofnięcie zmian w przypadku błędu
        return jsonify({"msg": "Failed to register user", "error": str(e)}), 500

@auth.route('/login', methods=['POST'])
def login():
    email = request.json.get('email', None)
    password = request.json.get('password', None)
    user = User.query.filter_by(email=email).first()
    if user is None or not check_password_hash(user.hashed_password, password):
        return jsonify({"msg": "Bad username or password"}), 401

    # Zbieranie ról użytkownika do dodania do tokena
    roles = [role.name for role in user.roles]

    # Dodanie roli do claims tokena
    additional_claims = {'roles': roles}
    access_token = create_access_token(identity=email, additional_claims=additional_claims)
    refresh_token = create_refresh_token(identity=email, additional_claims=additional_claims)

    return jsonify(access_token=access_token, refresh_token=refresh_token)

@auth.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user)
    return jsonify(access_token=new_access_token)

@auth.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    jti = get_jwt()['jti']  # JTI to "JWT ID", unikalny identyfikator dla każdego tokena
    # Tutaj dodaj jti do bazy danych lub cache'u jako 'wyrejestrowany'
    revoked_token = RevokedToken(jti=jti)
    db.session.add(revoked_token)
    db.session.commit()
    return jsonify({"msg": "Successfully logged out"}), 200

@jwt.token_in_blocklist_loader
def check_if_token_in_blacklist(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    return RevokedToken.is_jti_blacklisted(jti)

def require_role(role):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            # print(claims)
            if claims.get('roles') and role in claims['roles']:
                return fn(*args, **kwargs)
            else:
                return jsonify({"msg": "Insufficient permissions"}), 403
        return decorator
    return wrapper