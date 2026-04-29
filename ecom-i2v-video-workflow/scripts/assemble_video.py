#!/usr/bin/env python
"""Assemble final ad video from 04_final_edit_plan.json with ffmpeg."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any


DEFAULT_PLAN_NAME = "04_final_edit_plan.json"


def build_ffmpeg_command(plan: dict[str, Any], product_folder: Path) -> list[str]:
    output_path = product_folder / plan["output"]["path"]
    clips = plan["clips"]
    command = ["ffmpeg", "-y"]

    filter_parts: list[str] = []
    concat_inputs: list[str] = []
    for index, clip in enumerate(clips):
        source = product_folder / clip["source_video"]
        command.extend(["-i", str(source)])
        trim_in = float(clip["trim_in"])
        trim_out = float(clip["trim_out"])
        label = f"v{index}"
        filter_parts.append(
            f"[{index}:v]trim=start={trim_in}:end={trim_out},setpts=PTS-STARTPTS,"
            f"scale=1080:1920:force_original_aspect_ratio=decrease,"
            f"pad=1080:1920:(ow-iw)/2:(oh-ih)/2[{label}]"
        )
        concat_inputs.append(f"[{label}]")

    filter_parts.append("".join(concat_inputs) + f"concat=n={len(clips)}:v=1:a=0[outv]")
    command.extend(["-filter_complex", ";".join(filter_parts), "-map", "[outv]", str(output_path)])
    return command


def load_plan(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("stage") != "final":
        raise ValueError("04_final_edit_plan.json must have stage=final")
    if not data.get("clips"):
        raise ValueError("04_final_edit_plan.json must include clips")
    if not data.get("output", {}).get("path"):
        raise ValueError("04_final_edit_plan.json must include output.path")
    return data


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Assemble video using ffmpeg and 04_final_edit_plan.json.")
    parser.add_argument("product_folder")
    parser.add_argument("--plan", default=DEFAULT_PLAN_NAME)
    parser.add_argument("--dry-run", action="store_true", help="Print ffmpeg command without executing it.")
    args = parser.parse_args(argv)

    product_folder = Path(args.product_folder)
    plan = load_plan(product_folder / args.plan)
    command = build_ffmpeg_command(plan, product_folder)
    if args.dry_run:
        print(json.dumps(command, ensure_ascii=False, indent=2))
        return 0
    subprocess.run(command, check=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
