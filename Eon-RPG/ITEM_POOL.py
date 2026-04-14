# ─── ITEMS ────────────────────────────────────────────────────────────────────
ITEM_POOL = [
    # Weapons
    {"name":"Rusty Sword",       "type":"weapon",    "value":3,  "description":"A blade worn by centuries. Still cuts."},
    {"name":"Iron Sword",        "type":"weapon",    "value":6,  "description":"Standard-issue steel. Reliable."},
    {"name":"Shadow Dagger",     "type":"weapon",    "value":5,  "description":"Light and fast. Made for the dark."},
    {"name":"Eldrosian Spear",   "type":"weapon",    "value":8,  "description":"Etched with imperial sigils. Old, perfectly balanced."},
    {"name":"Bone Hatchet",      "type":"weapon",    "value":4,  "description":"Crudely made from something's femur. Effective."},
    {"name":"Serrated Blade",    "type":"weapon",    "value":7,  "description":"Notched edges designed to tear. Whoever made this was not kind."},
    {"name":"Obsidian Knife",    "type":"weapon",    "value":6,  "description":"Volcanic glass, impossibly sharp. Chips if used carelessly."},
    {"name":"Bonespike",         "type":"weapon",    "value":9,  "description":"Carved from something large. Holds an edge badly."},
    {"name":"Needle of Vaethar", "type":"weapon",    "value":10, "description":"A thin blade. Something inside it hums when near the Void-well."},
    {"name":"Echoed Blade",      "type":"weapon",    "value":14, "description":"A blade that leaves an afterimage when swung. The afterimage does damage too, slightly delayed."},
    {"name":"Voidforged Sword",  "type":"weapon",    "value":16, "description":"Forged in something other than fire. The metal is black and does not reflect light. It is heavier than it looks and lighter than it should be."},
    {"name":"Stonefather's Maul","type":"weapon",    "value":15, "description":"A massive hammerhead on a short handle.  The stone it is made from is not stone from this world. It carries Thar's patience — and his severity."},
    # Thrown Weapons (one-use combat items)
    {"name": "Ember Vial",             "type": "thrown", "value": 18,
     "description": "A sealed vial of captured flame. Throws for 18 fire damage. Single use.",
     "throw_damage": 18, "throw_effect": None},

    {"name": "Void Grenade",           "type": "thrown", "value": 0,
     "description": "A sphere of compressed void-stuff. Drains 12 HP and curses the target. "
                    "Single use. Handle carefully.",
     "throw_damage": 12, "throw_effect": "curse_enemy"},

    {"name": "Bone Shard",             "type": "thrown", "value": 8,
     "description": "A sharpened fragment of something's femur. Throws for 8 damage and bleeds. "
                    "Single use.",
     "throw_damage": 8, "throw_effect": "bleed"},

    {"name": "Clarity Shard",          "type": "thrown", "value": 0,
     "description": "A chip of bright crystal. Thrown at an enemy, it disorients them — "
                    "their next attack misses. Single use.",
     "throw_damage": 4, "throw_effect": "miss_next"},

    {"name": "Starlight Bomb",         "type": "thrown", "value": 0,
     "description": "A Veythari-made object: compacted starlight that releases on impact. "
                    "Particularly effective against void-type enemies (double damage). "
                    "Single use.",
     "throw_damage": 15, "throw_effect": "void_double"},
    # Armour
    {"name":"Wooden Shield",     "type":"armour",    "value":2,  "description":"Splinters, but holds."},
    {"name":"Iron Shield",       "type":"armour",    "value":5,  "description":"Heavy and dependable."},
    {"name":"Leather Armour",    "type":"armour",    "value":3,  "description":"Flexible protection."},
    {"name":"Scale Armour",      "type":"armour",    "value":6,  "description":"Worked from something's hide. Darker than iron, warmer than stone."},
    {"name":"Chain Vest",        "type":"armour",    "value":4,  "description":"Rings of iron, well-kept."},
    {"name":"Eldrosian Plate",   "type":"armour",    "value":8,  "description":"Imperial-issue chest armour. The emblem has been scraped off."},
    {"name":"Warden's Coat",     "type":"armour",    "value":5,  "description":"Heavy leather worked with iron rings. The coat of an Eldrosian official."},
    {"name":"Voidhardened Vest", "type":"armour",    "value":10, "description":"Treated with something from deep below. Resists drain."},
    {"name":"Null Plate",        "type":"armour",    "value":12, "description":"Armour that absorbs rather than deflects. Hits against it seem to matter less than they should."},
    {"name":"Starweave Cloak",   "type":"armour",    "value":11, "description":"A cloak worked from something the Veythari left behind. It is lighter than air and warmer than stone. It adjusts to what the wearer needs."},
    {"name":"Ashbound Coat",     "type":"armour",    "value":10, "description":"Treated in the ash of the inscription room. Resists curses. The treatment does not wash out."},
    # Consumables
    {"name":"Health Potion",     "type":"consumable",   "value":15, "description":"Restores 15 HP."},
    {"name":"Strong Tonic",      "type":"consumable",   "value":25, "description":"A thick, bitter draught. Restores 25 HP."},
    {"name":"Antidote",          "type":"consumable",   "value":0,  "description":"Cures poison."},
    {"name":"Ember Flask",       "type":"consumable",   "value":20, "description":"Captured flame. Burns going down. Restores 20 HP."},
    {"name":"Bloodmoss Tincture","type":"consumable",   "value":10, "description":"Dark paste on wounds. Restores 10 HP."},
    {"name":"Clarity Draught",   "type":"consumable",   "value":0,  "description":"Clears the mind. Removes curses."},
    {"name":"Void Salt",         "type":"consumable",   "value":0,  "description":"Black crystalline salt. Wards against draining attacks for one fight."},
    {"name":"Vein-Sealer",       "type":"consumable",   "value":50, "description":"Restores 50 HP. Hardens wounds against reopening."},
    # Food and Drink (minor consumables)
    {"name": "Eldrosian Wine",         "type": "food", "value": 5,
     "description": "A sealed clay bottle. Old but not spoiled. "
                    "Restores 5 HP. Briefly reduces the weight of everything.",
     "food_effect": {"hp": 5, "morale": True}},

    {"name": "Dried Cave Mushroom",    "type": "food", "value": 3,
     "description": "Found growing in the dark. Bitter. Safe, probably. "
                    "Restores 3 HP. Has a faint glow that persists for some time.",
     "food_effect": {"hp": 3, "glow": True}},

    {"name": "Hardtack",               "type": "food", "value": 4,
     "description": "Standard imperial military ration. "
                    "Could survive another thousand years. "
                    "Restores 4 HP. Absolutely nothing else.",
     "food_effect": {"hp": 4}},

    {"name": "Honey Flask",            "type": "food", "value": 8,
     "description": "Sealed wax flask of something golden. "
                    "The bees that made this are no longer alive. "
                    "Restores 8 HP and cures poison.",
     "food_effect": {"hp": 8, "cure_poison": True}},

    {"name": "Cave Water",             "type": "food", "value": 2,
     "description": "Collected from a dripping ceiling. Cold. Clean, by the taste of it. "
                    "Restores 2 HP. Clears the head.",
     "food_effect": {"hp": 2, "clarity": True}},
    # Relics (passive equipment, third slot)
    {"name": "Ring of the Warden","type": "relic",      "value": 0, "description": "A plain iron ring bearing the eye-and-scales emblem of the Warden's office. "
                                                                                   "Worn, but intact. Increases defence by 2 while equipped.",
     "relic_effect": {"type": "defence", "value": 2}},
    {"name": "Morvath Eye",       "type": "relic",      "value": 0, "description": "Preserved in something clear and cold. Fully black. Looking into it is inadvisable. Grants immunity to fear effects.",
     "relic_effect": {"type": "fear_immune", "value": 1}},
    {"name": "Veythari Feather",  "type": "relic",      "value": 0, "description": "Silver-white. Holds its own faint light. Lighter than it should be. Increases maximum HP by 8.",
     "relic_effect": {"type": "max_hp", "value": 8}},
    {"name": "Shard of Kindrael",  "type": "relic",     "value": 0, "description": "A fragment of what appears to be crystallised flame — orange-gold, warm to the touch, impossible not to look at. Increases base attack by 3.",
     "relic_effect": {"type": "attack", "value": 3}},
    {"name": "Thar's Patience",     "type": "relic",     "value": 0, "description": "A disc of grey stone, heavier than it looks, inscribed on both sides with the same character in a script older than Eldros. Halves all bleed damage received.",
     "relic_effect": {"type": "bleed_resist", "value": 0.5}},
    {"name": "Hollow Coin",         "type": "relic",     "value": 0, "description": "An Eldrosian coin with a hole drilled precisely through the centre. Looking through the hole at people shows what they are afraid of. "
                                                                                    "Increases flee chance by 25%.",
     "relic_effect": {"type": "flee_bonus", "value": 0.25}},
    {"name": "Ysena's Veil",        "type": "relic",     "value": 0, "description": "A scrap of shadow-cloth, impossibly light, that clings to the hand. Reduces drain chance from drain-special enemies by half.",
     "relic_effect": {"type": "drain_resist", "value": 0.5}},
    {"name": "Kelamaris Breath-Stone", "type": "relic", "value": 0,
     "description": "A smooth pebble that hums at a constant low frequency. "
                    "Poison ticks deal 1 HP instead of 2.",
     "relic_effect": {"type": "poison_resist", "value": 1}},
    # Upgrade Materials (for the forge)
    {"name": "Forge Dust",             "type": "material", "value": 0,
     "description": "Fine metallic powder collected from the forge floor. "
                    "It is warm. It should not still be warm."},

    {"name": "Void-Tempered Ore",      "type": "material", "value": 0,
     "description": "Metal that has been exposed to the Void-well's influence. "
                    "It is heavier than ordinary ore and reflects nothing."},

    {"name": "Starlight Thread",       "type": "material", "value": 0,
     "description": "Incredibly fine silver thread, Veythari-made. "
                    "Each strand holds its own faint glow. "
                    "Woven into armour it becomes almost weightless."},

    {"name": "Dragon Ash",             "type": "material", "value": 0,
     "description": "Ash collected from near where Atheron sleeps. "
                    "It is gold where ordinary ash is grey. "
                    "Working it into metal changes the metal's nature permanently."},

    {"name": "Bloodwood Resin",        "type": "material", "value": 0,
     "description": "Thick red resin from the wood of something that grew near the Bloodwell. "
                    "Hardens armour and makes blades hold an edge better."},
    # Artefacts — each has a specific use somewhere
    {"name":"Candle",                   "type":"artefact",  "value":0,  "description":"Flickers in still air. Resists being snuffed. Its flame changes colour near old script."},
    {"name":"Relic Coin",               "type":"artefact",  "value":0,  "description":"Engraved with an erased face. Inscription: ELDROS PRIMA."},
    {"name":"Crystal Mirror",           "type":"artefact",  "value":0,  "description":"Shows something not quite you. The reflection moves a fraction late."},
    {"name":"Old Crown",                "type":"artefact",  "value":0,  "description":"Heavy. Meant for a larger head. The metal is unlike anything you know."},
    {"name":"Void Shard",               "type":"artefact",  "value":0,  "description":"A sliver of absolute dark. Cold beyond cold. It should not exist."},
    {"name":"Starlight Shard",          "type":"artefact",  "value":0,  "description":"Holds its own faint glow. Hums very quietly."},
    {"name":"Broken Seal",              "type":"artefact",  "value":0,  "description":"Half a stone seal. The surviving half shows a serpent eating the sun."},
    {"name":"Dragon Scale",             "type":"artefact",  "value":0,  "description":"Larger than your head. Black as a collapsed star. Warm to the touch."},
    {"name":"Blood Amber",              "type":"artefact",  "value":0,  "description":"A deep red gem, clouded from within. Something moves inside it slowly."},
    {"name":"Hollow Stone",             "type":"artefact",  "value":0,  "description":"Smooth stone with a perfectly round hole through it. Looking through the hole shows a different room."},
    {"name":"Dawn Shard",               "type":"artefact",  "value":0,  "description":"A chip of pale orange stone with its own warmth. Smells faintly of something just before sunrise."},
    {"name":"Warden's Seal",            "type":"artefact",  "value":0,  "description":"A flat disc bearing an eye above scales — the emblem of an Eldrosian Warden."},
    {"name":"Godshard Fragment",        "type":"artefact",  "value":0,  "description":"A sliver of something that was once much larger. It vibrates at a frequency you feel in your chest, not your ears. Imperial in origin. Older than the empire."},
    {"name":"Vaethar's Tear",           "type":"artefact",  "value":0,  "description":"A small ovoid of translucent gold material. Warm. It seems to breathe, very slowly."},
    {"name":"Second Godshard",          "type":"artefact",  "value":0,  "description":"A second fragment of Vaethar's divided form. It resonates with the first. Together they produce a frequency that is almost a chord."},
    {"name":"Third Godshard",           "type":"artefact",  "value":0,  "description":"A third fragment. Holding it alongside the others, you feel something beginning to cohere — something that was once whole recognising what it was."},
    {"name":"Agreement Stone",          "type":"artefact",  "value":0,  "description":"A flat disc of black stone, warm on one side, ice-cold on the other. It hums at a frequency that is not comfortable. This was present at something that should not have happened."},
    {"name":"Codex of the First Age",   "type":"artefact",  "value":0,  "description":"A heavy book bound in something that is not leather."},
    {"name": "Fragment of the Seal",    "type": "artefact", "value": 0, "description": "A shard of the Shattered Crown's sealing mechanism. It vibrates faintly when near a Godshard. Imperial goldsmiths made these — their names are on the back in tiny script."},
    {"name": "Cultist's Sigil",         "type": "artefact", "value": 0, "description": "A disc of dark metal stamped with a symbol: a circle with a crack through it. It is warm. It should not be warm."},
    # Lore items
    {"name":"Ashen Tablet",             "type":"lore",      "value":0,  "description":"Flat pale stone, dense Eldrosian script. One passage is legible."},
    {"name":"Charred Ledger",           "type":"lore",      "value":0,  "description":"A ledger, burned at edges. Pages list names — all crossed out in the same black ink."},
    {"name":"Imperial Edict",           "type":"lore",      "value":0,  "description":"A formal declaration on pressed material, embossed with the Eldrosian serpent-sun emblem."},
    {"name":"Priest's Journal",         "type":"lore",      "value":0,  "description":"A small journal, handwritten in two distinct inks. The second ink is darker and appears later."},
    {"name": "Talarion's Chronicle",    "type":"lore",      "value": 0, "description": "A thick, handwritten volume. The author gives his name on the first page: Talarion. The last line reads: 'And so I tell it, because someone must.'"},
    {"name": "Remnant Scholar's Notes", "type":"lore",      "value": 0, "description": "Hurriedly written field notes. Scholarly handwriting, ink-stained. The last entry ends mid-sentence."},
    {"name": "Shard-Seeker's Map",      "type":"lore",      "value": 0, "description": "A rough map of the upper ruins, annotated in a mercenary's hand. Three locations are circled and labelled: SHARD? SHARD? SHARD?. All three circles are crossed out."},
    {"name": "Rolled Parchment",        "type":"lore",      "value": 0, "description": "Rolled tight and sealed with black wax. The wax is already cracked."},
    # Fixed Books (full text, specific locations)
    {"name": "The Last Warden's Log",  "type": "lore", "value": 0,
     "description": "Serethan's personal log. Bound in Warden's leather, clasp still sealed. "
                    "The last entry is not finished."},

    {"name": "A Field Guide to the Void-Touched",
     "type": "lore", "value": 0,
     "description": "Scholarly annotations and field observations. "
                    "Written by someone who spent too long observing the Void-Touched "
                    "and not long enough leaving."},

    {"name": "Vaelan's Private Journal","type": "lore", "value": 0,
     "description": "Small, personal, water-damaged. The emperor's handwriting — "
                    "confirmed by the signature on the first page. "
                    "He writes as someone who knows something is coming and does not know how to stop it."},
    # Keys
    {"name":"Iron Key",          "type":"key",       "value":0,  "description":"Heavy iron. Teeth worn smooth. Opens something down here."},
    {"name":"Ashen Key",         "type":"key",       "value":0,  "description":"Forged from compacted ash. Should crumble — does not. Writing on the bow: older than Eldros."},
    {"name":"Starlight Key",     "type":"key",       "value":0,  "description":"Appears made of solidified moonlight. Glows faintly."},
    {"name":"Blood Key",         "type":"key",       "value":0,  "description":"Deep red, warm. Not comforting. The teeth are shaped like no lock you have seen."},
    {"name":"Warden's Key",      "type":"key",       "value":0,  "description":"A long iron key stamped with the Warden's eye-and-scales emblem. Official issue."},
    {"name":"Throne Key",        "type":"key",       "value":0,  "description":"Black iron, heavy, ornate. The bow is shaped like a crown. This opened something important."},
    # Enemy-Specific Drops
    {"name": "Shepherd's Hook",        "type": "weapon", "value": 12,
     "description": "A crook-shaped weapon taken from the Unmade Shepherd. "
                    "It hums with void-resonance. Void enemies it strikes take +3 additional damage."},

    {"name": "Named's Grimoire",       "type": "lore", "value": 0,
     "description": "A book of void-inscriptions written by The Named. "
                    "The text is partially in a language that should not be legible "
                    "and yet you can read it. This is probably not fine."},

    {"name": "Witness's Memory",       "type": "artefact", "value": 0,
     "description": "A coin-sized disc of black stone dropped by the Agreement's Witness. "
                    "Holding it, you see — briefly — what it saw. "
                    "Two figures. A circle. The moment of the Agreement."},

    {"name": "Nightmare Fragment",     "type": "artefact", "value": 0,
     "description": "A piece of something that was not real. "
                    "It exists because you killed the thing it came from. "
                    "It is warm in a way that feels like remembered fear."},
]

# Items that should exist at most once per character, ever.
# The string is the flag set when the item is first obtained.
UNIQUE_ITEMS = {
    # item name                 : flag name
    "Godshard Fragment"         : "obtained_godshard_1",
    "Second Godshard"           : "obtained_godshard_2",
    "Third Godshard"            : "obtained_godshard_3",
    "Ashen Key"                 : "obtained_ashen_key",
    "Starlight Key"             : "obtained_starlight_key",
    "Starlight Shard"           : "obtained_starlight_shard",
    "Agreement Stone"           : "obtained_agreement_stone",
    "Crystal Mirror"            : "obtained_crystal_mirror",
    "Hollow Stone"              : "obtained_hollow_stone",
    "Dawn Shard"                : "obtained_dawn_shard",
    "Void Shard"                : "obtained_void_shard",
    "Vaethar's Tear"            : "obtained_vaethars_tear",
    "Old Crown"                 : "obtained_old_crown",
    "Broken Seal"               : "obtained_broken_seal",
    "Warden's Seal"             : "obtained_wardens_seal",
    "Ashen Tablet"              : "obtained_ashen_tablet",
    "Charred Ledger"            : "obtained_charred_ledger",
    "Rolled Parchment"          : "obtained_rolled_parchment",
    "Imperial Edict"            : "obtained_imperial_edict",
    "Codex of the First Age"    : "obtained_codex",
    "Blood Key"                 : "obtained_blood_key",
    "Warden's Key"              : "obtained_wardens_key",
    "Throne Key"                : "obtained_throne_key",
}

