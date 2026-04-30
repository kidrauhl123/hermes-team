# Oblique 8-Frame Walk-Cycle Failure Notes (2026-04-30)

Context: user wanted to verify whether a pure image-generation workflow could turn an Alkaka-style chibi character image into a Shimeji/desktop-pet walk animation without a bone/puppet rig. The hypothesis was that a 3/4 oblique view would make left/right feet easier to distinguish than a strict side view.

## What was tested

Several pure-AI `4x2` / 8-frame walk sprite sheets were generated from a chibi botanist/mechanic character reference, then cut into frames, normalized to a common baseline, exported as GIFs, and visually checked.

Prompts attempted:

1. General 3/4 front-oblique right-walk prompt with explicit frame 1 left foot forward/right hand forward and frame 5 right foot forward/left hand forward.
2. Same, but adding left/right boot identity markers so the model and reviewer could distinguish feet.
3. Same, but replacing character-left/right language with viewer/image-side language:
   - frame 1: image-left boot forward + image-right fist forward
   - frame 5: image-right boot forward + image-left fist forward

## Observed failures

- The model often duplicated the first half-cycle into the second half: frame 1 ~= frame 5, frame 2 ~= frame 6, etc.
- Even when the leading foot changed, arms often became same-side/same-forward (`顺拐`) rather than opposite arm/leg swing.
- The model treated "8-frame walk cycle" as eight similar cute walking poses, not a mechanically coherent gait.
- Image-side directions improved prompt clarity but did **not** reliably force frame 5 to become the opposite-foot contact pose.
- Some sheets had cell-edge/cropping fragments after generation, so grid cutting alone is not enough for final quality.

## Important user correction

The user objected that the assistant was overcomplicating the problem and asked to return to the earlier 3/4 oblique-view idea before using a skeleton/puppet method. Future responses should acknowledge that the oblique idea is reasonable and test it directly, but should not overclaim success unless frame 1 vs frame 5 and opposite arms pass visual inspection.

## Practical takeaway

A single pure-AI prompt for a full 8-frame walk sheet is **not yet reliable enough** for production, even in a 3/4 oblique view. The next no-rig workflow to try is:

1. Generate only two clean contact-key poses first:
   - A: left/image-left boot forward + opposite/right arm forward.
   - B: right/image-right boot forward + opposite/left arm forward.
2. Verify A and B are true opposites before creating any GIF.
3. Then generate/interpolate A→B and B→A transition frames in smaller batches.
4. Only after the contact poses are correct, cut/normalize/export GIF/contact sheet.

This remains an AI frame-animation workflow, not a bone rig, but reduces the model's tendency to fake an 8-frame cycle by repetition.

## Acceptance rule reinforced

For any 8-frame walk cycle, do not call it usable unless:

- frame 1 and frame 5 have opposite leading boots;
- the forward arm is opposite the leading boot in both contact poses;
- the second half is not a duplicate of the first half;
- the GIF reads as alternating feet, not one foot repeatedly stepping.
