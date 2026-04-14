# ─── ROOM LISTS ───────────────────────────────────────────────────────────────
SPECIAL_ROOMS = [
    {"name":"The Shrine of Eon",           "weight":4,"min_depth":0, "event":"shrine",
     "description":"A stone altar: a serpent devouring its own tail. Candles burn without wax. The air is warm and patient."},
    {"name":"The Merchant's Alcove",       "weight":5,"min_depth":0, "event":"merchant",
     "description":"A weathered merchant sits cross-legged on a rolled mat. His eyes are the wrong colour."},
    {"name":"The Trapped Vault",           "weight":4,"min_depth":0, "event":"trap_vault",
     "description":"A heavy iron door stands ajar. Inside, glittering objects. The flagstones look wrong."},
    {"name":"The Whispering Library",      "weight":3,"min_depth":0, "event":"library",
     "description":"Shelves of rotting tomes. One book lies open on a lectern, pages turning in no wind."},
    {"name":"The Prisoner's Cell",         "weight":4,"min_depth":0, "event":"prisoner",
     "description":"Iron bars. A thin mattress. Tally marks in the thousands. A figure that looks up."},
    {"name":"The Hall of the Mural",       "weight":3,"min_depth":3, "event":"mural_hall",
     "description":"A vast hall covered in a painted mural. Impossibly vivid. It depicts the beginning of things."},
    {"name":"Chamber of the Near-Mortal",  "weight":2,"min_depth":5, "event":"sael_chamber",
     "description":"Cleaner air. Silver-threaded script on the walls. A figure stands at the far end."},
    {"name":"The Inscription Room",        "weight":3,"min_depth":2, "event":"inscription_room",
     "description":"A perfectly preserved chamber. Every surface covered in a single looping sentence. A dish of ash at the centre."},
    {"name":"The Dragon-Hall",             "weight":1,"min_depth":8, "event":"dragon_hall",
     "description":"A vault built for something immense. Something breathes at the far end. You feel its warmth from the doorway."},
    {"name":"The Vault Door",              "weight":3,"min_depth":4, "event":"vault_door",
     "description":"A chamber that exists only to contain a door. 'What the empire buried, the empire kept.'"},
    {"name":"The Sealed Sanctum",          "weight":1,"min_depth":10,"event":"sealed_sanctum",
     "description":"A door of pale stone. No hinges, no handle. Ash-coloured runes that absorb light."},
    {"name":"The Veythari Door",           "weight":1,"min_depth":7, "event":"veythari_door",
     "description":"A door of white stone etched with star-patterns. It glows from itself. The keyhole is shard-shaped."},
    {"name":"The Well Chamber",            "weight":1,"min_depth":15,"event":"void_well",
     "description":"The stairs end here. A circular chamber of absolute silence. In its centre: a well of solid darkness."},
    {"name":"The Blood Door",              "weight":1,"min_depth":9, "event":"blood_door",
     "description":"A door of dark red stone, warm to the touch. The keyhole is organic in shape."},
    {"name":"The Warden's Archive",        "weight":2,"min_depth":6, "event":"wardens_archive",
     "description":"A door bearing the eye-and-scales emblem of the Warden's office. Records wait behind it."},
    {"name":"The Throne of Eldros-Verath", "weight":1,"min_depth":13,"event":"throne_room",
     "description":"A grand chamber, not ruined — arrested. Something happened here and everything stayed where it fell."},
    {"name":"Chamber of Orrath",           "weight":2,"min_depth":6, "event":"orrath_chamber",
     "description":"Darker than the others. The darkness has presence. A shape in the corner resolves into a figure."},
    {"name":"The Gambling Den",            "weight":3,"min_depth":2, "event":"gambling_den",
     "description":"Three figures around a low table. Cards and coins between them. 'Room for one more.'"},
    {"name":"The Broken Altar",            "weight":3,"min_depth":1, "event":"broken_altar",
     "description":"An altar split clean in two by force. Between the halves: a sealed cavity in the stone base."},
    {"name":"The Ossuary",                 "weight":2,"min_depth":3, "event":"ossuary",
     "description":"Bones stacked with care. Each skull has something placed in its eye sockets — all the same."},
    {"name":"The Empty Throne",            "weight":2,"min_depth":5, "event":"empty_throne",
     "description":"A throne room, grand in ruin. The throne itself is intact. Something about it resists you."},
    {"name":"The Mirror Chamber",          "weight":2,"min_depth":4, "event":"mirror_chamber",
     "description":"Two surviving mirrors face each other. In the reflections: something that is not you."},
    {"name":"The Well of Stars",           "weight":1,"min_depth":11,"event":"astral_well_hint",
     "description":"No ceiling — or rather, a ceiling that is open sky: stars visible, unmoving, underground."},
    {"name":"The Hollow Wall",             "weight":2,"min_depth":5, "event":"hollow_stone_room",
     "description":"A room with one sealed wall — perfectly flat, no seams. A circular indentation at its centre."},
    {"name":"The Chamber of the Agreement", "weight":1, "min_depth":12, "event":"chamber_of_agreement",
     "description":"The air here is wrong. Not cold — wrong. As though the air itself remembers "
                   "something that happened in this room and cannot stop remembering it. "
                   "On the floor: a perfect circle, scorched into the stone, that no amount of time "
                   "has faded."},
    {"name":"The Ritual Chamber",           "weight":0, "min_depth":14, "event":"ritual_chamber",
     "description":"A circular room with a domed ceiling. "
                   "In the centre: a stone dais, carved with the nine-circle diagram of the wells. "
                   "The dais has a hollow at its centre — shaped precisely like a collection "
                   "of fragments pressed together."},

    {"name":"The Hall of the Nine",          "weight":2,"min_depth":6,  "event":"hall_of_nine",
     "description":"A circular hall. Nine alcoves are set into the walls at equal intervals, "
                   "each carved with a different symbol older than the empire. "
                   "A mosaic of nine circles covers the floor. The golden centre has been pried out."},
    {"name":"The Hall of the Shattered Crown","weight":1,"min_depth":10, "event":"hall_of_shattered_crown",
     "description":"Cruder stonework than the rest — this room was built after the fall. "
                   "The walls depict a war fought across three generations. "
                   "At the centre: a stone plinth."},
    {"name":"The Veythari Sanctuary",         "weight":1,"min_depth":7,  "event":"veythari_sanctuary",
     "description":"Silver light from the walls themselves. A pool of still water. "
                   "A pale tree, leafless, its branches holding small cold lights that do not flicker."},
    {"name":"The Chamber of Reflections",     "weight":2,"min_depth":4,  "event":"crystal_mirror_room",
     "description":"A small square chamber where every surface is polished. "
                   "The reflections are wrong. At the centre: a wooden stand, and on the stand, "
                   "a mirror, face-down."},
    {"name":"The Dawn Chamber",               "weight":1,"min_depth":3,  "event":"dawn_shard_room",
     "description":"A room lit by pale orange light with no source — "
                   "the colour of the sky just before sunrise. "
                   "On a flat stone at the far end: a small warm fragment."},
    {"name":"Talarion's Room",                "weight":1,"min_depth":8,  "event":"talarion_room",
     "description":"A scholar's room — desk, shelves, the remnants of a life spent writing. "
                   "Someone worked here for a very long time and left deliberately."},
    {"name":"The Deep Market",          "weight":2, "min_depth":15, "event":"black_market",
     "description":"A figure behind a low table. No candles — "
                   "the stock is lit by something the items themselves emit. "
                   "They do not look up when you enter."},
    {"name":"The Cartographer's Station","weight":2,"min_depth":3,  "event":"cartographers_station",
     "description":"A scholar's workspace — tools for mapping, rulers, inks, "
                   "partial maps of the upper ruins pinned to a large flat table. "
                   "Below a certain depth, the cartographer stopped."},
    {"name":"The Place Between",         "weight":0,"min_depth":0,  "event":"recovery_room",
     "description":"A room made from leftover space. On a shelf: things you recognise."},
    {'name':'The Warden Bell',           "weight":2,"min_depth":8,   "event":"warden_bell",
     "description":"A room with a large dark bell standing in the centre, covered in a thick layer of dust."},
    {"name": "The Forge",
     "weight": 2, "min_depth": 4, "event": "forge",
     "description": "A forge, still burning. The coals have not been replenished "
                    "in centuries and show no sign of going out. "
                    "The tools are laid out as though someone has just stepped away. "
                    "The bellows work on their own."
     },
    {"name": "The Archivist's Study",        "weight": 2, "min_depth": 2,  "event": "archivist",
     "description": "A folding stool. Papers everywhere. Maps annotated in a scholar's hand. "
                    "Someone has been here a very long time, working."},
    {"name": "The Bound One's Corner",       "weight": 2, "min_depth": 6,  "event": "bound_one",
     "description": "A figure against the wall, one hand pressing flat against the stone. "
                    "Neither hostile nor entirely present."},
    {"name": "The Warden's Echo",            "weight": 1, "min_depth": 7,  "event": "serethan_echo",
     "description": "The room holds a presence — not a ghost, not a person. "
                    "The strong memory of someone who stood here, felt very strongly "
                    "about something, and did not ring the bell."},
    {"name": "The Shard-Seeker Captain",     "weight": 2, "min_depth": 3,  "event": "seeker_captain",
     "description": "A mercenary — better equipped than the others — reading. "
                    "Not reaching for a weapon."},
    {"name": "The Deep Sleeper's Chamber",   "weight": 1, "min_depth": 16, "event": "deep_sleeper",
     "description": "The deepest room. Something vast and old has arranged itself here. "
                    "The air breathes very slowly. It is awake, in its way."},
    {"name": "The Ossuary of the Near-Mortals","weight":1,"min_depth": 8,  "event": "near_mortal_ossuary",
     "description": "Different from the human ossuary. These remains are Morvath and Veythari. "
                    "Some wrapped in silver cloth that still holds light. Some in cloth that holds dark."},
    {"name": "The War Room",                 "weight": 2, "min_depth": 5,  "event": "war_room",
     "description": "A large table covered in a map of the city as it was — "
                    "intact, radiating from a central keep. Markers. Routes. Plans never implemented."},
    {"name": "The Chapel of the Thrys",      "weight": 2, "min_depth": 3,  "event": "chapel_of_thrys",
     "description": "A small chapel. Nine niches, each carved with the symbol of one of the Sera. "
                    "The candles still burn. None of them have wax."},
    {"name": "The Observatory",              "weight": 1, "min_depth": 9,  "event": "observatory",
     "description": "The ceiling is open to the sky. This should be impossible. "
                    "The stars visible through the opening are not the right stars."},
    {"name": "The Naming Room",              "weight": 2, "min_depth": 4,  "event": "naming_room",
     "description": "Every surface covered in names. New names form as you watch. "
                    "The room is cataloguing the dead. It has been doing this "
                    "since the Night of Collapse."},
    {"name": "The Archive of Agreements",    "weight": 1, "min_depth": 11, "event": "archive_agreements",
     "description": "Shelves of bound volumes. Every formal agreement ever made in Eldros. "
                    "The final entry is not formatted like the others."},
    {"name": "The Atraxis Scar",             "weight": 1, "min_depth": 15, "event": "atraxis_scar",
     "description": "The floor is wrong. A red-black discolouration radiates from a central point "
                    "in perfect circles. Something came through here. "
                    "The air is present in a way air is not usually present."},
    {"name": "The Poison Garden",            "weight": 2, "min_depth": 6,  "event": "poison_garden",
     "description": "Plants that should not be underground. Planted in rows. Tended. "
                    "Several of them glow. Several of them are clearly toxic."},

    # Second-descent only
    {"name":"The Deeper Staircase",        "weight":0,"min_depth":1, "event":"deeper_staircase",
     "description":"A staircase you did not come from. It descends at a steep angle. Cold air rises from it."},

]

ATMOSPHERIC_ROOMS = [
    {"name":"A Warm Room",
     "description":"The room is warm. No heat source. The warmth comes from the walls — "
                   "as though the stone remembers something. It is not unpleasant. That is the most unsettling thing.",
     "event":None},
    {"name":"The Handprint Chamber",
     "description":"A single handprint on the far wall. Pressed in dark pigment. No other marking. "
                   "The handprint is not human-sized — just slightly wrong in its proportions. "
                   "You stay longer than you intend to.",
     "event":None},
    {"name":"The Flooded Antechamber",
     "description":"Water to ankle depth, cold and perfectly still. "
                   "The reflection shows the ceiling as it was: intact arches, lit sconces, a different time. "
                   "Below the surface, something catches the light.",
     "event":"flooded_room"},
    {"name":"The Listening Room",
     "description":"Acoustically strange. Your footsteps sound far away. "
                   "A murmur from the walls resolves, if you stand still enough, into voices. "
                   "Not threatening. Not intelligible. Just present.",
     "event":"listening_room"},
    {"name":"The Room Without a Door",
     "description":"You turn around and the passage you came through is gone. Solid wall. "
                   "One exit: forward. The wall behind you is warm and shows no seam.",
     "event":None},
    {"name":"The Gallery of Faces",
     "description":"Carved faces at eye level — dozens, each different, each looking inward. All eyes closed. "
                   "When you reach the centre, the faces behind you have their eyes open.",
     "event":None},
    {"name":"The Tilted Room",
     "description":"The floor slopes toward a drain. Not dramatically — but everything has gathered at the low end "
                   "over centuries. You find yourself checking your pockets.",
     "event":None},
    {"name":"The Sealed Window",
     "description":"A window, underground, bricked from the other side. A crack at eye level. "
                   "The light through it is a pale blue-white you have no name for.",
     "event":"sealed_window"},
    {"name":"The Scorched Corridor",
     "description":"The walls are black. The stone at the midpoint of this corridor is fused — "
                   "melted and re-hardened. Something passed through here that was much hotter than fire.",
     "event":None},
    {"name":"The Room of Clocks",
     "description":"A dozen timekeeping devices of Eldrosian make, all stopped at the same moment. "
                   "The hands point to a time that means nothing to you. They meant something once.",
     "event":None},
    {"name":"The Mirrored Ceiling",
     "description":"The ceiling is polished to reflectiveness. "
                   "Looking up, you see the room below you — and a figure standing in it, looking up at you. "
                   "The figure is you. The figure's room is the same as this one. "
                   "The figure's expression is slightly different from yours.",
     "event":None},
    {"name":"The Counting Room",
     "description":"Someone has been in this room for a very long time, counting things. "
                   "The walls are covered in tally marks, arranged in groups. "
                   "In the corner: a fresh mark, made recently, in dust.",
     "event":None},
]