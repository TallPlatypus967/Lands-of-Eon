
# ─── DIRECTIONS ───────────────────────────────────────────────────────────────
ALL_DIRS = ["north", "south", "east", "west"]
OPP      = {"north":"south","south":"north","east":"west","west":"east"}

def make_exits(came_from=None, forced_count=None):
    exits = {d: False for d in ALL_DIRS}
    if came_from:
        exits[came_from] = True
    available = [d for d in ALL_DIRS if not exits[d]]
    count = forced_count if forced_count is not None else random.randint(1, min(3, len(available)))
    for d in random.sample(available, min(count, len(available))):
        exits[d] = True
    return exits

def exit_list(exits):
    return [d for d, v in exits.items() if v]

def describe_exits(exits):
    od = exit_list(exits)
    if len(od) == 1:   return f"One passage leads {od[0]}."
    if len(od) == 2:   return f"Passages lead {od[0]} and {od[1]}."
    return f"Passages lead {', '.join(od[:-1])} and {od[-1]}."


# Floor dimensions: (width, height) per z-level
FLOOR_DIMS = {
    0: (8, 6),   # entrance — widestself.visited = False  # should be a boolDun
    1: (8, 6),
    2: (7, 5),
    3: (6, 5),
    4: (5, 4),   # deepest — smallest
}

# Target room counts per floor (carved cells)
FLOOR_TARGETS = {0: 18, 1: 18, 2: 16, 3: 14, 4: 12}

# Minimum graph distance between staircases on the same floor
MIN_STAIR_SEPARATION = 3

# ── Special room assignment table ────────────────────────────────────────────
# Format: (event_key, preferred_z, required_z_min, is_on_critical_path, sealed)
ROOM_ASSIGNMENT_TABLE = [
    # z=0 guaranteed rooms
    ("shrine",             0, 0, True,  False),
    ("merchant",           0, 0, True,  False),
    ("library",            0, 0, False, False),
    ("prisoner",           0, 0, True,  False),
    ("trap_vault",         0, 0, False, False),
    ("broken_altar",       0, 0, False, False),
    ("gambling_den",       0, 0, False, False),
    ("archivist",          0, 0, False, False),
    ("seeker_captain",     0, 0, False, False),
    # z=1
    ("mural_hall",         1, 1, True,  False),
    ("inscription_room",   1, 1, False, False),
    ("vault_door",         1, 1, True,  False),
    ("crystal_mirror_room",1, 1, False, False),
    ("dawn_shard_room",    1, 1, False, False),
    ("ossuary",            1, 1, False, False),
    ("cartographers_station",1,1,False, False),
    ("forge",              1, 1, False, False),   # z=1, non-critical, not sealed
    ("war_room",           1, 1, False, False),
    ("chapel_of_thrys",    1, 1, False, False),
    ("naming_room",        1, 1, False, False),
    # z=2
    ("sael_chamber",       2, 2, True,  False),
    ("orrath_chamber",     2, 2, False, False),
    ("dragon_hall",        2, 2, False, False),
    ("veythari_door",      2, 2, False, False),
    ("wardens_archive",    2, 2, False, False),
    ("hollow_stone_room",  2, 2, False, False),
    ("empty_throne",       2, 2, True,  False),
    ("mirror_chamber",     2, 2, False, False),
    ("bound_one",          2, 2, False, False),
    ("serethan_echo",      2, 2, False, False),
    ("near_mortal_ossuary",2, 2, False, False),
    ("observatory",        2, 2, False, False),
    ("poison_garden",      2, 2, False, False),
    # z=3
    ("throne_room",        3, 3, True,  True),   # sealed after godshard taken
    ("sealed_sanctum",     3, 3, True,  False),
    ("hall_of_nine",       3, 3, False, False),
    ("hall_of_shattered_crown",3,3,True,False),
    ("blood_door",         3, 3, False, False),
    ("talarion_room",      3, 3, False, False),
    ("veythari_sanctuary", 3, 3, False, False),
    ("astral_well_hint",   3, 3, False, False),
    ("warden_bell",        3, 3, False, False),  # NEW: Warden's Bell
    ("archive_agreements", 3, 3, False, False),
    # z=4
    ("void_well",          4, 4, True,  True),   # sealed after confrontation/sealing
    ("ritual_chamber",     4, 4, True,  True),   # sealed after ritual fires
    ("chamber_of_agreement",4,4,False, False),
    ("black_market",       4, 4, False, False),
    ("sealed_sanctum",     4, 4, False, False),  # second copy if needed
    ("atraxis_scar",       4, 4, False, False),
    ("deep_sleeper",       4, 4, False, False),
]

# Atmospheric room names (no event, pure flavour)
ATMOSPHERIC_NAMES = [
    "A Warm Room", "The Handprint Chamber", "The Flooded Antechamber",
    "The Listening Room", "The Room Without a Door", "The Gallery of Faces",
    "The Tilted Room", "The Sealed Window", "The Scorched Corridor",
    "The Room of Clocks", "The Mirrored Ceiling", "The Counting Room",
]

# Map display characters per event type
EVENT_GLYPHS = {
    "shrine":              ("◉", Fore.YELLOW),
    "merchant":            ("$", Fore.YELLOW),
    "library":             ("L", Fore.CYAN),
    "prisoner":            ("P", Fore.WHITE),
    "trap_vault":          ("!", Fore.RED),
    "broken_altar":        ("A", Fore.WHITE),
    "gambling_den":        ("G", Fore.YELLOW),
    "mural_hall":          ("M", Fore.CYAN),
    "inscription_room":    ("I", Fore.CYAN),
    "vault_door":          ("K", Fore.YELLOW),
    "crystal_mirror_room": ("◈", Fore.CYAN),
    "dawn_shard_room":     ("☀", Fore.YELLOW),
    "ossuary":             ("☠", Fore.WHITE),
    "cartographers_station":("C",Fore.CYAN),
    "sael_chamber":        ("S", Fore.WHITE),
    "orrath_chamber":      ("O", Fore.LIGHTBLUE_EX),
    "dragon_hall":         ("D", Fore.RED),
    "veythari_door":       ("✦", Fore.WHITE),
    "wardens_archive":     ("W", Fore.YELLOW),
    "hollow_stone_room":   ("◌", Fore.WHITE),
    "empty_throne":        ("T", Fore.WHITE),
    "mirror_chamber":      ("◫", Fore.MAGENTA),
    "warden_bell":         ("W", Fore.RED),
    "throne_room":         ("♛", Fore.RED),
    "sealed_sanctum":      ("▣", Fore.MAGENTA),
    "hall_of_nine":        ("9", Fore.YELLOW),
    "hall_of_shattered_crown":("⚔",Fore.RED),
    "blood_door":          ("B", Fore.RED),
    "talarion_room":       ("τ", Fore.CYAN),
    "veythari_sanctuary":  ("✧", Fore.WHITE),
    "astral_well_hint":    ("★", Fore.WHITE),
    "void_well":           ("◉", Fore.LIGHTBLUE_EX),
    "ritual_chamber":      ("Ψ", Fore.YELLOW),
    "chamber_of_agreement":("∅", Fore.MAGENTA),
    "black_market":        ("£", Fore.RED),
    "recovery_room":       ("↺", Fore.MAGENTA),
    "flooded_room":        ("~", Fore.CYAN),
    "listening_room":      (")", Fore.WHITE),
    "sealed_window":       ("⊟", Fore.WHITE),
}
