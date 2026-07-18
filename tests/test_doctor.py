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

def test_check_optional_returns_list():
    result = doctor.check_optional()
    assert isinstance(result, list)
    assert len(result) == len(doctor.OPTIONAL_PACKAGES)
    for item in result:
        assert {"name", "module", "feature", "ok"} <= set(item)
        assert isinstance(item["ok"], bool)

def test_run_healthy_when_core_present_even_if_optional_absent(tmp_path, monkeypatch):
    manifest_dir = tmp_path / ".claude-plugin"
    manifest_dir.mkdir()
    (manifest_dir / "plugin.json").write_text(json.dumps({"name": "datalab"}), encoding="utf-8")

    monkeypatch.setattr(doctor, "check_python", lambda *a, **k: {"name": "python", "ok": True, "detail": "3.99 (need >= 3.10)"})
    monkeypatch.setattr(
        doctor,
        "check_packages",
        lambda *a, **k: [{"name": "reportlab", "module": "reportlab", "ok": True}],
    )
    monkeypatch.setattr(
        doctor,
        "check_optional",
        lambda *a, **k: [{"name": "shap", "module": "shap", "feature": "explainability", "ok": False}],
    )

    report = doctor.run(tmp_path)
    assert report["healthy"] is True
    assert report["optional"][0]["ok"] is False

def test_run_unhealthy_when_core_package_missing(tmp_path, monkeypatch):
    manifest_dir = tmp_path / ".claude-plugin"
    manifest_dir.mkdir()
    (manifest_dir / "plugin.json").write_text(json.dumps({"name": "datalab"}), encoding="utf-8")

    monkeypatch.setattr(doctor, "check_python", lambda *a, **k: {"name": "python", "ok": True, "detail": "3.99 (need >= 3.10)"})
    monkeypatch.setattr(
        doctor,
        "check_packages",
        lambda *a, **k: [{"name": "reportlab", "module": "reportlab", "ok": False}],
    )
    monkeypatch.setattr(doctor, "check_optional", lambda *a, **k: [])

    report = doctor.run(tmp_path)
    assert report["healthy"] is False
