#!/usr/bin/env python
"""Load private I2V provider config without printing secrets."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


CONFIG_NAME = ".product_i2v_config.local.json"


def load_config(product_folder: str | Path, home: str | Path | None = None) -> dict[str, Any]:
    folder_config = Path(product_folder) / CONFIG_NAME
    home_config = Path(home).expanduser() / CONFIG_NAME if home else Path.home() / CONFIG_NAME

    for path in [folder_config, home_config]:
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            missing = [key for key in ["i2v_provider", "model", "api_key"] if not data.get(key)]
            if missing:
                raise ValueError(f"{path} missing required keys: {', '.join(missing)}")
            return {
                "config_path": str(path),
                "i2v_provider": data["i2v_provider"],
                "model": data["model"],
                "api_key": data["api_key"],
            }

    raise FileNotFoundError(
        f"No {CONFIG_NAME} found in product folder or home directory. Ask the user for provider, model, and api_key."
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Load private I2V config.")
    parser.add_argument("product_folder")
    args = parser.parse_args(argv)

    config = load_config(args.product_folder)
    public = {key: value for key, value in config.items() if key != "api_key"}
    public["api_key"] = "***"
    print(json.dumps(public, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
