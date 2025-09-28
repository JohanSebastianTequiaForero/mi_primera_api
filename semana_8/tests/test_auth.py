# tests/test_auth.py
import os
import tempfile
import pytest
import models

# Import app lazily
import app as app_module

@pytest.fixture
def client(tmp_path, monkeypatch):
    # Crear DB temporal para tests
    test_db = tmp_path / "test_database.db"
    # Forzamos models.DB_NAME a archivo temporal
    monkeypatch.setattr(models, "DB_NAME", str(test_db))
    # Inicializar esquema en test DB
    models.init_db()

    app = app_module.app
    app.config["TESTING"] = True
    # usar el mismo SECRET_KEY en tests
    app.config["SECRET_KEY"] = "clave_super_segura_123"
    with app.test_client() as client:
        yield client

def test_register_login_profile(client):
    # register
    rv = client.post("/register", json={"username": "testuser", "password": "pass123", "email": "t@example.com"})
    assert rv.status_code == 201
    data = rv.get_json()
    assert "id" in data

    # login
    rv = client.post("/login", json={"username": "testuser", "password": "pass123"})
    assert rv.status_code == 200
    data = rv.get_json()
    assert "token" in data
    token = data["token"]

    # profile with token
    rv = client.get("/profile", headers={"Authorization": f"Bearer {token}"})
    assert rv.status_code == 200
    profile = rv.get_json()
    assert profile["username"] == "testuser"
    assert profile["email"] == "t@example.com"

def test_register_duplicate(client):
    rv = client.post("/register", json={"username": "dup", "password": "p"})
    assert rv.status_code == 201
    rv2 = client.post("/register", json={"username": "dup", "password": "p"})
    assert rv2.status_code == 400
