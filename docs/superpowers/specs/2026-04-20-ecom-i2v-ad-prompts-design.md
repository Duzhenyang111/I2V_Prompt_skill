## Overview

Create a Codex skill for generating high-precision image-to-video prompts for overseas ecommerce household-product ads. The skill must treat one folder of images as one product, analyze every image individually, assign each image a role in the final ad sequence, and produce both per-image English prompts and a final multi-video editing prompt.

## Goals

- Support overseas ecommerce household and daily-use products.
- Accept a minimal required input set:
  - `product_name`
  - `category`
  - `target_audience`
  - `selling_points`
  - `platform`
  - `product_folder`
- Infer or auto-tune other defaults from product info and image content.
- Generate one prompt per image for 5-10 second videos.
- Produce highly structured outputs with strong first-pass usability.
- Add a final cross-shot edit/composition prompt for turning multiple generated clips into one short ad.
- Ask the user to confirm the target platform before generation whenever `platform` is missing or ambiguous.

## Non-Goals

- Do not build a computer-vision pipeline or external image-analysis dependency in v1.
- Do not include batch automation scripts in v1 unless validation shows they are needed.
- Do not optimize for non-ecommerce domains.

## User Workflow

1. The user provides product metadata and a folder path containing all product images.
2. Codex reads the folder contents and inspects each image.
3. The skill produces a product-level ad strategy.
4. The skill assigns each image a sequence role in the final ad.
5. The skill outputs a Chinese analysis card and an English final prompt for each image.
6. The skill outputs a final multi-clip editing/storyboard prompt for downstream composition.

## Input Contract

Default recommended input:

```yaml
product_name: ""
category: ""
target_audience: ""
selling_points:
  - ""
platform: "amazon"
product_folder: "/abs/path/to/product_images"
```

Optional overrides:

- `campaign_goal`
- `brand_tone`
- `preferred_aspect_ratio`
- `video_model`

## Output Contract

The skill must produce six sections in order:

1. Image screening result in Chinese
2. Product-level ad strategy in Chinese
3. Image sequencing table for the final ad
4. Per-image analysis card in Chinese plus final English prompt and generation parameters
5. Chinese pre-editing explanation
6. `planned_final_edit_plan.json`

Single-platform runs output one `planned_final_edit_plan.json`. Dual-platform runs output `planned_final_edit_plan_tiktok.json` and `planned_final_edit_plan_amazon.json`.

## Decision Framework

The skill must explicitly map image view types to video strategies rather than relying on freeform prompting.

Required view classes:

- `hero/front`
- `side/angle`
- `detail/close-up`
- `in-use/lifestyle`
- `top`
- `back`
- `packaging`
- `texture/material`
- `scale/size`

For each detected class, the skill must define:

- likely function in the final ad
- preferred camera motion
- preferred pace
- background complexity guidance
- lighting guidance
- forbidden mistakes

## Default Prompting Rules

- Default target clip duration: 6 seconds unless the image needs 7-8 seconds for slower premium motion.
- Allowed range: 5-10 seconds.
- Default aspect ratio depends on platform and campaign intent.
- Preserve product identity, proportions, materials, and sellable realism.
- Avoid hallucinated accessories, text artifacts, logo distortion, anatomy errors for hands, and dramatic motion that breaks ad realism.

## Skill Resources

The skill should contain:

- `SKILL.md`
- `references/view-to-video-strategy.md`
- `references/platform-presets.md`
- `references/prompt-template.md`
- `agents/openai.yaml`
- `scripts/prefilter_images.py`
- root `requirements.txt`
- root `quick_validate.py`

README files may exist at the repository root to explain installation and usage.

## Validation

- Run `quick_validate.py` on the finished skill.
- Run the Python tests that cover the validator, prefilter behavior, dependency declaration, and output contract.
- Manually inspect the generated `agents/openai.yaml` values for clarity and correct `$skill-name` usage.
- Verify the skill instructions are concise, procedural, and contain no placeholder text.

## Open Decisions Resolved

- Output language: Chinese analysis plus English final prompt
- Mode support: both single-image prompt generation and optional multi-image final edit planning
- Core workflow: product-folder driven, not manually tagged-image driven
