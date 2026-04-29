# Prompt Template

Use these templates as output shapes. Fill them with concrete, image-specific decisions.

## Image Screening Template

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

## Product-Level Strategy Template

```yaml
商品级广告策略:
  核心路线: ""
  转化目标: ""
  受众感受: ""
  推荐画幅: ""
  节奏建议: ""
  视觉风险:
    - ""
```

## Sequence Table Template

```yaml
图片分镜规划表:
  - image_id: ""
    detected_view: ""
    sequence_role: ""
    clip_goal: ""
    placement_note: ""
```

## Per-Image Analysis Card Template

```yaml
- image_id: ""
  中文分析卡:
    detected_view: ""
    sequence_role: ""
    marketing_job: ""
    recommended_duration: "6s"
    recommended_aspect_ratio: ""
    camera_motion: ""
    lens_feel: ""
    background_strategy: ""
    lighting_strategy: ""
    product_focus: ""
    must_keep:
      - ""
    risk_controls:
      - ""
    reasoning: ""
  generation:
    prompt: >
      Create a commercially realistic image-to-video advertisement shot for [product].
      Use this image as a [sequence role] shot. Preserve the exact product identity,
      proportions, materials, and key design features. [Describe camera movement,
      framing, product focus, background handling, lighting, motion intensity, and
      commercial mood in concrete terms.]
    negative_prompt: >
      deformation, extra objects, text artifacts, logo distortion, incorrect
      proportions, floating parts, awkward hands, overly dramatic motion
    generation_params:
      recommended_duration_seconds: 6
      recommended_aspect_ratio: ""
      motion_intensity: "subtle"
      model_notes: ""
```

## Dual-Platform Generation Template

Use this when the user requests both TikTok and Amazon:

```yaml
- image_id: ""
  中文分析卡:
    detected_view: ""
    sequence_role: ""
    marketing_job: ""
    reasoning: ""
  platform_variants:
    tiktok:
      generation:
        prompt: ""
        negative_prompt: ""
        generation_params:
          recommended_duration_seconds: 0
          recommended_aspect_ratio: ""
          motion_intensity: ""
          model_notes: ""
    amazon:
      generation:
        prompt: ""
        negative_prompt: ""
        generation_params:
          recommended_duration_seconds: 0
          recommended_aspect_ratio: ""
          motion_intensity: ""
          model_notes: ""
```

Use `platform-presets.md` to fill platform-specific values.

## Planned Edit Plan Summary Template

```yaml
中文预剪辑说明:
  成片目标: ""
  推荐顺序:
    - ""
  节奏设计: ""
  转场建议: "默认使用 cut，除非执行层另有支持"
  15秒版本建议: ""
  重要限制: "这只是生成前预案，不是 ffmpeg 最终执行计划；真实 final_edit_plan.json 需要在小视频生成后通过视频质检再生成。"
```

## Review AI Template

Use this after each major AI-authored stage. Review AI evaluates the current stage output and returns only this schema:

```yaml
Review AI:
  review_result:
    status: "pass"
    failed_checks: []
    retry_instruction: ""
    user_question: ""
```

Possible statuses:

```yaml
Review AI:
  review_result:
    status: "pass"
    failed_checks: []
    retry_instruction: ""
    user_question: ""
---
Review AI:
  review_result:
    status: "retry"
    failed_checks:
      - "The prompt invents an unsupported product feature."
    retry_instruction: "Rewrite the per-image prompt using only visible product details and the provided selling points."
    user_question: ""
---
Review AI:
  review_result:
    status: "ask_user"
    failed_checks:
      - "The platform request is unsupported or ambiguous."
    retry_instruction: ""
    user_question: "Should this be optimized for TikTok, Amazon, or both?"
```

Review AI must not rewrite the stage output directly. It only decides `pass`, `retry`, or `ask_user`, then provides the narrow instruction needed for the next action.

## planned_final_edit_plan.json Template

```json
{
  "version": "1.0",
  "stage": "pre_generation",
  "total_duration": 14.5,
  "output": {
    "aspect_ratio": "4:5"
  },
  "clips": [
    {
      "clip_id": "clip_01",
      "source_image_id": "image_03.jpg",
      "sequence_role": "hook opener",
      "expected_render_path": "renders/image_03_tiktok.mp4",
      "source_video": "renders/output_3.mp4",
      "planned_trim_in": 0.8,
      "planned_trim_out": 2.8,
      "timeline_start": 0.0,
      "timeline_end": 2.0,
      "transition": "cut"
    },
    {
      "clip_id": "clip_02",
      "source_image_id": "image_02.jpg",
      "sequence_role": "feature proof",
      "expected_render_path": "renders/image_02_tiktok.mp4",
      "source_video": "renders/output_2.mp4",
      "planned_trim_in": 1.0,
      "planned_trim_out": 3.5,
      "timeline_start": 2.0,
      "timeline_end": 4.5,
      "transition": "cut"
    }
  ]
}
```

## planned_final_edit_plan.json Rules

- `total_duration` must be numeric and `<= 15.0`
- `stage` must equal `pre_generation`
- every clip must include `source_image_id`, `sequence_role`, and `expected_render_path`
- every `source_video` must point to the expected generated clip path, not an image path
- before generation exists, `source_video` should match `expected_render_path`
- `planned_trim_out` must be greater than `planned_trim_in`
- `timeline_end` must be greater than `timeline_start`
- clips must be listed in ascending timeline order
- first version should use `cut` unless the user explicitly asks for a different transition system
- this file is a generation and assembly intention, not the final executable timeline for `ffmpeg`
- after generated videos are reviewed, a second-stage workflow must convert actual usable video ranges into `final_edit_plan.json`

## English Prompt Quality Rules

- Name the product or clearly identify it by category.
- Tie the shot to its role in the ad.
- Specify camera movement with one dominant motion.
- Specify what the background should do.
- Specify how lighting should support the product.
- Use commerce-safe realism language.
- Keep negative constraints in `negative_prompt`, not mixed into the positive prompt.
