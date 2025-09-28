# app.py
from flask import Flask, request, jsonify
from werkzeug.security import check_password_hash
import models
import auth
import os

app = Flask(__name__)

# SECRET_KEY fijo (en producción usa variable de entorno)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "clave_super_segura_123")

@app.route("/")
def home():
    return {"message": "Bienvenido a mi primera API con Flask y SQLite (Auth)"}

# POST /register
@app.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")
    email = data.get("email")

    if not username or not password:
        return jsonify({"error": "username y password son obligatorios"}), 400

    existing = models.get_user_by_username(username)
    if existing:
        return jsonify({"error": "El usuario ya existe"}), 400

    try:
        uid = models.create_user(username, password, email)
        return jsonify({"message": "Usuario creado", "id": uid}), 201
    except Exception as e:
        return jsonify({"error": "Error al crear usuario", "detail": str(e)}), 500

# POST /login
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "username y password son obligatorios"}), 400

    user = models.get_user_by_username(username)
    if not user:
        return jsonify({"error": "Credenciales inválidas"}), 401

    if not check_password_hash(user["password_hash"], password):
        return jsonify({"error": "Credenciales inválidas"}), 401

    token = auth.generate_token(user["id"], hours=24)
    return jsonify({"token": token})

# GET /profile (protegida)
@app.route("/profile", methods=["GET"])
@auth.token_required
def profile(user_id):
    user = models.get_user_by_id(user_id)
    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404
    return jsonify({"id": user["id"], "username": user["username"], "email": user["email"]})

# Nota: no inicializamos DB aquí al importar para facilitar tests
if __name__ == "__main__":
    # Solo al ejecutar server local inicializamos la BD
    models.init_db()
    app.run(debug=True)
