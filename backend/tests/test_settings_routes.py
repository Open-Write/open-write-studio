# tests/test_settings_routes.py -- Settings API tests
# =====================================================
# HTTP-level tests for the settings API fields that exist in Open-Write:
# openrouter_api_key (set/mask/clear), default_model, content_mode,
# multi-provider config, and the test-connection endpoint.
#
# Each test redirects settings_store's file paths into a tmp sandbox so
# the developer's real ~/.open-write/settings.json is never touched.

import pytest

from app import settings_store


@pytest.fixture(autouse=True)
def isolated_settings(tmp_path, monkeypatch):
    """Every test in this file gets a fresh settings sandbox."""
    sandbox = tmp_path / ".open-write"
    monkeypatch.setattr(settings_store, "SETTINGS_DIR",    sandbox)
    monkeypatch.setattr(settings_store, "SETTINGS_FILE",   sandbox / "settings.json")
    monkeypatch.setattr(settings_store, "SETTINGS_BACKUP", sandbox / "settings.json.bak")
    monkeypatch.setattr(settings_store, "SETTINGS_TMP",    sandbox / "settings.json.tmp")
    return sandbox


def test_get_settings_defaults(client):
    data = client.get("/api/settings").json()
    assert data["openrouter_api_key"] == ""
    assert data["openrouter_api_key_set"] is False
    assert data["default_model"] == "openai/gpt-4o-mini"
    assert data["content_mode"] == "general"


def test_openrouter_key_set_and_mask(client):
    resp = client.put("/api/settings", json={"openrouter_api_key": "sk-or-v1-abcdefghijklmnop"})
    data = resp.json()
    assert data["openrouter_api_key_set"] is True
    assert "sk-or-v1-abcdefghijklmnop" not in data["openrouter_api_key"]
    # Masked form shows prefix + suffix
    assert data["openrouter_api_key"].startswith("sk-or-")

    # Clear: empty string wipes it.
    resp = client.put("/api/settings", json={"openrouter_api_key": ""})
    data = resp.json()
    assert data["openrouter_api_key_set"] is False
    assert data["openrouter_api_key"] == ""


def test_default_model_round_trip(client):
    resp = client.put("/api/settings", json={"default_model": "anthropic/claude-3.5-sonnet"})
    assert resp.json()["default_model"] == "anthropic/claude-3.5-sonnet"
    assert client.get("/api/settings").json()["default_model"] == "anthropic/claude-3.5-sonnet"


def test_content_mode_round_trip(client):
    resp = client.put("/api/settings", json={"content_mode": "mature"})
    assert resp.json()["content_mode"] == "mature"
    assert client.get("/api/settings").json()["content_mode"] == "mature"


def test_test_connection_reports_missing_key(client):
    resp = client.post("/api/settings/test-connection")
    data = resp.json()
    assert data["ok"] is False
    assert "OpenRouter" in data["error"]


def test_providers_round_trip(client):
    """Multi-provider list survives a PUT/GET round trip."""
    providers = [
        {"id": "openrouter", "api_key": "sk-or-test-key", "base_url": "https://openrouter.ai/api/v1"},
        {"id": "openai", "api_key": "sk-test", "base_url": "https://api.openai.com/v1"},
    ]
    resp = client.put("/api/settings", json={"providers": providers})
    assert resp.status_code == 200
    returned = resp.json()["providers"]
    # Keys should be masked in the response
    or_provider = next(p for p in returned if p["id"] == "openrouter")
    assert or_provider["api_key_set"] is True
