"""
LANDS OF EON  —  Ruins of Eldros-Verath, capital of the first empire.
"""
import random, textwrap, sys
import json, os, pathlib, copy
import DungeonRoom, Dungeon, DungeonMap, ENEMY_POOL, ITEM_POOL, Player

# ─── COLOUR ───────────────────────────────────────────────────────────────────
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    COLOUR = True
except ImportError:
    class _Stub:
        def __getattr__(self, _): return ""
    Fore = Style = _Stub()
    COLOUR = False

def c(text, colour=""):
    return colour + text + Style.RESET_ALL if COLOUR else text

def wrap(text, colour="", width=72):
    filled = textwrap.fill(text, width)
    print(colour + filled + Style.RESET_ALL if (COLOUR and colour) else filled)

def hr(char="─", width=56, colour=""):
    print(colour + char*width + Style.RESET_ALL if (COLOUR and colour) else char*width)

def title_bar(text):
    hr(colour=Fore.YELLOW)
    print(c(f"  {text}", Fore.YELLOW))
    hr(colour=Fore.YELLOW)

def pause():
    input(c("\n  [ Press Enter to continue ]", Fore.LIGHTBLUE_EX + Style.BRIGHT))
    print()

def prompt(options):
    for i, opt in enumerate(options, 1):
        print(c(f"  [{i}]", Fore.CYAN) + f" {opt}")
    while True:
        raw = input(c("  > ", Fore.CYAN)).strip()
        if raw.isdigit() and 1 <= int(raw) <= len(options):
            return options[int(raw) - 1]
        print(c("  Enter a number from the list.", Fore.RED))

def secret_input(player, prompt_text=""):
    raw = input(c(f"  {prompt_text}> ", Fore.MAGENTA)).strip().lower()
    player.secrets_spoken.add(raw)
    return raw

# ── Helper functions used during generation ──────────────────────────────────
def _staircase_desc(room: DungeonRoom) -> str:
    if room.exits.get("down") and room.exits.get("up"):
        return ("A landing between floors. Stone steps lead both up and down. "
                "The air changes noticeably as you pass through.")
    elif room.exits.get("down"):
        return ("Stone steps descend into the next level of the ruins. "
                "The air below is colder, or older, or both.")
    else:
        return ("Stone steps lead upward. The light above is different from the light below.")


def _normal_room_def(rng: random.Random, z: int) -> dict:
    desc, ambient = rng.choice(NORMAL_ROOMS)
    return {
        "name":         "Chamber",
        "description":  desc,
        "special_event":None,
        "items":        [],
        "enemies":      [],
        "ambient":      ambient,
    }

# ─── PLAYER ───────────────────────────────────────────────────────────────────
class Player:
    def __init__(self, name):
        self.name = name
        self.max_hp  = 30    # was 45
        self.hp      = 30
        self.attack  = 6
        self.defence = 2
        self.gold    = 0
        self.inventory      = []
        self.equipped       = {"weapon": None, "armour": None, "relic": None}
        self.poisoned       = False
        self.cursed         = False
        self.void_ward      = False   # Void Salt protection vs drain
        self.visited_rooms  = 0
        self.depth          = 0
        self.descent        = 1      # which descent (1 = first, 2 = second etc.)
        self.secrets_spoken = set()
        self.flags          = set()
        self.dungeon     = None          # set by run_game
        self.dungeon_pos = (0, 0, 0)     # current position in dungeon
        self.map         = DungeonMap()  # for tracking visited rooms
        # Faction reputation: -2 (hostile) to +2 (allied)
        self.reputation = {
            "scholars":    0,   # Remnant Scholars
            "void_touched": 0,  # Void-Touched cultists
            "seekers":     0,   # Shard-Seekers
        }

    def total_attack(self):
        b = self.equipped["weapon"]["value"] if self.equipped["weapon"] else 0
        curse = -2 if self.cursed else 0
        relic_bonus = 0
        relic = self.equipped.get("relic")
        if relic:
            effect = relic.get("relic_effect", {})
            if effect.get("type") == "attack":
                relic_bonus = effect["value"]
        return max(1, self.attack + b + curse + relic_bonus)

    def total_defence(self):
        b = self.equipped["armour"]["value"] if self.equipped["armour"] else 0
        relic_bonus = 0
        relic = self.equipped.get("relic")
        if relic:
            effect = relic.get("relic_effect", {})
            if effect.get("type") == "defence":
                relic_bonus = effect["value"]
        return self.defence + b + relic_bonus

    def pick_up(self, item):
        if item:
            self.inventory.append(item)
            print(c(f"  Picked up: {item['name']}", Fore.GREEN))

    def has_item(self, name):
        return any(it["name"] == name for it in self.inventory)

    def remove_item(self, name):
        it = next((i for i in self.inventory if i["name"] == name), None)
        if it: self.inventory.remove(it)

    def sorted_inventory(self, mode: str = "type") -> list:
        """
        Return a sorted copy of inventory.
        Modes: 'type' | 'name' | 'value' | 'recent'
        """
        if mode == "type":
            TYPE_ORDER = {
                "weapon": 0, "armour": 1, "relic": 2, "consumable": 3,
                "thrown": 4, "food": 5, "artefact": 6,
                "material": 7, "lore": 8, "key": 9
            }
            return sorted(self.inventory,
                          key=lambda it: (TYPE_ORDER.get(it["type"], 9), it["name"]))
        elif mode == "name":
            return sorted(self.inventory, key=lambda it: it["name"].lower())
        elif mode == "value":
            return sorted(self.inventory,
                          key=lambda it: -(it.get("value", 0)))
        elif mode == "recent":
            return list(self.inventory)  # original insertion order
        return list(self.inventory)

    def show_inventory(self, sort_mode: str = None):
        title_bar("INVENTORY")

        # Determine sort mode — persist on the player object
        if sort_mode is not None:
            self._inv_sort = sort_mode
        current_sort = getattr(self, "_inv_sort", "type")

        if not self.inventory:
            print(c("  (empty)", Fore.LIGHTBLUE_EX + Style.BRIGHT))
        else:
            items = self.sorted_inventory(current_sort)
            last_type = None
            for item in items:
                # Print a divider when the type changes (only in 'type' mode)
                if current_sort == "type" and item["type"] != last_type:
                    last_type = item["type"]
                    label = {
                        "weapon":"── Weapons ──", "armour":"── Armour ──",
                        "relic":"── Relics ──", "consumable":"── Consumables ──",
                        "thrown":"── Thrown Weapons ──", "food":"── Food & Drink ──",
                        "artefact":"── Artefacts ──", "material":"── Materials ──",
                        "lore":"── Lore ──", "key":"── Keys ──"
                    }.get(item["type"], "──")
                    print(c(f"\n  {label}", Fore.YELLOW))

                tag = ""
                if item is self.equipped["weapon"]:    tag = c(" [weapon]", Fore.GREEN)
                elif item is self.equipped["armour"]:  tag = c(" [armour]", Fore.GREEN)
                elif item is self.equipped.get("relic"): tag = c(" [relic]", Fore.MAGENTA)
                col = {"key":Fore.YELLOW,"lore":Fore.CYAN,"artefact":Fore.MAGENTA}.get(
                    item["type"], Fore.WHITE)
                print(c(f"    {item['name']}", col) + tag +
                      c(f"  —  {item['description']}", Fore.LIGHTBLUE_EX + Style.BRIGHT))

        print()
        print(c(f"  Gold: {self.gold}", Fore.YELLOW) +
              c(f"  |  HP: {self.hp}/{self.max_hp}", Fore.GREEN) +
              c(f"  |  ATK: {self.total_attack()}  DEF: {self.total_defence()}", Fore.CYAN))
        if self.poisoned:   print(c("  [POISONED — -2 HP per room]", Fore.RED))
        if self.cursed:     print(c("  [CURSED — ATK-2, cure with Clarity Draught]", Fore.MAGENTA))
        if self.void_ward:  print(c("  [VOID WARD — protected vs drain]", Fore.CYAN))

    def equip_relic(self, relic_item):
        """Equip a relic. Handles max_hp bonus correctly."""
        # Remove old relic
        old = self.equipped.get("relic")
        if old:
            old_effect = old.get("relic_effect", {})
            if old_effect.get("type") == "max_hp":
                self.max_hp -= old_effect["value"]
                self.hp = min(self.hp, self.max_hp)
        # Apply new relic
        self.equipped["relic"] = relic_item
        if relic_item:
            new_effect = relic_item.get("relic_effect", {})
            if new_effect.get("type") == "max_hp":
                bonus = new_effect["value"]
                self.max_hp += bonus
                self.hp = min(self.hp + bonus, self.max_hp)

    def use_item(self):
        usable = [it for it in self.inventory
                  if it["type"] in ("consumable","weapon","armour","lore","artefact", "food", "thrown", "relic", "material")]
        if not usable:
            print(c("  Nothing usable in your pack.", Fore.LIGHTBLUE_EX + Style.BRIGHT)); return
        opts = [it["name"] for it in usable] + ["Cancel"]
        ch = prompt(opts)
        if ch == "Cancel": return
        item = next(it for it in usable if it["name"] == ch)

        if item["type"] == "consumable":
            consumed = True
            if item["name"] == "Health Potion":
                r = min(item["value"], self.max_hp - self.hp); self.hp += r
                wrap(f"  Restored {r} HP. ({self.hp}/{self.max_hp})", Fore.GREEN)
            elif item['name'] == 'Vein-Sealer':
                r = min(item['value'], self.max_hp - self.hp); self.hp += r
                wrap(f"  Hardens your wounds. Restores {r} HP. ({self.hp}/{self.max_hp})", Fore.GREEN)
            elif item["name"] == "Strong Tonic":
                r = min(item["value"], self.max_hp - self.hp); self.hp += r
                wrap(f"  The tonic hits hard. Restored {r} HP. ({self.hp}/{self.max_hp})", Fore.GREEN)
            elif item["name"] == "Ember Flask":
                r = min(item["value"], self.max_hp - self.hp); self.hp += r
                wrap(f"  Fire down your throat. Restored {r} HP. ({self.hp}/{self.max_hp})", Fore.GREEN)
            elif item["name"] == "Bloodmoss Tincture":
                r = min(item["value"], self.max_hp - self.hp); self.hp += r
                wrap(f"  The tincture works. Restored {r} HP. ({self.hp}/{self.max_hp})", Fore.GREEN)
            elif item["name"] == "Antidote":
                if self.poisoned: self.poisoned = False; wrap("  Poison cleared.", Fore.GREEN)
                else: print("  Not poisoned."); consumed = False
            elif item["name"] == "Clarity Draught":
                if self.cursed: self.cursed = False; wrap("  Curse lifted.", Fore.GREEN)
                else: print("  Not cursed."); consumed = False
            elif item["name"] == "Void Salt":
                self.void_ward = True
                wrap("  The salt coats your skin with cold. You are warded against draining for your next fight.", Fore.CYAN)
            if consumed: self.inventory.remove(item)

        elif item["type"] in ("weapon","armour"):
            self.equipped[item["type"]] = item
            wrap(f"  Equipped {item['name']}. +{item['value']} to {item['type']}.", Fore.GREEN)

        elif item["type"] == "lore":
            _read_lore(self, item)

        elif item["type"] == "relic":
            self.equip_relic(item)
            wrap(f"  Relic equipped: {item['name']}.", Fore.MAGENTA)
            if item.get("relic_effect", {}).get("type") == "max_hp":
                print(c(f"  Max HP +{item['relic_effect']['value']}.", Fore.GREEN))
            elif item.get("relic_effect", {}).get("type") == "attack":
                print(c(f"  ATK +{item['relic_effect']['value']} while equipped.", Fore.GREEN))
            elif item.get("relic_effect", {}).get("type") == "defence":
                print(c(f"  DEF +{item['relic_effect']['value']} while equipped.", Fore.GREEN))

        elif item["type"] == "food":
            _eat_food(self, item)
            self.inventory.remove(item)

        elif item["type"] == "thrown":
            wrap(f"  The {item['name']} is a thrown weapon — use it during combat.", Fore.YELLOW)

        elif item["type"] == "material":
            wrap(f"  {item['description']}", Fore.YELLOW)
            wrap("  This material is used at the Forge.", Fore.YELLOW)

        elif item["type"] == "artefact":
            wrap(f"  You examine the {item['name']}.", Fore.MAGENTA)
            wrap(f"  {item['description']}", Fore.MAGENTA)
            wrap("  You sense it has a purpose, but not here.",
                 Fore.LIGHTBLUE_EX + Style.BRIGHT)
            pause()   # ← added

    def apply_poison_tick(self):
        if self.poisoned:
            self.hp -= 2
            print(c(f"  Poison. -2 HP. ({self.hp}/{self.max_hp})", Fore.RED))



def get_item(name):
    item = next((it for it in ITEM_POOL if it["name"] == name), None)
    return dict(item) if item else None

def random_item():
    """Return a random non-unique equipment or consumable item."""
    EXCLUDE = set(UNIQUE_ITEMS.keys())
    pool = [it for it in ITEM_POOL
            if it["type"] not in ("key", "lore", "artefact")
            or (it["type"] == "artefact" and it["name"] not in EXCLUDE)]
    # Further exclude artefacts from random drops entirely — placed deliberately
    pool = [it for it in pool if it["type"] != "artefact"]
    return dict(random.choice(pool))

class Dungeon:
    """
    The pre-generated 3D dungeon.

    grid[x][y][z] → DungeonRoom | None
    Player navigates by moving between connected rooms.
    """

    def __init__(self):
        self.grid:   dict  = {}   # (x,y,z) → DungeonRoom
        self.entrance: tuple = (0, 0, 0)
        self.seed:   int   = 0

    # ── Access ────────────────────────────────────────────────────────────────

    def get(self, pos: tuple) -> "DungeonRoom | None":
        return self.grid.get(pos)

    def room_at(self, x, y, z) -> "DungeonRoom | None":
        return self.grid.get((x, y, z))

    def all_rooms(self) -> list:
        return list(self.grid.values())

    # ── Phase 1: Carve ────────────────────────────────────────────────────────

    def _carve_floor(self, z: int, seed: int):
        """
        Randomised DFS maze carver for one floor.
        Carves approximately FLOOR_TARGETS[z] rooms into the grid.
        Rooms are connected horizontally only on the same floor.
        """
        rng = random.Random(seed * 31 + z * 97)
        w, h = FLOOR_DIMS[z]
        target = FLOOR_TARGETS[z]

        # Start from a random interior cell
        start_x = rng.randint(1, w - 2)
        start_y = rng.randint(1, h - 2)
        start   = (start_x, start_y, z)

        carved   = set()
        stack    = [start]
        carved.add(start)

        DIR_DELTA = {
            "north": (0, 1, 0), "south": (0, -1, 0),
            "east":  (1, 0, 0), "west":  (-1, 0, 0),
        }

        while stack and len(carved) < target:
            current = stack[-1]
            cx, cy, cz = current

            # Find unvisited neighbours
            dirs = list(DIR_DELTA.items())
            rng.shuffle(dirs)
            moved = False
            for direction, (dx, dy, dz) in dirs:
                nx, ny, nz = cx+dx, cy+dy, cz+dz
                npos = (nx, ny, nz)
                if (0 <= nx < w and 0 <= ny < h
                        and npos not in carved
                        and len(carved) < target):
                    # Carve this cell and connect
                    if current not in self.grid:
                        self.grid[current] = DungeonRoom(current)
                    if npos not in self.grid:
                        self.grid[npos] = DungeonRoom(npos)
                    opp = DungeonRoom.OPP[direction]
                    self.grid[current].exits[direction] = npos
                    self.grid[npos].exits[opp] = current
                    carved.add(npos)
                    stack.append(npos)
                    moved = True
                    break
            if not moved:
                stack.pop()

        # Ensure start is in grid
        if start not in self.grid:
            self.grid[start] = DungeonRoom(start)

        return carved

    def _place_staircases(self, carved_by_floor: dict, rng: random.Random):
        """
        Connect floors with staircases.
        Each floor (except z=4) gets 2 staircases down.
        Staircases are placed at carved cells far from each other.
        """
        for z in range(len(FLOOR_DIMS) - 1):
            upper_cells = list(carved_by_floor.get(z,   set()))
            lower_cells = list(carved_by_floor.get(z+1, set()))
            if not upper_cells or not lower_cells:
                continue

            rng.shuffle(upper_cells)
            rng.shuffle(lower_cells)

            placed = 0
            used_upper = []

            for upper_pos in upper_cells:
                if placed >= 2:
                    break
                # Check separation from previously placed staircases
                ux, uy, _ = upper_pos
                too_close = any(
                    abs(ux - px) + abs(uy - py) < MIN_STAIR_SEPARATION
                    for px, py, _ in used_upper
                )
                if too_close:
                    continue

                # Find a lower cell to connect to
                lower_pos = lower_cells[placed % len(lower_cells)]

                upper_room = self.grid.get(upper_pos)
                lower_room = self.grid.get(lower_pos)
                if upper_room and lower_room:
                    upper_room.exits["down"] = lower_pos
                    lower_room.exits["up"]   = upper_pos
                    used_upper.append(upper_pos)
                    placed += 1

    # ── Phase 2: Assign room types ────────────────────────────────────────────

    def _assign_rooms(self, rng: random.Random, descent: int = 1):
        """
        Assign special room definitions to carved cells.
        Works floor by floor, guaranteed placement for critical-path rooms.
        """
        # Count how many special rooms are needed per floor
        needed_per_floor = {}
        for event_key, pref_z, min_z, critical, seal in ROOM_ASSIGNMENT_TABLE:
            needed_per_floor[pref_z] = needed_per_floor.get(pref_z, 0) + 1

        # Group carved rooms by z-level
        by_z: dict = {}
        for pos, room in self.grid.items():
            z = pos[2]
            by_z.setdefault(z, []).append(room)

        # For each floor, if there aren't enough non-staircase assignable rooms
        # to hold all the special rooms assigned to it, carve more rooms.
        for z, needed in needed_per_floor.items():
            assignable = [
                r for r in by_z.get(z, [])
                if not (r.exits.get("down") or r.exits.get("up"))
            ]
            shortfall = needed - len(assignable)
            if shortfall <= 0:
                continue

            # Carve extra rooms on this floor by extending existing dead ends
            w, h = FLOOR_DIMS.get(z, (8, 6))
            existing_positions = set(self.grid.keys())
            added = 0
            # Find dead-end rooms on this floor (only one horizontal exit)
            # and try to extend them into adjacent uncarved cells
            dead_ends = [
                r for r in by_z.get(z, [])
                if sum(1 for d in DungeonRoom.HORIZONTAL
                       if r.exits.get(d)) == 1
                   and not (r.exits.get("down") or r.exits.get("up"))
            ]
            rng.shuffle(dead_ends)

            DIR_DELTA = {
                "north": (0, 1, 0), "south": (0, -1, 0),
                "east":  (1, 0, 0), "west":  (-1, 0, 0),
            }

            for dead_end in dead_ends:
                if added >= shortfall:
                    break
                cx, cy, cz = dead_end.pos
                for direction, (dx, dy, dz) in DIR_DELTA.items():
                    nx, ny, nz = cx + dx, cy + dy, cz + dz
                    npos = (nx, ny, nz)
                    if (0 <= nx < w and 0 <= ny < h
                            and npos not in existing_positions):
                        # Carve the new room and connect it
                        new_room = DungeonRoom(npos)
                        opp = DungeonRoom.OPP[direction]
                        dead_end.exits[direction] = npos
                        new_room.exits[opp] = dead_end.pos
                        self.grid[npos] = new_room
                        existing_positions.add(npos)
                        by_z.setdefault(z, []).append(new_room)
                        added += 1
                        break  # move to next dead end

            if added < shortfall:
                # Last resort: expand the floor dimensions and try again
                # by finding any carved room with a free adjacent cell
                for pos, room in list(self.grid.items()):
                    if pos[2] != z:
                        continue
                    if added >= shortfall:
                        break
                    cx, cy, cz = pos
                    for direction, (dx, dy, dz) in DIR_DELTA.items():
                        if added >= shortfall:
                            break
                        nx, ny, nz = cx + dx, cy + dy, cz + dz
                        npos = (nx, ny, nz)
                        # Allow slightly outside original bounds for overflow rooms
                        if (npos not in existing_positions
                                and room.exits.get(direction) is None):
                            new_room = DungeonRoom(npos)
                            opp = DungeonRoom.OPP[direction]
                            room.exits[direction] = npos
                            new_room.exits[opp] = pos
                            self.grid[npos] = new_room
                            existing_positions.add(npos)
                            by_z.setdefault(z, []).append(new_room)
                            added += 1

        # Shuffle each floor's room list
        for z in by_z:
            rng.shuffle(by_z[z])

        # Track which rooms have been assigned
        assigned: set = set()   # set of (x,y,z)

        # ... rest of _assign_rooms is unchanged from here
        # Assign special rooms from the table
        for event_key, pref_z, min_z, critical, seal in ROOM_ASSIGNMENT_TABLE:
            # Pick target floor
            target_z = pref_z
            candidates = [
                r for r in by_z.get(target_z, [])
                if r.pos not in assigned
                   # Don't place on staircase cells
                   and not (r.exits.get("down") or r.exits.get("up"))
            ]
            # Fallback: any floor at or above min_z
            if not candidates:
                for z in range(min_z, len(FLOOR_DIMS)):
                    candidates = [
                        r for r in by_z.get(z, [])
                        if r.pos not in assigned
                           and not (r.exits.get("down") or r.exits.get("up"))
                    ]
                    if candidates:
                        break
            if not candidates:
                continue  # skip if truly no space

            # Pick the candidate
            if critical:
                # Critical rooms go near the "centre" of their floor
                w, h = FLOOR_DIMS.get(target_z, (8, 6))
                candidates.sort(
                    key=lambda r: abs(r.x - w//2) + abs(r.y - h//2)
                )
                chosen = candidates[0]
            else:
                chosen = rng.choice(candidates)

            # Look up the full special room definition
            spec = next(
                (sr for sr in SPECIAL_ROOMS if sr["event"] == event_key),
                None
            )
            if spec:
                chosen.room_def = {
                    "name":         spec["name"],
                    "description":  spec["description"],
                    "special_event":spec["event"],
                    "items":        [],
                    "enemies":      [],
                    "ambient":      None,
                }
                chosen.sealed = seal
                assigned.add(chosen.pos)

        # Assign atmospheric rooms
        atmo_pool = list(ATMOSPHERIC_ROOMS)
        rng.shuffle(atmo_pool)
        atmo_idx = 0
        for pos, room in self.grid.items():
            if pos in assigned:
                continue
            if room.exits.get("down") or room.exits.get("up"):
                # Staircase cell — give it a minimal description
                room.room_def = {
                    "name":         "Staircase",
                    "description":  _staircase_desc(room),
                    "special_event":None,
                    "items":        [],
                    "enemies":      [],
                    "ambient":      None,
                }
                assigned.add(pos)
                continue
            if atmo_idx < len(atmo_pool):
                atmo = atmo_pool[atmo_idx]; atmo_idx += 1
                room.room_def = {
                    "name":         atmo["name"],
                    "description":  atmo["description"],
                    "special_event":atmo.get("event"),
                    "items":        [],
                    "enemies":      [],
                    "ambient":      None,
                }
            else:
                room.room_def = _normal_room_def(rng, pos[2])
            assigned.add(pos)

        # Fill remaining unassigned rooms with normal rooms
        for pos, room in self.grid.items():
            if pos not in assigned:
                room.room_def = _normal_room_def(rng, pos[2])

        # Place items and enemies
        self._populate_rooms(rng)

    def _populate_rooms(self, rng: random.Random):
        """
        Place items and enemies into normal rooms.
        Unique items are placed in their fixed locations.
        """
        bell_rung = hasattr(self, 'player') and "warden_bell_rung" in self.player.flags

        for pos, room in self.grid.items():
            z = pos[2]
            ev = room.room_def.get("special_event")

            # Skip special rooms — they handle their own items
            if ev:
                continue

            # Items
            items = []
            if rng.random() < 0.50:
                items.append(random_item())
            if rng.random() < 0.18:
                items.append(random_item())
            if z >= 2 and rng.random() < 0.20:
                items.append(get_item("Health Potion"))
            room.room_def["items"] = items

            # Enemies — scale by z-level
            if bell_rung:
                spawn_chances = {0: 0.55, 1: 0.68, 2: 0.78, 3: 0.85, 4: 0.92}
            else:
                spawn_chances = {0: 0.35, 1: 0.50, 2: 0.62, 3: 0.72, 4: 0.80}
            spawn_chance = spawn_chances.get(z, 0.50)
            pool = enemy_pool_for_depth(z * 4)
            enemies = []
            if rng.random() < spawn_chance:
                count = 2 if (z >= 2 and rng.random() < 0.30) else 1
                enemies = [spawn_enemy(rng.choice(pool)) for _ in range(count)]
            room.room_def["enemies"] = enemies

    # ── Phase 3: Validate ─────────────────────────────────────────────────────

    def _validate_connectivity(self) -> bool:
        """BFS from entrance — check all rooms are reachable."""
        if self.entrance not in self.grid:
            return False
        visited = set()
        queue   = [self.entrance]
        while queue:
            pos = queue.pop()
            if pos in visited:
                continue
            visited.add(pos)
            room = self.grid.get(pos)
            if room:
                for dest in room.exits.values():
                    if dest and dest not in visited:
                        queue.append(dest)
        return len(visited) == len(self.grid)

    # ── Map display ───────────────────────────────────────────────────────────

    def display_map(self, player_pos: tuple, player):
        """
        Display the current floor as a 2D grid.
        Shows only visited rooms (fog of war).
        Staircase connections shown with ↓/↑.
        """
        from colorama import Fore, Style
        px, py, pz = player_pos
        w, h = FLOOR_DIMS.get(pz, (8, 6))

        # Build display grid
        print()
        print(c(f"  FLOOR {pz + 1} OF 5  —  position ({px},{py})", Fore.YELLOW + Style.BRIGHT))
        print()

        legend_shown = set()

        for y in range(h - 1, -1, -1):
            row = ""
            conn = ""
            for x in range(w):
                pos   = (x, y, pz)
                room  = self.grid.get(pos)

                if not room or not room.visited:
                    row  += "    "
                    conn += "    "
                    continue

                ev = room.room_def.get("special_event")
                if pos == player_pos:
                    cell_txt = c("[@ ]", Fore.YELLOW + Style.BRIGHT)
                elif ev and ev in EVENT_GLYPHS:
                    glyph, col = EVENT_GLYPHS[ev]
                    sealed_mark = c("×", Fore.RED) if room.sealed and room.completed else " "
                    cell_txt = c(f"[{glyph}", col) + sealed_mark + c("]", col)
                    legend_shown.add(ev)
                else:
                    cell_txt = c("[· ]", Fore.WHITE)

                # East connection
                east = (x+1, y, pz)
                east_room = self.grid.get(east)
                if (east_room and east_room.visited
                        and room.exits.get("east") == east):
                    east_conn = c("─", Fore.LIGHTBLUE_EX)
                else:
                    east_conn = " "

                row  += cell_txt + east_conn

                # South connection (for next row)
                south = (x, y-1, pz)
                south_room = self.grid.get(south)
                if (south_room and south_room.visited
                        and room.exits.get("south") == south):
                    conn += c(" │  ", Fore.LIGHTBLUE_EX)
                else:
                    conn += "    "

                # Down/up indicators
                if room.exits.get("down"):
                    row = row.rstrip() + c("▼", Fore.MAGENTA) + " "
                elif room.exits.get("up"):
                    row = row.rstrip() + c("▲", Fore.MAGENTA) + " "

            print(f"  {row}")
            if y > 0:
                print(f"  {conn}")

        print()
        # Legend for special rooms seen this floor
        if legend_shown:
            print(c("  Legend:", Fore.YELLOW))
            for ev in sorted(legend_shown):
                spec = next((sr for sr in SPECIAL_ROOMS if sr["event"] == ev), None)
                if spec:
                    glyph, col = EVENT_GLYPHS.get(ev, ("?", Fore.WHITE))
                    print(c(f"    [{glyph}]", col) + c(f" {spec['name']}", Fore.WHITE))

        # Show other floors summary
        print()
        print(c("  Floors:", Fore.CYAN))
        for z in range(len(FLOOR_DIMS)):
            rooms_on_floor  = [r for r in self.grid.values() if r.pos[2] == z]
            visited_on_floor = [r for r in rooms_on_floor if r.visited]
            marker = c("►", Fore.YELLOW + Style.BRIGHT) if z == pz else " "
            print(c(f"  {marker} Floor {z+1}: "
                    f"{len(visited_on_floor)}/{len(rooms_on_floor)} rooms explored",
                    Fore.WHITE))
        print()

    # ── Serialisation ─────────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        return {
            "entrance": list(self.entrance),
            "seed":     self.seed,
            "rooms":    {
                f"{x},{y},{z}": room.to_dict()
                for (x, y, z), room in self.grid.items()
            },
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Dungeon":
        d = cls()
        d.entrance = tuple(data["entrance"])
        d.seed     = data.get("seed", 0)
        d.grid     = {}
        for key, rdata in data["rooms"].items():
            parts = key.split(",")
            pos   = (int(parts[0]), int(parts[1]), int(parts[2]))
            room  = DungeonRoom.from_dict(rdata)
            d.grid[pos] = room
        return d


class DungeonMap:
    """Lightweight tracker — the Dungeon itself handles display."""

    def __init__(self):
        self.visited:     dict = {}   # pos → room_name
        self.connections: set  = set()

    def visit(self, pos: tuple, name: str):
        self.visited[pos] = name

    def connect(self, a: tuple, b: tuple):
        self.connections.add((a, b))

    def to_dict(self) -> dict:
        return {
            "visited": {
                f"{int(p[0])},{int(p[1])},{int(p[2])}": n
                for p, n in self.visited.items()
            },
            "connections": [
                [[int(x) for x in a], [int(x) for x in b]]
                for a, b in self.connections
            ],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "DungeonMap":
        m = cls()
        for k, v in data.get("visited", {}).items():
            parts = k.split(",")
            m.visited[tuple(int(x) for x in parts)] = v
        for pair in data.get("connections", []):
            m.connections.add((
                tuple(int(x) for x in pair[0]),
                tuple(int(x) for x in pair[1])
            ))
        return m

class DungeonRoom:
    """
    A single room in the pre-generated dungeon graph.

    Attributes:
        pos: (x, y, z) — grid coordinates.
        exits: dict mapping direction → (x,y,z) or None.
                Horizontal: "north","south","east","west"
                Vertical:   "down","up"
        room_def: dict — name, description, special_event, items, enemies, ambient.
        visited: bool — has the player been here this run?
        sealed: bool — one-time room, cannot be re-entered after completion.
        completed: bool — set when a sealing room is finished.
        state: dict — persistent room state (books opened, prisoner asked, etc.)
    """

    HORIZONTAL = ("north", "south", "east", "west")
    VERTICAL   = ("down", "up")
    ALL_DIRS   = HORIZONTAL + VERTICAL
    OPP = {
        "north": "south", "south": "north",
        "east":  "west",  "west":  "east",
        "down":  "up",    "up":    "down",
    }

    def __init__(self, pos: tuple):
        self.pos      = pos                          # (x, y, z)
        self.exits    = {d: None for d in self.ALL_DIRS}
        self.room_def = {}                           # assigned in Phase 2
        self.visited  = False
        self.sealed   = False
        self.completed= False
        self.state    = {}                           # replaces per-room dict keys

    # ── Convenience ──────────────────────────────────────────────────────────

    @property
    def x(self): return self.pos[0]
    @property
    def y(self): return self.pos[1]
    @property
    def z(self): return self.pos[2]

    @property
    def name(self):
        return self.room_def.get("name", "Chamber")

    @property
    def special_event(self):
        return self.room_def.get("special_event", None)

    @property
    def depth(self):
        """Approximate depth = z-level * 4 + graph distance within floor."""
        return self.z * 4

    def get_open_exits(self) -> list:
        return [d for d, dest in self.exits.items() if dest is not None]

    # ── Serialisation ─────────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        # Convert any sets in state to lists for JSON serialisation
        safe_state = {}
        for k, v in self.state.items():
            if isinstance(v, set):
                safe_state[k] = {"__set__": True, "values": sorted(v)}
            else:
                safe_state[k] = v
        return {
            "pos":       list(self.pos),
            "exits":     {d: list(v) if v else None for d, v in self.exits.items()},
            "room_def":  self.room_def,
            "visited":   self.visited,
            "sealed":    self.sealed,
            "completed": self.completed,
            "state":     safe_state,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "DungeonRoom":
        room = cls(tuple(data["pos"]))
        room.exits = {
            d: tuple(int(x) for x in v) if v else None
            for d, v in data["exits"].items()
        }
        room.room_def  = data.get("room_def", {})
        room.visited   = data.get("visited",   False)
        room.sealed    = data.get("sealed",    False)
        room.completed = data.get("completed", False)
        # Restore sets that were converted to tagged dicts
        raw_state = data.get("state", {})
        restored_state = {}
        for k, v in raw_state.items():
            if isinstance(v, dict) and v.get("__set__") is True:
                restored_state[k] = set(v["values"])
            else:
                restored_state[k] = v
        room.state = restored_state
        return room


# ─── ENEMIES ──────────────────────────────────────────────────────────────────
# special: None | "poison" | "drain" | "bleed" | "fear"
ENEMY_POOL = [
    # Tier 1
    {"name":"Goblin Scavenger",     "hp":14,"attack":4, "defence":1,"tier":1,"gold":(1,4),
     "loot_chance":0.6,"loot":"Relic Coin",      "death_line":"It collapses with a gurgling shriek.",                       "special":None},
    {"name":"Animated Skeleton",    "hp":18,"attack":5, "defence":3,"tier":1,"gold":(0,3),
     "loot_chance":0.5,"loot":"Iron Key",         "death_line":"The bones clatter apart. Silence returns.",                  "special":None},
    {"name":"Giant Spider",         "hp":12,"attack":5, "defence":1,"tier":1,"gold":(0,1),
     "loot_chance":0.4,"loot":"Antidote",         "death_line":"The spider curls into itself. Venom smell lingers.",         "special":"poison"},
    {"name":"Feral Hound",          "hp":16,"attack":6, "defence":2,"tier":1,"gold":(0,2),
     "loot_chance":0.3,"loot":"Bloodmoss Tincture","death_line":"The hound drops mid-lunge.",                               "special":None},
    {"name":"Goblin Archer",        "hp":10,"attack":5, "defence":1,"tier":1,"gold":(1,5),
     "loot_chance":0.4,"loot":"Health Potion",    "death_line":"The archer topples from its perch.",                        "special":None},
    {"name":"Tomb Rat Swarm",       "hp":8, "attack":4, "defence":0,"tier":1,"gold":(0,1),
     "loot_chance":0.2,"loot":"Antidote",         "death_line":"The swarm disperses into dark cracks.",                     "special":"poison"},
    {"name": "Cave Leech",
     "hp": 6, "attack": 3, "defence": 0, "tier": 1,
     "gold": (0, 2),
     "loot_chance": 0.2, "loot": "Bloodmoss Tincture",
     "death_line": "It drops from wherever it had attached. The wound it leaves is small but deliberate.",
     "special": "drain",
     "flavour": "Small, pale, wrong. They are not aggressive — they are simply hungry, "
                "and they have been hungry for a very long time."},
    {"name": "Bone Collector",
     "hp": 10, "attack": 4, "defence": 2, "tier": 1,
     "gold": (0, 3),
     "loot_chance": 0.4, "loot": "Relic Coin",
     "death_line": "The bones it had assembled collapse. They were never really attached.",
     "special": None,
     "flavour": "It builds armour from what it finds. The bones are not its own. "
                "This is somehow worse."},
    {"name": "Dust Wraith",
     "hp": 8, "attack": 5, "defence": 1, "tier": 1,
     "gold": (0, 1),
     "loot_chance": 0.3, "loot": "Antidote",
     "death_line": "Disperses. The dust that settles is a slightly different colour from the rest.",
     "special": "fear",
     "flavour": "Nearly invisible in the low light. You know it is there because the air moves wrong."},
    # Tier 2
    {"name":"Bandit",               "hp":18,"attack":6, "defence":2,"tier":2,"gold":(3,10),
     "loot_chance":0.9,"loot":"Health Potion",    "death_line":"They slump forward. Coins scatter.",                        "special":None},
    {"name":"Cave Troll",           "hp":30,"attack":8, "defence":5,"tier":2,"gold":(2,7),
     "loot_chance":0.8,"loot":"Iron Shield",      "death_line":"The troll falls like a felled tree.",                       "special":None},
    {"name":"Corrupted Sentinel",   "hp":24,"attack":7, "defence":4,"tier":2,"gold":(1,5),
     "loot_chance":0.6,"loot":"Eldrosian Spear",  "death_line":"Eldrosian markings fade from its breastplate as it stills.","special":None},
    {"name":"Wraith",               "hp":20,"attack":9, "defence":2,"tier":2,"gold":(0,4),
     "loot_chance":0.7,"loot":"Crystal Mirror",   "death_line":"It unravels into cold air, whispering something.",          "special":"drain"},
    {"name":"Ashbound Hound",       "hp":16,"attack":7, "defence":2,"tier":2,"gold":(0,2),
     "loot_chance":0.3,"loot":"Ember Flask",      "death_line":"Burns out. A scorch mark shaped like a running animal.",    "special":None},
    {"name":"Pit Crawler",          "hp":20,"attack":6, "defence":3,"tier":2,"gold":(1,4),
     "loot_chance":0.4,"loot":"Bloodmoss Tincture","death_line":"It retreats into its pit, fatally.",                       "special":"bleed"},
    {"name":"Bandit Captain",       "hp":26,"attack":8, "defence":3,"tier":2,"gold":(6,15),
     "loot_chance":0.9,"loot":"Strong Tonic",     "death_line":"The captain falls. Their crew — if any — are no longer a crew.", "special":None},
    {"name":"Shard-Seeker",          "hp":20, "attack":7,  "defence":3,  "tier":2, "gold":(8,18), "loot_chance":0.6, "loot":"Shard-Seeker's Map",
     "death_line": "The mercenary falls without ceremony. Professional to the last.", "special":None},
    {"name": "Void Hound",
     "hp": 22, "attack": 8, "defence": 2, "tier": 2,
     "gold": (2, 8),
     "loot_chance": 0.4, "loot": "Void Salt",
     "death_line": "It collapses inward. The space it occupied is briefly colder than the rest of the room.",
     "special": "bleed",
     "flavour": "Hunts by something other than smell. You cannot tell what. "
                "It always knows where you are."},
    {"name": "Corrupted Scholar",
     "hp": 18, "attack": 7, "defence": 2, "tier": 2,
     "gold": (5, 12),
     "loot_chance": 0.8, "loot": "Priest's Journal",
     "death_line": "Falls still. The book they were reading drops open. You will not look at the page.",
     "special": "drain",
     "flavour": "They came looking for answers. The answers found them first."},
    {"name": "Shard-Touched Soldier",
     "hp": 24, "attack": 9, "defence": 3, "tier": 2,
     "gold": (4, 10),
     "loot_chance": 0.5, "loot": "Fragment of the Seal",
     "death_line": "The Godshard fragment in their chest dims and goes dark. "
                   "It was keeping them upright.",
     "special": "bleed",
     "flavour": "A Godshard fragment is embedded in their sternum. "
                "It was not put there willingly. "
                "The fragment radiates something that makes your own shard pulse uncomfortably."},
    {"name": "Stone Sentinel",
     "hp": 40, "attack": 6, "defence": 14, "tier": 2,
     "gold": (8, 15),
     "loot_chance": 0.6, "loot": "Eldrosian Plate",
     "death_line": "Stops. Exactly where it stood. It does not fall. It simply stops.",
     "special": None,
     "flavour": "Carved from the same stone as the walls. Moves as though it has always moved. "
                "Hits infrequently but with great patience."},
    # Tier 3
    {"name":"Shade of Morvath",     "hp":22,"attack":10,"defence":3,"tier":3,"gold":(0,5),
     "loot_chance":0.7,"loot":"Void Shard",       "death_line":"The shade dissolves. The floor where it stood is grave-cold.","special":"drain"},
    {"name":"Void-Touched Soldier", "hp":28,"attack":9, "defence":4,"tier":3,"gold":(4,11),
     "loot_chance":0.6,"loot":"Eldrosian Plate",  "death_line":"The soldier crumples. The darkness in its eyes fades.",      "special":None},
    {"name":"Blood Crawler",        "hp":20,"attack":8, "defence":2,"tier":3,"gold":(0,4),
     "loot_chance":0.5,"loot":"Blood Amber",      "death_line":"Collapses into itself. A wet red stain.",                    "special":"poison"},
    {"name":"Deep Sentinel",        "hp":32,"attack":11,"defence":5,"tier":3,"gold":(4,14),
     "loot_chance":0.7,"loot":"Ashen Key",        "death_line":"Falls slowly, as though surprised.",                         "special":None},
    {"name":"Hollow Knight",        "hp":25,"attack":9, "defence":6,"tier":3,"gold":(3,10),
     "loot_chance":0.6,"loot":"Warden's Key",     "death_line":"The armour empties. Nothing was inside. Or nothing remains.","special":"fear"},
    {"name":"Void-Touched Cultist",  "hp":24, "attack":9,  "defence":3,  "tier":3, "gold":(1,8), "loot_chance":0.7, "loot":"Cultist's Sigil",
     "death_line": "The cultist falls. Their eyes, even closed, seem to be looking at something you cannot see.", "special":"drain"},
    {"name": "Morvath Shade",
     "hp": 30, "attack": 11, "defence": 4, "tier": 3,
     "gold": (0, 8),
     "loot_chance": 0.7, "loot": "Morvath Eye",
     "death_line": "The darkness it carried is released. The room is briefly, completely black. "
                   "Then ordinary dark.",
     "special": "drain",
     "flavour": "A true Morvath — not corrupted, not summoned. One of the last. "
                "It is here because this is the darkness it chose."},
    {"name": "Flesh Architect",
     "hp": 28, "attack": 10, "defence": 3, "tier": 3,
     "gold": (3, 10),
     "loot_chance": 0.5, "loot": "Blood Amber",
     "death_line": "What it had assembled separates. The pieces are from several different sources.",
     "special": "bleed",
     "flavour": "Builds itself from whatever is in the room. Each round of combat "
                "it becomes slightly harder to hurt, if you let it."},
    {"name": "Void Priest",
     "hp": 26, "attack": 12, "defence": 3, "tier": 3,
     "gold": (6, 14),
     "loot_chance": 0.9, "loot": "Cultist's Sigil",
     "death_line": "Falls mid-chant. The word it was saying is not completed. "
                   "You do not want to know what word.",
     "special": "drain",
     "flavour": "Calls on Atraxis by name. The name has partial effect. "
                "The drain attacks feel intentional in a way other drains do not."},
    {"name": "The Hollow",
     "hp": 32, "attack": 13, "defence": 5, "tier": 3,
     "gold": (0, 0),
     "loot_chance": 0.4, "loot": "Void Shard",
     "death_line": "Nothing. It was nothing. Now it is less.",
     "special": "fear",
     "flavour": "No name. No face. No reason to be here. "
                "It does not attack because it wants to. "
                "It attacks because you are here and it is not nothing."},
    # Tier 4
    {"name":"Unmade Fragment",      "hp":38,"attack":13,"defence":4,"tier":4,"gold":(5,15),
     "loot_chance":0.8,"loot":"Void Shard",       "death_line":"Tears apart silently. The pieces do not stay where they fall.","special":"drain"},
    {"name":"Herald of the Dark",   "hp":30,"attack":12,"defence":6,"tier":4,"gold":(8,20),
     "loot_chance":0.6,"loot":"Agreement Stone",        "death_line":"Speaks one word as it dies. You will not forget it.",         "special":None},
    {"name":"Void-Born Serpent",    "hp":34,"attack":11,"defence":3,"tier":4,"gold":(5,15),
     "loot_chance":0.7,"loot":"Void Shard","death_line":"The serpent stills. The darkness it carried disperses.",       "special":"poison"},
    {"name":"Corrupted High Priest", "hp":50, "attack":16, "defence":7,  "tier":4, "gold":(15,29), "loot_chance":0.9, "loot":"Second Godshard",
     "death_line": "The priest collapses. Something leaks from the wounds that is not blood. The robes continue to move for a moment after the body is still.",
     "special":"drain"},
    {"name":"Atraxis Fragment",      "hp":44, "attack":15, "defence":5,  "tier":4, "gold":(0, 0), "loot_chance":0.5, "loot":"Cultist's Sigil",
     "death_line": "The fragment tears itself apart. The pieces do not fall — they drift, slowly, as though gravity has an opinion about this but is choosing not to enforce it.",
     "special":"drain"},
    {"name": "Keeper's Remnant",
     "hp": 42, "attack": 14, "defence": 6, "tier": 4,
     "gold": (12, 25),
     "loot_chance": 0.8, "loot": "Ashen Tablet",
     "death_line": "Whatever was holding it together releases. "
                   "It falls in stages — first the form, then the will.",
     "special": "drain",
     "flavour": "What is left of a High Keeper who attempted the Agreement and failed — "
                "or succeeded only partially. "
                "It still performs the ritual gestures. It no longer has a mouth to speak the words."},
    {"name": "Atheron's Nightmare",
     "hp": 38, "attack": 15, "defence": 4, "tier": 4,
     "gold": (0, 0),
     "loot_chance": 0.6, "loot": "Dragon Scale",
     "death_line": "Dissolves. It was not real. Nothing from dreams is real when you are awake.",
     "special": "fear",
     "flavour": "This is not Atheron. This is something from Atheron's sleep. "
                "Dragons dream. This is what a sleeping dragon fears."},
    {"name": "Void-Fused Knight",
     "hp": 50, "attack": 16, "defence": 8, "tier": 4,
     "gold": (15, 28),
     "loot_chance": 0.9, "loot": "Voidforged Sword",
     "death_line": "The armour empties and the void within it disperses. "
                   "The metal itself looks relieved.",
     "special": "drain",
     "flavour": "Full plate armour, Eldrosian-made, Void-corrupted. "
                "Whatever was inside the armour originally is gone. "
                "What is there now is not a soldier. It is a direction."},
    # Tier 5
    {"name":"Void Colossus",         "hp":65, "attack":18, "defence":8,  "tier":5, "gold":(20,40), "loot_chance":0.8, "loot":"Void Shard",
     "death_line": "The Colossus unravels from the outside inward — the last thing to go is whatever was at its centre, which turns out to be nothing.",
     "special":"drain"},
    {"name":"Architect's Echo",      "hp":55, "attack":20, "defence":6,  "tier":5, "gold":(15,35), "loot_chance":0.7, "loot":"Echoed Blade",
     "death_line": "The Echo dissolves mid-strike, leaving the impression of a shape in the air that fades over several seconds.",
     "special":"fear"},
    {"name":"Atraxis Tendril",       "hp":48, "attack":16, "defence":10, "tier":5, "gold":(0,0), "loot_chance":0.6, "loot":"Cultist's Sigil",
     "death_line": "The tendril retreats into a crack in the wall. You are not sure it is dead. It is simply elsewhere.",
     "special":"drain"},
    {"name":"The Hollow Warden",     "hp":70, "attack":17, "defence":9,  "tier":5, "gold":(27,47), "loot_chance":0.9, "loot":"Warden's Coat",
     "death_line": "The Warden falls in sections — first the will, then the form. Whatever made it move has gone back where it came from.",
     "special":"fear"},
    {"name": "The Agreement's Witness",
     "hp": 60, "attack": 18, "defence": 7, "tier": 5,
     "gold": (0, 0),
     "loot_chance": 0.7, "loot": "Cultist's Sigil",
     "death_line": "Falls. Has been standing since the Agreement. "
                   "It did not die of anything you did. It died of being finally permitted to.",
     "special": "fear",
     "flavour": "Was present when Maelvyr made the Agreement. Has not left this level since. "
                "It witnessed. Witnessing changed it. It does not speak. "
                "It watches you with the specific attention of something that was there."},

    {"name": "Architect's Hand",
     "hp": 55, "attack": 20, "defence": 6, "tier": 5,
     "gold": (0, 0),
     "loot_chance": 0.5, "loot": "Void Shard",
     "death_line": "Something vast shifts, far away, as if registering the loss of a finger.",
     "special": "drain",
     "flavour": "Not a metaphor. A literal hand, the size of a room, emerging from the Void. "
                "It was not sent. It wandered here. "
                "Hands without bodies reach for things. This one is reaching."},
    {"name": "The Named",
     "hp": 52, "attack": 17, "defence": 9, "tier": 5,
     "gold": (20, 35),
     "loot_chance": 0.9, "loot": "Void Shard",
     "death_line": "Falls. The name they learned is still in them. It will not leave with the body.",
     "special": "drain",
     "flavour": "A cultist who learned Atraxis's true name. The name is partially transforming them. "
                "They are becoming a Demongod — incompletely, agonisingly. "
                "They fight with the desperation of something that cannot decide "
                "whether it wants to finish the process or be stopped."},
    {"name": "The Unmade Shepherd",
     "hp": 68, "attack": 16, "defence": 10, "tier": 5,
     "gold": (25, 40),
     "loot_chance": 0.8, "loot": "Voidhardened Vest",
     "death_line": "The things it was herding scatter. Without direction they are less dangerous. "
                   "They were never the threat. It was.",
     "special": "drain",
     "flavour": "Commands other void creatures. Fights from behind them. "
                "When the Shepherd dies, all remaining void creatures in the room flee. "
                "It is not a commander by choice. It is a commander by nature."},
]

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




# ─── LORE JOURNAL ─────────────────────────────────────────────────────────────
ALL_FLAGS = [
    "found_mural","found_ysena","read_ashen_tablet","read_charred_ledger","read_parchment_wells",
    "read_imperial_edict","read_priests_journal","found_library_collapse","found_blank_book",
    "found_histories","found_wells_book","found_thrys_survey","found_near_mortal_book",
    "found_vaethar_book","found_audience_protocols","found_demongod_etymology",
    "spoke_maelvyr_shrine","spoke_atheron_shrine","spoke_myrrakhel_shrine","spoke_vaelan_shrine",
    "spoke_vaethar_shrine","spoke_ysena_shrine","met_sael","sael_spoke_maelvyr","sael_myrrakhel",
    "sael_told_wells","sael_told_vaelan","sael_vaethar","sael_dravennis_connection",
    "met_orrath","orrath_maelvyr","orrath_myrrakhel","orrath_told_vaelan","orrath_vaethar","orrath_dravennis",
    "found_vault_door","found_sealed_sanctum","sanctum_vaelan_detail","full_truth_known",
    "found_veythari_archive","looked_void_well","void_well_witnessed","void_well_myrrakhel",
    "void_well_vaelan","void_well_vaethar","shard_returned","spoke_unmade","godshard_offered_well",
    "vaethar_tear_well","dawn_shard_offered_well","hollow_stone_well",
    "studied_atheron","atheron_woke_and_spared","atheron_named","atheron_ysena_named","atheron_vaethar_named",
    "scale_returned_atheron","vaethar_tear_atheron","ysena_handprint",
    "candle_mural_secret","inscription_variation","inscription_unmade","inscription_myrrakhel",
    "inscription_vaelan","inscription_vaethar","candle_inscription_secret","mirror_inscription_secret",
    "warden_seal_inscription","mirror_mural_secret",
    "found_blood_door","heard_dravennis","prisoner_dravennis","orrath_dravennis",
    "found_wardens_archive","found_throne_room","throne_full_context","took_godshard_from_vaelan",
    "crown_returned_throne","mirror_throne_room","hollow_stone_vaelan",
    "seal_restored","vaethar_inscription","hollow_stone_door","hollow_stone_astral",
    "dawn_shard_mirror","mirror_crystal_secret","mirror_figure",
    "ossuary_name","ossuary_secret_passage","altar_myrrakhel_hint",
    "heard_listening_room","saw_sealed_window","touched_astral_water","studied_astral_room",
    "prisoner_told_eldros","prisoner_told_well","prisoner_told_gods","prisoner_told_vaelan","prisoner_dravennis",
    "merchant_told_wells","merchant_myrrakhel","merchant_godshards",
    "dawn_shard_offered","godshard_offered_shrine","vaethar_tear_offered","old_crown_shrine","scale_shrine_blessed",
    "spoke_maelvyr_shrine","void_pointed","throne_vision","throne_carvings",
    "took_deeper_staircase","found_chamber_of_agreement", "stood_in_circle", "agreement_stone_circle", "agreement_chamber_inscription",
    "candle_agreement_chamber", "knows_ritual_phrase", "decoded_codex", "ritual_summmoned_confrontation",
    "refused_the_offer", "confrontation_done", "unmade_spoke_its_nature", "unmade_spoke_maelvyr", "knows_agreement_stone_use",
    "ritual_failed_once", "found_hall_of_nine", "nine_completed", "kindrael_alcove", "loria_alcove",
    "thalas_alcove", "thar_alcove", "ishak_alcove", "ysena_alcove", "vastino_alcove",
    "kelamaris_alcove", "myrrakhel_alcove", "candle_hall_of_nine", "dawn_shard_nine",
    "found_shattered_crown_hall", "read_shattered_crown_mural", "found_tolos_memorial",
    "candle_crown_hall", "found_third_godshard",
    "found_veythari_sanctuary", "sanctuary_pool_vision", "sanctuary_sael_tree",
    "arukiel_memory", "sanctuary_mirror_figure",
    "mirror_room_vision", "studied_reflection_walls", "mirror_scholar_vision",
    "sat_in_dawn_light", "talarion_room_found", "found_tolos_plinth",
    "read_talarion_chronicle", "read_scholar_notes", "read_shard_map", "read_wars_record",
    "atraxis_named", "atraxis_well", "heard_dissonance",
    "scholar_gave_info", "scholar_told_locations", "seeker_exchanged",
    "fought_cultist", "hollow_stone_door","found_recovery_room", "recovery_door_found",
    "found_cartographers_station", "read_cartographer_maps", "has_compass",
    "atraxis_well", "heard_dissonance","read_serethan_note", "read_wars_summary", "read_myrrakhel_fragment",
    "read_thaun_account", "read_eldros_founding", "read_atraxis_description", "read_tolos_account", "read_nine_gods_list",
    "read_maelvyr_survival", "found_forge", "forge_dust_found","met_named","met_shepherd", "met_witness",
    "killed_flesh_architect", "killed_void_priest","equipped_morvath_eye","equipped_veythari_feather",

    # NPC encounter flags
    "met_archivist", "met_bound_one", "met_serethan", "met_seeker_captain",
    "found_deep_sleeper", "deep_sleeper_answered", "deep_sleeper_approached",
    "talarion_echo_active", "talarion_echo_spoken", "talarion_full_account",
    # Archivist progress
    "archivist_factions", "archivist_history", "archivist_void_touched",
    "archivist_godshards", "archivist_atraxis", "archivist_ritual_site",
    # Bound One progress
    "bound_one_explained", "bound_one_atraxis", "bound_one_ritual",
    "bound_one_helped", "bound_one_passage", "bound_one_guided",
    "bound_one_name_spoken",
    # Serethan
    "serethan_bell", "serethan_collapse", "serethan_vaelan",
    "serethan_choice", "serethan_truth_told",
    # Captain
    "captain_employer", "captain_status", "captain_allied",
    "sold_godshard_captain", "betrayed_seekers",
    # Deep Sleeper answers
    "sleeper_atraxis_answer", "sleeper_well_answer", "sleeper_shards_answer",
    "sleeper_myrrakhel_answer", "sleeper_self_answer", "sleeper_custom_answer",
    # New room discoveries
    "found_near_mortal_ossuary", "found_veythari_remains", "found_morvath_remains",
    "found_war_room", "war_room_map", "war_room_contingency", "war_room_blood_door_hint",
    "found_chapel_thrys", "found_observatory", "observatory_stars",
    "observatory_telescope", "observatory_centre", "observatory_hollow_truth",
    "found_naming_room", "naming_room_read", "naming_room_spoke",
    "naming_serethan_found", "naming_tolos_found",
    "found_archive_agreements", "archive_vaelan_agreement", "read_agreement_terms",
    "found_atraxis_scar", "scar_understood", "scar_atraxis_spoken",
    "scar_maelvyr_spoken", "scar_myrrakhel_spoken", "scar_candle", "scar_hollow_truth",
    "found_poison_garden", "garden_examined",
    # Book lore flags
    "read_warden_log", "read_void_touched_guide", "read_vaelan_journal", "read_named_grimoire",
    # Spoken word expansion
    "inscription_atraxis", "inscription_thalas", "inscription_kindrael",
    "void_well_thalas", "void_well_kindrael", "void_well_serethan",
    # Reputation actions
    "obtained_veythari_feather", "obtained_morvath_eye",
    "near_mortal_ossuary_sael", "near_mortal_ossuary_orrath",
    "chapel_myrrakhel", "chapel_kindrael", "chapel_loria", "chapel_thalas",
    "chapel_thar", "chapel_ishak", "chapel_ysena", "chapel_vastino", "chapel_kelamaris",
]

DISCOVERY_TEXT = {
    "found_mural":             "You found the Hall of the Mural: Thaun rising from the Void-well, Arukiel falling, Atheron coiled around the world — and a fourth figure facing something painted over.",
    "found_ysena":             "The mural's central panel showed Ysena, Weaver of Shadows — one of the nine gods — standing beside Atheron. She was his spouse.",
    "read_ashen_tablet":       "An Ashen Tablet described the Night of Collapse — a priest who visited the Gods and did not return the same.",
    "read_charred_ledger":     "A Charred Ledger: hundreds of crossed-out names. Final line: 'The agreement was not with the Gods. It was with what stands behind them.'",
    "read_parchment_wells":    "A Rolled Parchment showed a diagram of nine circles — the nine wells — four labelled: BLOOD, ASTRAL, HOLLOW, DAWN. A tenth, larger, filled black at the centre.",
    "read_imperial_edict":     "An Imperial Edict, signed by Emperor Vaelan, sealed the High Keeper's records three days before the Night of Collapse.",
    "read_priests_journal":    "A Priest's Journal: careful scholarship, then a second darker ink mid-entry. Final line: 'If they knew what I was going to — ' The entry ends.",
    "found_library_collapse":  "A library book described the Night of Collapse — one person, unnamed, responsible.",
    "found_blank_book":        "A sealed blank book held one page: a firsthand account of the betrayer — M___VYR — who came back from the Gods as something else.",
    "spoke_maelvyr_shrine":    "At a shrine you spoke a name. The candles died. DEMONGOD appeared in the ash.",
    "spoke_atheron_shrine":    "You named Atheron at the shrine. The flame turned gold. Something acknowledged you.",
    "spoke_myrrakhel_shrine":  "You named Myrrakhel at the shrine. Every candle burned brighter and colder simultaneously.",
    "spoke_vaelan_shrine":     "You named Vaelan at the shrine. The flame turned crimson. A sound like a distant echo of something that happened here.",
    "spoke_vaethar_shrine":    "You named Vaethar at the shrine. Gold warmth — sustaining rather than sudden. The ash formed wings briefly.",
    "spoke_ysena_shrine":      "You named Ysena at the shrine. The candles went blue-grey. A warmth in the shadows, briefly, then gone.",
    "met_sael":                "You met Sael — a Veythari, near-mortal of the starlight.",
    "sael_spoke_maelvyr":      "Sael named the betrayer: Maelvyr, a High Keeper who made an agreement with the Unmade. The empire fell the same night. DEMONGOD.",
    "sael_myrrakhel":          "Sael named all nine gods: Myrrakhel and the Thrys. She said Myrrakhel may not be what Myrrakhel was.",
    "sael_told_wells":         "Sael described the wells and their products: from the Dawnwell came Auridan, first human; from the Bloodwell came Mograx, first Orkyn.",
    "sael_told_vaelan":        "Sael confirmed Emperor Vaelan held all the Godshards — fragments of Vaethar — and died on his throne, stormed.",
    "sael_vaethar":            "Sael described Vaethar: Atheron's chosen child, who fragmented their form into the Godshards to empower the imperial line.",
    "sael_dravennis_connection":"Sael drew the line: Maelvyr, the Demongod, is also Dravennis — he who drinks the blood of magi.",
    "met_orrath":              "You met Orrath — a Morvath, near-mortal of the darkness, from the Hollow-well.",
    "orrath_maelvyr":          "Orrath confirmed Maelvyr is active, elsewhere, building something. He is very hungry.",
    "orrath_told_vaelan":      "Orrath was nearby on the Night of Collapse. The one who killed Vaelan had already agreed to become something else.",
    "orrath_vaethar":          "Orrath met Vaethar before the fragmentation. 'What they chose was not a sacrifice. It was a decision.'",
    "orrath_dravennis":        "Orrath named Dravennis: the man made into a Demongod at Eldros, who left, and has been building something, elsewhere, for a very long time.",
    "found_vault_door":        "An Iron Key opened a vault: 'Look for what was agreed with in the dark. The name is secondary.' Beneath: UNMADE.",
    "found_sealed_sanctum":    "The sealed sanctum held the full account: Maelvyr, High Keeper, made an agreement with the Unmade. He stormed the capital. He killed Emperor Vaelan on his throne. He became a Demongod.",
    "found_veythari_archive":  "A Veythari archive: the Unmade predates the wells. At Eldros it succeeded — briefly — through one man who opened the door.",
    "looked_void_well":        "You looked into the Void-well. Something looked back. Vast, old, not Atheron.",
    "void_well_witnessed":     "You spoke Maelvyr's name into the Void-well. WITNESSED was pressed into the rim from below.",
    "void_well_vaelan":        "You named Vaelan at the well. A sound from deep below — like something heavy settling, finally, to rest.",
    "studied_atheron":         "You studied the sleeping dragon: ATH___N, the King of Dragons.",
    "atheron_woke_and_spared": "Atheron woke. You stood still. It let you leave.",
    "atheron_named":           "You named Atheron to his face. He acknowledged it.",
    "atheron_ysena_named":     "You named Ysena to Atheron. Both his eyes opened. The sound was not a roar. Memory.",
    "found_throne_room":       "You found the Throne of Eldros-Verath — not ruined, but arrested. Emperor Vaelan still sits in his throne, still holding a Godshard.",
    "throne_full_context":     "You stood in the throne room knowing everything: who killed Vaelan, what Maelvyr became, what the Godshards are.",
    "took_godshard_from_vaelan":"You took the Godshard from Vaelan's hand. His armour settled. Something that had been holding it upright was released.",
    "crown_returned_throne":   "You returned the Old Crown to the throne room. The Godshard pulsed once in acknowledgement. ATK +2, Max HP +10.",
    "found_blood_door":        "The Blood Door contained research on the Bloodwell — a hunger that outlasts the body that carries it. 'We should have stopped sooner.'",
    "sael_dravennis_connection":"Sael drew the line between Maelvyr and Dravennis explicitly.",
    "orrath_dravennis":        "Orrath described Dravennis as Maelvyr, building something, elsewhere, for a very long time. Very hungry.",
    "heard_dravennis":         "The merchant warned you: the name Dravennis carries differently in the deep rooms.",
    "prisoner_told_vaelan":    "The prisoner told you about Vaelan — he held the Godshards and died on his throne.",
    "ossuary_name":            "In the ossuary, one alcove had a name chiselled through above it: M — something — L. Then a gap. Then R.",
    "inscription_variation":   "One iteration of the inscription room's loop changed: 'M___VYR UNMADE THE AGREEMENT.'",
    "found_wardens_archive":   "The Warden's Archive recorded the final entry: the Warden's office lodged a formal objection to the High Keeper's audience request. It was overruled.",
    "vaethar_inscription":     "Hidden behind a Hollow Stone wall: 'Vaethar's gift was not a sacrifice. It was an investment. The Godshards remember what Vaethar chose to become.'",
    "mirror_throne_room":      "In the Crystal Mirror in the throne room: Vaelan on his throne, a robed figure before him — and behind that figure, the Unmade's shadow falling over everything.",
    "ysena_handprint":         "On Atheron's flank: a handprint, small, pressed deliberately. Ysena's. Even here, her mark remains.",
    "found_thrys_survey":      "A theological survey named all nine gods: Myrrakhel and the eight Thrys — Kindrael, Loría, Thalás, Thar, Ishak, Ysena, Vastinö, Kelamaris.",
    "found_vaethar_book":      "A book on Vaethar confirmed: Vaelan was the first and last emperor to hold all godshards simultaneously. The theological implications were being debated when the Night of Collapse rendered them moot.",
    "found_audience_protocols":"The Audience Protocols recorded the final audience as unusual — requested by the High Keeper himself, approved by Vaelan with noted reluctance. The High Keeper's name is blank.",
    "found_demongod_etymology": "An etymological study of DEMONGOD: coined after the Night of Collapse by survivors. 'The scholars noted: this word is still not enough.'",
    "found_chamber_of_agreement":
        "You found the Chamber of the Agreement — the room where Maelvyr met the Unmade. "
        "Two sets of footprints are pressed into the stone. One human. One not.",
    "stood_in_circle":
        "You stood in the circle where the Agreement was made. "
        "For a moment you understood what it felt like to say yes.",
    "agreement_chamber_inscription":
        "The Chamber of the Agreement's walls read: 'The Unmade requires a willing door. "
        "It cannot force entry. It can only wait.'",
    "decoded_codex":
        "Using the Crystal Mirror, you decoded the Codex of the First Age. "
        "The ritual phrase: name Vaethar, name Atheron as witness, "
        "and claim: I am the vessel.",
    "refused_the_offer":
        "The Unmade — speaking through the shadow of Maelvyr — offered you what it offered him. "
        "You said no. The shadow called this interesting.",
    "unmade_spoke_its_nature":
        "The Unmade described itself: not the absence of something, but a presence. "
        "Here before the wells. Before the gods. Before everything. Patient.",
    "unmade_spoke_maelvyr":
        "The Unmade described Maelvyr's fate: he killed Vaelan, walked away from the ruins, "
        "and has been building something elsewhere ever since. He grows. He is a door, "
        "learning to open wider.",
    "knows_agreement_stone_use":
        "You learned that the Agreement Stone is a record — a receipt — "
        "of what happened in the Chamber of the Agreement. It can invoke that event.",
    "found_hall_of_nine":
        "You found the Hall of the Nine — nine alcoves, each bearing the symbol of one of the Sera. "
        "The golden centre of the floor mosaic has been pried out.",
    "nine_completed":
        "You stood before all nine alcoves. Something settled — "
        "the sense of a set finally seen whole.",
    "found_shattered_crown_hall":
        "You found the Hall of the Shattered Crown — built after the fall, "
        "by someone who came back. It depicts the Wars of the Shattered Crown: "
        "three generations of heirs, each holding one Godshard, each believing the full set "
        "would restore the empire.",
    "found_tolos_memorial":
        "The walls of the Shattered Crown Hall list the war dead. "
        "Three names are largest: Calyren. Vaelan. Tolos. "
        "Beneath Tolos: 'He tried.'",
    "found_third_godshard":
        "You took the Third Godshard from the Hall of the Shattered Crown. "
        "The three shards pulsed together — once — and then settled into a shared frequency.",
    "found_veythari_sanctuary":
        "You found the Veythari Sanctuary — silver-lit, still, with a pale leafless tree "
        "and a pool that shows things that are not the room.",
    "arukiel_memory":
        "You offered the Starlight Shard to the sanctuary pool and witnessed a memory of Arukiel — "
        "the Falling Light, choosing to be part of the world. "
        "The memory is now yours.",
    "found_tolos_plinth":
        "In the throne room: a secondary plinth, added after the fact. "
        "TOLOS. A date. HE TRIED. "
        "Talarion placed it there.",
    "read_talarion_chronicle":
        "Talarion's Chronicle: he was there when it ended. He saw Maelvyr weep over Tolos. "
        "He saw Maelvyr leave — injured, diminished, but alive. "
        "'I tell the story because someone must.'",
    "read_wars_record":
        "The Wars of the Shattered Crown lasted three generations. "
        "The Godshards were returned to Eldros-Verath by common agreement — "
        "no heir trusted to hold all three. They were placed in the Hall. They waited.",
    "atraxis_named":
        "You learned the name Atraxis — the deeper name for the Unmade. "
        "The Void-Touched cultists use it. It is older than the name Unmade.",
    "atraxis_well":
        "You spoke Atraxis into the Void-well. The darkness rose to the rim and rested there. "
        "The word pressed into stone: KNOWN.",
    "heard_dissonance":
        "In the Chamber of the Agreement, you heard Dissonance — "
        "a resonance between a voice and music that your mind cannot interpret as either.",
    "candle_crown_hall":
        "The Candle revealed a covered section of the Shattered Crown mural: "
        "a fourth figure watching the wars from a distance, and a covered caption: "
        "'AND HE WATCHED FROM AFAR, AND WAS GLAD.'",
    "mirror_scholar_vision":
        "In the Crystal Mirror, in Talarion's room, you saw Talarion himself — "
        "writing at his desk. He looked up and saw you.",
    "scholar_gave_info":
        "A Remnant Scholar in the ruins told you: "
        "'The thing in the well is older than the wells. The Remnant Scholars call it Atraxis.'",
    "found_recovery_room":
        "You found the Place Between — a room made from leftover space. "
        "The ruins receive offerings and remember them.",
    "found_cartographers_station":
        "You found the Cartographer's Station — a scholar's abandoned workspace "
        "with partial maps of the upper ruins and notes on the three factions.",
    "read_cartographer_maps":
        "The cartographer's maps confirmed: Void-Touched presence from depth 8+. "
        "Three factions in the ruins — scholars, cultists, mercenaries.",
    "read_serethan_note":
        "A Rolled Parchment was a note from Serethan, Warden-Commander: "
        "he chose not to ring the bell. He left the decision to whoever came after.",
    "read_wars_summary":
        "A Rolled Parchment described the Wars of the Shattered Crown — "
        "three generations of heirs, each holding one Godshard. "
        "The wars ended in exhaustion. The shards were returned to Eldros-Verath.",
    "read_myrrakhel_fragment":
        "A Rolled Parchment described something before Myrrakhel — the Architect. "
        "The Architect was destroyed. Its mind did not die with its form. "
        "Where it went: the question the Remnant Scholars cannot answer.",
    "read_thaun_account":
        "A Rolled Parchment was written by Thaun himself: "
        "'I am what happens when the void decides to have opinions. "
        "What is beneath the well is older than I am.'",
    "read_eldros_founding":
        "A Rolled Parchment described the founding of Eldros-Verath: "
        "the city was built here because of the Void-well. "
        "'The near-mortals said the well was a source of power. They were not wrong. They were incomplete.'",
    "read_atraxis_description":
        "A Rolled Parchment described Atraxis: not wanting, but gravity — "
        "pulling everything toward void. The margin note read: 'Yes.' "
        "Atraxis is aware of what it is.",
    "read_tolos_account":
        "A Rolled Parchment was a letter from Tolos to Maelvyr, never sent: "
        "'You wanted the gods to listen. So did I. "
        "The difference is I accepted that they might not.'",
    "read_nine_gods_list":
        "A Rolled Parchment listed all nine Sera by their near-mortal names. "
        "The final line: 'Myrrakhel made the others. Who made Myrrakhel is not recorded here.'",
    "read_maelvyr_survival":
        "A Rolled Parchment was a field report compiled by Talarion: "
        "Maelvyr was seen leaving Eldros-Verath on the night of the collapse. Injured. Alive. "
        "Recommendation: assume he survived. Assume he is dangerous.",
    "found_forge":
        "You found the Forge — still burning after centuries. "
        "Above it: 'This work is a poor shadow of the Forge Above.' "
        "The mortals who built it knew exactly what they were imitating.",
    "met_named":
        "You encountered The Named — a cultist in incomplete transformation. "
        "One half of their face was becoming something else. "
        "They spoke Atraxis's name once. The name has partial power.",
    "met_shepherd":
        "You encountered the Unmade Shepherd — a void-creature that commands others. "
        "When it fell, everything it was herding scattered.",
    "met_witness":
        "You encountered the Agreement's Witness — a being that was present "
        "when Maelvyr made the Agreement and has not left since. "
        "It did not die of anything you did. It was finally permitted to.",
    "killed_void_priest":
        "You killed a Void Priest — a cultist who invoked Atraxis by name during combat. "
        "The name had partial effect. The drain felt intentional.",
    "met_archivist":
        "You met the Archivist — a Remnant Scholar who has been in the ruins for eleven years. "
        "They know the factions, the layout, and that something is being organised in the deep.",
    "met_bound_one":
        "You met the Bound One — a cultist partially resisting the Void's pull. "
        "They are becoming a direction. They know this.",
    "met_serethan":
        "You encountered Serethan's Echo — the Warden-Commander's strong memory, "
        "still standing at a window that no longer exists.",
    "serethan_truth_told":
        "You told Serethan's Echo the full truth about Maelvyr and the Agreement. "
        "'Thank you for telling me. It is important to know. Even here. Even now.'",
    "serethan_choice":
        "Serethan did not ring the bell because he knew the lockdown "
        "would wake everything they had caged. He left the decision to whoever came after.",
    "found_deep_sleeper":
        "You found the Deep Sleeper — something vast and old in the deepest room, "
        "coiled around itself. Not a dragon. Something that existed before the categories.",
    "sleeper_shards_answer":
        "The Deep Sleeper's answer about the Godshards: "
        "they hold intention — Vaethar's original intention at the moment of fragmentation. "
        "The ritual gives you Vaethar's intention, not merely power.",
    "sleeper_myrrakhel_answer":
        "The Deep Sleeper's answer about Myrrakhel: "
        "Myrrakhel has been listening since the Night of Collapse. "
        "Waiting for a quality of attention. Not a name. Not a ritual. A quality.",
    "talarion_full_account":
        "Talarion's Echo, through the Crystal Mirror, gave the full account: "
        "Vaelan stayed because emperors do not run. "
        "Tolos jumped because friends do not calculate. "
        "Talarion built the Hall because someone had to.",
    "found_near_mortal_ossuary":
        "You found the Ossuary of the Near-Mortals — "
        "Morvath and Veythari remains, placed with ceremony. "
        "The same hand placed both.",
    "found_archive_agreements":
        "You found the Archive of Agreements — every formal agreement Eldros ever made. "
        "The final entry is Maelvyr's Agreement with the Void.",
    "read_agreement_terms":
        "You read the terms of the Agreement in the Archive: "
        "'In exchange for his mortal limitation, the first party will be remade.' "
        "WITNESSED AND AGREED. Filed. Catalogued. An empire in its own archive.",
    "found_atraxis_scar":
        "You found the Atraxis Scar — where the Void physically breached the stone "
        "at the moment of Maelvyr's Agreement. The stone has not recovered.",
    "scar_understood":
        "Standing at the centre of the Atraxis Scar, knowing the full truth, "
        "you understood: this is where it happened. "
        "This is the physical mark of the moment that ended the empire.",
    "war_room_contingency":
        "The War Room held a file labelled CONTINGENCY MAELVYR. "
        "The plan was prepared. The activation order was never signed.",
    "captain_employer":
        "The Shard-Seeker Captain's employer knew exactly where the Godshards were. "
        "People who know what's in ruins they've never visited are not archaeologists. "
        "They are retrieval agents.",
    "bound_one_helped":
        "You helped the Bound One resist using the Dawn Shard. "
        "In return, they told you about a passage the Void-Touched use "
        "behind the Naming Room.",
    "observatory_hollow_truth":
        "Through the Hollow Stone, the Observatory's sky revealed itself: "
        "a window into the space between wells. "
        "The thing in the centre is on the other side of everything. "
        "It is not Atraxis. It is something Atraxis fears.",
    "naming_tolos_found":
        "In the Naming Room, you found Tolos Merinain's name. "
        "No titles — they were stripped. Just the name. "
        "And beneath it, in the smallest script the stone could manage: "
        "'He loved his friend. That is what the room remembers.'",
    "read_warden_log":
        "The Last Warden's Log: Serethan stood at the bell on the night of the collapse. "
        "He could not ring it. The lockdown would have woken everything they caged.",
    "read_vaelan_journal":
        "Vaelan's journal: he approved Maelvyr's audience request because he was running out of options. "
        "'I made a mistake. I do not know how large a mistake yet.'",
    "read_named_grimoire":
        "The Named's Grimoire: 'I have learned the name. The name is changing me. "
        "I wanted power. This is not power. This is direction. I am becoming a direction.'",
}

def show_lore_journal(player):
    title_bar("DISCOVERIES")
    found = [(f, DISCOVERY_TEXT[f]) for f in ALL_FLAGS
             if f in player.flags and f in DISCOVERY_TEXT]
    if not found:
        print(c("  Nothing recorded yet.", Fore.LIGHTBLUE_EX+Style.BRIGHT)); return
    for _, text in found:
        print(c("  ·", Fore.CYAN))
        wrap(f"  {text}", Fore.WHITE)
    print()
    discoverable = len(DISCOVERY_TEXT)
    print(c(f"  {len(found)} of {discoverable} notable discoveries made.", Fore.CYAN))




def try_give_unique(player, item_name: str) -> bool:
    """
    Attempt to give the player a unique item.
    Returns True if successful, False if the player already obtained it.
    Prints an appropriate message either way.
    """
    flag = UNIQUE_ITEMS.get(item_name)
    if flag is None:
        # Not unique — just give it
        item = get_item(item_name)
        if item:
            player.pick_up(item)
            return True
        return False

    if flag in player.flags:
        print(c(f"  (You have already found the {item_name} — you carry one already.)",
                Fore.LIGHTBLUE_EX + Style.BRIGHT))
        return False

    item = get_item(item_name)
    if item:
        player.flags.add(flag)
        player.pick_up(item)
        return True
    return False

def random_artefact():
    pool = [it for it in ITEM_POOL if it["type"] == "artefact"]
    return dict(random.choice(pool))

def random_lore():
    """Return a random lore item. Parchments are always variant parchments."""
    # Fixed lore items that are placed deliberately — not in random pool
    EXCLUDED_LORE = {
        "Ashen Tablet", "Charred Ledger", "Imperial Edict",
        "Priest\\'s Journal", "Talarion\\'s Chronicle",
        "Remnant Scholar\\'s Notes", "Shard-Seeker\\'s Map",
    }
    # Always return a parchment variant for random lore drops
    return pick_parchment_variant()


def adjust_reputation(player, faction: str, delta: int):
    """
    Adjust player reputation with a faction.
    Clamps to [-2, 2]. Prints a brief note on significant changes.
    Also adjusts opposing factions slightly.
    """
    if not hasattr(player, "reputation"):
        player.reputation = {"scholars": 0, "void_touched": 0, "seekers": 0}

    old = player.reputation.get(faction, 0)
    new = max(-2, min(2, old + delta))
    player.reputation[faction] = new

    # Reputation change messages
    labels = {"scholars": "Remnant Scholars", "void_touched": "Void-Touched",
              "seekers": "Shard-Seekers"}
    if new != old:
        if new >= 2:
            print(c(f"  [{labels[faction]}: ALLIED]", Fore.GREEN))
        elif new <= -2:
            print(c(f"  [{labels[faction]}: HOSTILE]", Fore.RED))
        elif delta > 0:
            print(c(f"  [{labels[faction]} reputation improved]", Fore.GREEN))
        elif delta < 0:
            print(c(f"  [{labels[faction]} reputation worsened]", Fore.RED))

    # Cross-faction effects — being allied with void_touched makes scholars hostile
    OPPOSITION = {
        "void_touched": "scholars",
        "scholars": None,
        "seekers": None,
    }
    if delta > 0:
        opposed = OPPOSITION.get(faction)
        if opposed:
            old_opp = player.reputation.get(opposed, 0)
            player.reputation[opposed] = max(-2, old_opp - 1)


def get_reputation(player, faction: str) -> int:
    if not hasattr(player, "reputation"):
        return 0
    return player.reputation.get(faction, 0)


def is_hostile(player, faction: str) -> bool:
    return get_reputation(player, faction) <= -2


def is_allied(player, faction: str) -> bool:
    return get_reputation(player, faction) >= 2


# Reputation display — call this from show_inventory or review discoveries
def show_reputation(player):
    from colorama import Fore, Style
    hr(colour=Fore.YELLOW)
    print(c("  FACTION STANDING", Fore.YELLOW + Style.BRIGHT))
    hr(colour=Fore.YELLOW)
    labels = {
        "scholars":     ("Remnant Scholars",  "Academics seeking truth in the ruins."),
        "void_touched": ("Void-Touched",       "Cultists who serve Atraxis."),
        "seekers":      ("Shard-Seekers",      "Mercenaries hunting the Godshards."),
    }
    bars = {-2: "HOSTILE  ██░░░░", -1: "Wary     ███░░░",
            0: "Neutral  ████░░",  1: "Friendly ████░░",  2: "Allied   ██████"}
    rep = getattr(player, "reputation", {})
    for key, (name, desc) in labels.items():
        val = rep.get(key, 0)
        col = Fore.RED if val < 0 else (Fore.GREEN if val > 0 else Fore.WHITE)
        print(c(f"  {name:20}", Fore.YELLOW) +
              c(f" {bars.get(val, '???')}", col))
        print(c(f"  {' '*20} {desc}", Fore.LIGHTBLUE_EX + Style.BRIGHT))
    print()


def spawn_enemy(template):
    return dict(template)

def enemy_pool_for_depth(depth):
    if depth >= 18: return ENEMY_POOL          # all tiers including 5
    if depth >= 15: return [e for e in ENEMY_POOL if e["tier"] <= 4]
    if depth >= 10: return [e for e in ENEMY_POOL if e["tier"] <= 3]
    if depth >= 5:  return [e for e in ENEMY_POOL if e["tier"] <= 2]
    return [e for e in ENEMY_POOL if e["tier"] == 1]


def _eat_food(player, item):
    """Handle food consumption."""
    from colorama import Fore
    effect = item.get("food_effect", {})
    hp_restored = effect.get("hp", 0)
    if hp_restored:
        r = min(hp_restored, player.max_hp - player.hp)
        player.hp += r
        print(c(f"  Restored {r} HP. ({player.hp}/{player.max_hp})", Fore.GREEN))
    if effect.get("cure_poison") and player.poisoned:
        player.poisoned = False
        print(c("  The honey clears the venom.", Fore.GREEN))
    if effect.get("morale"):
        player.attack += 1
        print(c("  The wine steadies your hand. ATK +1 for this room.", Fore.YELLOW))
        # Note: this is not tracked as permanent — just a short flavour line
    if effect.get("clarity") and player.cursed:
        player.cursed = False
        print(c("  The cold water clears something. Curse lifted.", Fore.GREEN))
    if effect.get("glow"):
        print(c("  The mushroom leaves a faint glow on your fingertips. "
                "Not useful. But present.", Fore.CYAN))


def get_relic_effect(player, effect_type: str):
    """Return the relic effect value for the given type, or 0/None."""
    relic = player.equipped.get("relic")
    if not relic:
        return None
    effect = relic.get("relic_effect", {})
    if effect.get("type") == effect_type:
        return effect.get("value")
    return None

# ─── COMBAT ───────────────────────────────────────────────────────────────────
def combat(player, enemy):
    from colorama import Fore, Style
    hr("═", colour=Fore.RED)
    print(c(f"  {enemy['name'].upper()}", Fore.RED + Style.BRIGHT))
    if enemy.get("flavour"):
        wrap(f"  {enemy['flavour']}", Fore.RED)
    hr("═", colour=Fore.RED)

    enemy_hp      = enemy["hp"]
    flesh_bonus   = 0     # Flesh Architect defence buildup
    miss_next     = False # Clarity Shard effect
    applied_bleed = False # thrown bleed

    # Relic: fear immunity
    fear_immune = bool(get_relic_effect(player, "fear_immune"))
    # Relic: drain resist halves drain chance
    drain_resist = get_relic_effect(player, "drain_resist") or 1.0
    # Relic: bleed resist halves bleed damage
    bleed_resist = get_relic_effect(player, "bleed_resist") or 1.0
    # Relic: poison resist (handled in tick)
    poison_resist_active = bool(get_relic_effect(player, "poison_resist"))

    # The Named: brief acknowledgement
    if enemy["name"] == "The Named":
        wrap(
            "It looks at you. One half of its face is still human — "
            "the other is becoming something else. "
            "It speaks the name once. The name is not in a language "
            "that should be spoken aloud.",
            Fore.MAGENTA)
        print()

    while player.hp > 0 and enemy_hp > 0:
        print()
        print(c(f"  Your HP: {player.hp}/{player.max_hp}", Fore.GREEN) +
              c(f"  |  {enemy['name']} HP: {enemy_hp}", Fore.RED))

        # Build options
        has_thrown = any(it["type"] == "thrown" for it in player.inventory)
        opts = ["Strike", "Use item"]
        if has_thrown:
            opts.append("Throw weapon")
        opts.append("Attempt to flee")
        ch = prompt(opts)

        if ch == "Strike":
            dmg = max(1, player.total_attack() - (enemy["defence"] + flesh_bonus)
                      + random.randint(-2, 2))
            enemy_hp -= dmg
            print(c(f"  You deal {dmg} damage.", Fore.GREEN))

            # Shepherd: when first damaged, add a warning
            if enemy["name"] == "The Unmade Shepherd" and enemy_hp < enemy["hp"] * 0.5:
                if "shepherd_warned" not in enemy:
                    enemy["shepherd_warned"] = True
                    wrap(
                        "The things behind the Shepherd scatter briefly, "
                        "then regroup. The Shepherd does not move.",
                        Fore.RED)

        elif ch == "Use item":
            player.use_item()

        elif ch == "Throw weapon":
            enemy_hp, throw_effect = use_thrown_weapon(player, enemy_hp, enemy)
            if throw_effect == "bleed":
                applied_bleed = True
            elif throw_effect == "miss_next":
                miss_next = True

        elif ch == "Attempt to flee":
            # Relic flee bonus
            flee_bonus = get_relic_effect(player, "flee_bonus") or 0
            if random.random() < 0.40 + flee_bonus:
                print(c("  You slip away into the shadows.", Fore.YELLOW))
                return True
            print(c("  The enemy cuts off your escape.", Fore.RED))

        # Flesh Architect: gains defence each round
        if enemy["name"] == "Flesh Architect" and enemy_hp > 0:
            if flesh_bonus < 4:
                flesh_bonus += 1
                print(c(f"  The Flesh Architect incorporates more debris. "
                        f"DEF +1 (now DEF {enemy['defence'] + flesh_bonus}).", Fore.RED))

        # Enemy attacks
        if enemy_hp > 0:
            if miss_next:
                print(c(f"  {enemy['name']} swings — and misses, still disoriented.", Fore.GREEN))
                miss_next = False
            else:
                dmg = max(1, enemy["attack"] - player.total_defence() + random.randint(-1, 2))
                player.hp -= dmg
                print(c(f"  {enemy['name']} hits you for {dmg}.", Fore.RED))

            spec = enemy.get("special")
            if spec == "poison" and not player.poisoned and random.random() < 0.4:
                player.poisoned = True
                print(c("  Its attack carries venom. POISONED.", Fore.RED))
            elif spec == "drain" and not player.void_ward:
                drain_chance = 0.30 * drain_resist
                if random.random() < drain_chance:
                    player.cursed = True
                    print(c("  Something drains from you. [CURSED]", Fore.MAGENTA))
                    # Ysena's Veil message
                    if drain_resist < 1.0:
                        print(c("  (The Veil reduced the chance.)", Fore.MAGENTA))
            elif spec == "bleed" and random.random() < 0.35:
                extra = int(random.randint(2, 5) * bleed_resist)
                player.hp -= extra
                print(c(f"  The wound bleeds. -{extra} more HP.", Fore.RED))
                if bleed_resist < 1.0:
                    print(c("  (Thar's Patience reduced the bleed.)", Fore.YELLOW))
            elif spec == "fear" and random.random() < 0.25:
                if fear_immune:
                    print(c("  The fear washes over you but finds nothing to grip. "
                            "(Morvath Eye.)", Fore.MAGENTA))
                else:
                    player.attack = max(1, player.attack - 1)
                    print(c("  Something about the enemy's presence unnerves you. ATK-1.", Fore.MAGENTA))

            if spec == "drain" and player.void_ward:
                print(c("  The Void Salt wards off the draining effect.", Fore.CYAN))

            # Applied bleed from thrown weapon
            if applied_bleed and random.random() < 0.5:
                extra = random.randint(1, 3)
                player.hp -= extra
                print(c(f"  The thrown wound bleeds. -{extra} HP.", Fore.RED))

        # Poison tick (respect relic)
        if player.poisoned:
            tick = 1 if poison_resist_active else 2
            player.hp -= tick
            relic_note = " (Kelamaris Breath-Stone.)" if poison_resist_active else ""
            print(c(f"  Poison. -{tick} HP. ({player.hp}/{player.max_hp}){relic_note}", Fore.RED))

    # After combat
    player.void_ward = False

    if player.hp <= 0:
        return False

    print(c(f"\n  {enemy.get('death_line', 'The enemy falls.')}", Fore.YELLOW))

    # Unmade Shepherd: remaining void enemies flee
    if enemy["name"] == "The Unmade Shepherd":
        wrap(
            "Whatever it was commanding loses direction. "
            "The void-things scatter into the walls. "
            "The room is ordinary.",
            Fore.RED)

    # Loot
    if random.random() < enemy["loot_chance"]:
        loot_name = enemy["loot"]
        loot = get_item(loot_name)
        if loot:
            print(c(f"  Left behind: {loot['name']}.", Fore.YELLOW))
            player.pick_up(loot)

    lo, hi = enemy.get("gold", (0, 6))
    gold = random.randint(lo, hi) if lo > 0 else 0
    if gold:
        player.gold += gold
        print(c(f"  You find {gold} gold.", Fore.YELLOW))

    return True


def use_thrown_weapon(player, enemy_hp: int, enemy: dict) -> tuple:
    """
    Let player select and throw a weapon during combat.
    Returns (new_enemy_hp, special_effect_applied).
    """
    thrown = [it for it in player.inventory if it["type"] == "thrown"]
    if not thrown:
        print(c("  You have no thrown weapons.", Fore.RED))
        return enemy_hp, None

    opts = [f"{it['name']} — {it['description']}" for it in thrown] + ["Cancel"]
    ch = prompt(opts)
    if ch == "Cancel":
        return enemy_hp, None

    item = next(it for it in thrown if it["name"] in ch)
    player.inventory.remove(item)

    dmg = item.get("throw_damage", 5)
    effect = item.get("throw_effect")

    # Void double vs void-type enemies
    if effect == "void_double" and enemy.get("special") in ("drain",):
        dmg *= 2
        print(c("  The starlight detonates against the void-corrupted. Double damage!", Fore.WHITE))

    enemy_hp -= dmg
    print(c(f"  You hurl the {item['name']}. {dmg} damage.", Fore.GREEN))

    applied_effect = None
    if effect == "bleed" and enemy_hp > 0:
        print(c("  The wound bleeds.", Fore.RED))
        applied_effect = "bleed"
    elif effect == "miss_next" and enemy_hp > 0:
        print(c("  The target is disoriented. Their next attack misses.", Fore.CYAN))
        applied_effect = "miss_next"

    return enemy_hp, applied_effect

# ─── ROOM DESCRIPTIONS (NORMAL) ───────────────────────────────────────────────
# Each entry: (description, ambient_hint)
# ambient_hint is shown at the bottom of the room as a faint sensory clue.
# None = no hint. Hints loosely suggest nearby room types without naming them.
NORMAL_ROOMS = [
    ("A low-ceilinged chamber smelling of damp stone. The walls are older than anything above ground.",
     None),
    ("Torchlight — somehow still burning — flickers across walls of imperial script you cannot read.",
     "A faint smell of old wax drifts from somewhere ahead."),
    ("The floor is thick with dust. Something large passed through here, not recently enough to matter.",
     None),
    ("A wide hall with collapsed pillars. Each pillar bears the same emblem: a sun consumed from below.",
     None),
    ("Water runs through a crack in the far wall, pooling somewhere below the flags.",
     None),
    ("Crude drawings of creatures cover every surface. Some have been scratched out with force.",
     "You hear, very faintly, the scrape of something being dragged."),
    ("Bone fragments crunch underfoot. Some of the bones are very large.",
     None),
    ("A cold wind pushes through cracks you cannot locate. The cold does not feel natural.",
     "Something breathes, far below. Very slowly."),
    ("The chamber opens into what was once a grand antechamber. The ceiling is lost in dark.",
     None),
    ("Shelves of rotting wood line the walls. Most have collapsed. A few sealed jars remain.",
     "A faint smell of ink and old paper from the east."),
    ("An archway carved with two figures flanking a circular door stands ahead. The door is solid stone.",
     None),
    ("Scorch marks radiate from the centre of the floor. Something burned here at tremendous heat.",
     "The air is slightly warmer from one passage."),
    ("The walls here are smoother than the others. Polished deliberately, or worn by many hands.",
     None),
    ("A long corridor. At the far end, light. At the close end, the sound of something breathing.",
     None),
    ("The room is perfectly square. Four identical arches stand in each wall. Three are bricked over.",
     None),
    ("Rows of stone benches face a raised dais. Whatever stood on the dais has been removed.",
     None),
    ("A mosaic floor, cracked but partially visible: a city from above, radiating from a central point.",
     None),
    ("The chamber smells of something burnt and sweet — a smell without a source.",
     None),
    ("A collapsed section of ceiling has let in soil from above. Roots have grown through the gap.",
     None),
    ("Words are scratched into the floor in many hands, all writing the same sentence in a language you cannot read.",
     None),
    ("The room is dominated by a single stone table, cracked down the middle. Tools are still laid on it.",
     None),
    ("A wide chamber with a low channel cut into the floor — a waterway, now dry.",
     None),
    ("The ceiling here is covered in carved stars. The constellations are not ones you recognise.",
     "A soft glow pulses from somewhere to the north, then is gone."),
    ("Three stone pillars bear the same face, repeated. The face is calm and has its eyes closed.",
     None),
    ("A small chamber. The only remarkable thing is a single hook set into the wall at head height, very precisely.",
     None),
    ("This corridor is longer than it should be. The walls gradually narrow as you move through it.",
     None),
    ("A chamber where every surface — walls, floor, ceiling — has been covered in the same symbol, "
     "stamped in something dark.", None),
    ("Old military equipment is stacked along one wall. Most is rusted into uselessness. Some is not.",
     "A faint smell of blood from somewhere ahead."),
    ("A wide gallery with empty frames on the walls — paintings removed, or destroyed. The frames are gilded.",
     None),
    ("The stone here is a different colour from the rest of the ruins — older, grey instead of tan.",
     None),
    ("A room with no features except a drain in the centre of the floor. The drain goes very deep.",
     None),
    ("Claw marks on the walls, at shoulder height, running in long continuous lines.",
     "You hear something skitter quickly away in the dark."),
    ("A chamber that smells strongly of something organic — not decay, but life. Underground life.",
     None),
    ("The walls are covered in numbers, scratched carefully, in columns. You cannot determine their purpose.",
     None),
    ("A room where half the floor has collapsed into a lower level. The lower level is dark.",
     "A voice, very briefly, from below. You are not certain you heard it."),
]

# Item-present hints — shown instead of ambient when the room has items
ITEM_HINTS = [
    "Something catches the light from a corner of the room.",
    "You notice the dust has been disturbed around one section of wall.",
    "A shape on the floor that might be more than debris.",
    "Something reflects the torchlight from beneath a collapsed shelf.",
    "An odd shape protrudes from beneath the rubble.",
    "The air near the far wall smells faintly different — less old.",
    "One stone near the base of the wall is a slightly different shade.",
]

def get_room_hint(room, player=None):
    """Return a hint line for the room if applicable."""
    if room.get("items"):
        return c(f"  {random.choice(ITEM_HINTS)}", Fore.YELLOW + Style.BRIGHT)
    ambient = room.get("ambient")

    # Compass gives better hints
    if player and "has_compass" in player.flags and ambient:
        return c(f"  [Compass] {ambient}", Fore.CYAN + Style.BRIGHT)
    if ambient:
        return c(f"  {ambient}", Fore.LIGHTBLUE_EX + Style.BRIGHT)
    return None

FORGE_RECIPES = {
    # Weapons
    "Rusty Sword":       [("Forge Dust",          5,  6, "Tempered Rusty Sword",
                           "The rust has been worked out. Reliable now.")],
    "Iron Sword":        [("Forge Dust",          10, 9, "Sharpened Iron Sword",
                           "A keener edge. Still standard-issue, but less forgiving."),
                          ("Dragon Ash",           25, 14, "Ash-Forged Sword",
                           "Dragon ash worked into the steel. The metal remembers heat.")],
    "Shadow Dagger":     [("Void-Tempered Ore",   15, 10, "Void Dagger",
                           "The blade drinks light now. Fast and very dark.")],
    "Eldrosian Spear":   [("Forge Dust",          12, 12, "Restored Eldrosian Spear",
                           "The imperial sigils are cleaner. The balance is perfect.")],
    "Bone Hatchet":      [("Bloodwood Resin",     8,  8,  "Bloodwood Hatchet",
                           "Resin-treated handle and edge. Unsettling but effective.")],
    "Serrated Blade":    [("Bloodwood Resin",     10, 11, "Barbed Serrated Blade",
                           "Additional barbs. Wounds from this do not close easily.")],
    "Bonespike":         [("Dragon Ash",          20, 14, "Ash-Crowned Bonespike",
                           "Dragon ash binds the bone. It holds an edge now.")],
    "Obsidian Knife":    [("Starlight Thread",    18, 11, "Starlight-Hafted Knife",
                           "The haft is woven with starlight thread. Won't chip now.")],
    # Armour
    "Wooden Shield":     [("Bloodwood Resin",     5,  5,  "Resin-Hardened Shield",
                           "The wood is dense as stone now. Will not splinter.")],
    "Iron Shield":       [("Forge Dust",          10, 8,  "Worked Iron Shield",
                           "Better shaped, better balanced. Less heavy, more protective.")],
    "Leather Armour":    [("Starlight Thread",    15, 7,  "Thread-Woven Leather",
                           "Veythari thread worked through the leather. Lighter. Stronger.")],
    "Chain Vest":        [("Void-Tempered Ore",   20, 9,  "Void-Linked Chain",
                           "Void-ore links resist drain. The rings are perfectly dark.")],
    "Scale Armour":      [("Dragon Ash",          25, 11, "Ash-Blessed Scale",
                           "Dragon ash treated. The scales hold warmth differently now.")],
    "Eldrosian Plate":   [("Forge Dust",          15, 12, "Restored Eldrosian Plate",
                           "The emblem is scraped off. The metal is imperial-grade.")],
    "Warden's Coat":     [("Bloodwood Resin",     12, 9,  "Reinforced Warden's Coat",
                           "Resin-hardened leather and rings. The coat of an official who meant it.")],
}

def _forge_slug(item_name: str) -> str:
    return "forged_" + item_name.lower().replace(" ", "_").replace("'", "")


def event_forge(player, room):
    """
    The Forge Room — a mortal imitation of Ishak's divine forge.
    Upgrades weapons and armour for materials and gold.
    """
    from colorama import Fore, Style
    hr("═", colour=Fore.RED)
    print(c("  THE FORGE", Fore.RED + Style.BRIGHT))
    hr("═", colour=Fore.RED)
    print()
    wrap(
        "A forge, still burning. That alone is remarkable — "
        "the fuel has not been replenished in centuries. "
        "The fire burns at a lower temperature than it should, "
        "as though it is managing itself. "
        "The tools are Eldrosian-quality. The workmanship is excellent. "
        "Someone built this to last.",
        Fore.RED)
    print()
    wrap(
        "Above the forge, barely legible through the soot: "
        "'This work is a poor shadow of the Forge Above — "
        "where metals are born already knowing what they will become. "
        "We built this because we could not reach that one. "
        "We built it well, despite.'",
        Fore.RED + Style.BRIGHT)
    print()
    player.flags.add("found_forge")

    done = room.get("_forge_done", set())

    while True:
        # Find upgradeable items the player carries
        upgradeable = []
        for item in player.inventory:
            iname = item["name"]
            slug = _forge_slug(iname)
            if iname in FORGE_RECIPES and slug not in player.flags:
                for material, cost, new_val, new_name, new_desc in FORGE_RECIPES[iname]:
                    has_mat = player.has_item(material)
                    can_afford = player.gold >= cost
                    upgradeable.append((item, material, cost, new_val, new_name,
                                        new_desc, has_mat, can_afford))

        opts = []
        if "examine" not in done:
            opts.append("Examine the forge")
        if upgradeable:
            opts.append("Upgrade an item")
        else:
            opts.append("(No upgradeable items — bring weapons, armour, and materials)")
        if "materials" not in done:
            opts.append("Ask about materials")
        opts.append("Leave")
        ch = prompt(opts)

        if ch == "Leave":
            break

        elif ch == "Examine the forge":
            done.add("examine")
            wrap(
                "The bellows work on their own. Slowly — one breath every few minutes. "
                "The coals are some kind of stone you have not seen before. "
                "They glow red-orange and do not diminish. "
                "The anvil is Eldrosian iron, unrusted. "
                "Around it: the marks of a thousand strikes, perfectly centred.",
                Fore.RED)

        elif "Ask about materials" in ch:
            done.add("materials")
            wrap(
                "Materials needed for the forge:",
                Fore.YELLOW)
            MATERIAL_SOURCES = [
                ("Forge Dust",         "Collected from the forge floor — this room. Look carefully."),
                ("Void-Tempered Ore",  "Dropped by void-corrupted enemies, especially Void-Fused Knights."),
                ("Starlight Thread",   "Found in the Veythari Sanctuary. Morvath Shades sometimes carry fragments."),
                ("Dragon Ash",         "Collected near where Atheron sleeps. Handle with care."),
                ("Bloodwood Resin",    "Dropped by Flesh Architects and Blood Crawlers."),
            ]
            for mat, source in MATERIAL_SOURCES:
                print(c(f"  {mat:20}", Fore.YELLOW) +
                      c(f" — {source}", Fore.WHITE))

            # Forge dust is findable in this room
            if "forge_dust_found" not in player.flags:
                print()
                wrap(
                    "On the floor around the forge: fine metallic powder. "
                    "It is warm to the touch.",
                    Fore.RED)
                ch2 = prompt(["Collect the Forge Dust", "Leave it"])
                if ch2 == "Collect the Forge Dust":
                    player.flags.add("forge_dust_found")
                    # Give 1-3 Forge Dust
                    count = random.randint(1, 3)
                    for _ in range(count):
                        player.pick_up({"name": "Forge Dust", "type": "material",
                                        "value": 0,
                                        "description": "Fine metallic powder collected from the forge floor. "
                                                       "It is warm. It should not still be warm."})
                    print(c(f"  Collected {count} Forge Dust.", Fore.GREEN))

        elif "Upgrade an item" in ch and upgradeable:
            # Build selection menu
            upgrade_opts = []
            for (item, material, cost, new_val, new_name, new_desc,
                 has_mat, can_afford) in upgradeable:
                status = ""
                if not has_mat:
                    status = c(f" [need {material}]", Fore.RED)
                elif not can_afford:
                    status = c(f" [need {cost}g — have {player.gold}g]", Fore.RED)
                else:
                    status = c(f" [ready: {material} + {cost}g]", Fore.GREEN)
                upgrade_opts.append(
                    f"{item['name']} → {new_name}{status}")
            upgrade_opts.append("Cancel")
            uch = prompt(upgrade_opts)
            if uch == "Cancel":
                continue

            # Find which upgrade was selected
            chosen = None
            for entry in upgradeable:
                item, material, cost, new_val, new_name, new_desc, has_mat, can_afford = entry
                if item["name"] in uch:
                    chosen = entry
                    break
            if not chosen:
                continue

            item, material, cost, new_val, new_name, new_desc, has_mat, can_afford = chosen

            if not has_mat:
                print(c(f"  You need {material} to forge this.", Fore.RED))
                continue
            if not can_afford:
                print(c(f"  You need {cost} gold. You have {player.gold}.", Fore.RED))
                continue

            # Perform the upgrade
            player.remove_item(material)
            player.gold -= cost
            slug = _forge_slug(item["name"])
            player.flags.add(slug)

            # Update the item in place
            old_name = item["name"]
            item["name"] = new_name
            item["value"] = new_val
            item["description"] = new_desc

            # Re-link equipped items if this was equipped
            for slot in ("weapon", "armour"):
                if player.equipped.get(slot) is item:
                    pass  # already the same object — no re-link needed

            print()
            hr(colour=Fore.RED)
            wrap(
                f"The forge takes the {old_name}. "
                f"The fire responds — briefly hotter, briefly brighter. "
                f"What comes out is the {new_name}.",
                Fore.RED + Style.BRIGHT)
            wrap(f"  Value: {new_val}  |  {new_desc}", Fore.YELLOW)
            hr(colour=Fore.RED)
            print(c(f"  -{cost} gold, -{material}.", Fore.YELLOW))

        room["_forge_done"] = done



# ─── NPC GATE HELPERS ─────────────────────────────────────────────────────────
# These functions check what the player knows before unlocking NPC questions.

def knows_eldros(p):
    return True  # always

def knows_wells(p):
    return any(f in p.flags for f in ("prisoner_told_well","merchant_told_wells",
                                      "read_parchment_wells","sael_told_wells","read_ashen_tablet"))

def knows_mural(p):
    return "found_mural" in p.flags

def knows_thaun(p):
    return knows_mural(p)

def knows_arukiel(p):
    return knows_mural(p)

def knows_fall(p):
    return any(f in p.flags for f in ("prisoner_told_eldros","found_library_collapse",
                                      "read_ashen_tablet","read_imperial_edict"))

def knows_gods(p):
    return any(f in p.flags for f in ("merchant_myrrakhel","spoke_myrrakhel_shrine",
                                      "prisoner_told_gods","sael_myrrakhel","altar_myrrakhel_hint",
                                      "read_priests_journal","orrath_myrrakhel"))

def knows_betrayer_hint(p):
    # knows something is missing from the records
    return any(f in p.flags for f in ("read_charred_ledger","found_vault_door",
                                      "found_library_collapse","inscription_variation","read_ashen_tablet"))

def knows_name_partial(p):
    # knows the name is M___VYR or similar
    return any(f in p.flags for f in ("found_blank_book","spoke_maelvyr_shrine",
                                      "candle_mural_secret","ossuary_name","inscription_variation"))

def knows_vaelan(p):
    return any(f in p.flags for f in ("read_imperial_edict","found_throne_room",
                                      "prisoner_told_vaelan","orrath_told_vaelan","sael_told_vaelan"))

def knows_dravennis(p):
    return any(f in p.flags for f in ("heard_dravennis","prisoner_dravennis",
                                      "found_blood_door","read_priests_journal"))

def knows_godshards(p):
    return any(f in p.flags for f in ("read_imperial_edict","found_throne_room",
                                      "merchant_godshards","sael_godshards"))

def knows_vaethar(p):
    return any(f in p.flags for f in ("found_throne_room","sael_vaethar","orrath_vaethar"))


# ── FACTION ENCOUNTER SYSTEM ────────────────────────────────────────────────

def faction_encounter(player, room):
    """
    Called occasionally in normal rooms to place a faction NPC.
    Returns True if an encounter happened (so the caller can note it).
    Only fires once per room.
    """
    if "faction_done" in room:
        return False

    depth = player.depth

    # Faction probabilities by depth
    roll = random.random()
    if depth < 5:
        # Early: mostly scholars, occasionally shard-seekers
        if roll < 0.08:
            _scholar_encounter(player, room)
            room["faction_done"] = True
            return True
    elif depth < 12:
        # Mid: scholars, seekers, occasional cultist
        if roll < 0.05:
            _scholar_encounter(player, room)
            room["faction_done"] = True
            return True
        elif roll < 0.10:
            _seeker_encounter(player, room)
            room["faction_done"] = True
            return True
        elif roll < 0.13:
            _cultist_encounter(player, room)
            room["faction_done"] = True
            return True
    else:
        # Deep: mostly cultists, seekers rare, scholars absent
        if roll < 0.07:
            _cultist_encounter(player, room)
            room["faction_done"] = True
            return True
        elif roll < 0.10:
            _seeker_encounter(player, room)
            room["faction_done"] = True
            return True

    return False


def _scholar_encounter(player, room):
    if is_hostile(player, "scholars"):
        wrap("They back away. You have made enemies of the Scholars.", Fore.CYAN)
        return False

    wrap(
        "In the corner of the room: a figure in scholar's robes, "
        "taking frantic notes. They look up at you without alarm — "
        "academics in ruins are, apparently, not easily startled.",
        Fore.CYAN)
    print()

    SCHOLAR_LINES = [
        "'The inscriptions in the lower chambers are pre-imperial. I've never seen the script before.'",
        "'The Void-well — do you know if it actually exists? "
        "My notes suggest it's in the lowest accessible level.'",
        "'I've been following the cultists. They know where they're going. That concerns me.'",
        "'The Hall of the Nine — if you find it — examine all of them. "
        "The order matters. Start with Myrrakhel.'",
        "'Someone cleaned the Dawn Chamber deliberately. The stonework is too smooth.'",
        "'I found a reference to a man named Talarion. He was here. He wrote everything down.'",
    ]
    print(c(f"  {random.choice(SCHOLAR_LINES)}", Fore.CYAN))
    print()

    ch = prompt(["Ask what they know", "Give them a Health Potion", "Leave them to it"])

    if ch == "Ask what they know":
        EXTRA_LINES = [
            "'The Godshards were returned here after the Wars. Placed deliberately. Not lost.'",
            "'Maelvyr survived the throne room. Injured, but alive. He was seen leaving the city.'",
            "'The thing in the well is older than the wells. The Remnant Scholars call it Atraxis.'",
            "'The cultists are called the Void-Touched. They believe the Unmade will give them power.'",
            "'There are at least three factions in these ruins. We are all looking for different things.'",
        ]
        print(c(f"  {random.choice(EXTRA_LINES)}", Fore.CYAN))
        player.flags.add("scholar_gave_info")

    elif ch == "Give them a Health Potion":
        potion = next((it for it in player.inventory if it["name"] == "Health Potion"), None)
        if potion:
            player.inventory.remove(potion)
            wrap(
                "They take it with genuine gratitude. "
                "'I can tell you where I've found useful things.' "
                "They mark three locations on a rough sketch — "
                "you can't take the sketch, but the information stays with you.",
                Fore.GREEN)
            # Small buff — they've marked useful rooms
            player.flags.add("scholar_told_locations")
            player.gold += 10
            print(c("  Also, they press 10 gold into your hand. 'For the road.'", Fore.YELLOW))
        else:
            print("  You have no potion to give.")


def _seeker_encounter(player, room):
    wrap(
        "A mercenary — well-equipped, cautious — stops when they see you. "
        "One hand near a weapon. Not drawing it. Yet.",
        Fore.YELLOW)
    print()

    SEEKER_LINES = [
        "'We're after the same things, I expect. Stay out of my way and I'll stay out of yours.'",
        "'The Godshards. You know where they are? I'll split the finder's fee.'",
        "'The cultists are organised. Three of my crew are dead. Don't go south.'",
        "'I've got a map. Incomplete. Worth something, maybe.'",
    ]
    print(c(f"  {random.choice(SEEKER_LINES)}", Fore.YELLOW))
    print()

    if is_hostile(player, "seekers"):
        wrap("They recognise you. This is not a good recognition.", Fore.YELLOW)
        # Fight
        seeker = next((e for e in ENEMY_POOL if e["name"] == "Shard-Seeker"), None)
        if seeker:
            combat(player, spawn_enemy(seeker))
        return False

    ch = prompt(["Trade information", "Buy their map (20 gold)", "Fight them", "Leave"])

    if ch == "Trade information":
        if "found_throne_room" in player.flags or "found_shattered_crown_hall" in player.flags:
            wrap(
                "'The Godshards are in the Hall of the Shattered Crown. "
                "One is in the throne room — still in the emperor's hand.' "
                "They seem surprised you know this. "
                "'You've been deeper than me, then.'",
                Fore.YELLOW)
            player.flags.add("seeker_exchanged")
            player.gold += 15
            print(c("  They give you 15 gold. Fair exchange.", Fore.YELLOW))
        else:
            wrap("'I don't need what you've got.' They turn away.", Fore.YELLOW)

    elif ch == "Buy their map (20 gold)":
        if player.gold >= 20:
            player.gold -= 20
            player.pick_up(get_item("Shard-Seeker's Map"))
            wrap("They hand it over. 'It's incomplete. But the throne room is real.'", Fore.YELLOW)
        else:
            print(c("  'You can't afford it.'", Fore.YELLOW))

    elif ch == "Fight them":
        wrap("They draw their weapon. Professional. This will be difficult.", Fore.RED)
        seeker = next((e for e in ENEMY_POOL if e["name"] == "Shard-Seeker"), None)
        if seeker:
            combat(player, spawn_enemy(seeker))
    else:
        print("  You leave them to their work.")


def _cultist_encounter(player, room):
    wrap(
        "A figure in dark robes steps from a shadow that should not have been large enough to hide them. "
        "Their eyes are wrong — not silver like a Veythari, not black like a Morvath. "
        "Just — wrong.",
        Fore.RED)
    print()

    CULTIST_LINES = [
        "'You have come far. You will go no further.'",
        "'The Unmade sees you. It has been watching since you entered.'",
        "'You should not be here. But neither should we. We are here anyway.'",
        "'Join us or leave. Those are the only options.'",
    ]
    print(c(f"  {random.choice(CULTIST_LINES)}", Fore.RED))
    print()

    if is_allied(player, "void_touched"):
        wrap("They recognise your standing. 'You are known to us.'", Fore.RED)
        ch2 = prompt(["Ask what they know (Atraxis lore)", "Leave them"])
        if "Ask" in ch2:
            CULTIST_LORE = [
                "Atraxis is not the Void. It is the mind of what the Void was before it was void.",
                "The Scar on the fourth level is where the breach happened. "
                "The Void-Touched perform rituals there to widen it.",
                "The Named — one of our order — learned the full name. "
                "The name is consuming them. It is the price of knowing.",
                "Atraxis does not want to destroy. It wants to incorporate. "
                "The distinction is important and not comforting.",
            ]
            print(c(f"  '{random.choice(CULTIST_LORE)}'", Fore.RED))
            adjust_reputation(player, "void_touched", 0)  # no change, just info
        return False

    ch = prompt(["Fight them", "Ask what they want", "Try to leave"])

    if ch == "Ask what they want":
        wrap(
            "'We are the Void-Touched. We serve the Unmade — Atraxis, the thing beneath the well. '",
            Fore.RED)
        wrap(
            "'We believe that when Atraxis reclaims its power, those who served it will be remade. '",
            Fore.RED)
        player.flags.add("atraxis_named")  # player learns the name Atraxis
        wrap(
            "'We know what you carry. We know where you are going. '",
            Fore.RED + Style.BRIGHT)
        wrap("'Leave, or we will stop you.'", Fore.RED + Style.BRIGHT)
        print()
        ch2 = prompt(["Fight them anyway", "Leave"])
        if ch2 == "Fight them anyway":
            _do_cultist_fight(player)
        else:
            print("  You back away. They watch you go.")

    elif ch == "Fight them":
        _do_cultist_fight(player)

    else:
        if random.random() < 0.5:
            print("  They let you go. This time.")
        else:
            wrap("They don't let you leave that easily.", Fore.RED)
            _do_cultist_fight(player)


def _do_cultist_fight(player):
    cultist = next((e for e in ENEMY_POOL if e["name"] == "Void-Touched Cultist"), None)
    if cultist:
        survived = combat(player, spawn_enemy(cultist))
        if survived and player.hp > 0:
            player.flags.add("fought_cultist")




# ─── HANDLE SPECIAL EVENT DISPATCH ───────────────────────────────────────────
NPC_EVENTS = {"sael_chamber","orrath_chamber","prisoner","merchant","gambling_den"}

def handle_special_event(key, player, room):
    handlers = {
        "shrine":             event_shrine,
        "merchant":           event_merchant,
        "trap_vault":         event_trap_vault,
        "library":            event_library,
        "prisoner":           event_prisoner,
        "mural_hall":         event_mural_hall,
        "sael_chamber":       event_sael_chamber,
        "inscription_room":   event_inscription_room,
        "dragon_hall":        event_dragon_hall,
        "vault_door":         event_vault_door,
        "sealed_sanctum":     event_sealed_sanctum,
        "veythari_door":      event_veythari_door,
        "void_well":          event_void_well,
        "blood_door":         event_blood_door,
        "wardens_archive":    event_wardens_archive,
        "throne_room":        event_throne_room,
        "orrath_chamber":     event_orrath_chamber,
        "gambling_den":       event_gambling_den,
        "broken_altar":       event_broken_altar,
        "ossuary":            event_ossuary,
        "empty_throne":       event_empty_throne,
        "mirror_chamber":     event_mirror_chamber,
        "astral_well_hint":   event_astral_well_hint,
        "hollow_stone_room":  event_hollow_stone_room_fixed,
        "deeper_staircase":   event_deeper_staircase,
        "flooded_room":       event_flooded_room,
        "listening_room":     event_listening_room,
        "sealed_window":      event_sealed_window,
        "chamber_of_agreement":event_chamber_of_agreement,
        "ritual_chamber":     event_ritual_chamber,
        "hall_of_nine":       event_hall_of_the_nine,
        "hall_of_shattered_crown":  event_hall_of_shattered_crown,
        "veythari_sanctuary": event_veythari_sanctuary,
        "crystal_mirror_room":event_crystal_mirror_room,
        "dawn_shard_room":    event_dawn_shard_room,
        "talarion_room":      event_tolarion_room,
        "black_market":       event_black_market,
        "cartographers_station": event_cartographers_station,
        "recovery_room":      event_recovery_room,
        "warden_bell":        event_warden_bell,
        "forge":              event_forge,
        "archivist":          event_archivist,
        "bound_one":          event_bound_one,
        "serethan_echo":      event_serethan_echo,
        "seeker_captain":     event_seeker_captain,
        "deep_sleeper":       event_deep_sleeper,
        "near_mortal_ossuary":event_near_mortal_ossuary,
        "war_room":           event_war_room,
        "chapel_of_thrys":    event_chapel_of_thrys,
        "observatory":        event_observatory,
        "naming_room":        event_naming_room,
        "archive_agreements": event_archive_of_agreements,
        "atraxis_scar":       event_atraxis_scar,
        "poison_garden":      event_poison_garden,
    }
    fn = handlers.get(key)
    if fn:
        fn(player, room)



def generate_dungeon(descent: int = 1) -> Dungeon:
    """
    Build a complete 3D dungeon for one descent.
    Returns a Dungeon with all rooms placed, typed, and populated.
    """
    seed = random.randint(0, 10_000_000)
    rng  = random.Random(seed)
    d    = Dungeon()
    d.seed = seed

    # Phase 1 — Carve all floors
    carved_by_floor = {}
    for z in range(len(FLOOR_DIMS)):
        carved = d._carve_floor(z, seed + z)
        carved_by_floor[z] = carved

    # Place staircases
    d._place_staircases(carved_by_floor, rng)

    # Ensure entrance exists
    entrance_candidates = [
        pos for pos in d.grid
        if pos[2] == 0
    ]
    if entrance_candidates:
        d.entrance = rng.choice(entrance_candidates)
        # Mark entrance room
        entrance_room = d.grid[d.entrance]
        entrance_room.room_def = {
            "name":         "The Entrance",
            "description":  ("You stand at the entrance to the Ruins of Eldros-Verath. "
                             "The stones beneath your feet are older than memory. "
                             "The air smells of centuries."),
            "special_event":None,
            "items":        [],
            "enemies":      [],
            "ambient":      None,
        }
        entrance_room.visited = True   # player starts here

    # Phase 2 — Assign room types
    d._assign_rooms(rng, descent)

    # Validate — retry up to 3 times if disconnected
    for attempt in range(3):
        if d._validate_connectivity():
            break
        # Re-carve with different seed
        seed += 1
        rng   = random.Random(seed)
        d     = Dungeon()
        d.seed = seed
        carved_by_floor = {}
        for z in range(len(FLOOR_DIMS)):
            carved_by_floor[z] = d._carve_floor(z, seed + z)
        d._place_staircases(carved_by_floor, rng)
        d._assign_rooms(rng, descent)

    return d


# ─── SEARCHING ────────────────────────────────────────────────────────────────
def search_room(room, player):
    if not room["items"]:
        print(c("  You find nothing.", Fore.LIGHTBLUE_EX+Style.BRIGHT)); return
    print(c("  You search carefully. You uncover:", Fore.YELLOW))
    for item in list(room["items"]):
        col = {"key":Fore.YELLOW,"lore":Fore.CYAN,"artefact":Fore.MAGENTA}.get(item["type"],Fore.WHITE)
        print(c(f"    {item['name']}", col) + c(f"  —  {item['description']}", Fore.LIGHTBLUE_EX+Style.BRIGHT))
        if prompt(["Take it","Leave it"]) == "Take it":
            player.pick_up(item); room["items"].remove(item)

def enter_dungeon_room(room: DungeonRoom, player) -> str:
    """
    Handle one room. Returns a result string:
        "move:<direction>"  — player chose to move
        "quit"              — player quit
        "died"              — player's HP hit 0
        "ended"             — an ending fired (sys.exit inside ending fn)
    """
    rd = room.room_def
    print()
    autosave(player)
    hr("═", colour=Fore.YELLOW)
    print(c(f"  {rd.get('name','Chamber').upper()}", Fore.YELLOW + Style.BRIGHT))
    hr("═", colour=Fore.YELLOW)
    wrap(rd.get("description", "")); print()

    # Ambient hint
    hint = get_room_hint(rd, player)
    if hint: print(hint); print()

    # Fire event (NPC events fire every visit; others fire once)
    ev = rd.get("special_event")
    npc_events = {"sael_chamber","orrath_chamber","prisoner","merchant","gambling_den",
                  "shrine","library","broken_altar","ossuary","mirror_chamber",
                  "dragon_hall","empty_throne","inscription_room","mural_hall",
                  "astral_well_hint","hollow_stone_room","crystal_mirror_room",
                  "dawn_shard_room","talarion_room","cartographers_station",
                  "hall_of_nine","hall_of_shattered_crown","veythari_sanctuary",
                  "black_market","trap_vault","vault_door",
                  "sealed_sanctum","veythari_door","void_well",
                  "blood_door","wardens_archive","throne_room",
                  "chamber_of_agreement","ritual_chamber","recovery_room",
                  "warden_bell",
                  "flooded_room","listening_room","sealed_window"}
    revisitable = {"sael_chamber","orrath_chamber","prisoner","merchant",
                   "gambling_den","shrine","black_market",
                   "hall_of_nine","ossuary","mural_hall","inscription_room",
                   "dragon_hall","empty_throne","mirror_chamber","broken_altar",
                   "astral_well_hint","hollow_stone_room","crystal_mirror_room",
                   "dawn_shard_room","talarion_room","cartographers_station",
                   "hall_of_shattered_crown","veythari_sanctuary","library",
                   "vault_door","sealed_sanctum","veythari_door","void_well",
                   "blood_door","wardens_archive","throne_room",
                   "chamber_of_agreement","ritual_chamber","trap_vault"}

    if ev:
        first_visit = "_event_fired" not in room.state
        if first_visit or ev in revisitable:
            room.state["_event_fired"] = True
            try:
                handle_special_event(ev, player, room.state)
            except SystemExit:
                return "ended"

    # Combat
    enemies = list(rd.get("enemies", []))
    for enemy in enemies:
        if player.hp <= 0:
            return "died"
        # Apply bell boost if active
        boosted = _apply_bell_boost(enemy, player)
        survived = combat(player, boosted)
        if not survived or player.hp <= 0:
            return "died"
    rd["enemies"] = []   # clear after combat


    if "warden_bell_rung" in player.flags and not ev:
         extra_pool = enemy_pool_for_depth(room.z * 4)
         if random.random() < 0.3:   # 30% chance of an extra enemy
            extra = spawn_enemy(random.choice(extra_pool))
            rd["enemies"] = rd.get("enemies", []) + [extra]

    # Faction encounter (normal rooms only)
    if not ev and player.hp > 0:
        faction_encounter(player, room.state)

    # Candle trigger for recovery room
    if player.has_item("Candle") and not ev:
        _trigger_recovery_room_check(player, room.state)

    def _room_completion_check(event_key: str, player) -> bool:
        """
        Return True if a sealable room should now be permanently closed.
        More comprehensive than the Part 1 version.
        """
        checks = {
            "throne_room": lambda p: (
                    "took_godshard_from_vaelan" in p.flags
                    and "crown_returned_throne" in p.flags
            ),
            "void_well": lambda p: any(f in p.flags for f in (
                "confrontation_done",
                "sealing_done",
                "void_well_witnessed",
                "shard_returned",
            )),
            "ritual_chamber": lambda p: any(f in p.flags for f in (
                "full_truth_known",
                "refused_the_offer",
                "ritual_summoned_confrontation",
                "vaethar_tear_atheron",
            )),
            "chamber_of_agreement": lambda p: (
                    "stood_in_circle" in p.flags
                    and "agreement_chamber_inscription" in p.flags
            ),
        }
        fn = checks.get(event_key)
        return fn(player) if fn else False

    # Check sealing condition
    if room.sealed and not room.completed:
        if _room_completion_check(ev, player):
            room.completed = True

    if room.sealed and room.completed:
        hr("═", colour=Fore.LIGHTBLUE_EX)
        print(c(f"  {room.name.upper()} — SEALED", Fore.LIGHTBLUE_EX + Style.BRIGHT))
        hr("═", colour=Fore.LIGHTBLUE_EX)
        wrap(
            "This room is closed to you now. "
            "What happened here is done, and the ruins have acknowledged it. "
            "The way in is sealed.",
            Fore.LIGHTBLUE_EX + Style.BRIGHT)
        # Find any open exit and push player there
        for direction, dest in room.exits.items():
            if dest:
                return f"move:{direction}"
        return "quit"

    # ── Exploration loop ─────────────────────────────────────────────────────
    while True:
        # Build exit list
        autosave(player)
        open_exits = room.get_open_exits()
        print()
        _describe_dungeon_exits(room, player)

        opts = ["Search for items", "Check inventory", "View map", "Review discoveries"]
        if is_admin(player):
            opts.append("Admin mode")
        if ev in revisitable:
            opts.append("Interact with this room again")
        for d in open_exits:
            label = _exit_label(d, room, player)
            opts.append(f"Go {label}")
        opts.append("Quit")

        ch = prompt(opts)

        if ch == "Search for items":
            search_room(rd, player)

        elif ch == "Check inventory":
            while True:
                player.show_inventory()
                print()
                inv_ch = prompt(["Use or equip an item", "Sort inventory", "Back"])
                if inv_ch == "Use or equip an item":
                    player.use_item()
                elif inv_ch == "Sort inventory":
                    sort_ch = prompt(["By type","By name","By value","By recent"])
                    sort_map = {"By type":"type","By name":"name",
                                "By value":"value","By recent":"recent"}
                    player._inv_sort = sort_map[sort_ch]
                else:
                    break

        elif ch == "View map":
            player.dungeon.display_map(player.dungeon_pos, player)

        elif ch == "Review discoveries":
            ch2 = prompt(["View discoveries", "View faction standing", "Back"])
            if ch2 == "View discoveries":
                show_lore_journal(player)
            elif ch2 == "View faction standing":
                show_reputation(player)

        elif ch == "Interact with this room again":
            if ev:
                try:
                    handle_special_event(ev, player, room.state)
                except SystemExit:
                    return "ended"

        # With this:
        elif ch == "Admin mode":
            admin_result = admin_menu(player)
            if admin_result is not None and admin_result[0] == "teleport":
                dest_pos = admin_result[1]
                # Return a move instruction so run_game repositions properly
                return f"teleport:{dest_pos[0]},{dest_pos[1]},{dest_pos[2]}"

        elif ch == "Quit":
            return "quit"

        elif ch.startswith("Go "):
            # Parse direction from label
            direction = _parse_direction_from_label(ch)
            if direction and room.exits.get(direction):
                return f"move:{direction}"
            print(c("  That passage is blocked.", Fore.RED))


def _describe_dungeon_exits(room: DungeonRoom, player):
    """Describe available exits with compass directions and floor changes."""
    open_exits = room.get_open_exits()
    if not open_exits:
        print(c("  No exits visible.", Fore.LIGHTBLUE_EX + Style.BRIGHT))
        return
    parts = []
    for d in open_exits:
        dest = room.exits[d]
        dest_room = player.dungeon.get(dest) if dest else None
        visited_mark = ""
        if dest_room and dest_room.visited:
            visited_mark = c(" (visited)", Fore.LIGHTBLUE_EX + Style.BRIGHT)
        if d in ("down", "up"):
            arrow = "▼" if d == "down" else "▲"
            parts.append(c(f"{arrow} {d} (next floor){visited_mark}", Fore.MAGENTA))
        else:
            parts.append(f"{d}{visited_mark}")
    print(c("  Exits: ", Fore.LIGHTBLUE_EX + Style.BRIGHT) + ", ".join(parts))


def _exit_label(direction: str, room: DungeonRoom, player) -> str:
    """Return a descriptive label for a direction option."""
    dest = room.exits.get(direction)
    if not dest:
        return direction
    dest_room = player.dungeon.get(dest)
    if direction in ("down", "up"):
        arrow = "▼" if direction == "down" else "▲"
        return f"{arrow} {direction} (to floor {dest[2]+1})"
    visited = dest_room and dest_room.visited
    return f"{direction}" + (" (revisit)" if visited else "")


def _parse_direction_from_label(ch: str) -> str | None:
    """Extract the direction from a 'Go ...' choice string."""
    label = ch[3:]   # strip "Go "
    for d in DungeonRoom.ALL_DIRS:
        if label.startswith(d) or (d in ("down","up") and d in label):
            return d
    return None


def _apply_bell_boost(enemy: dict, player) -> dict:
    """Return a boosted copy of an enemy if the bell has been rung."""
    if "warden_bell_rung" not in player.flags:
        return enemy
    boosted = dict(enemy)
    boosted["hp"]     = int(enemy["hp"]     * 2.0)
    boosted["attack"] = int(enemy["attack"] * 2.0)
    return boosted


# ─── WIN / DESCENT ────────────────────────────────────────────────────────────
def win_screen(player) -> bool:
    """
    Called when the player returns to the entrance after sufficient exploration.
    Routes to _ending_truth if they know enough, otherwise basic escape.
    """
    flags = player.flags
    found_count = sum(1 for f in ALL_FLAGS if f in flags and f in DISCOVERY_TEXT)

    # Full truth ending
    if "full_truth_known" in flags or found_count >= 25:
        result = _ending_truth(player)
        return result == "descend"

    # Partial knowledge endings — flavour varies by what they found
    hr("═", colour=Fore.GREEN)
    print(c("  Daylight. A staircase, and daylight.", Fore.GREEN))
    print()

    if found_count >= 15:
        wrap(
            f"  {player.name} emerges carrying significant pieces of the truth. "
            "Not all of it. Enough to know that not all of it is a comfortable thing to carry. "
            "The ruins remain. They will remain after you. "
            "What you found down there is yours now, whether you wanted it or not.",
            Fore.GREEN)
    elif found_count >= 8:
        wrap(
            f"  {player.name} emerges with fragments — names, inscriptions, "
            "things seen that cannot be unseen. "
            "The ruins gave what they gave. "
            "There is more down there. You could feel it.",
            Fore.GREEN)
    else:
        wrap(
            f"  {player.name} emerges into daylight. "
            "The ruins of Eldros-Verath stand behind you. "
            "You crossed through a fraction of them. "
            "The darkness below did not particularly notice.",
            Fore.GREEN)

    print()
    print(c(f"  Rooms explored: {player.visited_rooms}  |  Gold: {player.gold}",
            Fore.YELLOW))
    print(c(f"  Discoveries: {found_count} of {len(DISCOVERY_TEXT)}", Fore.CYAN))

    remaining = len(DISCOVERY_TEXT) - found_count
    if remaining > 20:
        print(c(f"  {remaining} secrets remain in the dark. Many of them significant.",
                Fore.CYAN))
    elif remaining > 5:
        print(c(f"  {remaining} secrets remain in the dark.", Fore.CYAN))
    else:
        print(c(f"  {remaining} secrets remain. You are close to the whole truth.",
                Fore.CYAN + Style.BRIGHT))

    hr("═", colour=Fore.GREEN)
    print()

    ch = prompt([
        "Descend again — there is more to find",
        "End here",
    ])
    return ch.startswith("Descend")


# ─── MAIN ─────────────────────────────────────────────────────────────────────
WIN_ROOMS_FIRST  = 50
WIN_ROOMS_SECOND = 70

TITLE_ART = """
  ╔══════════════════════════════════════════════════════╗
  ║                                                      ║
  ║               L A N D S   O F   E O N                ║
  ║                                                      ║
  ║         Ruins of Eldros-Verath, First Empire         ║
  ║                                                      ║
  ╚══════════════════════════════════════════════════════╝
"""
def run_game(player) -> bool:
    """
    Main game loop using pre-generated dungeon.
    Returns True if the player wants to descend again, False otherwise.
    """
    # Generate dungeon if not already present
    if not hasattr(player, "dungeon") or player.dungeon is None:
        print(c("  Generating the ruins...", Fore.YELLOW))
        player.dungeon = generate_dungeon(player.descent)
        player.dungeon_pos = player.dungeon.entrance
        # Give the map to the player
        if not hasattr(player, "map") or player.map is None:
            player.map = DungeonMap()
        player.map.visit(player.dungeon_pos,
                         player.dungeon.grid[player.dungeon_pos].name)

    while True:
        pos  = player.dungeon_pos
        room = player.dungeon.get(pos)

        if room is None:
            # Shouldn't happen, but recover gracefully
            print(c("  (Something went wrong — returning to entrance.)", Fore.RED))
            player.dungeon_pos = player.dungeon.entrance
            continue

        # Check for sealed room the player has already completed
        if room.sealed and room.completed:
            wrap("The way is sealed. What happened here is done.", Fore.LIGHTBLUE_EX)
            # Force player back — find any open exit
            for dest in room.exits.values():
                if dest:
                    player.dungeon_pos = dest
                    break
            continue

        # Enter the room
        result = enter_dungeon_room(room, player)

        # result is one of: "quit", "died", "ended", "move:<direction>"
        if result == "quit":
            print(c("\n  You set down your pack. Your story ends here.",
                    Fore.LIGHTBLUE_EX + Style.BRIGHT))
            return False

        elif result == "died":
            print(); hr("═", colour=Fore.RED)
            print(c(f"  {player.name.upper()} HAS FALLEN.", Fore.RED))
            _print_end_stats(player)
            hr("═", colour=Fore.RED)
            return False

        elif result == "ended":
            # An ending was triggered (sys.exit called inside ending fns)
            return False

        elif result and result.startswith("move:"):
            direction = result.split(":", 1)[1]
            dest = room.exits.get(direction)
            if dest is None:
                print(c("  That passage is blocked.", Fore.RED))
                continue

            # Move
            old_pos = player.dungeon_pos
            player.dungeon_pos = dest
            player.visited_rooms += 1
            player.depth = dest[2] * 4 + 2   # approximate depth for enemy scaling

            # Mark destination visited
            dest_room = player.dungeon.get(dest)
            if dest_room and not dest_room.visited:
                dest_room.visited = True

            # Update map
            if hasattr(player, "map") and player.map:
                player.map.visit(dest, dest_room.name if dest_room else "Chamber")
                player.map.connect(old_pos, dest)

            # Poison tick on move
            player.apply_poison_tick()
            if player.hp <= 0:
                print(); hr("═", colour=Fore.RED)
                print(c(f"  {player.name.upper()} HAS FALLEN TO POISON.", Fore.RED))
                _print_end_stats(player)
                hr("═", colour=Fore.RED)
                return False

            # Autosave
            autosave(player)

            # Check win condition: all endings require specific triggers
            # The only non-ending escape: find the surface exit room
            # (a specific room on floor 0 that becomes available after reaching floor 3)
            if _check_surface_escape(player):
                return win_screen(player)

        # Add this new block directly after the move block:
        elif result and result.startswith("teleport:"):
            # Admin teleport — move directly to coordinates, no poison tick, no win check
            coords = result.split(":", 1)[1].split(",")
            dest = (int(coords[0]), int(coords[1]), int(coords[2]))
            old_pos = player.dungeon_pos
            player.dungeon_pos = dest
            player.depth = dest[2] * 4 + 2

            dest_room = player.dungeon.get(dest)
            if dest_room:
                dest_room.visited = True
                if hasattr(player, "map") and player.map:
                    player.map.visit(dest, dest_room.name)
                    player.map.connect(old_pos, dest)


def _check_surface_escape(player) -> bool:
    """
    Returns True if player is in the entrance room AND has been
    deep enough to trigger the basic escape condition.
    """
    if player.dungeon_pos == player.dungeon.entrance:
        if player.visited_rooms >= 30:   # must have actually explored
            return True
    return False


def _print_end_stats(player):
    found = sum(1 for f in ALL_FLAGS if f in player.flags and f in DISCOVERY_TEXT)
    print(c(f"  Rooms explored: {player.visited_rooms}  |  Gold: {player.gold}", Fore.YELLOW))
    print(c(f"  Discoveries: {found} of {len(DISCOVERY_TEXT)}", Fore.CYAN))


SAVE_DIR = pathlib.Path(__file__).parent  # same folder as the game file

def _save_path(name: str) -> pathlib.Path:
    """Return the save file path for a given character name."""
    safe = "".join(ch for ch in name if ch.isalnum() or ch in (" ", "_", "-")).strip()
    safe = safe.replace(" ", "_") or "unknown"
    return SAVE_DIR / f"eon_save_{safe}.json"


def save_exists(name: str) -> bool:
    return _save_path(name).exists()


def list_saves() -> list:
    """Return a list of (character_name, summary_string) for all save files found."""
    saves = []
    for path in sorted(SAVE_DIR.glob("eon_save_*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            name    = data.get("name", "Unknown")
            rooms   = data.get("visited_rooms", 0)
            gold    = data.get("gold", 0)
            descent = data.get("descent", 1)
            flags   = len(data.get("flags", []))
            summary = (f"{name}  —  "
                       f"Rooms: {rooms}  |  Gold: {gold}  |  "
                       f"Descent: {descent}  |  Discoveries: {flags}")
            saves.append((name, summary, path))
        except Exception:
            pass  # corrupted save — skip silently
    return saves


def player_to_dict(player) -> dict:
    equipped_weapon = player.equipped["weapon"]["name"] if player.equipped["weapon"] else None
    equipped_armour = player.equipped["armour"]["name"] if player.equipped["armour"] else None

    # Serialise inventory — strip any non-JSON-safe values just in case
    safe_inventory = []
    for item in player.inventory:
        safe_item = {k: v for k, v in item.items()
                     if isinstance(v, (str, int, float, bool, type(None)))}
        safe_inventory.append(safe_item)

    return {
        # Identity
        "name":           player.name,
        # Stats
        "max_hp":         player.max_hp,
        "hp":             player.hp,
        "attack":         player.attack,
        "defence":        player.defence,
        "gold":           player.gold,
        # Status
        "poisoned":       player.poisoned,
        "cursed":         player.cursed,
        "void_ward":      player.void_ward,
        # Progress
        "visited_rooms":  player.visited_rooms,
        "depth":          player.depth,
        "descent":        player.descent,
        # Inventory — stored as full item dicts (they are already plain dicts)
        "inventory":      player.inventory,
        # Equipped — stored as item names; re-linked on load
        "equipped_weapon": equipped_weapon,
        "equipped_armour": equipped_armour,
        "equipped_relic": player.equipped["relic"]["name"] if player.equipped.get("relic") else None,
        # Discovery / secret tracking (sets → lists for JSON)
        "flags":          sorted(player.flags),
        "secrets_spoken": sorted(player.secrets_spoken),
        "purchased_uniques": sorted(getattr(player, "purchased_uniques", set())),
        # Map / Dungeon
        "dungeon_pos": list(player.dungeon_pos),
        "dungeon":     player.dungeon.to_dict() if player.dungeon else None,
        "map":         player.map.to_dict() if player.map else {},
        # Reputation
        "reputation": player.reputation,
    }


def dict_to_player(data: dict):
    """
    Reconstruct a Player object from a saved dict.
    Imported lazily so this function works wether or not Player is in scope.
    """
    try:
        p = Player(data["name"])
    except NameError:
        raise RuntimeError("dict_to_player must be used inside eon_rpg_v4.py")

    p.max_hp         = data.get("max_hp",        15)
    p.hp             = data.get("hp",             15)
    p.attack         = data.get("attack",          4)
    p.defence        = data.get("defence",         1)
    p.gold           = data.get("gold",            0)
    p.poisoned       = data.get("poisoned",    False)
    p.cursed         = data.get("cursed",      False)
    p.void_ward      = data.get("void_ward",   False)
    p.visited_rooms  = data.get("visited_rooms",   0)
    p.depth          = data.get("depth",           0)
    p.descent        = data.get("descent",         1)
    p.inventory      = data.get("inventory",      [])
    p.flags          = set(data.get("flags",      []))
    p.reputation = data.get("reputation", {"scholars": 0, "void_touched": 0, "seekers": 0})
    p.secrets_spoken = set(data.get("secrets_spoken", []))
    p.purchased_uniques = set(data.get("purchased_uniques", []))
    p.dungeon_pos    = tuple(int(x) for x in data.get("dungeon_pos", [0, 0, 0]))

    raw_dungeon = data.get("dungeon")
    p.dungeon   = Dungeon.from_dict(raw_dungeon) if raw_dungeon else None
    p.map       = DungeonMap.from_dict(data.get("map", {}))

    # Re-link equipped items by name
    weapon_name = data.get("equipped_weapon")
    armour_name = data.get("equipped_armour")
    relic_name = data.get("equipped_relic")
    if relic_name:
        for item in p.inventory:
            if item.get("name") == relic_name:
                p.equipped["relic"] = item
                break
    for item in p.inventory:
        if weapon_name and item.get("name") == weapon_name and p.equipped["weapon"] is None:
            p.equipped["weapon"] = item
        if armour_name and item.get("name") == armour_name and p.equipped["armour"] is None:
            p.equipped["armour"] = item

    return p


def save_game(player, slot_label: str = ""):
    """Write player state to disk. Returns True on success."""
    path = _save_path(player.name)
    data = player_to_dict(player)
    try:
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        label = f" ({slot_label})" if slot_label else ""
        print(c(f"  Game saved{label}.", Fore.GREEN))
        return True
    except Exception as e:
        print(c(f"  Save failed: {e}", Fore.RED))
        return False


def load_game(name: str):
    """Load a player from disk by character name. Returns Player or None."""
    path = _save_path(name)
    if not path.exists():
        print(c(f"  No save found for '{name}'.", Fore.RED))
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        player = dict_to_player(data)
        print(c(f"  Save loaded: {player.name}.", Fore.GREEN))
        return player
    except Exception as e:
        print(c(f"  Save file corrupted or unreadable: {e}", Fore.RED))
        return None


def delete_save(name: str) -> bool:
    """Delete a save file. Returns True if it existed and was removed."""
    path = _save_path(name)
    if path.exists():
        path.unlink()
        print(c(f"  Save for '{name}' deleted.", Fore.YELLOW))
        return True
    return False


def autosave(player):
    """
    Called automatically when the player moves between rooms.
    Silent — no message printed unless it fails.
    Saves the current state without interrupting flow.
    """
    path = _save_path(player.name)
    try:
        path.write_text(
            json.dumps(player_to_dict(player), indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
    except Exception:
        pass  # autosave failure is non-fatal — never crash the game over it



TITLE_ART = """
  ╔══════════════════════════════════════════════════════╗
  ║                                                      ║
  ║               L A N D S   O F   E O N                ║
  ║                                                      ║
  ║         Ruins of Eldros-Verath, First Empire         ║
  ║                                                      ║
  ╚══════════════════════════════════════════════════════╝
"""

def _start_menu() -> "Player | None":
    """
    Show the start menu and return a Player (new or loaded), or None to quit.
    Also handles save management (load, delete, list).
    """
    print(c(TITLE_ART, Fore.YELLOW))
    saves = list_saves()

    while True:
        opts = ["New character"]
        if saves:
            opts.append("Load a saved character")
            opts.append("Manage saves (view / delete)")
        opts.append("Quit")

        ch = prompt(opts)

        if ch == "Quit":
            return None

        elif ch == "New character":
            print()
            name = input(c("  Your name, traveller: ", Fore.CYAN)).strip() or "Stranger"
            if name.lower() == ADMIN_NAME:
                print(c("  Admin character. Admin mode available in any room.", Fore.MAGENTA))
            # Warn if a save already exists for that name
            if save_exists(name):
                print()
                wrap(f"  A save already exists for '{name}'. "
                     "Starting a new character will overwrite it when you next save.",
                     Fore.YELLOW)
                confirm = prompt(["Continue anyway", "Choose a different name", "Cancel"])
                if confirm == "Cancel":
                    continue
                elif confirm == "Choose a different name":
                    continue
            player = Player(name)
            print()
            print(c(f"  Welcome, {player.name}. What you find here is yours to carry.",
                    Fore.YELLOW))
            pause()
            return player

        elif ch == "Load a saved character":
            saves = list_saves()  # refresh
            if not saves:
                print(c("  No saves found.", Fore.RED))
                continue
            print()
            load_opts = [summary for _, summary, _ in saves] + ["Back"]
            sel = prompt(load_opts)
            if sel == "Back":
                continue
            # Match selection back to a name
            for name, summary, path in saves:
                if summary == sel:
                    player = load_game(name)
                    if player:
                        print()
                        wrap(f"  Welcome back, {player.name}. "
                             f"You have explored {player.visited_rooms} rooms "
                             f"and carry {player.gold} gold.", Fore.YELLOW)
                        pause()
                        return player
                    break

        elif ch == "Manage saves (view / delete)":
            saves = list_saves()
            if not saves:
                print(c("  No saves found.", Fore.RED))
                continue
            print()
            print(c("  SAVED CHARACTERS", Fore.YELLOW))
            print()
            for _, summary, _ in saves:
                print(c(f"    {summary}", Fore.WHITE))
            print()
            manage_opts = ([f"Delete save for: {name}" for name, _, _ in saves]
                           + ["Back"])
            sel = prompt(manage_opts)
            if sel == "Back":
                continue
            for name, _, _ in saves:
                if sel == f"Delete save for: {name}":
                    confirm = prompt([f"Confirm: delete '{name}'?", "Cancel"])
                    if confirm != "Cancel":
                        delete_save(name)
                    break
            saves = list_saves()


def _save_prompt(player):
    """
    Ask the player if they want to manually save.
    Called at natural pause points (between descents, after winning a room).
    """
    print()
    ch = prompt(["Save and continue", "Continue without saving"])
    if ch == "Save and continue":
        save_game(player)
    print()


def main():
    if not COLOUR:
        print("  (pip install colorama for colour)"); print()

    player = _start_menu()
    if player is None:
        print(c("  Farewell.", Fore.YELLOW))
        return

    # ── Main game loop ────────────────────────────────────────────────────────
    while True:
        descend = run_game(player)

        if not descend:
            # Player died or quit — offer a final save so discoveries survive
            # (inventory and depth are reset on death, but flags/gold persist)
            print()
            save_game(player)
            wrap("Your character's knowledge and gold have been preserved, "
                 "even in defeat.", Fore.YELLOW)
            # On death: reset combat stats but keep lore and gold
            player.hp         = player.max_hp
            player.poisoned   = False
            player.cursed     = False
            player.void_ward  = False
            player.depth      = 0
            # Keep inventory, flags, gold, stats — only combat state resets
            ch = prompt(["Save progress and return to menu",
                         "Return to menu without saving",
                         "Try again immediately"])
            if ch == "Save progress and return to menu":
                save_game(player, slot_label="after defeat")
                break
            elif ch == "Return to menu without saving":
                break
            else:
                # Try again: reset depth/rooms for new run
                player.visited_rooms = 0
                player.depth         = 0
                wrap("You stand again at the entrance. The ruins wait.",
                     Fore.YELLOW)
                pause()
                continue

        # Player chose to descend again or won
        player.descent += 1
        player.dungeon     = None          # triggers fresh generation in run_game()
        player.dungeon_pos = (0, 0, 0)     # will be overwritten by new entrance
        player.map         = DungeonMap()  # fresh map
        player.visited_rooms = 0
        player.depth         = 0
        player.hp = min(player.hp, player.max_hp)
        # flags, inventory, gold, stats are all preserved

        print()
        wrap("You stand again at the top of the stairs. The dark below is the same dark. "
             "You know more than you did. The ruins do not care.", Fore.YELLOW)
        if player.descent == 2:
            wrap("You notice something you did not see before: a second staircase, "
                 "deeper, that was not visible on your first descent. "
                 "Or perhaps you were not ready to see it.", Fore.MAGENTA)
        print()

        # Offer a save between descents
        _save_prompt(player)
        pause()



if __name__ == "__main__":
    main()