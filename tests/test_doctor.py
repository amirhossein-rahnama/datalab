import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import doctor  # noqa: E402

def test_check_python_rejects_old_version():
    result = doctor.check_python((3, 8, 0))
    assert result["ok"] is False

def test_check_python_accepts_current():
    result = doctor.check_python((3, 11, 0))
    assert result["ok"] is True

def test_missing_pip_install_builds_command():
    pkgs = [{"name": "reportlab", "ok": True}, {"name": "python-pptx", "ok": False}]
    assert doctor.missing_pip_install(pkgs) == "pip install python-pptx"

def test_missing_pip_install_none_when_all_present():
    pkgs = [{"name": "reportlab", "ok": True}]
    assert doctor.missing_pip_install(pkgs) is None

def test_check_plugin_valid(tmp_path):
    manifest_dir = tmp_path / ".claude-plugin"
    manifest_dir.mkdir()
    (manifest_dir / "plugin.json").write_text(json.dumps({"name": "datalab"}), encoding="utf-8")
    result = doctor.check_plugin(tmp_path)
    assert result["ok"] is True and result["detail"] == "datalab"

def test_check_plugin_missing(tmp_path):
    result = doctor.check_plugin(tmp_path)
    assert result["ok"] is False
