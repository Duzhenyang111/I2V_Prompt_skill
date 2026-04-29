---
name: ecom-i2v-prompt-generator
description: Generate optimized ecommerce image-to-video prompt packages from one product image folder. Use when Codex needs to inspect product images, default to TikTok unless specified, screen usable images, create a human-readable storyboard plan, and create a machine-readable 02_i2v_prompt_manifest.json for downstream automated I2V video generation.
---

# Ecom I2V Prompt Generator

Use this skill for stage-one planning only. It does not call an I2V model, review generated videos, create `final_edit_plan.json`, or assemble the final video.

## Required Input

```yaml
product_name: ""
category: ""
target_audience: ""
selling_points:
  - ""
platform: "tiktok" # default; also supports "amazon" or ["tiktok", "amazon"]
product_folder: "/abs/path/to/product_images"
```

If `platform` is missing, default to `tiktok`. Ask only when the platform is unsupported or ambiguous.

## Workflow

1. Enumerate all image files in `product_folder`.
2. Run objective prefiltering using `scripts/prefilter_images.py`.
3. Inspect pass/review images directly; do not classify by filename alone.
4. Screen images into accepted, rejected, and manual-review groups.
5. Run unified Review AI on screening output.
6. Build the product-level strategy and image sequence.
7. Run unified Review AI on strategy and sequence.
8. Write per-image Chinese analysis cards and English I2V prompts.
9. Run unified Review AI on prompts.
10. Write exactly two primary artifacts into the product folder:
    - `01_storyboard_plan.md`
    - `02_i2v_prompt_manifest.json`

## Output Split

`01_storyboard_plan.md` is for humans. Include product info, screening decisions, strategy, sequence table, review results, and the planned edit outline.

`02_i2v_prompt_manifest.json` is for scripts. Keep it pure JSON, with no Markdown. Use [references/prompt-manifest-template.md](references/prompt-manifest-template.md). Every accepted generation item must include:

- `clip_id`
- `image_id`
- `source_image`
- `sequence_role`
- `expected_render_path`
- `prompt`
- `negative_prompt`
- `generation_params`

Do not put final video paths, `final_edit_plan.json`, ffmpeg commands, API keys, or provider credentials in this skill's output.

## Review AI Contract

After screening, strategy, and prompt writing, return:

```yaml
review_result:
  status: "pass" # pass | retry | ask_user
  failed_checks: []
  retry_instruction: ""
  user_question: ""
```

If `retry`, rerun the failed stage once using `retry_instruction`. If `ask_user`, stop and ask `user_question`.

## References

- Use [references/prompt-manifest-template.md](references/prompt-manifest-template.md) for the machine-readable manifest.
- Use [references/storyboard-plan-template.md](references/storyboard-plan-template.md) for the human-readable plan.
