import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app, get_db
from database import Base

# Base de datos de prueba única para tu dominio
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_clean.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def session(db):
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()

# Fixture con datos realistas para Limpieza (contrato)
@pytest.fixture
def sample_contrato_data():
    return {
        "cliente": "Empresa Aseo Colombia",
        "direccion": "Cra 10 #20-30 Bogotá",
        "fecha_inicio": "2025-09-01",
        "duracion_meses": 6,
        "tipo_servicio": "empresarial",
        "valor": 2500000,
        "observaciones": "Incluye limpieza profunda mensual"
    }

@pytest.fixture
def auth_headers(client):
    response = client.post("/auth/register", json={
        "username": "admin_clean",
        "password": "test123",
        "role": "admin_limpieza"
    })
    login_response = client.post("/auth/login", data={
        "username": "admin_clean",
        "password": "test123"
    })
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
