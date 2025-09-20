class TestLimpiezaAuth:
    def test_register_limpieza_user(self, client):
        data = {
            "username": "usuario_clean_test",
            "password": "password123",
            "role": "operario_limpieza"
        }
        response = client.post("/auth/register", json=data)
        assert response.status_code == 201

    def test_login_limpieza_user(self, client):
        client.post("/auth/register", json={
            "username": "admin_clean",
            "password": "admin123",
            "role": "admin_limpieza"
        })
        response = client.post("/auth/login", data={
            "username": "admin_clean",
            "password": "admin123"
        })
        assert response.status_code == 200
        assert "access_token" in response.json()

    def test_create_contrato_requires_auth(self, client, sample_contrato_data):
        response = client.post("/clean_contratos/", json=sample_contrato_data)
        assert response.status_code == 401

    def test_admin_can_delete_contrato(self, client, sample_contrato_data):
        # Crear admin
        client.post("/auth/register", json={
            "username": "admin_clean",
            "password": "admin123",
            "role": "admin_limpieza"
        })
        login = client.post("/auth/login", data={
            "username": "admin_clean",
            "password": "admin123"
        })
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        created = client.post("/clean_contratos/", json=sample_contrato_data, headers=headers).json()
        response = client.delete(f"/clean_contratos/{created['id']}", headers=headers)
        assert response.status_code == 200
