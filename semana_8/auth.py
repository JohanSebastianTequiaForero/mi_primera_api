# auth.py
from functools import wraps
from flask import request, jsonify, current_app
import jwt
from datetime import datetime, timedelta
from werkzeug.security import check_password_hash

def generate_token(user_id: int, hours: int = 24):
    """Genera un JWT firmado con SECRET_KEY del app context."""
    secret = current_app.config.get("SECRET_KEY")
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(hours=hours)
    }
    token = jwt.encode(payload, secret, algorithm="HS256")
    # PyJWT v2 devuelve str; en v1 puede devolver bytes. Aseguramos str.
    if isinstance(token, bytes):
        token = token.decode("utf-8")
    return token

def decode_token(token: str):
    secret = current_app.config.get("SECRET_KEY")
    payload = jwt.decode(token, secret, algorithms=["HS256"])
    return payload  # contiene user_id y exp

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", None)
        if not auth_header:
            return jsonify({"error": "Authorization header missing"}), 401
        parts = auth_header.split()
        if parts[0].lower() != "bearer" or len(parts) != 2:
            return jsonify({"error": "Authorization header must be: Bearer <token>"}), 401
        token = parts[1]
        try:
            payload = decode_token(token)
            user_id = payload.get("user_id")
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
        # inyectamos user_id como primer argumento de la función protegida
        return f(user_id, *args, **kwargs)
    return decorated
