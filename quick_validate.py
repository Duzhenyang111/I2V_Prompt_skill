#!/usr/bin/env python
"""Validate the ecom-i2v-ad-prompts skill repository contract."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SKILL = ROOT / "ecom-i2v-ad-prompts"


REQUIRED_FILES = [
    SKILL / "SKILL.md",
    SKILL / "agents" / "openai.yaml",
    SKILL / "references" / "image-selection-rules.md",
    SKILL / "references" / "platform-presets.md",
    SKILL / "references" / "prompt-template.md",
    SKILL / "references" / "view-to-video-strategy.md",
    SKILL / "scripts" / "prefilter_images.py",
    ROOT / "requirements.txt",
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
    if "ask the user which platform" not in lower_skill:
        errors.append("SKILL.md must instruct the model to ask the user which platform before generation.")
    if "do not generate" not in lower_skill:
        errors.append("SKILL.md must say not to generate prompts/plans until platform is known.")
    for section in OUTPUT_SECTIONS:
        if section not in skill:
            errors.append(f"SKILL.md missing output section: {section}")


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

    if "Pillow" not in requirements:
        errors.append("requirements.txt must declare Pillow.")


def main() -> int:
    errors: list[str] = []
    validate_required_files(errors)
    if not errors:
        validate_skill_contract(errors)
        validate_reference_contract(errors)

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print("Skill contract validated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
