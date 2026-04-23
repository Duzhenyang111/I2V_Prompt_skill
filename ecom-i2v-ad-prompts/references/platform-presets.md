# Platform Presets

Optimize primarily for TikTok and Amazon. If another platform is provided, map it to the closer of these two patterns instead of inventing a third full workflow.

## Platform Decision

- Use `TikTok` when the goal is paid social, short-video feed discovery, creator-style demonstration, fast hook, or vertical ad testing.
- Use `Amazon` when the goal is ecommerce listing support, Sponsored Brands Video, product page media, marketplace conversion, or product-first trust.
- If the user says both `TikTok` and `Amazon`, generate platform-specific prompt variants and planned edit plans. Do not force one compromise prompt.

## TikTok Rules

Primary objective: stop scrolling, explain value quickly, and make the product feel useful in daily life.

Defaults:

- aspect ratio: `9:16`
- total planned cut: `10-15s`
- selected planned clips: `4-6`
- opening clip: `1.2-2.0s`
- feature proof clips: `2.0-3.0s`
- lifestyle proof clips: `2.0-3.0s`
- closing clip: `1.0-2.0s`
- motion intensity: `moderate` unless the source image is risky

Prefer images that:

- show the product in a real use context
- include a clear before/after, open/close, transform, capacity, or ease-of-use cue
- can support a fast first-second hook
- show scale, hands, people, or home context without severe anatomy risk

Prompt style:

- start with the product benefit visible in the first second
- use direct movement language: `quick push-in`, `smooth lateral reveal`, `natural handheld-style drift`
- keep the product readable even when motion is more energetic
- make scene changes feel like short-form ad beats, not cinematic montage

Avoid:

- slow luxury pacing in the first 3 seconds
- static product-only shots with no use or context
- excessive camera spin, crash zoom, whip pan, or motion that can deform the product
- tiny product framing that reads poorly on mobile

## Amazon Rules

Primary objective: build trust, product clarity, and conversion confidence.

Defaults:

- aspect ratio: `4:5` for feed-style marketplace video; `1:1` for square placements; use `16:9` only when the user asks for widescreen media
- total planned cut: `10-15s`
- selected planned clips: `4-5`
- opening clip: `2.0-2.5s`
- hero reveal clip: `2.5-3.0s`
- feature proof clips: `2.5-3.0s`
- closing packshot: `2.0-2.5s`
- motion intensity: `subtle` or `moderate`

Prefer images that:

- show the full product clearly
- explain size, compartments, material, controls, or functional details
- have clean backgrounds and low generation risk
- can support a trustworthy packshot or feature-proof sequence

Prompt style:

- preserve exact product identity and dimensions
- use restrained camera movement: `slow centered push-in`, `controlled arc`, `subtle slider move`
- emphasize sellable realism, clean lighting, and product-first composition
- avoid unsupported claims and invented features

Avoid:

- overly social, chaotic, or influencer-like scene language
- stylized props that distract from product comprehension
- heavy transitions or aggressive motion
- risky human/pet emphasis unless it directly supports scale or usage

## Dual-Platform Output

When both TikTok and Amazon are requested:

1. Run one shared image screening pass.
2. Generate one shared per-image analysis card when the image facts are the same.
3. Generate separate platform variants for:
   - `prompt`
   - `negative_prompt` only when risk changes
   - `generation_params`
   - `planned_final_edit_plan.json`

Use the dual-platform output schema in `prompt-template.md`.

For planned edit plans, output:

- `planned_final_edit_plan_tiktok.json`
- `planned_final_edit_plan_amazon.json`

## planned_final_edit_plan Selection Priority

TikTok priority:

1. one scroll-stopping `hook opener`
2. one fast `feature proof`
3. one practical `lifestyle credibility` or use-context shot
4. one `detail reinforcement` shot if it proves the main selling point
5. one short `packshot closer`

Amazon priority:

1. one clear `hero reveal`
2. one product-first `feature proof`
3. one `detail reinforcement` shot for material, capacity, compartments, or dimensions
4. one restrained `lifestyle credibility` shot if it improves trust
5. one clean `packshot closer`

## Category Biases

### Kitchen and dining

- TikTok: show fast utility, clean transformations, easy use, or problem-solution framing.
- Amazon: show full product form, clean surfaces, capacity, dimensions, and trustworthy finish.

### Storage and organization

- TikTok: prioritize visible tidiness payoff and fast spatial transformation.
- Amazon: prioritize capacity, footprint, compartments, and stable product geometry.

### Cleaning tools and accessories

- TikTok: emphasize satisfying use and before/after clarity.
- Amazon: emphasize practical function, hygiene, materials, and controlled product proof.

### Bathroom and home comfort

- TikTok: emphasize daily-life comfort and quick aesthetic upgrade.
- Amazon: emphasize calm, neat, low-risk visuals and clear product benefit.
