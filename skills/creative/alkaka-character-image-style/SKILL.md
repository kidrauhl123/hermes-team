---
name: alkaka-character-image-style
description: "Generate Alkaka character images in the user's reference-sheet style: diverse original chibi anime human personas, using references when possible and creating fresh characters within that visual system."
version: 1.1.2
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [alkaka, character-design, image-reference, avatar, chibi]
    related_skills: [pixel-art, popular-web-designs]
---

# Alkaka Character Image Style

Use this skill whenever the user asks to generate an “Alkaka形象”, Alkaka avatar, Alkaka role character, or Alkaka-style character sheet/persona.

## Definition

“Alkaka形象” means the style of the user-provided reference examples: a Q版二次元人形角色 / chibi anime human persona, like a polished cute game/VTuber sticker or character-sheet set.

The reference sheet is a **style system**, not a single character template. Generate a new original character that belongs in that system.

## Core Rule

If a reference image is available and the image tool supports references, use the image itself as the style source of truth.

Study the reference sheet for its shared visual language: proportions, line quality, rendering polish, cute expressive face design, compact full-body silhouette, fashion/detail density, clean presentation, and character-sheet feel.

Then create a fresh Alkaka persona that feels like another member of the same lineup, not a redraw of one existing example.

If the current image tool cannot attach reference images, write a prompt that captures the character-set logic without overfitting to any one example.

## Reference Image Handling

- Persistent style anchor: `assets/alkaka-style-reference.jpg`.
- Prefer attaching/passing that reference image directly whenever the image model supports image references.
- If the user provides a newer/better reference, save it as a skill asset/reference file and update this skill to point to it.
- Do **not** store large base64 image blobs inside `SKILL.md`.
- If references cannot be attached, mention that limitation briefly if the user is evaluating fidelity.

## Prompt Strategy

A good Alkaka character prompt needs three layers:

1. **Style family**
   - “single full-body chibi anime human character”
   - “in the style of the user's Alkaka reference sheet”
   - “polished cute game/VTuber sticker look”
   - “oversized expressive eyes, detailed hair and outfit”
   - “clean white background, soft ground shadow”

2. **Original role/persona**
   - Give the character a fresh identity: profession, hobby, field, or fantasy/social role.
   - Prefer cross-domain combinations when useful: e.g. botanist + tiny robot repairer, urban explorer + map archivist, pastry engineer + drone courier.
   - The role should be readable through costume, props, pose, and expression.

3. **Distinct visual cues**
   - Hair color/style/accessory.
   - Eye color/expression/personality.
   - Outfit silhouette and palette.
   - One or two readable props tied to the role.
   - Pose or stance.

## Reference-Image Prompt Template

When direct image-reference input is supported:

```text
Use the provided reference sheet as the Alkaka character style reference. Generate a new original Alkaka [role/persona]. Keep the same chibi anime character-sheet family and polished cute game/VTuber sticker feel. Make the character clearly new through distinct hair, outfit silhouette, palette, expression, pose, and role props. Clean white background, soft ground shadow. No text, no watermark.
```

Example:

```text
Use the provided reference sheet as the Alkaka character style reference. Generate a new original Alkaka urban botanist and tiny-robot repairer. Mint-green short wavy hair with a leaf hairpin, amber eyes, cream utility apron over oversized sage jacket, small tool belt, holding a sprouting plant sensor and a tiny friendly leaf-propeller drone. Clean white background, soft ground shadow. No text, no watermark.
```

## Fallback Prompt Template When References Cannot Be Attached

```text
original Alkaka character: single full-body chibi anime human persona, in the style of the user's Alkaka reference examples, polished cute game/VTuber sticker character-sheet style, oversized expressive eyes, detailed hair and outfit, compact appealing full-body silhouette, clean white background, soft ground shadow. [fresh role/persona]: [hair], [eyes/expression], [outfit silhouette and color palette], [1-2 role props], [pose/personality]. No text, no watermark.
```

## Good Role Ideas

Use these as inspiration, not as a fixed list:

- 城市植物学家 + 微型机器人维修师
- 星际图书管理员 + 纸鹤无人机指挥员
- 深海资料采样员 + 水母灯笼助手
- 甜点工程师 + 糖霜机械臂
- 天气观测员 + 云朵背包
- 赛博考古学家 + 全息罗盘
- 睡眠研究员 + 月亮枕头终端
- 街头滑板信使 + AR地图护目镜
- 咖啡炼金师 + 小型蒸汽仪器
- 折纸建筑师 + 迷你蓝图卷轴

## Fidelity Notes

- Optimize for matching the user's reference-sheet visual language, not for listing everything that could go wrong.
- Keep prompts positive and style-forward. Avoid cluttering prompts with a long negative list derived from prior failed outputs.
- The main creative challenge is balance: same style family, new character identity.
- Avoid near-duplicates of any one reference character; vary role, hair, outfit, palette, props, and pose enough that the result feels like a new member of the lineup.

## Shimeji / Sprite-Sheet Animation Extension

When the user provides an Alkaka-style character image and asks to make it move, generate animation frames, or try a Shimeji/desktop-pet workflow, this skill still applies. Use the character image as the visual anchor, but switch the output goal from a single persona image to a compact sprite sheet.

User preference learned from use: if the user asks to generate the image now, do not spend a full turn only describing or analyzing the character. Extract only the minimum stable anchors needed for prompting, then immediately call the image-generation tool.

Default first pass:
- Create a 4×3 Shimeji-style sprite sheet with 12 core frames, not the full 46-frame Shimeji-ee set.
- Keep the same chibi character, outfit, palette, face, proportions, and key accessories in every cell.
- Use clean white or transparent-looking background, no labels/text/watermark, full body visible, consistent scale and foot baseline.
- Simplify handheld props unless they are essential identity anchors; extra props make multi-frame consistency worse.
- Frame order: standing idle; walking A; walking B; jumping; falling; landing; sitting; sitting looking up; pinched/dangling; resisting drag A; resisting drag B; sleeping curled up.

Detailed reusable notes live in:
- `references/shimeji-sprite-sheet-workflow.md` for the original 12-frame first-pass workflow.
- `references/controlled-shimeji-sprite-generation.md` for the improved controlled action-group workflow: one action at a time, right-facing directional frames only, script-mirrored left-facing frames, baseline/height normalization, GIF/contact-sheet outputs, and walk-cycle foot-alternation rules.
- `references/walk-cycle-8frame-prompt.md` for the reusable 8-frame walk-cycle prompt spec: same 3/4 reference angle, explicit frame-by-frame leg/arm alternation, opposite leading boot in frame 1 vs frame 5, acceptance checklist, and fallback to two verified contact-key poses when a full 8-frame sheet fails.
- `references/oblique-walk-cycle-failures-20260430.md` for session-specific failure notes showing that oblique view helps but does not by itself make pure-AI 8-frame walk cycles reliable.

## Controlled Sprite-Sheet Corrections

Lessons from user correction during desktop-pet experiments:

- Do **not** assume a 12/24-frame mixed-action sheet is production-usable. It is only a rough concept test; mixed actions play like choppy unrelated key poses.
- Do **not** use naive head/body puppet splitting for a full-body chibi character unless real semantic segmentation/inpainting is available; rough splitting can make the character look “腰斩” / cut in half.
- Prefer controlled action groups: `walk_right_8`, `idle_4`, `drag_right_6`, `jump_right_6`, `sit_sleep_6`.
- For directional actions, generate **only one direction** with AI, default right-facing. Create left-facing assets by horizontal mirroring in post-processing. This reduces cost and prevents mixed-direction errors.
- For walk cycles, frame 1 and frame 5 must visibly switch the leading foot. If the second half does not alternate feet, the walk cycle is not usable.
- For chibi legs, explicitly ask for exaggerated boot/leg silhouettes; otherwise foot alternation can be too subtle.
- When the user asks to try a workflow, produce artifacts immediately: generated sheet, normalized GIF, slow GIF, contact sheet, and quality report. Keep explanation brief and tied to observed output.

## Quality Checklist

Before finalizing, verify:

- [ ] If reference-image input is available, the reference sheet was used directly.
- [ ] If references cannot be attached, the prompt clearly states the user's Alkaka reference-example style.
- [ ] The output fits the chibi anime human persona / character-sheet look of the reference examples.
- [ ] The character is original and not a near-duplicate of any one reference character.
- [ ] The persona has a clear role/profession/hobby beyond generic “cute character”.
- [ ] Hair, outfit silhouette, palette, expression, and props are distinctive.
- [ ] Background is clean white or transparent-looking with no text/watermark.
- [ ] If the user criticizes the result, update this skill with the learned correction immediately.
