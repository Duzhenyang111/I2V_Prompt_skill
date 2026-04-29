import importlib.util
import json
import shutil
import subprocess
import sys
import uuid
from contextlib import contextmanager
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "ecom-i2v-ad-prompts"


@contextmanager
def workspace_tmpdir():
    path = ROOT / "validation" / "test_tmp" / uuid.uuid4().hex
    path.mkdir(parents=True, exist_ok=False)
    try:
        yield path
    finally:
        shutil.rmtree(path, ignore_errors=True)


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_quick_validate_passes_for_repository_contract():
    result = subprocess.run(
        [sys.executable, str(ROOT / "quick_validate.py")],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "validated" in result.stdout.lower()


def test_requirements_declares_pillow_for_prefilter_dependency():
    requirements = (ROOT / "requirements.txt").read_text(encoding="utf-8")

    assert "Pillow" in requirements


def test_prefilter_handles_empty_folder_and_creates_output_parent():
    prefilter = load_module(SKILL / "scripts" / "prefilter_images.py", "prefilter_images")
    with workspace_tmpdir() as tmp_path:
        output = tmp_path / "nested" / "image_prefilter_report.json"

        exit_code = prefilter.main([str(tmp_path), "--output", str(output)])

        assert exit_code == 0
        report = json.loads(output.read_text(encoding="utf-8"))
        assert report["summary"]["total_images"] == 0
        assert "no_supported_images" in report["summary"]["warnings"]


def test_prefilter_rejects_missing_folder_without_traceback(capsys):
    prefilter = load_module(SKILL / "scripts" / "prefilter_images.py", "prefilter_images")
    with workspace_tmpdir() as tmp_path:
        exit_code = prefilter.main([str(tmp_path / "missing")])

        captured = capsys.readouterr()
        assert exit_code == 2
        assert "does not exist" in captured.err
        assert "Traceback" not in captured.err


def test_prefilter_report_links_duplicate_to_prior_image():
    prefilter = load_module(SKILL / "scripts" / "prefilter_images.py", "prefilter_images")
    with workspace_tmpdir() as tmp_path:
        Image.new("RGB", (800, 800), "white").save(tmp_path / "a.jpg")
        Image.new("RGB", (800, 800), "white").save(tmp_path / "b.jpg")

        report = prefilter.build_report(tmp_path)

        assert report["summary"]["total_images"] == 2
        assert report["summary"]["review"] >= 1
        assert report["images"][1]["near_duplicate_of"] == "a.jpg"


def test_skill_docs_require_platform_confirmation_and_dual_platform_outputs():
    skill_text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    platform_text = (SKILL / "references" / "platform-presets.md").read_text(encoding="utf-8")
    prompt_text = (SKILL / "references" / "prompt-template.md").read_text(encoding="utf-8")

    assert "ask the user which platform" in skill_text.lower()
    assert "do not generate" in skill_text.lower()
    assert "planned_final_edit_plan_tiktok.json" in platform_text
    assert "planned_final_edit_plan_amazon.json" in platform_text
    assert "source_image_id" in prompt_text
    assert "expected_render_path" in prompt_text
    assert "sequence_role" in prompt_text
