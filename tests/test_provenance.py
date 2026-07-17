import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import provenance  # noqa: E402

def test_build_manifest_includes_python_version():
    manifest = provenance.build_manifest()
    assert manifest["python_version"]

def test_build_manifest_does_not_raise_when_git_unavailable(monkeypatch):
    def fake_run(*args, **kwargs):
        raise FileNotFoundError("git not found")
    monkeypatch.setattr(provenance.subprocess, "run", fake_run)
    manifest = provenance.build_manifest()
    assert manifest["git_commit"] is None

def test_build_manifest_includes_package_versions():
    manifest = provenance.build_manifest()
    assert "pandas" in manifest["packages"]

def test_build_manifest_data_sha256(tmp_path):
    data_file = tmp_path / "data.csv"
    data_file.write_text("a,b\n1,2\n", encoding="utf-8")
    manifest = provenance.build_manifest(data_path=str(data_file))
    assert manifest["data_sha256"] is not None
    assert len(manifest["data_sha256"]) == 64

def test_write_manifest_creates_readable_json(tmp_path):
    out_path = tmp_path / "manifest.json"
    result = provenance.write_manifest(out_path, seed=42)
    assert result == out_path
    data = json.loads(out_path.read_text(encoding="utf-8"))
    assert data["seed"] == 42
