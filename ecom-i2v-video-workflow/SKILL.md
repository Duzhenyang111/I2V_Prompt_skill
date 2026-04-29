---
name: ecom-i2v-video-workflow
description: Execute ecommerce image-to-video production from a prompt manifest. Use when Codex needs to read 02_i2v_prompt_manifest.json, obtain an I2V model key from a local private config or user prompt, generate one video clip per image, review generated clips, build final_edit_plan.json, and assemble a final TikTok or ecommerce ad video with ffmpeg.
---

# Ecom I2V Video Workflow

Use this skill for stage-two execution. It consumes `02_i2v_prompt_manifest.json` created by `ecom-i2v-prompt-generator`.

Do not create new product strategy or rewrite prompts unless Review AI returns `retry` and the prompt manifest contains enough information to make a bounded correction.

## Required Input

```yaml
prompt_manifest: "/abs/path/to/product_folder/02_i2v_prompt_manifest.json"
i2v_provider: "" # optional if present in config
model: ""        # optional if present in config
```

## I2V Model Key

Look for an I2V model key in this order:

1. Product folder config: `.product_i2v_config.local.json`
2. User home config: `.product_i2v_config.local.json`
3. Ask the user for provider, model, and API key

Never write API keys into Markdown reports, prompt manifests, git-tracked files, or terminal summaries. If the user agrees to save the key, write only to `.product_i2v_config.local.json`, which must remain private.

Example private config:

```json
{
  "i2v_provider": "provider-name",
  "model": "model-name",
  "api_key": "replace-with-private-key"
}
```

## Workflow

1. Read and validate `02_i2v_prompt_manifest.json`.
2. Resolve I2V provider config and API key.
3. For each item in `items`, call the I2V model with `source_image`, `prompt`, `negative_prompt`, and `generation_params`.
4. Save each generated clip to `expected_render_path`, usually under `renders/`.
5. Run Review AI on each generated clip record. At minimum verify file exists, duration is readable, aspect ratio matches, and the clip is mapped to the correct `clip_id`.
6. Retry failed clips only when the failure is bounded and retryable.
7. Build `03_video_review_report.json`.
8. Build `04_final_edit_plan.json` from reviewed usable clips, not from the pre-generation plan.
9. Assemble the final video with `ffmpeg`.
10. Run final Review AI on the assembled video and write a concise production report.

## Required Outputs

```text
product_folder/
+-- 02_i2v_prompt_manifest.json
+-- renders/
|   +-- <clip files>.mp4
+-- 03_video_review_report.json
+-- 04_final_edit_plan.json
+-- final_tiktok_ad.mp4
```

## Review AI Contract

```yaml
review_result:
  status: "pass" # pass | retry | ask_user
  failed_checks: []
  retry_instruction: ""
  user_question: ""
```

Use [references/video-workflow-template.md](references/video-workflow-template.md) for config, report, and final edit plan shapes.
