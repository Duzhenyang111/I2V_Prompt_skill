# Prompt Manifest Template

Write `02_i2v_prompt_manifest.json` as strict JSON.

```json
{
  "version": "1.0",
  "platform": "tiktok",
  "product_name": "",
  "product_folder": "",
  "output_dir": "renders",
  "items": [
    {
      "clip_id": "clip_01",
      "image_id": "output (16).png",
      "source_image": "C:\\\\abs\\\\path\\\\output (16).png",
      "sequence_role": "hook opener",
      "expected_render_path": "renders/output_16_tiktok.mp4",
      "prompt": "",
      "negative_prompt": "",
      "generation_params": {
        "recommended_duration_seconds": 6,
        "recommended_aspect_ratio": "9:16",
        "motion_intensity": "moderate",
        "model_notes": ""
      }
    }
  ]
}
```

Rules:

- `items` order must match the intended ad sequence.
- `source_image` must be an absolute path.
- `expected_render_path` must be relative to `product_folder` unless the user asks otherwise.
- Keep all generation text in `prompt` and `negative_prompt`; keep human explanation in `01_storyboard_plan.md`.
- Do not include API keys.
