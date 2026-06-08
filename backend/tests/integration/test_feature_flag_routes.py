from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)
ADMIN_HEADERS = {"X-Demo-User": "admin_user", "X-Demo-Role": "ADMIN"}
ROOT = Path(__file__).resolve().parents[3]
STORES = [
    ROOT / "data" / "synthetic" / "admin_config.json",
    ROOT / "data" / "synthetic" / "admin_config_history.json",
]


@pytest.fixture(autouse=True)
def preserve_admin_config_stores():
    originals = {path: path.read_text(encoding="utf-8") if path.exists() else "{}" for path in STORES}
    yield
    for path, content in originals.items():
        path.write_text(content, encoding="utf-8")


def test_feature_flag_routes_list_and_update() -> None:
    listed = client.get("/api/v1/admin/feature-flags", headers=ADMIN_HEADERS)
    updated = client.patch("/api/v1/admin/feature-flags/FEATURE_ENABLE_COST_DASHBOARD", headers=ADMIN_HEADERS, json={"enabled": False, "comment": "test"})

    assert listed.status_code == 200
    assert any(flag["key"] == "FEATURE_ENABLE_COST_DASHBOARD" for flag in listed.json())
    assert updated.status_code == 200
    assert updated.json()["value"] is False
