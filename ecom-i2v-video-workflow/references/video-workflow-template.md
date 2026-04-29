# Video Workflow Template

## Private Config

`.product_i2v_config.local.json`

```json
{
  "i2v_provider": "provider-name",
  "model": "model-name",
  "api_key": "private-key"
}
```

Do not commit or copy `api_key` into reports.

## Runtime Loop

For each manifest item:

1. Read `source_image`.
2. Send `prompt`, `negative_prompt`, and `generation_params` to the selected I2V provider.
3. Save output to `expected_render_path` under `renders/`.
4. Record status, provider job id, output path, duration, width, height, retry count, and error if any.

## 03_video_review_report.json

```json
{
  "version": "1.0",
  "clips": [
    {
      "clip_id": "clip_01",
      "source_image": "",
      "render_path": "renders/output_16_tiktok.mp4",
      "status": "pass",
      "usable_trim_in": 0.0,
      "usable_trim_out": 2.0,
      "review_notes": []
    }
  ]
}
```

## 04_final_edit_plan.json

```json
{
  "version": "1.0",
  "stage": "final",
  "platform": "tiktok",
  "total_duration": 14.2,
  "output": {
    "aspect_ratio": "9:16",
    "path": "final_tiktok_ad.mp4"
  },
  "clips": [
    {
      "clip_id": "clip_01",
      "source_video": "renders/output_16_tiktok.mp4",
      "trim_in": 0.0,
      "trim_out": 1.8,
      "timeline_start": 0.0,
      "timeline_end": 1.8,
      "transition": "cut"
    }
  ]
}
```

Use `ffmpeg` to assemble clips after `04_final_edit_plan.json` is created.
