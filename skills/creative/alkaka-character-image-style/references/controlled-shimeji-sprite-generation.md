# Controlled Shimeji / Desktop-Pet Sprite Generation

Session learning from an Alkaka desktop-pet animation experiment: directly asking an image model to generate a 12/24-frame mixed-action sprite sheet often produces choppy, inconsistent GIFs. A better class-level workflow is controlled, action-group sprite generation with deterministic post-processing.

## What failed

- **Mixed-action 12/24-frame sheets**: Putting idle, walk, jump, sit, drag, sleep into one sheet creates unrelated key poses rather than a smooth animation.
- **AI redraws every frame**: Faces, hair, clothing details, scale, foot placement, and center drift across frames.
- **Naive puppet split**: Roughly splitting a full-body character into head/body layers can look like the character was cut in half unless real semantic segmentation, inpainting, and rigging are available.
- **Generating both directions**: Asking the AI to produce left- and right-facing motion in one pass causes direction errors; heads may face the wrong direction.

## Recommended workflow

1. Generate **one action group at a time**, not a full Shimeji set.
   - `walk_right_8`
   - `idle_4`
   - `drag_right_6`
   - `jump_right_6`
   - `sit_sleep_6`

2. For directional actions, generate **only one direction**, default **right-facing**.
   - Left-facing frames are produced by deterministic horizontal mirroring.
   - This halves image-generation cost and avoids mixed-direction confusion.

3. Use a fixed layout per action group:
   - 4 frames: `1x4` or `4x1`
   - 8 frames: `4x2`
   - 12 frames: `4x3`
   - Avoid 16+ until 8/12-frame groups are stable.

4. Post-process with a script:
   - fixed grid cutting
   - near-white background alpha masking
   - subject bbox detection
   - normalize subject height
   - normalize foot baseline
   - center/pivot normalization
   - generate right/left GIFs and contact sheets
   - emit `quality_report.json`

## Walk-cycle rules

For an 8-frame right-facing walk cycle, the frame semantics must be explicit:

1. `CONTACT A`: near/front visible leg forward toward screen-right, far leg back.
2. `DOWN A`: weight low on near/front visible leg, far leg starts passing.
3. `PASSING A`: feet close under body, far leg passes forward.
4. `UP A`: body highest, far leg swinging forward, near leg pushing off.
5. `CONTACT B`: far leg forward toward screen-right, near/front visible leg back. **Must visibly be the opposite foot from frame 1.**
6. `DOWN B`: weight low on far leg, near leg starts passing.
7. `PASSING B`: feet close under body, near leg passes forward.
8. `UP B`: body highest, near leg swinging forward, ready to loop.

Critical prompt rule: frame 1 and frame 5 must visibly switch the leading foot. If they do not, the cycle is not production-usable.

For chibi characters, ask for exaggerated boot/leg silhouettes:

```text
exaggerated chibi walk, wide leg separation, large visible boot silhouette,
front boot clearly ahead of body, rear boot clearly behind body
```

## Direction prompt rule

Use wording like:

```text
CRITICAL DIRECTION RULE: the character is facing and walking toward screen-right in EVERY frame. Head and eyes look to the RIGHT in every frame. Use a right-facing 3/4 side view only. Do not make front-facing poses.
```

Then mirror in post-processing:

```text
walk_left_01.png = mirror(walk_right_01.png)
...
walk_left_08.png = mirror(walk_right_08.png)
```

## Quality report fields

At minimum, report:

```json
{
  "raw_height_deviation_percent": [],
  "raw_center_deviation_px": [],
  "raw_bottom_deviation_px": [],
  "outputs": {
    "right_gif": "...",
    "left_gif": "...",
    "right_frames": "...",
    "left_frames": "...",
    "contact_sheet": "..."
  }
}
```

Useful thresholds:
- Height deviation under ~3% is good.
- Baseline/bottom deviation under ~10px is workable after normalization.
- Center deviation can be large during walking because legs extend; normalize by chosen pivot, not raw bbox center alone.

## User preference learned

When experimenting, show concrete artifacts quickly: generated sheet, normalized GIF, slow GIF, contact sheet, and quality report. Avoid long conceptual explanation when the user asks to “try it.” If an output is visibly bad, acknowledge it directly and adjust the workflow rather than defending it.

If the user says the approach is being overcomplicated, return to the simplest testable hypothesis they named and run that experiment before proposing heavier rigging/engineering. For Alkaka/Shimeji walk cycles, that means validating the 3/4 oblique pure-AI sprite-sheet attempt first, then only escalating after the contact-frame checks fail.
