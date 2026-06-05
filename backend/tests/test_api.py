import os
from pathlib import Path

TEST_DB_PATH = Path("test_linguaflow.db")
if TEST_DB_PATH.exists():
    TEST_DB_PATH.unlink()

os.environ.setdefault("DATABASE_URL", "sqlite:///./test_linguaflow.db")

from fastapi.testclient import TestClient

from app.main import app


def test_health_endpoint() -> None:
    with TestClient(app) as client:
        response = client.get("/api/health")
        assert response.status_code == 200
        payload = response.json()
        assert payload["status"] == "ok"


def test_terms_endpoint_lists_seed_data() -> None:
    with TestClient(app) as client:
        response = client.get("/api/terms")
        assert response.status_code == 200
        data = response.json()
        assert any(item["source"] == "Remote Sensing" for item in data)


def test_create_and_delete_term() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/api/terms",
            json={"domain": "General", "source": "Test Term", "target": "测试术语"},
        )
        assert response.status_code == 201
        term_id = response.json()["id"]

        delete_response = client.delete(f"/api/terms/{term_id}")
        assert delete_response.status_code == 200
        assert delete_response.json()["deleted"] == 1
