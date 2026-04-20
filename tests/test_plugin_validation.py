import json
import os


def test_plugin_json_exists():
    path = os.path.join(
        os.path.dirname(__file__), os.pardir, "plugins", "omc-copilot", "plugin.json"
    )
    assert os.path.exists(path), f"plugin.json not found at {path}"


def test_plugin_json_valid():
    path = os.path.join(
        os.path.dirname(__file__), os.pardir, "plugins", "omc-copilot", "plugin.json"
    )
    with open(path, "r") as f:
        data = json.load(f)
    assert isinstance(data, dict)
    assert "agents" in data or "skills" in data or "hooks" in data
