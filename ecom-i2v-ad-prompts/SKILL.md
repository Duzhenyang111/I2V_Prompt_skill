---
name: ecom-i2v-ad-prompts
description: Generate stage-one structured image-to-video prompts for overseas ecommerce household and lifestyle product ads. Use when Codex needs to analyze one product folder containing multiple product images, run objective image prefiltering, perform AI semantic image screening, assign each accepted image a planned role in a short ad, produce a Chinese analysis card plus separate English prompt and negative prompt for every image, and create a machine-readable planned_final_edit_plan.json for pre-generation clip planning.
---

# Ecom I2V Ad Prompts

Create high-precision stage-one image-to-video prompts for one ecommerce product at a time. Treat one folder of images as one product campaign, not as unrelated single images.

This skill only handles the pre-generation planning stage. It analyzes source images and creates prompts plus `planned_final_edit_plan.json`. Do not use it to create the final executable `final_edit_plan.json`; that belongs to a separate post-generation video review and assembly-planning skill.

## Required Input

Start from this minimum input:

```yaml
product_name: ""
category: ""
target_audience: ""
selling_points:
  - ""
platform: "tiktok" # default; also supports "amazon" or ["tiktok", "amazon"]
product_folder: "/abs/path/to/product_images"
```

Accept these optional overrides when provided:

- `campaign_goal`
- `brand_tone`
- `preferred_aspect_ratio`
- `video_model`

If optional fields are missing, infer sane defaults from the product category, target audience, platform, and image content.

If `platform` is missing, default to `tiktok`. Ask the user which platform to target only when the provided platform is unsupported or ambiguous, such as "social and marketplace" without naming TikTok, Amazon, or both.

## Operating Rules

Follow these rules every time:

1. Enumerate all image files in `product_folder` before writing prompts.
2. Inspect each image directly. Do not guess view type from the filename alone.
3. Complete programmatic prefiltering and AI semantic image screening before building the product-level ad strategy.
4. Build the product-level ad strategy from accepted and manual-review images only.
5. Assign each accepted image a planned role in the ad sequence before writing that image's prompt.
6. Preserve product identity, proportions, materials, and commercial realism.
7. Prefer controlled, ad-safe motion over cinematic excess.
8. Keep each generated clip in the 5-10 second range. Default to 6 seconds unless a slower premium move is justified.
9. Write analysis in Chinese and generation prompts in English.
10. Split every per-image generation result into `prompt`, `negative_prompt`, and `generation_params`.
11. Output `planned_final_edit_plan.json` as a pre-generation plan only. It is not directly executable by `ffmpeg`.
12. Never call the pre-generation plan `final_edit_plan.json`.
13. Default to `tiktok` when `platform` is omitted. Ask the user which platform to target only when the provided platform is unsupported or ambiguous.
14. Use one unified Review AI after each major AI-authored stage. Review AI judges whether the stage output is usable; it does not create campaign content.

## Unified Review AI

Run Review AI after these stages:

- AI semantic image screening
- product-level ad strategy
- per-image analysis cards and generation prompts
- planned edit plan

Review AI must return a compact machine-readable block:

```yaml
review_result:
  status: "pass" # pass | retry | ask_user
  failed_checks:
    - ""
  retry_instruction: ""
  user_question: ""
```

If Review AI returns `pass`, continue to the next stage. If Review AI returns `retry`, rerun the failed stage once using `retry_instruction` and then review again. If Review AI returns `ask_user`, stop and ask `user_question` before continuing.

Do not let Review AI rewrite prompts, change strategy, or invent product facts directly. Its job is only to evaluate, explain failure, and provide bounded retry instructions.

## Workflow

## Stage Boundary

Use this skill for stage one only:

```text
product image folder
-> programmatic image prefilter
-> AI semantic image screening
-> Review AI gate
-> image inspection for accepted images
-> per-image prompt / negative_prompt / generation_params
-> Review AI gate
-> planned_final_edit_plan.json
-> Review AI gate
-> image-to-video generation happens outside this skill
```

Do not inspect generated videos in this skill. After generated videos exist, use a separate stage-two workflow to review actual video quality, choose stable usable ranges, and create `final_edit_plan.json` for `ffmpeg` or another assembly tool.

### 1. Run Objective Image Prefiltering

Run the bundled prefilter script before semantic image analysis:

```bash
python ecom-i2v-ad-prompts/scripts/prefilter_images.py "<product_folder>" --output "<product_folder>/image_prefilter_report.json"
```

Use the script output as a cheap first-pass quality report only. It can reject broken files and flag objective risks, but it cannot decide advertising value.

The report contains:

- `status`: `pass`, `review`, or `reject`
- dimensions and aspect ratio
- brightness score
- blur/detail score
- near-duplicate warning
- objective warnings

Do not inspect images marked `reject` unless the user explicitly asks. Inspect `pass` and `review` images during AI screening.

### 2. Perform AI Semantic Image Screening

Use [references/image-selection-rules.md](references/image-selection-rules.md). Combine the prefilter report with direct image inspection.

Output an image screening section before the product-level strategy:

```yaml
图片筛选结果:
  accepted_images:
    - image_id: ""
      selection_score: 92
      planned_use: "hook opener"
      reason: ""
  rejected_images:
    - image_id: ""
      rejection_reason: ""
  needs_manual_review:
    - image_id: ""
      review_reason: ""
```

Only accepted images should receive full per-image generation prompts by default. Manual-review images may receive prompts only if they add unique value and their risk controls are clear.

### 3. Build the Product-Level Strategy

Summarize the product campaign in Chinese:

- product positioning
- likely conversion angle
- recommended ad style
- recommended pace
- recommended aspect ratio
- visual risk warnings

Use [references/platform-presets.md](references/platform-presets.md) before choosing visual style, aspect ratio, pacing, image selection priority, and planned clip timing.

Choose one dominant ad route:

- `clean studio conversion`
- `premium aesthetic showcase`
- `practical lifestyle utility`
- `feature-proof detail focus`

Use the product category, target audience, selling points, and platform to justify the choice.

After writing the strategy, run Review AI. It should reject strategies that ignore TikTok-first defaults, invent product claims, mismatch the selected platform, or fail to explain the campaign route.

### 4. Inspect and Classify Accepted Images

For each accepted image, classify the most useful view type. Use [references/view-to-video-strategy.md](references/view-to-video-strategy.md).

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

Also note:

- whether the product is isolated or in scene
- whether the background should be preserved, simplified, or rebuilt
- whether the image is better for opening, middle proof, or closing
- whether hand interaction or object interaction is safe

### 5. Plan the Intended Ad Sequence

Create a sequencing table before per-image prompts. Assign each image one primary role:

- `hook opener`
- `hero reveal`
- `feature proof`
- `detail reinforcement`
- `lifestyle credibility`
- `material close`
- `packshot closer`

Do not force all roles to appear. Use only the roles justified by the image set.

Prefer this sequencing logic:

1. Start with the strongest shape or most scroll-stopping frame.
2. Move to product comprehension.
3. Prove important selling points.
4. End with a clean, memorable close.

### 6. Produce the Per-Image Analysis Card

For every accepted image, output a Chinese analysis card with these fields:

```yaml
image_id: ""
detected_view: ""
sequence_role: ""
marketing_job: ""
recommended_duration: ""
recommended_aspect_ratio: ""
camera_motion: ""
lens_feel: ""
background_strategy: ""
lighting_strategy: ""
product_focus: ""
must_keep: []
risk_controls: []
reasoning: ""
```

Keep `reasoning` short and operational. Explain why this image should become this type of shot.

### 7. Write the Final Per-Image Generation Block

Use [references/prompt-template.md](references/prompt-template.md).

Every per-image generation block must include:

- `prompt`
- `negative_prompt`
- `generation_params`

Use [references/prompt-template.md](references/prompt-template.md) for the required fields, negative prompt rules, generation parameter schema, and dual-platform output shape. Use [references/platform-presets.md](references/platform-presets.md) for TikTok and Amazon differences.

Do not write vague prompts like "make it cinematic" or "high quality advertisement". Replace vague adjectives with concrete shot instructions.

After writing per-image prompts, run Review AI. It should reject prompts that are not image-specific, are not in English, mix negative constraints into the positive prompt, invent product features, or use risky motion that may deform the product.

### 8. Build the Planned 15-Second Assembly Plan

After all per-image outputs, choose only the strongest source images for the intended short ad. Do not assume every image should be generated or that every generated clip will be usable.

Produce two outputs:

1. `中文预剪辑说明`
2. `planned_final_edit_plan.json`

For a single platform, output one `planned_final_edit_plan.json`. For dual-platform requests, output `planned_final_edit_plan_tiktok.json` and `planned_final_edit_plan_amazon.json` instead of one compromise plan.

Use [references/prompt-template.md](references/prompt-template.md) for the exact JSON schema and validation rules. Use [references/platform-presets.md](references/platform-presets.md) for platform-specific planned edit variants. Each planned clip must preserve the source mapping with `source_image_id`, `expected_render_path`, and `sequence_role`.

After building the planned edit plan, run Review AI. It should reject plans with invalid JSON, total duration over 15 seconds, non-ascending timelines, missing source mappings, or platform-inconsistent sequencing.

## Hard Constraints

Do not:

- invent product features not present in the input
- generate impossible hand interactions
- inspect generated videos in this stage-one skill
- output the pre-generation plan as `final_edit_plan.json`
- silently invent a third platform workflow when the provided platform is unsupported or ambiguous

Use [references/prompt-template.md](references/prompt-template.md) for negative prompt constraints and output schema details.

## Output Order

Always return results in this order:

1. `图片筛选结果`
2. `商品级广告策略`
3. `图片分镜规划表`
4. `逐图分析卡与生成参数`
5. `中文预剪辑说明`
6. `planned_final_edit_plan.json`

## References

- Use [references/view-to-video-strategy.md](references/view-to-video-strategy.md) for view-to-shot mapping.
- Use [references/image-selection-rules.md](references/image-selection-rules.md) for AI semantic image screening after programmatic prefiltering.
- Use [references/platform-presets.md](references/platform-presets.md) for platform defaults.
- Use [references/prompt-template.md](references/prompt-template.md) for the exact output shapes.
