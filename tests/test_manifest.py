import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def _load(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))

def test_plugin_json_is_valid_and_named():
    data = _load(".claude-plugin/plugin.json")
    assert data["name"] == "datalab"
    assert "version" in data and "description" in data
    assert isinstance(data.get("skills", []), list)

def test_marketplace_json_lists_datalab():
    data = _load(".claude-plugin/marketplace.json")
    names = [p.get("name") for p in data.get("plugins", [])]
    assert "datalab" in names

def test_every_listed_skill_dir_exists():
    data = _load(".claude-plugin/plugin.json")
    for entry in data.get("skills", []):
        skill_dir = (ROOT / entry).resolve()
        assert skill_dir.is_dir(), f"missing skill dir: {entry}"
        assert (skill_dir / "SKILL.md").exists(), f"missing SKILL.md in {entry}"
