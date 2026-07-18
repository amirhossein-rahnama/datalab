import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import scaffold_render  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
BASE_TEMPLATE = ROOT / "templates" / "base"
STACKS_PATH = ROOT / "templates" / "stacks.yaml"

CONTEXT = {"pkg": "myproj", "project": "My Proj", "python": "3.11"}


def test_render_creates_expected_base_files(tmp_path):
    result = scaffold_render.render(BASE_TEMPLATE, tmp_path, CONTEXT)
    for name in ["requirements.txt", "tasks.py", "config.yaml", "pipeline.py", "README.md"]:
        assert (tmp_path / name).exists(), f"missing {name}"
    assert result["written"]
    assert result["skipped"] == []


def test_render_renames_package_placeholder_directory(tmp_path):
    scaffold_render.render(BASE_TEMPLATE, tmp_path, CONTEXT)
    pkg_dir = tmp_path / "src" / "myproj"
    assert pkg_dir.is_dir()
    assert (pkg_dir / "__init__.py").exists()
    assert (pkg_dir / "config.py").exists()
    assert not (tmp_path / "src" / "{{pkg}}").exists()


def test_render_leaves_no_literal_tokens_in_text_files(tmp_path):
    scaffold_render.render(BASE_TEMPLATE, tmp_path, CONTEXT)
    checked_any = False
    for path in tmp_path.rglob("*"):
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        checked_any = True
        assert "{{pkg}}" not in text, f"unrendered {{{{pkg}}}} token in {path}"
        assert "{{project}}" not in text, f"unrendered {{{{project}}}} token in {path}"
        assert "{{python}}" not in text, f"unrendered {{{{python}}}} token in {path}"
    assert checked_any


def test_render_is_non_clobbering(tmp_path):
    scaffold_render.render(BASE_TEMPLATE, tmp_path, CONTEXT)
    sentinel = tmp_path / "README.md"
    sentinel.write_text("SENTINEL DO NOT OVERWRITE", encoding="utf-8")

    result = scaffold_render.render(BASE_TEMPLATE, tmp_path, CONTEXT, overwrite=False)

    assert sentinel.read_text(encoding="utf-8") == "SENTINEL DO NOT OVERWRITE"
    assert "README.md" in result["skipped"]
    assert "README.md" not in result["written"]


def test_render_overwrite_true_replaces_existing_file(tmp_path):
    scaffold_render.render(BASE_TEMPLATE, tmp_path, CONTEXT)
    sentinel = tmp_path / "README.md"
    sentinel.write_text("SENTINEL", encoding="utf-8")

    result = scaffold_render.render(BASE_TEMPLATE, tmp_path, CONTEXT, overwrite=True)

    assert sentinel.read_text(encoding="utf-8") != "SENTINEL"
    assert "README.md" in result["written"]
    assert "README.md" not in result["skipped"]


def test_render_binary_fallback_copies_bytes_unchanged(tmp_path):
    template_dir = tmp_path / "tpl"
    (template_dir / "{{pkg}}").mkdir(parents=True)
    binary_content = bytes([0xFF, 0xFE, 0x00, 0x01, 0x02, 0x80, 0x81])
    (template_dir / "{{pkg}}" / "asset.bin").write_bytes(binary_content)

    dest = tmp_path / "dest"
    result = scaffold_render.render(template_dir, dest, CONTEXT)

    out_file = dest / "myproj" / "asset.bin"
    assert out_file.exists()
    assert out_file.read_bytes() == binary_content
    assert "myproj/asset.bin" in result["written"]


def test_render_missing_template_dir_raises(tmp_path):
    try:
        scaffold_render.render(tmp_path / "does-not-exist", tmp_path / "dest", CONTEXT)
        assert False, "expected FileNotFoundError"
    except FileNotFoundError:
        pass


def test_load_stacks_has_expected_structure():
    stacks = scaffold_render.load_stacks(str(STACKS_PATH))
    assert "base" in stacks and "packages" in stacks["base"]
    assert "tasks" in stacks
    for task in [
        "eda",
        "classification",
        "regression",
        "clustering",
        "timeseries",
        "nlp",
        "cv",
        "recommendation",
        "genai_rag",
    ]:
        assert task in stacks["tasks"], f"missing task type: {task}"
        assert "packages" in stacks["tasks"][task]
        assert "recipe" in stacks["tasks"][task]
    assert "tiers" in stacks
    for tier in ["ml", "dl", "mlops"]:
        assert tier in stacks["tiers"], f"missing tier: {tier}"
        assert "packages" in stacks["tiers"][tier]


def test_slugify_pkg_derives_importable_name():
    assert scaffold_render.slugify_pkg("Breast Cancer") == "breast_cancer"
    assert scaffold_render.slugify_pkg("My-Proj 2!") == "my_proj_2"
    assert scaffold_render.slugify_pkg("123data").startswith("p_")
    assert scaffold_render.slugify_pkg("   ") == "project"


def test_main_tier_mode_renders_tiers_and_derives_pkg(tmp_path):
    rc = scaffold_render.main([
        "--tier", "base,ml",
        "--task-type", "classification",
        "--project", "My Proj",
        "--dest", str(tmp_path),
    ])
    assert rc == 0
    assert (tmp_path / "src" / "my_proj").is_dir()      # pkg derived from --project
    assert (tmp_path / "params.yaml").exists()          # ml tier rendered
    reqs = (tmp_path / "requirements.txt").read_text(encoding="utf-8")
    assert "optuna" in reqs                             # ml-tier package appended


def test_main_requires_template_or_tier(tmp_path):
    import pytest

    with pytest.raises(SystemExit):
        scaffold_render.main(["--project", "X", "--dest", str(tmp_path)])


def test_augment_requirements_dedupes(tmp_path):
    req = tmp_path / "requirements.txt"
    req.write_text("pandas>=2.0\noptuna>=3.0\n", encoding="utf-8")
    added = scaffold_render.augment_requirements(
        tmp_path, task_type=None, tiers=["ml"], stacks_path=STACKS_PATH
    )
    text = req.read_text(encoding="utf-8")
    assert text.count("optuna") == 1   # already present -> not duplicated
    assert added                       # at least one new ml-tier package added
