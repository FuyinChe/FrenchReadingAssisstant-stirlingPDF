from fastapi.testclient import TestClient

from french_reader.main import app
from french_reader.plugin_version import get_plugin_version_info, get_plugin_version_string

client = TestClient(app)


def test_plugin_version_string_matches_json():
    info = get_plugin_version_info()
    assert get_plugin_version_string() == info["version"]
    assert info["name"] == "french-reading-assistant"
    assert "displayName" in info


def test_version_endpoint_shape():
    response = client.get("/french-reader/version")
    assert response.status_code == 200
    payload = response.json()
    assert payload["version"] == get_plugin_version_string()


def test_health_includes_plugin():
    response = client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["plugin"]["version"] == get_plugin_version_string()
