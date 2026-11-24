# Biome example: jarmark (Christmas market)

Ready prompts for the old PixelArt LoRAs and the sprites they produced, so each result can be traced back to its
prompt. Generated 2026-11-19 on a RunPod pod (Krea-2 Turbo bf16, 8 steps, CFG 1, LoRA strength 1.0), then
post-processed to game size with `tools/postprocess.py`. Only the sprites that were kept are included.

How to read it: `<lora>-prompts.txt` has one prompt per line; `--d` is the seed. A result file named
`<seed>[letter].png` comes from the prompt line with that seed (the letter is the part of a multi-part sheet, e.g.
a, b, c, d for the four wall parts or the two halves of a pair). `results/<lora>/overview.png` shows all kept sprites.

To generate them again: `sh pod/generate.sh loras/Krea2-PixelArt-<lora>.safetensors prompts/biomes/jarmark/<lora>-prompts.txt results/jarmark-<lora>`

## walls

Prompts: [`walls-prompts.txt`](walls-prompts.txt), sprites at game size (64x64),
overview: [`results/walls/overview.png`](results/walls/overview.png)

| seed | what the prompt asks for | result files |
|---|---|---|
| 70013 | wooden market hut wall with snow and a pine garland | [70013a.png](results/walls/70013a.png), [70013b.png](results/walls/70013b.png), [70013c.png](results/walls/70013c.png), [70013d.png](results/walls/70013d.png) |
| 70014 | wooden market hut wall with snow and a pine garland | [70014a.png](results/walls/70014a.png), [70014b.png](results/walls/70014b.png), [70014c.png](results/walls/70014c.png), [70014d.png](results/walls/70014d.png) |
| 70015 | brown gingerbread wall with white icing trim | [70015a.png](results/walls/70015a.png), [70015b.png](results/walls/70015b.png), [70015c.png](results/walls/70015c.png), [70015d.png](results/walls/70015d.png) |
| 70016 | brown gingerbread wall with white icing trim | [70016a.png](results/walls/70016a.png), [70016b.png](results/walls/70016b.png), [70016c.png](results/walls/70016c.png), [70016d.png](results/walls/70016d.png) |
| 70017 | low white picket fence with snow | [70017a.png](results/walls/70017a.png), [70017b.png](results/walls/70017b.png), [70017c.png](results/walls/70017c.png), [70017d.png](results/walls/70017d.png) |
| 70018 | low white picket fence with snow | [70018a.png](results/walls/70018a.png), [70018b.png](results/walls/70018b.png), [70018c.png](results/walls/70018c.png), [70018d.png](results/walls/70018d.png) |
| 70019 | wooden steps with snow and red ribbons | [70019a.png](results/walls/70019a.png), [70019d.png](results/walls/70019d.png) |
| 70020 | wooden steps with snow and red ribbons | [70020a.png](results/walls/70020a.png), [70020b.png](results/walls/70020b.png), [70020d.png](results/walls/70020d.png) |

## ground

Prompts: [`ground-prompts.txt`](ground-prompts.txt), sprites at game size (32x32),
overview: [`results/ground/overview.png`](results/ground/overview.png)

| seed | what the prompt asks for | result files |
|---|---|---|
| 70001 | red brick pavement covered with thin snow | [70001/](results/ground/70001/) |
| 70002 | red brick pavement covered with thin snow | [70002/](results/ground/70002/) |
| 70003 | trampled snow with scattered straw | [70003/](results/ground/70003/) |
| 70004 | trampled snow with scattered straw | [70004/](results/ground/70004/) |
| 70005 | white snow with red and gold confetti | [70005/](results/ground/70005/) |
| 70006 | white snow with red and gold confetti | [70006/](results/ground/70006/) |
| 70007 | frozen dark cobblestone with salt grains | [70007/](results/ground/70007/) |
| 70008 | frozen dark cobblestone with salt grains | [70008/](results/ground/70008/) |
| 70009 | wooden boardwalk with snow on the edges | [70009/](results/ground/70009/) |
| 70010 | wooden boardwalk with snow on the edges | [70010/](results/ground/70010/) |
| 70011 | green pine needles scattered on snow | [70011/](results/ground/70011/) |
| 70012 | green pine needles scattered on snow | [70012/](results/ground/70012/) |

## pairs

Prompts: [`pairs-prompts.txt`](pairs-prompts.txt), sprites at game size (64x64),
overview: [`results/pairs/overview.png`](results/pairs/overview.png)

| seed | what the prompt asks for | result files |
|---|---|---|
| 70055 | large wrapped gift box with a gold bow | [70055a.png](results/pairs/70055a.png), [70055b.png](results/pairs/70055b.png) |
| 70056 | tall red and white candy cane pole | [70056a.png](results/pairs/70056a.png), [70056b.png](results/pairs/70056b.png) |
| 70057 | snow globe on a wooden stand | [70057a.png](results/pairs/70057a.png), [70057b.png](results/pairs/70057b.png) |
| 70058 | stack of colorful wrapped presents | [70058a.png](results/pairs/70058a.png), [70058b.png](results/pairs/70058b.png) |
| 70059 | giant shiny red ornament ball with a gold cap | [70059a.png](results/pairs/70059a.png), [70059b.png](results/pairs/70059b.png) |
| 70060 | carousel horse on a golden pole | [70060a.png](results/pairs/70060a.png), [70060b.png](results/pairs/70060b.png) |
| 70061 | wooden reindeer with a red collar | [70061a.png](results/pairs/70061a.png), [70061b.png](results/pairs/70061b.png) |
| 70062 | tall wooden toy soldier with a red coat | [70062a.png](results/pairs/70062a.png), [70062b.png](results/pairs/70062b.png) |
| 70063 | barrel of mulled wine with a ladle | [70063a.png](results/pairs/70063a.png), [70063b.png](results/pairs/70063b.png) |
| 70064 | wicker basket of oranges and nuts | [70064a.png](results/pairs/70064a.png), [70064b.png](results/pairs/70064b.png) |
| 70065 | red sack full of presents | [70065a.png](results/pairs/70065a.png), [70065b.png](results/pairs/70065b.png) |
| 70066 | wooden crate full of colorful toys | [70066a.png](results/pairs/70066a.png), [70066b.png](results/pairs/70066b.png) |
| 70067 | large copper kettle on legs | [70067a.png](results/pairs/70067a.png), [70067b.png](results/pairs/70067b.png) |
| 70068 | market stall with a red roof and a garland | [70068a.png](results/pairs/70068a.png), [70068b.png](results/pairs/70068b.png) |
| 70069 | wooden bench with a red blanket | [70069a.png](results/pairs/70069a.png), [70069b.png](results/pairs/70069b.png) |
| 70070 | wooden table with candles and pine branches | [70070a.png](results/pairs/70070a.png), [70070b.png](results/pairs/70070b.png) |
| 70071 | small wooden shelf with toy figures | [70071a.png](results/pairs/70071a.png), [70071b.png](results/pairs/70071b.png) |
| 70072 | tall street lamp with a red ribbon | [70072a.png](results/pairs/70072a.png), [70072b.png](results/pairs/70072b.png) |
| 70073 | lantern with a candle and snow on top | [70073a.png](results/pairs/70073a.png), [70073b.png](results/pairs/70073b.png) |
| 70074 | iron fire bowl with roasting chestnuts | [70074a.png](results/pairs/70074a.png), [70074b.png](results/pairs/70074b.png) |
| 70075 | wooden candle arch with seven candles | [70075a.png](results/pairs/70075a.png), [70075b.png](results/pairs/70075b.png) |

## sheets

Prompts: [`sheets-prompts.txt`](sheets-prompts.txt), sprites at game size (64x64),
overview: [`results/sheets/overview.png`](results/sheets/overview.png)

| seed | what the prompt asks for | result files |
|---|---|---|
| 70076 | golden star shaped hanging lamp | [70076a.png](results/sheets/70076a.png), [70076b.png](results/sheets/70076b.png), [70076c.png](results/sheets/70076c.png), [70076d.png](results/sheets/70076d.png) |
| 70077 | red glass lantern with a gold frame | [70077a.png](results/sheets/70077a.png), [70077b.png](results/sheets/70077b.png), [70077c.png](results/sheets/70077c.png), [70077d.png](results/sheets/70077d.png) |
| 70078 | candle in a ring of holly | [70078a.png](results/sheets/70078a.png), [70078b.png](results/sheets/70078b.png), [70078c.png](results/sheets/70078c.png), [70078d.png](results/sheets/70078d.png) |
| 70079 | brass lantern with a red bow | [70079a.png](results/sheets/70079a.png), [70079b.png](results/sheets/70079b.png), [70079c.png](results/sheets/70079c.png), [70079d.png](results/sheets/70079d.png) |
| 70080 | green wreath with a red bow | [70080a.png](results/sheets/70080a.png), [70080b.png](results/sheets/70080b.png), [70080c.png](results/sheets/70080c.png) |
| 70081 | red stocking hanging on a hook | [70081a.png](results/sheets/70081a.png), [70081b.png](results/sheets/70081b.png), [70081c.png](results/sheets/70081c.png) |
| 70082 | pine garland with golden balls | [70082a.png](results/sheets/70082a.png), [70082b.png](results/sheets/70082b.png), [70082c.png](results/sheets/70082c.png) |
| 70083 | framed painting of a snowy village | [70083a.png](results/sheets/70083a.png), [70083b.png](results/sheets/70083b.png), [70083c.png](results/sheets/70083c.png) |
| 70084 | string of colorful paper stars | [70084a.png](results/sheets/70084a.png), [70084b.png](results/sheets/70084b.png), [70084c.png](results/sheets/70084c.png) |
| 70085 | green velvet armchair with gold trim | [70085a.png](results/sheets/70085a.png), [70085b.png](results/sheets/70085b.png), [70085c.png](results/sheets/70085c.png), [70085d.png](results/sheets/70085d.png) |
| 70086 | painted wooden rocking horse with a red saddle | [70086a.png](results/sheets/70086a.png), [70086b.png](results/sheets/70086b.png), [70086c.png](results/sheets/70086c.png), [70086d.png](results/sheets/70086d.png) |
| 70087 | small wooden table with a cake | [70087a.png](results/sheets/70087a.png), [70087b.png](results/sheets/70087b.png), [70087c.png](results/sheets/70087c.png), [70087d.png](results/sheets/70087d.png) |
| 70088 | white painted chair with a heart cutout | [70088a.png](results/sheets/70088a.png), [70088b.png](results/sheets/70088b.png), [70088c.png](results/sheets/70088c.png), [70088d.png](results/sheets/70088d.png) |
| 70089 | stone fireplace with red stockings and a fire | [70089a.png](results/sheets/70089a.png), [70089b.png](results/sheets/70089b.png), [70089c.png](results/sheets/70089c.png), [70089d.png](results/sheets/70089d.png) |
| 70090 | tall wooden cupboard with painted stars | [70090a.png](results/sheets/70090a.png), [70090b.png](results/sheets/70090b.png), [70090c.png](results/sheets/70090c.png), [70090d.png](results/sheets/70090d.png) |

## flora

Prompts: [`flora-prompts.txt`](flora-prompts.txt), sprites at game size (64x64),
overview: [`results/flora/overview.png`](results/flora/overview.png)

| seed | what the prompt asks for | result files |
|---|---|---|
| 70021 | pine tree decorated with red and gold balls | [70021.png](results/flora/70021.png) |
| 70022 | pine tree decorated with red and gold balls | [70022.png](results/flora/70022.png) |
| 70023 | tall fir tree with a gold star on top | [70023.png](results/flora/70023.png) |
| 70024 | tall fir tree with a gold star on top | [70024.png](results/flora/70024.png) |
| 70025 | small fir tree with lit candles | [70025.png](results/flora/70025.png) |
| 70026 | small fir tree with lit candles | [70026.png](results/flora/70026.png) |
| 70027 | snowy pine with colorful light bulbs | [70027.png](results/flora/70027.png) |
| 70028 | snowy pine with colorful light bulbs | [70028.png](results/flora/70028.png) |
| 70029 | white frosted tree with silver baubles | [70029.png](results/flora/70029.png) |
| 70030 | white frosted tree with silver baubles | [70030.png](results/flora/70030.png) |
| 70031 | pine tree with red ribbons and candy canes | [70031.png](results/flora/70031.png) |
| 70032 | pine tree with red ribbons and candy canes | [70032.png](results/flora/70032.png) |
| 70033 | mistletoe bunch with white berries | [70033.png](results/flora/70033.png) |
| 70034 | small pine sapling with a red bow | [70034.png](results/flora/70034.png) |
| 70035 | evergreen bush with tiny lights | [70035.png](results/flora/70035.png) |
| 70036 | bundle of pine branches with pinecones | [70036.png](results/flora/70036.png) |
| 70037 | holly sprig with red berries | [70037.png](results/flora/70037.png) |
| 70038 | red pot with a red poinsettia | [70038.png](results/flora/70038.png) |
| 70039 | wooden tub with a small decorated pine | [70039.png](results/flora/70039.png) |
| 70040 | red and white striped candy mushroom | [70040.png](results/flora/70040.png) |
| 70041 | golden glowing mushroom with snow on its cap | [70041.png](results/flora/70041.png) |

## nature

Prompts: [`nature-prompts.txt`](nature-prompts.txt), sprites at game size (64x64),
overview: [`results/nature/overview.png`](results/nature/overview.png)

| seed | what the prompt asks for | result files |
|---|---|---|
| 70042 | snowy boulder tied with a red ribbon | [70042.png](results/nature/70042.png) |
| 70043 | stack of stones with small candles | [70043.png](results/nature/70043.png) |
| 70044 | smooth grey stone with a carved star | [70044.png](results/nature/70044.png) |
| 70045 | rock with icicles and a pine garland | [70045.png](results/nature/70045.png) |
| 70046 | round snowy rock with tiny lights | [70046.png](results/nature/70046.png) |
| 70047 | red and green crystal cluster | [70047.png](results/nature/70047.png) |
| 70048 | golden crystal shaped like a five pointed star | [70048.png](results/nature/70048.png) |
| 70049 | blue and silver snowflake shaped crystal | [70049.png](results/nature/70049.png) |
| 70050 | yule log with holly and candles | [70050.png](results/nature/70050.png) |
| 70051 | birch logs tied with a red ribbon | [70051.png](results/nature/70051.png) |
| 70052 | old tree stump topped with snow and a pinecone | [70052.png](results/nature/70052.png) |
| 70053 | cut pine trunk with green branches | [70053.png](results/nature/70053.png) |
| 70054 | fallen pine branch with red berries | [70054.png](results/nature/70054.png) |

## consumables

Prompts: [`consumables-prompts.txt`](consumables-prompts.txt), sprites at game size (32x32),
overview: [`results/consumables/overview.png`](results/consumables/overview.png)

| seed | what the prompt asks for | result files |
|---|---|---|
| 70091 | star shaped gingerbread cookie with white icing | [70091.png](results/consumables/70091.png) |
| 70092 | steaming mug of red mulled wine | [70092.png](results/consumables/70092.png) |
| 70093 | red and white candy cane | [70093.png](results/consumables/70093.png) |
| 70094 | roasted chestnuts in a paper cone | [70094.png](results/consumables/70094.png) |

