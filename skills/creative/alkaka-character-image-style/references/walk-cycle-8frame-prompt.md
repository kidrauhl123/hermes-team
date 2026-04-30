# Alkaka / Shimeji 8-Frame Walk-Cycle Prompt Spec

Use this reference when an Alkaka-style character image needs a usable 8-frame walk animation for a desktop pet / Shimeji workflow.

Status: reusable prompt/spec draft based on user correction and observed failures. Treat as a production candidate, but still verify with generated artifacts before calling it final.

## Core idea

For desktop-pet walking, the hard part is not only "more frames". The AI must be forced to create a readable walk cycle:

- Same character identity in every frame.
- Same 3/4 right-facing direction in every frame, matching the provided reference angle.
- Frame 1 and frame 5 must visibly swap the leading foot.
- Opposite arm/leg swing: left leg forward with right arm forward; right leg forward with left arm forward.
- Feet/boots need exaggerated readable silhouettes because chibi legs are short.
- Same canvas, same scale, same foot baseline, no cropping.

Generate only one direction, default right-facing. Create the opposite direction by horizontal mirroring in post-processing.

## Recommended layout

Prefer `1 row x 8 columns` for prompt clarity and easy cutting:

```text
[01][02][03][04][05][06][07][08]
```

If the image model struggles with very wide images, use `2 rows x 4 columns`, but preserve the same frame order left-to-right, top row first.

## Direction wording

Use "same three-quarter side view as the reference" instead of only "side view". For Alkaka-style chibi characters, a pure side view can lose face appeal, while a front view breaks walking direction.

Recommended phrase:

```text
same 3/4 right-facing side angle as the reference, body walking toward screen-right, head and eyes also facing screen-right, not front-facing, not walking toward viewer
```

## 8-frame semantics

Use explicit per-frame semantics in the prompt. Do not rely on "walking animation" alone.

1. `CONTACT A`: left leg / near visible leg forward toward screen-right; right leg back. Right arm forward, left arm back.
2. `DOWN A`: body slightly lower, weight on the forward left/near leg; rear right leg begins to pass; arms near middle.
3. `PASSING A`: feet close under body; right/rear leg passes forward; body centered.
4. `UP A`: body slightly higher; right leg swinging forward; left leg pushing back; left arm starts forward.
5. `CONTACT B`: right leg / far leg forward toward screen-right; left leg back. Left arm forward, right arm back. This must be visibly the opposite foot from frame 1.
6. `DOWN B`: body slightly lower, weight on the forward right/far leg; rear left leg begins to pass; arms near middle.
7. `PASSING B`: feet close under body; left/rear leg passes forward; body centered.
8. `UP B`: body slightly higher; left leg swinging forward; right leg pushing back; returns naturally to frame 1.

Note: If the provided character angle makes "near/far" ambiguous, use visual boot positions: frame 1 has the boot on the viewer-near side forward; frame 5 has the other boot forward.

## Strong prompt template

```text
Use the provided character as the exact identity reference. Create a clean sprite sheet for a desktop pet walk cycle: 1 row x 8 columns, eight full-body frames, no labels, no text, no watermark, clean white or transparent-looking background.

CRITICAL IDENTITY RULE: same chibi anime character in every frame, same face, same hair shape, same hair accessory, same outfit, same colors, same body proportions, same boots, same pouch/accessories. Do not redesign the character between frames.

CRITICAL DIRECTION RULE: every frame uses the same 3/4 right-facing side angle as the reference. The character is walking toward screen-right. Head, eyes, torso, and feet all face screen-right. Do not create front-facing poses. Do not rotate the character toward the viewer.

CRITICAL WALK-CYCLE RULE: make a readable 8-frame loop with opposite arm-and-leg motion. When the left/near leg steps forward, the right arm swings forward. When the right/far leg steps forward, the left arm swings forward. Frame 1 and frame 5 must visibly swap which boot is leading.

Frame order from left to right:
1 CONTACT A: left/near boot forward toward screen-right, right/far boot back, right arm forward, left arm back.
2 DOWN A: body slightly lower, weight on the forward left/near boot, rear right/far boot begins passing, arms near middle.
3 PASSING A: both boots closer under body, right/far boot passing forward, body centered.
4 UP A: body slightly higher, right/far boot swinging forward, left/near boot pushing back, left arm starts forward.
5 CONTACT B: right/far boot forward toward screen-right, left/near boot back, left arm forward, right arm back. This frame must be the opposite-foot version of frame 1.
6 DOWN B: body slightly lower, weight on the forward right/far boot, rear left/near boot begins passing, arms near middle.
7 PASSING B: both boots closer under body, left/near boot passing forward, body centered.
8 UP B: body slightly higher, left/near boot swinging forward, right/far boot pushing back, ready to loop back to frame 1.

CRITICAL SPRITE RULE: full body visible in every cell, no cropping, same scale in every cell, feet on the same horizontal baseline, character centered in each cell, consistent spacing between cells. Exaggerate the boot silhouettes and leg separation so the alternating steps are obvious despite chibi proportions.
```

## Negative constraints

Add only if the model responds well to negatives:

```text
Avoid front view, avoid random poses, avoid idle standing duplicates, avoid same foot leading in every frame, avoid both feet glued together, avoid changing outfit details, avoid changing hair, avoid cropped feet, avoid labels or frame numbers, avoid extra characters.
```

## Acceptance checklist

A generated walk sheet is usable only if:

- [ ] There are exactly 8 frames in the requested order.
- [ ] All frames keep the same character identity and outfit.
- [ ] Every frame faces the same direction.
- [ ] Frame 1 and frame 5 clearly show opposite leading boots.
- [ ] Arms swing opposite to legs, or at least do not contradict the foot cycle.
- [ ] The second half is not just a duplicate of the first half: frame 1 must not match frame 5, frame 2 must not match frame 6, etc.
- [ ] Feet are visible and not cropped.
- [ ] Character scale and foot baseline are consistent enough for post-processing.
- [ ] The loop from frame 8 back to frame 1 is plausible.

If any of these fail, regenerate or reduce the task scope before spending time on mirroring or final integration.

## Oblique-view lesson

The user's intuition is valid: a 3/4 oblique view can make two chibi feet easier to distinguish than a strict side view. However, session testing showed that oblique view alone does not make a single 8-frame pure-AI sheet reliable. The model may still repeat the first half-cycle or draw same-side arm/leg motion (`顺拐`).

If a full 8-frame prompt repeatedly fails, do **not** immediately over-explain or force a bone-rig workflow. Try the smaller no-rig workflow first:

1. Generate only the two contact-key poses A/B.
2. Verify A and B are true opposites: opposite leading boots and opposite forward arms.
3. Then ask for transition frames A→B and B→A in smaller batches.

Detailed failure notes: `references/oblique-walk-cycle-failures-20260430.md`.
