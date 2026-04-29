#!/usr/bin/env python
"""Validate ecommerce I2V skill repository contracts."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SKILL = ROOT / "ecom-i2v-ad-prompts"
PROMPT_SKILL = ROOT / "ecom-i2v-prompt-generator"
VIDEO_SKILL = ROOT / "ecom-i2v-video-workflow"


REQUIRED_FILES = [
    SKILL / "SKILL.md",
    SKILL / "agents" / "openai.yaml",
    SKILL / "references" / "image-selection-rules.md",
    SKILL / "references" / "platform-presets.md",
    SKILL / "references" / "prompt-template.md",
    SKILL / "references" / "view-to-video-strategy.md",
    SKILL / "scripts" / "prefilter_images.py",
    ROOT / "requirements.txt",
    PROMPT_SKILL / "SKILL.md",
    PROMPT_SKILL / "agents" / "openai.yaml",
    PROMPT_SKILL / "references" / "prompt-manifest-template.md",
    PROMPT_SKILL / "references" / "storyboard-plan-template.md",
    VIDEO_SKILL / "SKILL.md",
    VIDEO_SKILL / "agents" / "openai.yaml",
    VIDEO_SKILL / "references" / "video-workflow-template.md",
    VIDEO_SKILL / "scripts" / "load_i2v_config.py",
    VIDEO_SKILL / "scripts" / "validate_prompt_manifest.py",
    VIDEO_SKILL / "scripts" / "assemble_video.py",
]

OUTPUT_SECTIONS = [
    "图片筛选结果",
    "商品级广告策略",
    "图片分镜规划表",
    "逐图分析卡与生成参数",
    "中文预剪辑说明",
    "planned_final_edit_plan.json",
]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def validate_required_files(errors: list[str]) -> None:
    for path in REQUIRED_FILES:
        if not path.exists():
            errors.append(f"missing required file: {path.relative_to(ROOT)}")


def validate_skill_contract(errors: list[str]) -> None:
    skill = read(SKILL / "SKILL.md")
    lower_skill = skill.lower()
    if 'platform: "tiktok"' not in skill:
        errors.append('SKILL.md must make "tiktok" the default platform in the input example.')
    if "default to `tiktok`" not in lower_skill:
        errors.append("SKILL.md must state that missing platform defaults to TikTok.")
    if "ask the user which platform" not in lower_skill:
        errors.append("SKILL.md must instruct the model when to ask the user which platform.")
    if "unsupported or ambiguous" not in lower_skill:
        errors.append("SKILL.md must ask only when platform input is unsupported or ambiguous.")
    for section in OUTPUT_SECTIONS:
        if section not in skill:
            errors.append(f"SKILL.md missing output section: {section}")
    for required in ["Review AI", "review_result", "retry_instruction", "ask_user", "If Review AI returns `retry`"]:
        if required not in skill:
            errors.append(f"SKILL.md missing unified review loop contract: {required}")


def validate_reference_contract(errors: list[str]) -> None:
    platform = read(SKILL / "references" / "platform-presets.md")
    prompt = read(SKILL / "references" / "prompt-template.md")
    requirements = read(ROOT / "requirements.txt")

    for filename in ["planned_final_edit_plan_tiktok.json", "planned_final_edit_plan_amazon.json"]:
        if filename not in platform:
            errors.append(f"platform-presets.md missing dual-platform output name: {filename}")

    for field in ["source_image_id", "expected_render_path", "sequence_role"]:
        if field not in prompt:
            errors.append(f"prompt-template.md missing planned clip field: {field}")
    for required in ["Review AI", "review_result", "retry_instruction", "status: \"pass\"", "status: \"retry\"", "status: \"ask_user\""]:
        if required not in prompt:
            errors.append(f"prompt-template.md missing review schema field: {required}")

    if "Pillow" not in requirements:
        errors.append("requirements.txt must declare Pillow.")

    for readme_name in ["README.md", "README.zh-CN.md"]:
        readme = read(ROOT / readme_name)
        if "```mermaid" not in readme:
            errors.append(f"{readme_name} must include the skill workflow diagram.")
        for required in ["Review AI", "review_result", "retry_instruction", "ask_user"]:
            if required not in readme:
                errors.append(f"{readme_name} missing unified review loop contract: {required}")


def validate_split_skill_contracts(errors: list[str]) -> None:
    prompt_skill = read(PROMPT_SKILL / "SKILL.md")
    video_skill = read(VIDEO_SKILL / "SKILL.md")
    manifest_template = read(PROMPT_SKILL / "references" / "prompt-manifest-template.md")
    video_template = read(VIDEO_SKILL / "references" / "video-workflow-template.md")
    assemble_script = read(VIDEO_SKILL / "scripts" / "assemble_video.py")
    config_script = read(VIDEO_SKILL / "scripts" / "load_i2v_config.py")

    for required in ["name: ecom-i2v-prompt-generator", "01_storyboard_plan.md", "02_i2v_prompt_manifest.json"]:
        if required not in prompt_skill:
            errors.append(f"prompt generator missing contract: {required}")
    if "final_tiktok_ad.mp4" in prompt_skill:
        errors.append("prompt generator must not own final video assembly outputs.")

    for required in [
        "name: ecom-i2v-video-workflow",
        "02_i2v_prompt_manifest.json",
        "I2V model key",
        ".product_i2v_config.local.json",
        "final_edit_plan.json",
        "ffmpeg",
    ]:
        if required not in video_skill:
            errors.append(f"video workflow missing contract: {required}")

    for required in ["items", "source_image", "expected_render_path"]:
        if required not in manifest_template:
            errors.append(f"prompt manifest template missing field: {required}")
    for required in ["api_key", "renders/", "final_edit_plan.json"]:
        if required not in video_template:
            errors.append(f"video workflow template missing field: {required}")
    if "ffmpeg" not in assemble_script or "04_final_edit_plan.json" not in assemble_script:
        errors.append("assemble_video.py must describe ffmpeg assembly from 04_final_edit_plan.json.")
    if ".product_i2v_config.local.json" not in config_script or "api_key" not in config_script:
        errors.append("load_i2v_config.py must load private api_key config.")


def main() -> int:
    errors: list[str] = []
    validate_required_files(errors)
    if not errors:
        validate_skill_contract(errors)
        validate_reference_contract(errors)
        validate_split_skill_contracts(errors)

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print("Skill contract validated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
