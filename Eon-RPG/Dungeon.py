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