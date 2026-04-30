# Shimeji / Desktop-Pet Sprite Sheet Workflow Notes

Session learning: when the user provides a finished Alkaka-style 2D character and asks to “try generating” animation frames, do not spend a turn only analyzing the image. Extract the minimum stable visual anchors and immediately generate a first sprite sheet.

## First-pass target

Generate a compact 12-frame core sprite sheet before attempting full Shimeji-ee compatibility.

Recommended layout:
- 4 columns × 3 rows
- landscape canvas
- clean white or transparent-looking background
- no text, no labels, no watermark
- full body visible in every cell
- consistent character scale and foot baseline
- keep props simplified unless essential, because extra handheld props reduce cross-frame consistency

## 12-frame order

Left to right, top to bottom:
1. standing idle
2. walking frame A, left foot forward
3. walking frame B, right foot forward
4. jumping upward
5. falling downward
6. landing squash / knees bent
7. sitting
8. sitting and looking upward
9. pinched / dangling as if held from above
10. resisting drag frame A
11. resisting drag frame B
12. sleeping curled up

## Prompt pattern

Use this structure:

```text
Create a 4 columns x 3 rows sprite sheet for a Shimeji-style desktop pet animation. Same exact chibi anime character in every cell, based on this character description: [stable anchors: hair, eyes, head accessory, outfit, shoes, theme]. Keep the same outfit, hair, colors, face, proportions and accessories across all 12 frames.

Sprite sheet requirements: clean white or transparent-looking background, clear grid implied by spacing, no text, no labels, no watermark, full body visible in each cell, character centered in each cell, consistent scale and foot baseline, polished cute game/VTuber sticker style, soft clean anime rendering.

Frame order left to right, top to bottom:
1 [pose]
...
12 [pose]

Simplify or omit handheld props in most frames unless they are essential identity anchors.
```

## Why not full 46 frames first

Standard Shimeji-ee examples often use `shime1.png`–`shime46.png`, but generating all 46 poses at once is unreliable. Character consistency, action readability, and cell clarity degrade quickly. Start with 12, validate style and pose language, then expand to 24 or 46.

## Follow-up outputs

After the sprite sheet is accepted, useful next steps are:
- slice the sheet into 12 individual PNG frames
- remove/transparentize background if needed
- normalize canvas size and foot baseline
- export a preview GIF
- map frames to simplified Shimeji-style action names
