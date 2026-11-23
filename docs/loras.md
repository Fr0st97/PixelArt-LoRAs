# LoRA catalog

All LoRAs are for **Krea-2**: trained on Krea-2 Raw, used with **Krea-2 Turbo** (8 steps, no CFG).
Each LoRA draws one kind of game graphics as pixel art in a top-down oblique 45° view, on a plain gray
(128, 128, 128) background, at a fixed pixel scale so the result can be shrunk back to game size without loss.

Every prompt:

- starts with the LoRA's **trigger word**,
- continues with the LoRA's fixed **layout text** (copy it exactly, the LoRA learned it word for word),
- then the **kind** and a short **description** of the object in plain English,
- ends with `plain gray background` (outfits: a color request and `plain magenta background`),
- then the generation options: `--w <width> --h <height> --s 8 --l 1 --d <seed>`.

`--s 8 --l 1` means 8 denoising steps and guidance 1 (no CFG), the Turbo settings. `--d` is the seed: the same
prompt with the same seed gives the same image. 20 example wishes per LoRA are in `prompts/<lora>/examples.txt`.

Names: the LoRA in the first column of the table below is the model **Krea 2 PixelArt <LoRA>** and the file
`Krea2-PixelArt-<LoRA>.safetensors` (e.g. flora: Krea 2 PixelArt flora, `Krea2-PixelArt-flora.safetensors`).
They are derivatives of Krea 2, not official Krea products.

Status legend: **good** (checked by eye, usable), **usable** (works with known limits), **not evaluated**
(trained, few results looked at), **in training** (results not ready when this was written).

## Overview

| LoRA | Trigger | What it draws | Image | Pixel scale | Status |
|---|---|---|---|---|---|
| flora | `blnr_flora` | trees, plants, potted plants, mushrooms | 1024×1024, one object | ×16 | good |
| sheets | `blnr_sheet` | 2×2 sheets: lamps (unlit/lit), wall hangings, furniture in 4 directions | 1024×1024 | ×8 | not evaluated |
| nature | `blnr_nature` | rocks, crystals, bones, dead wood | 1024×1024, one object | ×16 | not evaluated |
| pairs | `blnr_pair` | an object in two versions side by side: two directions, or unlit/lit | 1024×1024 | ×8 | not evaluated |
| equipment | `blnr_eq` | 2×2 matching equipment sets (weapons, armor, mage items) | 1024×1024 | ×16 | not evaluated |
| accessories | `blnr_accessory` | amulets, rings, backpacks | 1024×1024, one item | ×16 | not evaluated |
| consumables | `blnr_utility` | runes, potions, food, tools, valuables | 1024×1024, one item | ×16 | usable |
| loot | `blnr_loot` | monster loot items | 1024×1024, one item | ×16 | not evaluated |
| ground | `blnr_ground` | ground tile sets: tiles with matching borders on a winding path | 1024×1024, 4×4 tiles | ×8 | not evaluated |
| corpses | `blnr_corpse` | a monster standing plus 3 corpse stages | 1024×1024, 2×2 | ×8 | not released yet |
| walls | `blnr_wall` | wall sets in 4 parts, stairs, floor openings, ladders | 1024×1024, 2×2 | ×6 | good (wall parts) |
| monsters-small | `blnr_mob` | small monster walk cycle: idle + 2 walk frames, front and back | 1152×768, 3×2 cells of 48 | ×8 | not evaluated |
| monsters-medium | `blnr_mob` | medium monster walk cycle | 1536×1024, 3×2 cells of 64 | ×8 | good |
| monsters-large-biped | `blnr_mob` | large two-legged monster walk cycle | 1920×1280, 3×2 cells of 80 | ×8 | very good |
| monsters-large | `blnr_mob` | large monster walk cycle, other shapes | 1920×1280, 3×2 cells of 80 | ×8 | very good |
| outfits | `blnr_outfit` | player character walk cycle: idle + 2 walk frames, front and back | 1536×1024, 3×2 cells of 64, magenta background | ×8 | excellent |

"Pixel scale ×8" means one game pixel is an 8×8 block in the image: a 64×64 game sprite fills 512×512.
Post-processing ([postprocessing.md](postprocessing.md)) finds this grid and shrinks the image back.

## flora

Single object (tree, plant, pot, mushroom), drawn as a 64×64 game sprite at ×16.

```
blnr_flora, pixel art game object, top-down oblique 45 degree view, tree leaning toward the upper left, fir tree, dense dark green conical crown, no visible trunk, plain gray background --w 1024 --h 1024 --s 8 --l 1 --d 42
blnr_flora, pixel art game object, top-down oblique 45 degree view, plant in a pot, small clay flower pot with a thin green leafy plant, plain gray background --w 1024 --h 1024 --s 8 --l 1 --d 43
```

Kinds used in training: `tree leaning toward the upper left`, `plant`, `plant in a pot`, `mushroom`.
Holds the 45° perspective well. Trees always lean toward the upper left, like the game's trees.

## sheets

2×2 sheet of one object. Three layouts; copy the layout text exactly:

- lamps: `top row facing south, bottom row facing east, left column unlit, right column lit, lamp`
- wall decorations: `top left hung on a north wall facing south, top right hung on a west wall facing east, bottom left lying on the floor as a loose item, bottom right empty, wall decoration`
- furniture: `top left facing south, top right facing east, bottom left facing north seen from the back, bottom right facing west seen from the back, furniture standing on the floor`

```
blnr_sheet, pixel art game sprite sheet, 2x2 grid, top-down oblique 45 degree view, top row facing south, bottom row facing east, left column unlit, right column lit, lamp, small round iron wall lamp, mounted on a wall, plain gray background --w 1024 --h 1024 --s 8 --l 1 --d 42
```

Known limits: unlit/lit works for all lamps; south and east of lamps are often identical; about 2/3 of
furniture gets 4 different directions, cabinets and dressers often repeat one direction.

## nature

Single object, ×16. Kinds: `rock`, `crystal`, `bones lying on the ground`, `dead wood lying on the ground`.

```
blnr_nature, pixel art game object, top-down oblique 45 degree view, rock, large smooth grey boulder shaped like an egg, plain gray background --w 1024 --h 1024 --s 8 --l 1 --d 42
```

## pairs

Two versions of one object side by side (left and right half, each a 64×64 sprite, ×8). Two layouts:

- `direction pair, left: facing south with the front facing down, right: facing east with the front facing right` (statues, decorations, chests, furniture)
- `unlit and lit pair, left: unlit, right: lit, no direction, looks the same from every side` (light sources)

```
blnr_pair, pixel art game object pair, top-down oblique 45 degree view, direction pair, left: facing south with the front facing down, right: facing east with the front facing right, statue, huntress statue, grey stone woman archer drawing a bow on a square pedestal, plain gray background --w 1024 --h 1024 --s 8 --l 1 --d 42
```

Kinds used: `statue`, `decoration`, `light source`, `container`, `furniture standing on the floor`.

## equipment

2×2 sheet of four matching 32×32 inventory items, ×16. **No perspective text** in the prompt (inventory icons
are flat). Layouts:

- knight: `top left sword, top right axe, bottom left club, bottom right shield, all pieces share one matching design, knight weapon set`
- paladin: `top left bow, top right crossbow, bottom left arrow, bottom right bolt, all pieces share one matching design, paladin weapon set`
- armor: `top left helmet, top right armor, bottom left legs, bottom right boots, all pieces share one matching design, armor set`
- mage: `top left wand, top right rod, bottom left sorcerer spellbook, bottom right druid spellbook, left column one sorcerer set, right column one druid set, mage weapon set`

```
blnr_eq, pixel art game inventory item sheet, 2x2 grid, top left helmet, top right armor, bottom left legs, bottom right boots, all pieces share one matching design, armor set, frozen ice set, plain gray background --w 1024 --h 1024 --s 8 --l 1 --d 8026
```

## accessories, consumables, loot

One inventory item at its real size in the middle of the image, ×16, no perspective text.

| LoRA | Trigger and kind text |
|---|---|
| accessories | `blnr_accessory, pixel art game inventory item, ` + `amulet or necklace` / `ring` / `backpack or bag` |
| consumables | `blnr_utility, pixel art game inventory item, ` + `magic rune stone` / `potion` / `food` / `tool` / `valuable treasure` |
| loot | `blnr_loot, pixel art game inventory item, monster loot` |

```
blnr_utility, pixel art game inventory item, potion, small red flask with a cork, plain gray background --w 1024 --h 1024 --s 8 --l 1 --d 42
blnr_loot, pixel art game inventory item, monster loot, green hydra head, plain gray background --w 1024 --h 1024 --s 8 --l 1 --d 43
```

Tip: describe shape, colors and symbol plainly. If the item ignores your description, lower the LoRA multiplier
to 0.7 (keeps less of the style, follows the prompt more). A custom item is just a new line in the same form, e.g.
`blnr_utility, pixel art game inventory item, magic rune stone, irregular rounded dark charcoal rune stone with a thick glowing purple rim around its whole edge, a large glowing purple paw print outline in the middle, a small purple spiral inside the big pad, plain gray background --w 1024 --h 1024 --s 8 --l 1 --d 9430`.

## ground

One ground type as a 4×4 sheet of 32×32 tiles (×8): plain tiles and border pieces arranged as a winding path
with gray around it.

```
blnr_ground, pixel art game ground tile sheet, 4x4 grid of tiles, top-down oblique 45 degree view, ground tiles forming a winding path from the bottom left to the top right edge, with matching border edges and corners, empty gray area around the path, green grass, plain gray background --w 1024 --h 1024 --s 8 --l 1 --d 42
```

## corpses

Not released yet; the weights are not shared.

2×2 sheet: a monster standing, then its fresh corpse, decaying corpse and remains (×8).

```
blnr_corpse, pixel art game monster corpse sheet, 2x2 grid, top-down oblique 45 degree view, top left the living monster standing idle facing south, top right its fresh corpse, bottom left the decaying corpse, bottom right the remains, humanoid monster, green goblin with a rusty dagger, plain gray background --w 1024 --h 1024 --s 8 --l 1 --d 43
```

## walls

Pixel scale ×6 (1024 is not divisible by 6, the grid starts 2 pixels in; the post-processing handles it).

- wall set: `4 separate wall parts, top left horizontal wall segment, top right vertical wall segment, bottom left thin corner pole, bottom right corner joint, wall`
- stairs: `stairs going up in separate cells, top left facing north, top right facing east, bottom left facing south, bottom right facing west, empty cell where that direction does not exist, stairs`
- floor openings: `4 separate pieces in a 2x2 grid, empty cell where there is no piece, floor opening`
- ladders: `4 separate pieces in a 2x2 grid, empty cell where there is no piece, ladder`

```
blnr_wall, pixel art game sprite sheet, top-down oblique 45 degree view, 4 separate wall parts, top left horizontal wall segment, top right vertical wall segment, bottom left thin corner pole, bottom right corner joint, wall, black obsidian wall, plain gray background --w 1024 --h 1024 --s 8 --l 1 --d 8702
```

Wall parts come out consistent (same material, height and thickness in all 4 parts; the corner is the
horizontal and vertical part joined). Organic materials (coral, hedges) are messier than masonry. Stairs
sometimes show only 2 of 4 directions. Floor openings and ladders were trained on few examples (14 sheets)
and are not evaluated. The LoRA also knows a "closed square room outline" layout; it was only a training aid,
its tile scale does not match the game, do not use it.

## monsters and outfits (walk cycles)

3×2 sheet, ×8, one frame per cell:

- top row facing south (toward the viewer), bottom row facing north (seen from the back);
- column 1 standing idle, columns 2 and 3 two walk frames with opposite steps.

Monsters come in four LoRAs by size. They share the trigger and the layout text; only the image size differs,
because the cell is bigger for bigger monsters and leaves room for the movement:

| LoRA | Cell (game pixels) | Image | For |
|---|---|---|---|
| monsters-small | 48 | 1152×768 | small creatures up to about 36 px: rats, imps, goblins, small animals |
| monsters-medium | 64 | 1536×1024 | human-sized monsters: orcs, bandits, wolves, skeletons |
| monsters-large-biped | 80 | 1920×1280 | large two-legged monsters: giants, ogres, trolls, golems |
| monsters-large | 80 | 1920×1280 | large monsters of other shapes: bears, rhinos, dragons, beasts |

Outfits (player characters) are drawn on a **magenta** background, with cells of 64 (1536×1024). The prompt asks
for full colors before the background; `tools/make_prompts.py` adds that text.

East and west are not drawn: make them by **transposing** the south and north frames (swap x and y, not a
mirror), see [postprocessing.md](postprocessing.md#walk-cycles-east-and-west).

```
blnr_mob, pixel art game monster sprite sheet, 3x2 grid, top-down oblique 45 degree view, walking animation, top row facing south, bottom row facing north seen from the back, first column standing idle pose, second and third columns walking frames with opposite steps, humanoid monster, gnoll hunter, hyena head, spotted fur, crude bow, bone necklace, ragged cloak, plain gray background --w 1536 --h 1024 --s 8 --l 1 --d 43
blnr_outfit, pixel art game character sprite sheet, 3x2 grid, top-down oblique 45 degree view, walking animation, top row facing south, bottom row facing north seen from the back, first column standing idle pose, second and third columns walking frames with opposite steps, female player character, archer, green hood, brown leather vest, grey trousers, black boots, fully colored outfit in its original vivid colors, colored clothes and hair, natural skin, plain magenta background --w 1536 --h 1024 --s 8 --l 1 --d 43
```

Kinds for monsters: `humanoid monster`, `animal`, `insect or spider`, `undead`, `demon`, `elemental or golem`,
`dragon or draken`, `aberration or magical creature`. For outfits: `female player character` or
`male player character`.

Monster descriptions work best as a short list of features: creature, then 3-5 details separated by commas
(`gnoll hunter, hyena head, spotted fur, crude bow, bone necklace`).

Describe the colors in the prompt: name the color of each main part (hat, shirt or armor, trousers, boots),
e.g. `green hood, brown leather vest, grey trousers, black boots`. Without colors the LoRA picks its own.

Avoid describing existing game outfits by name (knight, druid…): the LoRA then tends to redraw the training
outfit instead of a new one.

Large monsters are often bigger than 64×64 together with their movement (usually 66-80 px); post-processing
puts them on a 96×96 canvas (3×3 tiles) instead of shrinking them ([postprocessing.md](postprocessing.md)).
