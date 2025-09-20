import pytest

class TestLimpiezaAPI:
    """Tests específicos para contratos de limpieza"""

    def test_create_contrato_success(self, client, sample_contrato_data, auth_headers):
        response = client.post("/clean_contratos/", json=sample_contrato_data, headers=auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["cliente"] == sample_contrato_data["cliente"]
        assert data["valor"] == sample_contrato_data["valor"]

    def test_create_contrato_duplicate(self, client, sample_contrato_data, auth_headers):
        client.post("/clean_contratos/", json=sample_contrato_data, headers=auth_headers)
        response = client.post("/clean_contratos/", json=sample_contrato_data, headers=auth_headers)
        assert response.status_code == 400
        assert "ya existe" in response.json()["detail"].lower()

    def test_get_contrato_by_id(self, client, sample_contrato_data, auth_headers):
        created = client.post("/clean_contratos/", json=sample_contrato_data, headers=auth_headers).json()
        response = client.get(f"/clean_contratos/{created['id']}", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["id"] == created["id"]

    def test_update_contrato_complete(self, client, sample_contrato_data, auth_headers):
        created = client.post("/clean_contratos/", json=sample_contrato_data, headers=auth_headers).json()
        update_data = {**sample_contrato_data, "valor": 3000000, "duracion_meses": 12}
        response = client.put(f"/clean_contratos/{created['id']}", json=update_data, headers=auth_headers)
        assert response.status_code == 200
        updated = response.json()
        assert updated["valor"] == 3000000
        assert updated["duracion_meses"] == 12

    def test_delete_contrato_success(self, client, sample_contrato_data, auth_headers):
        created = client.post("/clean_contratos/", json=sample_contrato_data, headers=auth_headers).json()
        response = client.delete(f"/clean_contratos/{created['id']}", headers=auth_headers)
        assert response.status_code == 200
        get_response = client.get(f"/clean_contratos/{created['id']}", headers=auth_headers)
        assert get_response.status_code == 404

    def test_contrato_business_rules(self, client, auth_headers):
        # Contratos no pueden durar más de 12 meses ni tener valor negativo
        invalid_data = {
            "cliente": "Empresa XYZ",
            "direccion": "Calle 45 #67-89",
            "fecha_inicio": "2025-09-01",
            "duracion_meses": 15,
            "tipo_servicio": "residencial",
            "valor": -500000,
            "observaciones": "Prueba con valores inválidos"
        }
        response = client.post("/clean_contratos/", json=invalid_data, headers=auth_headers)
        assert response.status_code == 422
