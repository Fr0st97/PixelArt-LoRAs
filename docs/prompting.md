# Writing prompts

A prompt tells the model what to draw. With these LoRAs most of the prompt is fixed; you only describe the
object. You do not need to know anything about AI to do it.

## The short version

1. Pick the LoRA and the **kind** of thing from the table below.
2. Write what you want, one line per object: `kind | description`, in simple English.
3. Turn the lines into a prompt file with `tools/make_prompts.py`.
4. Generate, look at the results, adjust the descriptions, repeat.

## 1. Pick the LoRA and the kind

| I want… | LoRA | kind |
|---|---|---|
| a tree | flora | `tree` |
| a bush, flower, grass, small plant | flora | `plant` |
| a plant in a pot | flora | `pot` |
| a mushroom | flora | `mushroom` |
| a rock or boulder | nature | `rock` |
| a crystal | nature | `crystal` |
| bones or a skeleton on the ground | nature | `bones` |
| a log, stump, dead branch | nature | `wood` |
| a statue seen from the front and from the side | pairs | `statue` |
| a decoration (vase, sign, pillar…) from the front and the side | pairs | `decoration` |
| a chest, crate, barrel from the front and the side | pairs | `container` |
| a table, wardrobe, shelf from the front and the side | pairs | `furniture` |
| a brazier, campfire, torch stand: unlit and lit | pairs | `light` |
| a lamp facing two ways, unlit and lit | sheets | `lamp` |
| a painting, trophy, banner hung on two walls and lying on the floor | sheets | `wall_decoration` |
| a chair, throne, sofa in 4 directions | sheets | `furniture` |
| a matching sword, axe, club and shield | equipment | `knight` |
| a matching bow, crossbow, arrow and bolt | equipment | `paladin` |
| a matching helmet, armor, legs and boots | equipment | `armor` |
| a matching wand, rod and two spellbooks | equipment | `mage` |
| an amulet or necklace | accessories | `amulet` |
| a ring | accessories | `ring` |
| a backpack or bag | accessories | `bag` |
| a rune stone | consumables | `rune` |
| a potion | consumables | `potion` |
| food | consumables | `food` |
| a tool | consumables | `tool` |
| gold, gems, valuables | consumables | `valuable` |
| an item dropped by a monster (fang, fur, claw…) | loot | `loot` |
| a ground type with its borders (grass, sand, stone floor…) | ground | `ground` |
| a monster plus its corpse (not released yet) | corpses | `humanoid`, `animal`, `insect`, `undead`, `demon`, `elemental`, `dragon`, `magical` |
| a wall set (straight parts, pole, corner) | walls | `wall` |
| stairs | walls | `stairs` |
| a hole in the floor, trapdoor, stairs down | walls | `opening` |
| ladders | walls | `ladder` |
| a walking monster (front and back) | monsters-small, -medium, -large-biped, -large (by size, see [loras.md](loras.md#monsters-and-outfits-walk-cycles)) | same kinds as corpses |
| a walking player character (front and back) | outfits | `female`, `male` |

## 2. Write the description

One line per object: `kind | description`. The description is **5-15 words** of plain English, in this order:

**size or shape** → **material** → **main color** → **one or two details**

| Good | Why |
|---|---|
| `tree \| tall pine tree with dark green needles and a thin brown trunk` | shape, color, detail |
| `rock \| large red sandstone boulder with deep cracks` | size, material, color, detail |
| `potion \| small round blue flask with a cork` | size, shape, color, detail |
| `wall \| grey castle wall made of large square stone blocks` | color, material, detail |
| `humanoid \| green orc warrior with a rusty axe and a leather vest` | color, creature, equipment |
| `male \| wizard in a long purple robe with a pointed hat and a wooden staff` | clothes, colors, item |

Avoid:

- **Style words** (`pixel art`, `8-bit`, `realistic`, `3D`, `HD`): the LoRA already sets the style; extra words fight it.
- **Background or scene** (`in a forest`, `on a table`): the background must stay plain (gray, magenta for
  outfits) for post-processing.
- **Camera words** (`close-up`, `side view`): the view is fixed by the LoRA.
- **Several objects in one line**: one object per line (sheets and sets are handled by the layout).
- **Text, letters, numbers on the object**: they come out as noise.
- **Names of existing game items, outfits or characters**: the LoRA may redraw something it saw in training
  instead of a new design. Describe what it looks like instead.
- **Long stories**: the model reads the first details most.

Single-kind LoRAs (loot, ground) accept just the description, without `kind |`.

## 3. Make the prompt file

Save your lines in a text file, for example `my_plants.txt`:

```
tree | tall pine tree with dark green needles and a thin brown trunk
tree | small round bush tree with orange autumn leaves
pot | blue ceramic pot with a small spiky cactus
mushroom | big red mushroom with white dots
```

Then run (on your computer or on the pod, Python 3.9+, no extra packages needed):

```
python tools/make_prompts.py flora my_plants.txt flora_prompts.txt --variants 3
```

`--variants 3` makes 3 images of each line with different seeds, so you can pick the best one. The script adds
the trigger, the exact layout text, the background and the generation options. `python tools/make_prompts.py --list`
shows all LoRAs and kinds.

The result is a file you pass to `pod/generate.sh` (see [guide.md](guide.md), step 5).

## 4. Look at the results and adjust

| What you see | What to change |
|---|---|
| The object is not what you described | Simplify the description; put the most important word first; or generate with strength 0.7 |
| Wrong color | Name one main color clearly (`dark red`, `light blue`), not several |
| Every result looks the same | Use more `--variants`; change the description more than one word |
| It looks like an item from the training set, not new | Remove names of existing things, describe shape and material instead |
| Too much detail, messy | Fewer details; one or two are enough |
| Some sheets or directions are identical (sheets, pairs, stairs) | Known limit of these LoRAs; generate more variants and pick |
| The walking character barely moves | Known limit for large monsters; outfits move more. Pick the best of several variants |

Strength: `sh pod/generate.sh <lora> <prompts> <output> 0.7` follows the description more and the style less.
1.0 is the default; values below 0.6 usually lose the pixel art look.

## Ready examples

Copy these into a wish file to see what each LoRA does.

```
# flora
tree | oak tree with a round green crown and a short brown trunk
plant | small green fern with long curly leaves
pot | clay pot with a red flowering rose bush
mushroom | tall glowing blue mushroom with a thin white stem

# nature
rock | large grey boulder covered with green moss
crystal | cluster of purple amethyst crystals with sharp points
bones | old white ribcage lying in the dirt
wood | fallen hollow log with brown bark

# pairs
statue | grey stone knight statue holding a sword on a square pedestal
container | wooden treasure chest with iron bands, closed
light | iron brazier on three legs

# sheets
lamp | brass wall lamp with a glass dome
wall_decoration | framed painting of a mountain landscape
furniture | wooden chair with a red cushion

# equipment
knight | obsidian set with purple runes
armor | golden royal set with blue gems
mage | ice magic set with frozen crystals

# accessories, consumables, loot
amulet | silver chain with a green emerald pendant
rune | dark grey stone with a glowing yellow lightning symbol
potion | tall green bottle with a skull label
loot | sharp white wolf fang

# ground, walls
ground | yellow desert sand with small pebbles
wall | white plaster wall with dark wooden beams
stairs | grey stone stairs

# monsters-medium, outfits
humanoid | green orc warrior, lower jaw tusks, iron shoulder plate, crude battle axe
animal | grey wolf, white chest, yellow eyes, bushy tail
female | archer, green hood, brown leather vest, grey trousers, black boots
```

20 examples per LoRA: `prompts/<lora>/examples.txt`.

The `#` lines are comments and are skipped. Lines for different LoRAs must go into separate wish files,
because each run uses one LoRA.

## For the curious: what a finished prompt looks like

```
blnr_flora, pixel art game object, top-down oblique 45 degree view, tree leaning toward the upper left, oak tree with a round green crown and a short brown trunk, plain gray background --w 1024 --h 1024 --s 8 --l 1 --d 100
```

- `blnr_flora`: trigger word, switches the LoRA on;
- `pixel art game object, top-down oblique 45 degree view, tree leaning toward the upper left`: the layout text the
  LoRA was trained on;
- `oak tree with…`: your description;
- `plain gray background`: keeps the background clean for post-processing;
- `--w 1024 --h 1024`: image size; `--s 8 --l 1`: 8 steps, no guidance (Krea-2 Turbo); `--d 100`: seed.

All layout texts are in [loras.md](loras.md).
