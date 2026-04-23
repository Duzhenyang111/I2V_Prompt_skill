#!/usr/bin/env python
"""Objective image prefilter for ecommerce I2V prompt planning."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from PIL import Image, ImageFilter, ImageStat


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff"}


def perceptual_hash(image: Image.Image) -> str:
    thumb = image.convert("L").resize((8, 8), Image.Resampling.LANCZOS)
    if hasattr(thumb, "get_flattened_data"):
        pixels = list(thumb.get_flattened_data())
    else:
        pixels = list(thumb.getdata())
    avg = sum(pixels) / len(pixels)
    return "".join("1" if pixel >= avg else "0" for pixel in pixels)


def hamming_distance(left: str, right: str) -> int:
    return sum(a != b for a, b in zip(left, right))


def blur_score(image: Image.Image) -> float:
    edges = image.convert("L").filter(ImageFilter.FIND_EDGES)
    return float(ImageStat.Stat(edges).var[0])


def brightness_score(image: Image.Image) -> float:
    mean = ImageStat.Stat(image.convert("L")).mean[0]
    return round(mean / 255.0, 4)


def image_files(folder: Path) -> list[Path]:
    return sorted(
        path
        for path in folder.iterdir()
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
    )


def inspect_image(path: Path, min_size: int, blur_threshold: float) -> dict[str, Any]:
    item: dict[str, Any] = {
        "image_id": path.name,
        "path": str(path),
        "status": "pass",
        "width": None,
        "height": None,
        "aspect_ratio": None,
        "brightness_score": None,
        "blur_score": None,
        "near_duplicate_of": None,
        "warnings": [],
    }

    try:
        with Image.open(path) as opened:
            image = opened.convert("RGB")
    except Exception as exc:
        item["status"] = "reject"
        item["warnings"].append("open_failed")
        item["error"] = str(exc)
        return item

    width, height = image.size
    item["width"] = width
    item["height"] = height
    item["aspect_ratio"] = round(width / height, 4) if height else None
    item["brightness_score"] = brightness_score(image)
    item["blur_score"] = round(blur_score(image), 4)
    item["_hash"] = perceptual_hash(image)

    if width < min_size or height < min_size:
        item["warnings"].append("small_resolution")
    if item["brightness_score"] < 0.12:
        item["warnings"].append("too_dark")
    if item["brightness_score"] > 0.92:
        item["warnings"].append("too_bright")
    if item["blur_score"] < blur_threshold:
        item["warnings"].append("low_detail_or_blurry")
    if item["aspect_ratio"] and (item["aspect_ratio"] < 0.45 or item["aspect_ratio"] > 2.2):
        item["warnings"].append("extreme_aspect_ratio")

    if item["warnings"]:
        item["status"] = "review"

    return item


def mark_duplicates(items: list[dict[str, Any]], distance_threshold: int) -> None:
    seen: list[dict[str, Any]] = []
    for item in items:
        current_hash = item.get("_hash")
        if not current_hash:
            continue
        for previous in seen:
            previous_hash = previous.get("_hash")
            if previous_hash and hamming_distance(current_hash, previous_hash) <= distance_threshold:
                item["near_duplicate_of"] = previous["image_id"]
                item["warnings"].append("near_duplicate")
                if item["status"] == "pass":
                    item["status"] = "review"
                break
        seen.append(item)


def build_report(
    product_folder: str | Path,
    *,
    min_size: int = 512,
    blur_threshold: float = 18.0,
    duplicate_distance: int = 4,
) -> dict[str, Any]:
    folder = Path(product_folder)
    items = [inspect_image(path, min_size, blur_threshold) for path in image_files(folder)]
    mark_duplicates(items, duplicate_distance)
    for item in items:
        item.pop("_hash", None)

    return {
        "version": "1.0",
        "product_folder": str(folder),
        "thresholds": {
            "min_size": min_size,
            "blur_threshold": blur_threshold,
            "duplicate_distance": duplicate_distance,
        },
        "images": items,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Prefilter product images for I2V prompt planning.")
    parser.add_argument("product_folder", help="Folder containing product images.")
    parser.add_argument("--output", help="Path to write image_prefilter_report.json.")
    parser.add_argument("--min-size", type=int, default=512)
    parser.add_argument("--blur-threshold", type=float, default=18.0)
    parser.add_argument("--duplicate-distance", type=int, default=4)
    args = parser.parse_args()

    report = build_report(
        args.product_folder,
        min_size=args.min_size,
        blur_threshold=args.blur_threshold,
        duplicate_distance=args.duplicate_distance,
    )
    output = Path(args.output) if args.output else Path(args.product_folder) / "image_prefilter_report.json"
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(str(output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
