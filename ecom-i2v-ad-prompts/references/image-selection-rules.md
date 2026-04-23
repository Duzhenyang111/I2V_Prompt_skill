# Image Selection Rules

Use these rules after running `scripts/prefilter_images.py`. The script only performs objective quality screening; the AI review decides ecommerce usefulness and planned video value.

## Two-Level Screening

1. Program prefilter:
   - rejects broken or unreadable files
   - marks low-resolution, too dark, too bright, blurry, extreme-ratio, and near-duplicate images for review
   - writes `image_prefilter_report.json`
2. AI semantic screening:
   - reviews the report and inspects actual images
   - decides which images are usable for prompt generation
   - assigns ad roles and selection scores

## AI Screening Output

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

## Selection Score Guide

- `90-100`: strong candidate for planned short ad sequence
- `75-89`: usable for prompt generation, but not always needed in the 15s planned cut
- `60-74`: usable only if the image set lacks better coverage
- `<60`: reject unless the user explicitly asks to keep it

## Accept Images That

- show the product clearly
- preserve sellable product identity
- add a distinct view, function, scene, or scale cue
- are suitable for controlled 5-10 second I2V generation
- help build a 4-6 clip plan under 15 seconds

## Reject Images That

- are unreadable, broken, extremely small, or mostly blank
- hide or crop the product so the key selling point is unclear
- contain severe watermarks or text artifacts that will likely regenerate badly
- are near duplicates of stronger images
- rely on risky human or pet details unless those details are essential to scale or lifestyle proof

## Manual Review Cases

Mark an image as `needs_manual_review` when:

- the product is useful but the source has obvious AI artifacts
- the image has a strong role but also watermarks or distorted text
- the image is near-duplicate but might be the better composition
- the image includes people, pets, hands, food waste, or open lids where generation risk is higher

## Selection Priorities For planned_final_edit_plan.json

For the 15-second planned cut, adapt selection to the platform using `platform-presets.md`.

Do not include every accepted image in `planned_final_edit_plan.json`. Generate prompts for all accepted images when useful, but select only the strongest 4-6 planned clips for the intended final ad.
