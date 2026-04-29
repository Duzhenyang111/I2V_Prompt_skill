#!/usr/bin/env python
"""Validate 02_i2v_prompt_manifest.json before running I2V generation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REQUIRED_ITEM_KEYS = [
    "clip_id",
    "image_id",
    "source_image",
    "sequence_role",
    "expected_render_path",
    "prompt",
    "negative_prompt",
    "generation_params",
]


def validate_manifest(data: dict[str, Any], base_dir: Path) -> list[str]:
    errors: list[str] = []
    if data.get("version") != "1.0":
        errors.append("version must be 1.0")
    if not data.get("platform"):
        errors.append("platform is required")
    items = data.get("items")
    if not isinstance(items, list) or not items:
        errors.append("items must be a non-empty list")
        return errors

    seen_clip_ids: set[str] = set()
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            errors.append(f"items[{index}] must be an object")
            continue
        for key in REQUIRED_ITEM_KEYS:
            if key not in item:
                errors.append(f"items[{index}] missing {key}")
        clip_id = item.get("clip_id")
        if clip_id in seen_clip_ids:
            errors.append(f"duplicate clip_id: {clip_id}")
        if clip_id:
            seen_clip_ids.add(clip_id)
        source_image = item.get("source_image")
        if source_image and not Path(source_image).exists():
            errors.append(f"source_image does not exist: {source_image}")
        expected = item.get("expected_render_path")
        if expected and Path(expected).is_absolute():
            errors.append(f"expected_render_path should be relative to product folder: {expected}")
        params = item.get("generation_params", {})
        if not isinstance(params, dict):
            errors.append(f"items[{index}].generation_params must be an object")
        elif not params.get("recommended_aspect_ratio"):
            errors.append(f"items[{index}].generation_params.recommended_aspect_ratio is required")

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate an I2V prompt manifest.")
    parser.add_argument("manifest")
    args = parser.parse_args(argv)

    path = Path(args.manifest)
    data = json.loads(path.read_text(encoding="utf-8"))
    errors = validate_manifest(data, path.parent)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("Prompt manifest validated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
