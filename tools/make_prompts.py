"""Build a prompt file for one PixelArt LoRA from simple descriptions.

You (or your AI assistant) write only what you want, one per line, in a text file:

    tree | oak tree with a round green crown
    tree | dead tree with grey bare branches
    pot  | blue ceramic pot with a small cactus

The part before "|" is the kind (see the list for each LoRA below or run with --list); LoRAs with a single kind
accept just the description. This script adds the trigger word, the exact layout text the LoRA was trained on,
the background and the generation options, and gives every line its own seed.

Usage:
    python make_prompts.py <lora> <wishes.txt> <prompts_out.txt> [--seed 100] [--variants 2]
    python make_prompts.py --list            # show all LoRAs and their kinds

    --seed      first seed (default 100); seeds go up by one per line
    --variants  how many images per wish, each with its own seed (default 1)

Example:
    python make_prompts.py flora my_plants.txt flora_prompts.txt --variants 3
Then on the pod:  sh pod/generate.sh loras/Krea2-PixelArt-flora.safetensors flora_prompts.txt results/my_plants
"""
import argparse
import sys
from pathlib import Path

SQUARE = "--w 1024 --h 1024 --s 8 --l 1"
WIDE = "--w 1536 --h 1024 --s 8 --l 1"
SMALL_WALK = "--w 1152 --h 768 --s 8 --l 1"
LARGE_WALK = "--w 1920 --h 1280 --s 8 --l 1"
VIEW = "top-down oblique 45 degree view"

DIRECTION_PAIR = ("direction pair, left: facing south with the front facing down, "
                  "right: facing east with the front facing right")
WALK = ("walking animation, top row facing south, bottom row facing north seen from the back, "
        "first column standing idle pose, second and third columns walking frames with opposite steps")
MONSTER_KINDS = {
    "humanoid": "humanoid monster", "animal": "animal", "insect": "insect or spider", "undead": "undead",
    "demon": "demon", "elemental": "elemental or golem", "dragon": "dragon or draken",
    "magical": "aberration or magical creature",
}

MOB = f"blnr_mob, pixel art game monster sprite sheet, 3x2 grid, {VIEW}, {WALK}"
# text before the options; outfits are drawn on magenta and need the colors asked for
TAIL = {"outfits": "fully colored outfit in its original vivid colors, colored clothes and hair, natural skin, "
                   "plain magenta background"}

# lora: (header, {kind: layout and kind text}, options)
LORAS = {
    "flora": (f"blnr_flora, pixel art game object, {VIEW}", {
        "tree": "tree leaning toward the upper left", "plant": "plant", "pot": "plant in a pot",
        "mushroom": "mushroom"}, SQUARE),
    "nature": (f"blnr_nature, pixel art game object, {VIEW}", {
        "rock": "rock", "crystal": "crystal", "bones": "bones lying on the ground",
        "wood": "dead wood lying on the ground"}, SQUARE),
    "pairs": (f"blnr_pair, pixel art game object pair, {VIEW}", {
        "statue": f"{DIRECTION_PAIR}, statue", "decoration": f"{DIRECTION_PAIR}, decoration",
        "container": f"{DIRECTION_PAIR}, container",
        "furniture": f"{DIRECTION_PAIR}, furniture standing on the floor",
        "light": "unlit and lit pair, left: unlit, right: lit, no direction, looks the same from every side, "
                 "light source"}, SQUARE),
    "sheets": (f"blnr_sheet, pixel art game sprite sheet, 2x2 grid, {VIEW}", {
        "lamp": "top row facing south, bottom row facing east, left column unlit, right column lit, lamp",
        "wall_decoration": "top left hung on a north wall facing south, top right hung on a west wall facing east, "
                           "bottom left lying on the floor as a loose item, bottom right empty, wall decoration",
        "furniture": "top left facing south, top right facing east, bottom left facing north seen from the back, "
                     "bottom right facing west seen from the back, furniture standing on the floor"}, SQUARE),
    "equipment": ("blnr_eq, pixel art game inventory item sheet, 2x2 grid", {
        "knight": "top left sword, top right axe, bottom left club, bottom right shield, "
                  "all pieces share one matching design, knight weapon set",
        "paladin": "top left bow, top right crossbow, bottom left arrow, bottom right bolt, "
                   "all pieces share one matching design, paladin weapon set",
        "armor": "top left helmet, top right armor, bottom left legs, bottom right boots, "
                 "all pieces share one matching design, armor set",
        "mage": "top left wand, top right rod, bottom left sorcerer spellbook, bottom right druid spellbook, "
                "left column one sorcerer set, right column one druid set, mage weapon set"}, SQUARE),
    "accessories": ("blnr_accessory, pixel art game inventory item", {
        "amulet": "amulet or necklace", "ring": "ring", "bag": "backpack or bag"}, SQUARE),
    "consumables": ("blnr_utility, pixel art game inventory item", {
        "rune": "magic rune stone", "potion": "potion", "food": "food", "tool": "tool",
        "valuable": "valuable treasure"}, SQUARE),
    "loot": ("blnr_loot, pixel art game inventory item", {"loot": "monster loot"}, SQUARE),
    "ground": (f"blnr_ground, pixel art game ground tile sheet, 4x4 grid of tiles, {VIEW}", {
        "ground": "ground tiles forming a winding path from the bottom left to the top right edge, "
                  "with matching border edges and corners, empty gray area around the path"}, SQUARE),
    "corpses": (f"blnr_corpse, pixel art game monster corpse sheet, 2x2 grid, {VIEW}, top left the living monster "
                "standing idle facing south, top right its fresh corpse, bottom left the decaying corpse, "
                "bottom right the remains", MONSTER_KINDS, SQUARE),
    "walls": (f"blnr_wall, pixel art game sprite sheet, {VIEW}", {
        "wall": "4 separate wall parts, top left horizontal wall segment, top right vertical wall segment, "
                "bottom left thin corner pole, bottom right corner joint, wall",
        "stairs": "stairs going up in separate cells, top left facing north, top right facing east, "
                  "bottom left facing south, bottom right facing west, empty cell where that direction does not "
                  "exist, stairs",
        "opening": "4 separate pieces in a 2x2 grid, empty cell where there is no piece, floor opening",
        "ladder": "4 separate pieces in a 2x2 grid, empty cell where there is no piece, ladder"}, SQUARE),
    # four monster LoRAs by size, same trigger and layout, different image size (cells of 48, 64, 80 game pixels)
    "monsters-small": (MOB, MONSTER_KINDS, SMALL_WALK),
    "monsters-medium": (MOB, MONSTER_KINDS, WIDE),
    "monsters-large-biped": (MOB, MONSTER_KINDS, LARGE_WALK),
    "monsters-large": (MOB, MONSTER_KINDS, LARGE_WALK),
    "outfits": (f"blnr_outfit, pixel art game character sprite sheet, 3x2 grid, {VIEW}, {WALK}", {
        "female": "female player character", "male": "male player character"}, WIDE),
}


def build(lora: str, wishes: list[str], seed: int, variants: int) -> list[str]:
    header, kinds, options = LORAS[lora]
    out = []
    for n, raw in enumerate(wishes, 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "|" in line:
            kind, desc = (x.strip() for x in line.split("|", 1))
        elif len(kinds) == 1:
            kind, desc = next(iter(kinds)), line
        else:
            sys.exit(f"line {n}: write 'kind | description'; kinds for {lora}: {', '.join(kinds)}")
        if kind not in kinds:
            sys.exit(f"line {n}: unknown kind '{kind}' for {lora}; use one of: {', '.join(kinds)}")
        desc = desc.rstrip(" ,.")
        for _ in range(variants):
            out.append(f"{header}, {kinds[kind]}, {desc}, {TAIL.get(lora, 'plain gray background')} {options} --d {seed}")
            seed += 1
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("lora", nargs="?", choices=sorted(LORAS))
    ap.add_argument("wishes", nargs="?")
    ap.add_argument("out", nargs="?")
    ap.add_argument("--seed", type=int, default=100)
    ap.add_argument("--variants", type=int, default=1)
    ap.add_argument("--list", action="store_true", help="show LoRAs and kinds")
    a = ap.parse_args()
    if a.list or not (a.lora and a.wishes and a.out):
        for name, (_, kinds, options) in LORAS.items():
            size = "x".join(options.split()[1:4:2])
            print(f"{name:21} {size}  kinds: {', '.join(kinds)}")
        return 0 if a.list else 1
    wishes = Path(a.wishes).read_text(encoding="utf-8").splitlines()
    lines = build(a.lora, wishes, a.seed, a.variants)
    Path(a.out).write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(f"{a.out}: {len(lines)} prompts, seeds {a.seed}-{a.seed + len(lines) - 1}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
