import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import setup  # noqa: E402

# NOTE: these tests are hermetic - subprocess.run is always monkeypatched or (in the
# dry-run cases) never reached, so no test here performs a real `pip install`.


def test_plan_core_only_by_default():
    result = setup.plan()
    assert result == [setup.REQUIREMENTS_CORE]

def test_plan_full_and_genai_includes_all_three_req_files():
    result = setup.plan(full=True, genai=True)
    assert result == [setup.REQUIREMENTS_CORE, setup.REQUIREMENTS_OPTIONAL, setup.REQUIREMENTS_GENAI]
    assert len(result) == 3

def test_plan_full_only_excludes_genai():
    result = setup.plan(full=True, genai=False)
    assert setup.REQUIREMENTS_OPTIONAL in result
    assert setup.REQUIREMENTS_GENAI not in result

def test_plan_genai_only_excludes_optional():
    result = setup.plan(full=False, genai=True)
    assert setup.REQUIREMENTS_GENAI in result
    assert setup.REQUIREMENTS_OPTIONAL not in result

def test_pip_command_starts_with_python_module_pip_install_r():
    cmd = setup.pip_command("scripts/requirements.txt")
    assert cmd[:5] == [sys.executable, "-m", "pip", "install", "-r"]
    assert cmd[5] == "scripts/requirements.txt"

def test_pip_command_accepts_a_path_object():
    cmd = setup.pip_command(setup.REQUIREMENTS_CORE)
    assert cmd[-1] == str(setup.REQUIREMENTS_CORE)

def test_dry_run_never_invokes_pip(monkeypatch):
    calls = []
    monkeypatch.setattr(setup.subprocess, "run", lambda *a, **k: calls.append((a, k)))
    exit_code = setup.main(["--dry-run", "--full", "--genai"])
    assert exit_code == 0
    assert calls == []

def test_dry_run_default_plans_core_only(monkeypatch, capsys):
    def _unexpected_call(*a, **k):
        raise AssertionError("pip should not run during --dry-run")
    monkeypatch.setattr(setup.subprocess, "run", _unexpected_call)

    exit_code = setup.main(["--dry-run"])
    assert exit_code == 0

    out = capsys.readouterr().out
    assert "requirements.txt" in out
    assert "requirements-optional.txt" not in out
    assert "requirements-genai.txt" not in out

def test_install_group_reports_failure_without_raising(tmp_path, monkeypatch):
    req_file = tmp_path / "requirements.txt"
    req_file.write_text("pandas>=2.0\n", encoding="utf-8")

    def fake_run(cmd, check=False):
        raise subprocess.CalledProcessError(returncode=1, cmd=cmd)

    monkeypatch.setattr(setup.subprocess, "run", fake_run)
    result = setup.install_group(req_file, dry_run=False)
    assert result["ok"] is False
    assert "1" in result["detail"]

def test_install_group_missing_file_reported_not_raised(tmp_path):
    missing = tmp_path / "does-not-exist.txt"
    result = setup.install_group(missing, dry_run=False)
    assert result["ok"] is False

def test_main_reports_failure_exit_code_without_crashing(tmp_path, monkeypatch):
    def fake_run(cmd, check=False):
        raise subprocess.CalledProcessError(returncode=1, cmd=cmd)

    monkeypatch.setattr(setup.subprocess, "run", fake_run)
    exit_code = setup.main([])
    assert exit_code == 1
