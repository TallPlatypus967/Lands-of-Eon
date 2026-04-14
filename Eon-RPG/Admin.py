
# ─── ADMIN MODE ───────────────────────────────────────────────────────────────

ADMIN_NAME = "admin"

def is_admin(player) -> bool:
    return player.name.lower() == ADMIN_NAME

def admin_menu(player) -> "room_override | None":
    """
    Admin console. Returns a room dict if the player teleports,
    otherwise None (continue current room).
    """
    hr("═", colour=Fore.MAGENTA)
    print(c("  ADMIN MODE", Fore.MAGENTA + Style.BRIGHT))
    hr("═", colour=Fore.MAGENTA)
    print()
    print(c("  Type /help for a full command list.", Fore.MAGENTA))
    print()

    while True:
        raw = input(c("  admin> ", Fore.MAGENTA + Style.BRIGHT)).strip()
        if not raw:
            continue

        parts = raw.split(None, 1)
        cmd = parts[0].lower()
        arg = parts[1].strip() if len(parts) > 1 else ""

        # ── /exit ────────────────────────────────────────────────────────────
        if cmd == "/exit":
            print(c("  Leaving admin mode.", Fore.MAGENTA))
            return None

        # ── /stats ───────────────────────────────────────────────────────────
        elif cmd == "/stats":
            print(c(f"  HP: {player.hp}/{player.max_hp}  ATK: {player.total_attack()}"
                    f"  DEF: {player.total_defence()}  Gold: {player.gold}"
                    f"  Depth: {player.depth}  Rooms: {player.visited_rooms}"
                    f"  Descent: {player.descent}", Fore.CYAN))
            print(c(f"  Flags: {len(player.flags)}", Fore.CYAN))

        # ── /gold <amount> ────────────────────────────────────────────────────
        elif cmd == "/gold":
            try:
                amount = int(arg)
                player.gold += amount
                print(c(f"  Gold set. Now: {player.gold}", Fore.GREEN))
            except ValueError:
                print(c("  Usage: /gold <integer>", Fore.RED))

        # ── /item <name> ──────────────────────────────────────────────────────
        elif cmd == "/item":
            # Try exact match first, then case-insensitive partial
            match = get_item(arg)
            if match is None:
                arg_low = arg.lower()
                match = next(
                    (dict(it) for it in ITEM_POOL
                     if arg_low in it["name"].lower()),
                    None
                )
            if match:
                player.pick_up(match)
            else:
                print(c(f"  No item matching '{arg}'. Use /list to see all items.", Fore.RED))

        # ── /list ─────────────────────────────────────────────────────────────
        elif cmd == "/list":
            sub = arg.lower() if arg else "items"
            if sub in ("items", "item"):
                print(c("  All items:", Fore.MAGENTA))
                for it in ITEM_POOL:
                    print(c(f"    [{it['type']:10}] {it['name']}", Fore.WHITE))
            elif sub in ("flags", "flag", "discoveries"):
                print(c("  All discovery flags:", Fore.MAGENTA))
                for f in sorted(DISCOVERY_TEXT.keys()):
                    tick = c("✓", Fore.GREEN) if f in player.flags else c("·", Fore.LIGHTBLUE_EX + Style.BRIGHT)
                    print(f"    {tick} {f}")
            elif sub in ("rooms", "room", "events"):
                print(c("  All special room events:", Fore.MAGENTA))
                for sr in SPECIAL_ROOMS:
                    print(c(f"    {sr['event']:30} min_depth:{sr['min_depth']}", Fore.WHITE))
            else:
                print(c("  Usage: /list [items | flags | rooms]", Fore.RED))

        # ── /discover <flag> ─────────────────────────────────────────────────
        elif cmd == "/discover":
            if arg in DISCOVERY_TEXT or arg in ALL_FLAGS:
                player.flags.add(arg)
                print(c(f"  Flag '{arg}' added.", Fore.GREEN))
            else:
                # Try partial match
                matches = [f for f in ALL_FLAGS if arg.lower() in f.lower()]
                if len(matches) == 1:
                    player.flags.add(matches[0])
                    print(c(f"  Flag '{matches[0]}' added.", Fore.GREEN))
                elif matches:
                    print(c(f"  Ambiguous. Matches: {', '.join(matches[:8])}", Fore.YELLOW))
                else:
                    print(c(f"  No flag matching '{arg}'. Use /list flags.", Fore.RED))

        # ── /removeflag <flag> ────────────────────────────────────────────────
        elif cmd == "/removeflag":
            if arg in player.flags:
                player.flags.remove(arg)
                print(c(f"  Flag '{arg}' removed.", Fore.GREEN))
            else:
                matches = [f for f in player.flags if arg.lower() in f.lower()]
                if len(matches) == 1:
                    player.flags.remove(matches[0])
                    print(c(f"  Flag '{matches[0]}' removed.", Fore.GREEN))
                elif matches:
                    print(c(f"  Ambiguous. Current matching flags: {', '.join(matches[:8])}", Fore.YELLOW))
                else:
                    print(c(f"  You don't have a flag matching '{arg}'.", Fore.RED))

        # ── /clearflags ───────────────────────────────────────────────────────
        elif cmd == "/clearflags":
            count = len(player.flags)
            player.flags.clear()
            print(c(f"  All {count} flags cleared.", Fore.GREEN))

        # ── /flags ────────────────────────────────────────────────────────────
        # Shows every flag the player currently holds, with discovery text if available
        elif cmd == "/flags":
            if not player.flags:
                print(c("  No flags set.", Fore.LIGHTBLUE_EX + Style.BRIGHT))
            else:
                print(c(f"  Current flags ({len(player.flags)}):", Fore.MAGENTA))
                for f in sorted(player.flags):
                    text = DISCOVERY_TEXT.get(f, "")
                    suffix = c(f"  — {text[:60]}{'...' if len(text) > 60 else ''}", Fore.LIGHTBLUE_EX + Style.BRIGHT) if text else ""
                    print(c(f"    {f}", Fore.WHITE) + suffix)

        # ── /removegold <amount> ──────────────────────────────────────────────
        elif cmd == "/removegold":
            try:
                amount = int(arg)
                player.gold = max(0, player.gold - amount)
                print(c(f"  Gold reduced. Now: {player.gold}", Fore.GREEN))
            except ValueError:
                print(c("  Usage: /removegold <integer>", Fore.RED))

        # ── /setgold <amount> ─────────────────────────────────────────────────
        elif cmd == "/setgold":
            try:
                player.gold = max(0, int(arg))
                print(c(f"  Gold set to {player.gold}.", Fore.GREEN))
            except ValueError:
                print(c("  Usage: /setgold <integer>", Fore.RED))

        # ── /removeitem <name> ────────────────────────────────────────────────
        elif cmd == "/removeitem":
            arg_low = arg.lower()
            match = next((it for it in player.inventory if it["name"].lower() == arg_low), None)
            if match is None:
                match = next((it for it in player.inventory if arg_low in it["name"].lower()), None)
            if match:
                # Unequip if necessary
                if match is player.equipped.get("weapon"):
                    player.equipped["weapon"] = None
                if match is player.equipped.get("armour"):
                    player.equipped["armour"] = None
                player.inventory.remove(match)
                print(c(f"  Removed: {match['name']}", Fore.GREEN))
            else:
                print(c(f"  No inventory item matching '{arg}'.", Fore.RED))

        # ── /clearinventory ───────────────────────────────────────────────────
        elif cmd == "/clearinventory":
            player.inventory.clear()
            player.equipped["weapon"] = None
            player.equipped["armour"] = None
            print(c("  Inventory cleared.", Fore.GREEN))

        # ── /inventory ────────────────────────────────────────────────────────
        # Quick inventory view without leaving admin mode
        elif cmd == "/inventory":
            if not player.inventory:
                print(c("  Inventory is empty.", Fore.LIGHTBLUE_EX + Style.BRIGHT))
            else:
                print(c(f"  Inventory ({len(player.inventory)} items):", Fore.MAGENTA))
                for it in player.inventory:
                    tag = ""
                    if it is player.equipped.get("weapon"): tag = " [W]"
                    if it is player.equipped.get("armour"): tag = " [A]"
                    col = {"key":Fore.YELLOW,"lore":Fore.CYAN,"artefact":Fore.MAGENTA}.get(it["type"], Fore.WHITE)
                    print(c(f"    {it['name']}{tag}", col))

        # ── /equip <name> ─────────────────────────────────────────────────────
        elif cmd == "/equip":
            arg_low = arg.lower()
            match = next((it for it in player.inventory
                          if arg_low in it["name"].lower()
                          and it["type"] in ("weapon", "armour")), None)
            if match:
                player.equipped[match["type"]] = match
                print(c(f"  Equipped {match['name']}.", Fore.GREEN))
            else:
                print(c(f"  No weapon or armour matching '{arg}' in inventory.", Fore.RED))

        # ── /revealmap ────────────────────────────────────────────────────────────────
        elif cmd == "/revealmap":
            if not player.dungeon:
                print(c("  No dungeon loaded.", Fore.RED))
                continue
            for pos, room in player.dungeon.grid.items():
                room.visited = True
                if hasattr(player, "map") and player.map:
                    player.map.visit(pos, room.name)
            print(c(f"  All {len(player.dungeon.grid)} rooms revealed.", Fore.GREEN))

        # ── /regen ────────────────────────────────────────────────────────────────────
        elif cmd == "/regen":
            print(c("  Regenerating dungeon...", Fore.YELLOW))
            player.dungeon      = generate_dungeon(player.descent)
            player.dungeon_pos  = player.dungeon.entrance
            player.map          = DungeonMap()
            player.map.visit(player.dungeon_pos,
                             player.dungeon.grid[player.dungeon_pos].name)
            # Mark entrance visited
            player.dungeon.grid[player.dungeon_pos].visited = True
            player.visited_rooms = 0
            player.depth         = 0
            print(c(f"  New dungeon generated (seed {player.dungeon.seed}). "
                    f"Placed at entrance.", Fore.GREEN))
            return ("teleport", player.dungeon.entrance)  # exit admin mode so the new room loads immediately

        # ── /bell ─────────────────────────────────────────────────────────────────────
        elif cmd == "/bell":
            if "warden_bell_rung" in player.flags:
                player.flags.discard("warden_bell_rung")
                # Also unboost — nothing to undo retroactively, just clear the flag
                print(c("  Warden Bell unrung. Enemy boosts disabled.", Fore.GREEN))
            else:
                player.flags.add("warden_bell_rung")
                print(c("  Warden Bell rung. Enemies are now boosted.", Fore.RED))

        # ── /seed ─────────────────────────────────────────────────────────────────────
        elif cmd == "/seed":
            if not player.dungeon:
                print(c("  No dungeon loaded.", Fore.RED))
                continue
            if arg:
                # Regenerate with a specific seed
                try:
                    seed = int(arg)
                    print(c(f"  Regenerating with seed {seed}...", Fore.YELLOW))
                    rng  = random.Random(seed)
                    d    = generate_dungeon(player.descent)
                    # Patch the seed in after generation
                    # (generate_dungeon picks its own seed — rebuild manually)
                    d.seed = seed
                    player.dungeon     = d
                    player.dungeon_pos = d.entrance
                    player.map         = DungeonMap()
                    player.map.visit(player.dungeon_pos,
                                     player.dungeon.grid[player.dungeon_pos].name)
                    player.dungeon.grid[player.dungeon_pos].visited = True
                    player.visited_rooms = 0
                    player.depth         = 0
                    print(c(f"  Dungeon loaded. Seed: {player.dungeon.seed}.", Fore.GREEN))
                    return ("teleport", player.dungeon.entrance)
                except ValueError:
                    print(c("  Usage: /seed <integer>  or  /seed  (to show current seed)", Fore.RED))
            else:
                seed = player.dungeon.seed if player.dungeon else "none"
                print(c(f"  Current dungeon seed: {seed}", Fore.CYAN))

        # ── /goto ─────────────────────────────────────────────────────────────────────
        # Move to a specific grid position directly
        elif cmd == "/goto":
            if not player.dungeon:
                print(c("  No dungeon loaded.", Fore.RED))
                continue
            try:
                parts_xyz = [int(x.strip()) for x in arg.split(",")]
                if len(parts_xyz) != 3:
                    raise ValueError
                pos = tuple(parts_xyz)
                if pos not in player.dungeon.grid:
                    print(c(f"  Position {pos} does not exist in this dungeon.", Fore.RED))
                else:
                    old_pos = player.dungeon_pos
                    player.dungeon_pos = pos
                    room = player.dungeon.grid[pos]
                    room.visited = True
                    if hasattr(player, "map") and player.map:
                        player.map.visit(pos, room.name)
                        player.map.connect(old_pos, pos)
                    print(c(f"  Moved to {pos}: {room.name}", Fore.GREEN))
                    return ("teleport", pos)
            except ValueError:
                print(c("  Usage: /goto x,y,z  (e.g. /goto 3,2,1)", Fore.RED))

        # ── /complete ─────────────────────────────────────────────────────────────────
        # Force-complete (seal) the current room
        elif cmd == "/complete":
            if not player.dungeon:
                print(c("  No dungeon loaded.", Fore.RED))
                continue
            room = player.dungeon.get(player.dungeon_pos)
            if not room:
                print(c("  No room at current position.", Fore.RED))
            elif not room.sealed:
                print(c(f"  {room.name} is not a sealable room.", Fore.YELLOW))
            else:
                room.completed = True
                print(c(f"  {room.name} marked as completed and sealed.", Fore.GREEN))

        # ── /unsealed ─────────────────────────────────────────────────────────────────
        # List all sealable rooms and their completion status
        elif cmd == "/unsealed":
            if not player.dungeon:
                print(c("  No dungeon loaded.", Fore.RED))
                continue
            sealed_rooms = [(pos, r) for pos, r in player.dungeon.grid.items() if r.sealed]
            if not sealed_rooms:
                print(c("  No sealable rooms in this dungeon.", Fore.YELLOW))
            else:
                print(c(f"  Sealable rooms ({len(sealed_rooms)}):", Fore.YELLOW))
                for pos, room in sorted(sealed_rooms):
                    status = c("COMPLETE", Fore.GREEN) if room.completed else c("pending", Fore.YELLOW)
                    ev = room.room_def.get("special_event", "?")
                    here = c(" ◄", Fore.YELLOW + Style.BRIGHT) if pos == player.dungeon_pos else ""
                    print(c(f"    [{status}] {pos}  {room.name}  [{ev}]{here}", Fore.WHITE))

        # ── /floor ────────────────────────────────────────────────────────────────────
        # Jump directly to a floor (places player at the first unvisited room on that floor)
        elif cmd == "/floor":
            if not player.dungeon:
                print(c("  No dungeon loaded.", Fore.RED))
                continue
            try:
                target_z = int(arg) - 1  # 1-indexed for the player
                rooms_on_floor = [(pos, r) for pos, r in player.dungeon.grid.items()
                                  if pos[2] == target_z]
                if not rooms_on_floor:
                    print(c(f"  Floor {int(arg)} does not exist.", Fore.RED))
                else:
                    # Prefer an unvisited room; fall back to any room
                    unvisited = [(p, r) for p, r in rooms_on_floor if not r.visited]
                    target_pos, target_room = (unvisited[0] if unvisited
                                               else rooms_on_floor[0])
                    old_pos = player.dungeon_pos
                    player.dungeon_pos = target_pos
                    target_room.visited = True
                    player.depth = target_z * 4
                    if hasattr(player, "map") and player.map:
                        player.map.visit(target_pos, target_room.name)
                        player.map.connect(old_pos, target_pos)
                    print(c(f"  Jumped to floor {int(arg)}: {target_room.name} at {target_pos}",
                            Fore.GREEN))
                    return ("teleport", target_pos)
            except ValueError:
                print(c("  Usage: /floor <n>  (e.g. /floor 3)", Fore.RED))

        # ── /setatk <n> ───────────────────────────────────────────────────────
        elif cmd == "/setatk":
            try:
                player.attack = int(arg)
                print(c(f"  Base attack set to {player.attack}.", Fore.GREEN))
            except ValueError:
                print(c("  Usage: /setatk <integer>", Fore.RED))

        # ── /setdef <n> ───────────────────────────────────────────────────────
        elif cmd == "/setdef":
            try:
                player.defence = int(arg)
                print(c(f"  Base defence set to {player.defence}.", Fore.GREEN))
            except ValueError:
                print(c("  Usage: /setdef <integer>", Fore.RED))

        # ── /sethp <n> ────────────────────────────────────────────────────────
        elif cmd == "/sethp":
            try:
                val = int(arg)
                player.max_hp = val
                player.hp = val
                print(c(f"  Max HP and current HP set to {val}.", Fore.GREEN))
            except ValueError:
                print(c("  Usage: /sethp <integer>", Fore.RED))

        # ── /status ───────────────────────────────────────────────────────────
        # Toggle status effects for testing
        elif cmd == "/status":
            arg_low = arg.lower()
            if arg_low == "poison":
                player.poisoned = not player.poisoned
                print(c(f"  Poisoned: {player.poisoned}", Fore.GREEN))
            elif arg_low == "curse":
                player.cursed = not player.cursed
                print(c(f"  Cursed: {player.cursed}", Fore.GREEN))
            elif arg_low == "ward":
                player.void_ward = not player.void_ward
                print(c(f"  Void ward: {player.void_ward}", Fore.GREEN))
            elif arg_low == "clear":
                player.poisoned = False
                player.cursed = False
                player.void_ward = False
                print(c("  All status effects cleared.", Fore.GREEN))
            else:
                print(c("  Usage: /status [poison | curse | ward | clear]", Fore.RED))

        # ── /spawn <enemy name> ───────────────────────────────────────────────
        elif cmd == "/spawn":
            arg_low = arg.lower()
            match = next((e for e in ENEMY_POOL if e["name"].lower() == arg_low), None)
            if match is None:
                match = next((e for e in ENEMY_POOL if arg_low in e["name"].lower()), None)
            if match:
                print(c(f"  Spawning {match['name']} for a test fight...", Fore.RED))
                print()
                survived = combat(player, spawn_enemy(match))
                if not survived or player.hp <= 0:
                    print(c("  You died in the test fight. HP restored to 1.", Fore.RED))
                    player.hp = 1
            else:
                # List available enemies
                print(c(f"  No enemy matching '{arg}'. Available:", Fore.RED))
                for e in ENEMY_POOL:
                    print(c(f"    [T{e['tier']}] {e['name']}", Fore.WHITE))

        # ── /enemies ──────────────────────────────────────────────────────────
        elif cmd == "/enemies":
            print(c("  All enemies:", Fore.MAGENTA))
            for e in ENEMY_POOL:
                print(c(f"    [T{e['tier']}] {e['name']:30} HP:{e['hp']:3}  ATK:{e['attack']:3}"
                        f"  DEF:{e['defence']:2}  special:{e['special'] or 'none'}", Fore.WHITE))

        # ── /help ─────────────────────────────────────────────────────────────
        elif cmd == "/help":
            help_lines = [
                ("Navigation",  ["/tp <room>        — teleport to a room (partial event key or name)",
                                 "/goto x,y,z       — move to exact grid coordinates",
                                 "/floor <n>        — jump to floor n (1-5)",
                                 "/floorreveal      — list all rooms on floor n",
                                 "/revealmap        — mark all rooms as visited on the map",
                                 "/depth <n>        — set current depth value",]),
                ("Items",       ["/item <name>      — give yourself an item (partial name ok)",
                                 "/removeitem <n>   — remove item from inventory (partial ok)",
                                 "/clearinventory   — remove all items",
                                 "/inventory        — list current inventory",
                                 "/equip <name>     — equip a weapon or armour"]),
                ("Gold",        ["/gold <n>         — add gold",
                                 "/removegold <n>   — subtract gold",
                                 "/setgold <n>      — set gold to exact amount"]),
                ("Stats",       ["/sethp <n>        — set max HP and heal to full",
                                 "/setatk <n>       — set base attack",
                                 "/setdef <n>       — set base defence",
                                 "/heal             — full heal, clear poison/curse",
                                 "/status <effect>  — toggle poison/curse/ward, or 'clear'"]),
                ("Discoveries", ["/discover <flag>  — add a discovery flag (partial ok)",
                                 "/removeflag <f>   — remove a flag (partial ok)",
                                 "/discoverall      — add every flag",
                                 "/clearflags       — remove all flags",
                                 "/flags            — list all current flags with descriptions"]),
                ("Enemies",     ["/spawn <name>     — fight an enemy for testing (partial ok)",
                                 "/enemies          — list all enemies with stats"]),
                ("Info",        ["/stats            — show full player stats",
                                 "/list [items|flags|rooms] — browse all game content",
                                 "/pos              — show current dungeon position and room info",
                                 "/help             — this message",
                                 "/exit             — leave admin mode"]),
                ("Dungeon",     ["/regen            — regenerate the dungeon from scratch",
                                 "/seed             — show current dungeon seed",
                                 "/seed <n>         — regenerate with a specific seed",
                                 "/bell             — toggle the Warden Bell (boosts enemies)",
                                 "/complete         — force-complete (seal) the current room",
                                 "/unsealed         — list all sealable rooms and their status",
                                 ]),
            ]
            for section, lines in help_lines:
                print(c(f"\n  {section}", Fore.YELLOW))
                for line in lines:
                    print(c(f"    {line}", Fore.WHITE))
            print()

        # ── /discoverall ──────────────────────────────────────────────────────
        elif cmd == "/discoverall":
            for f in ALL_FLAGS:
                player.flags.add(f)
            print(c(f"  All {len(ALL_FLAGS)} flags added.", Fore.GREEN))

        # ── /heal ─────────────────────────────────────────────────────────────
        elif cmd == "/heal":
            player.hp = player.max_hp
            player.poisoned = False
            player.cursed = False
            print(c("  Fully healed. Poison and curse cleared.", Fore.GREEN))

        # ── /depth <n> ────────────────────────────────────────────────────────
        elif cmd == "/depth":
            try:
                player.depth = int(arg)
                print(c(f"  Depth set to {player.depth}.", Fore.GREEN))
            except ValueError:
                print(c("  Usage: /depth <integer>", Fore.RED))

        # ── /tp <event_key> ───────────────────────────────────────────────────
        elif cmd == "/tp":
            if not player.dungeon:
                print(c("  No dungeon loaded. Start a game first.", Fore.RED))
                continue

            arg_low = arg.lower().replace(" ", "_")

            # Find the room in the actual dungeon grid
            target_room = None
            target_pos  = None

            for pos, room in player.dungeon.grid.items():
                ev = room.room_def.get("special_event", "")
                name = room.room_def.get("name", "").lower()
                if ev and (ev == arg_low or arg_low in ev or arg_low in name):
                    target_room = room
                    target_pos  = pos
                    break

            if target_room:
                old_pos = player.dungeon_pos
                player.dungeon_pos = target_pos
                target_room.visited = True

                # Update map
                if hasattr(player, "map") and player.map:
                    player.map.visit(target_pos, target_room.name)
                    player.map.connect(old_pos, target_pos)

                print(c(f"  Teleported to: {target_room.name} at {target_pos}", Fore.GREEN))
                print(c(f"  (Event: {target_room.room_def.get('special_event', 'none')})", Fore.MAGENTA))
                print()
                return ("teleport", target_pos)  # exit admin mode and the room loop will pick up the new position

            else:
                # Show what's actually in the dungeon so the admin knows what to type
                print(c(f"  No room matching '{arg}' found in the current dungeon.", Fore.RED))
                print(c("  Special rooms present in this dungeon:", Fore.YELLOW))
                found_events = set()
                for pos, room in sorted(player.dungeon.grid.items(), key=lambda x: x[0]):
                    ev = room.room_def.get("special_event")
                    if ev and ev not in found_events:
                        found_events.add(ev)
                        visited = c("✓", Fore.GREEN) if room.visited else c("·", Fore.LIGHTBLUE_EX)
                        print(c(f"    {visited} [{ev:30}] {room.name} at {pos}", Fore.WHITE))

        # ── /pos ─────────────────────────────────────────────────────────────────────
        elif cmd == "/pos":
            if not player.dungeon:
                print(c("  No dungeon loaded.", Fore.RED))
                continue
            pos  = player.dungeon_pos
            room = player.dungeon.get(pos)
            print(c(f"  Position: {pos}  (floor {pos[2]+1})", Fore.CYAN))
            if room:
                ev      = room.room_def.get("special_event", "none")
                name    = room.room_def.get("name", "Chamber")
                exits   = {d: v for d, v in room.exits.items() if v is not None}
                sealed  = f"  [SEALED{'·COMPLETE' if room.completed else ''}]" if room.sealed else ""
                print(c(f"  Room: {name}  |  Event: {ev}{sealed}", Fore.CYAN))
                print(c(f"  Exits: {exits}", Fore.CYAN))
                enemies = room.room_def.get("enemies", [])
                items   = room.room_def.get("items",   [])
                print(c(f"  Enemies: {len(enemies)}  |  Items: {len(items)}", Fore.CYAN))
            print(c(f"  Depth: {player.depth}  |  Visited rooms: {player.visited_rooms}", Fore.CYAN))

        # ── /floorreveal ───────────────────────────────────────────────────────────────────
        elif cmd == "/floorreveal":
            if not player.dungeon:
                print(c("  No dungeon loaded.", Fore.RED))
                continue
            try:
                target_z = int(arg) - 1  # player-facing floors are 1-indexed
            except ValueError:
                target_z = player.dungeon_pos[2]

            rooms_on_floor = [(pos, r) for pos, r in player.dungeon.grid.items()
                              if pos[2] == target_z]
            print(c(f"  Floor {target_z + 1} ({len(rooms_on_floor)} rooms):", Fore.YELLOW))
            for pos, room in sorted(rooms_on_floor):
                ev      = room.room_def.get("special_event", "")
                name    = room.room_def.get("name", "Chamber")
                visited = c("✓", Fore.GREEN) if room.visited else c("·", Fore.LIGHTBLUE_EX)
                here    = c(" ◄ YOU", Fore.YELLOW + Style.BRIGHT) if pos == player.dungeon_pos else ""
                ev_str  = c(f" [{ev}]", Fore.CYAN) if ev else ""
                print(c(f"    {visited} {pos}  {name}", Fore.WHITE) + ev_str + here)

        else:
            print(c(f"  Unknown command '{cmd}'. Type /exit to leave admin mode.", Fore.RED))

PARCHMENT_VARIANTS = [
    {
        "id": "wells_diagram",
        "flag": "read_parchment_wells",
        "text": (
            "A diagram: nine circles arranged in a pattern you recognise vaguely as a "
            "constellation. Four labels are legible: BLOOD. ASTRAL. HOLLOW. DAWN. "
            "The others are damaged. "
            "At the centre, where the circles converge: a tenth circle, larger, "
            "filled solid black. No label."
        ),
    },
    {
        "id": "serethan_note",
        "flag": "read_serethan_note",
        "text": (
            "A short note, in a military hand: "
            "'The bell has not been rung. I have decided not to ring it. "
            "Whatever the lockdown protocol requires, I will not be the one to wake the ruins. "
            "If someone reads this after me: the bell is on the second level. "
            "The rope is intact. I leave the decision to you.' "
            "Signed: S.W.C. — WARDEN-COMMANDER SERETHAN."
        ),
    },
    {
        "id": "wars_summary",
        "flag": "read_wars_summary",
        "text": (
            "A summary, in formal Eldrosian: "
            "'The Wars of the Shattered Crown, being a brief account. "
            "Upon the death of Emperor Vaelan, the Godshards — three in number — "
            "passed to his heirs. Each heir believed the full set was rightfully theirs. "
            "The wars lasted three generations and ended not in victory but exhaustion. "
            "The shards were returned to Eldros-Verath by common agreement. "
            "No single heir was trusted to hold all three. "
            "They were placed in the Hall of the Shattered Crown, "
            "built for this purpose. They wait there still.'"
        ),
    },
    {
        "id": "myrrakhel_fragment",
        "flag": "read_myrrakhel_fragment",
        "text": (
            "A fragment of theological text: "
            "'Myrrakhel was not the first. There was something before Myrrakhel — "
            "something that the near-mortals call the Architect, though this may not be accurate. "
            "What is known: the Architect was destroyed. "
            "What it was before its destruction, and what destroyed it, "
            "is not recorded in any text that survives. "
            "Myrrakhel was made — or made itself — from what remained. "
            "The mind of the Architect did not die with its form. "
            "Where it went is the question the Remnant Scholars cannot answer.'"
        ),
    },
    {
        "id": "thaun_account",
        "flag": "read_thaun_account",
        "text": (
            "A first-person account, in a script that predates Eldrosian: "
            "'I rose from the well at the beginning of things. "
            "The well is not a place. It is a condition. "
            "I am what happens when the void decides to have opinions. "
            "Thaun is a name the near-mortals gave me. "
            "I have not corrected them. Names are useful. "
            "The void beneath the well is not me. "
            "I want to be clear about that. "
            "What is beneath the well is older than I am, "
            "and I was here before the world was finished.'"
        ),
    },
    {
        "id": "eldros_founding",
        "flag": "read_eldros_founding",
        "text": (
            "A historical account: "
            "'The empire of Eldros was founded in the third generation after the first humans — "
            "Auridan's children's children — learned to build in stone. "
            "The capital, Eldros-Verath, was chosen for the site of a well "
            "that the near-mortals had identified as significant. "
            "The Void-well was not the reason the city was built here. "
            "But it was the reason the city lasted as long as it did. "
            "The near-mortals said the well was a source of power. "
            "They were not wrong. They were incomplete.'"
        ),
    },
    {
        "id": "atraxis_description",
        "flag": "read_atraxis_description",
        "text": (
            "A page of dense philosophical notation, mostly incomprehensible. "
            "One passage is legible: "
            "'The entity called the Unmade, or Atraxis, does not want. "
            "Wanting implies a self that lacks something. "
            "What Atraxis does is closer to gravity — "
            "a force that pulls everything toward a particular outcome, "
            "not because it desires that outcome "
            "but because the outcome is what Atraxis is. "
            "The outcome is: everything becomes part of the void. "
            "The question the scholars could not answer: "
            "is Atraxis aware that this is what it is?' "
            "The margin note reads: 'Yes.'"
        ),
    },
    {
        "id": "tolos_account",
        "flag": "read_tolos_account",
        "text": (
            "A personal letter, unsealed and never sent: "
            "'Maelvyr — if you ever read this, which you won't, "
            "I want you to know that I understood what you wanted. "
            "You wanted the gods to listen. "
            "So did I. The difference between us is that I accepted "
            "that they might not. You could not accept it. "
            "I don't know if that makes you weaker than me or stronger. "
            "I've had a long time to think about it and I still don't know. "
            "I tried to stop you. I failed. "
            "That is the whole of it.' "
            "Signed: T."
        ),
    },
    {
        "id": "nine_gods_list",
        "flag": "read_nine_gods_list",
        "text": (
            "A liturgical text, formal and careful: "
            "'The nine Sera, as named by the near-mortals at the dawn of things: "
            "Myrrakhel the Deepest Pulse, who made the others. "
            "Kindrael the Flame at Dawn, who was second and impatient. "
            "Loría the Verdant Bloom, called also Allseer. "
            "Thalás, She of the Endless Tides. "
            "Thar the Stonefather, beneath whose Crown the nine peaks rise. "
            "Ishak the Storm-Forge, who loved the early Chaos. "
            "Ysena the Weaver of Shadows, spouse to Atheron. "
            "Vastinö the Frost-Child, who sits softly and remembers all. "
            "Kelamaris the Breath of the Heights, youngest and most brash. "
            "These are the nine. Myrrakhel made the others. "
            "Who made Myrrakhel is not recorded here.'"
        ),
    },
    {
        "id": "maelvyr_survival",
        "flag": "read_maelvyr_survival",
        "text": (
            "A field report, in military shorthand: "
            "'Eyewitness accounts from the Night of Collapse, compiled by order of Talarion. "
            "The subject known as Maelvyr was observed leaving Eldros-Verath "
            "on the night of the event. Injured — significantly. Moving west. "
            "Two witnesses confirm: he was alive. He was not pursued. "
            "There was no one left to pursue him. "
            "His current location is unknown. "
            "His current condition is unknown. "
            "Whether the transformation that was begun in the throne room "
            "is complete, partial, or ongoing — unknown. "
            "Recommendation: assume he survived. Assume he is dangerous. "
            "Assume he will not return here.' "
            "The recommendation was not acted upon, because there was no one left to act."
        ),
    },
]

def pick_parchment_variant(player=None) -> dict:
    """
    Return a Rolled Parchment item dict with a randomly chosen variant,
    excluding variants the player has already read (if player is provided).
    """
    if player:
        unread = [v for v in PARCHMENT_VARIANTS
                  if v["flag"] not in player.flags]
        pool = unread if unread else PARCHMENT_VARIANTS
    else:
        pool = PARCHMENT_VARIANTS

    variant = random.choice(pool)
    return {
        "name":        "Rolled Parchment",
        "type":        "lore",
        "value":       0,
        "description": "Rolled tight and sealed with black wax. The wax is already cracked.",
        "variant":     variant["id"],   # stored for later reading
        "_variant_flag": variant["flag"],
        "_variant_text": variant["text"],
    }

def _read_lore(player, item):
    hr(colour=Fore.CYAN)
    name = item["name"]
    if name == "Ashen Tablet":
        wrap("'In the final year of the Consolidated Age, the High Priests of Eldros were granted "
             "audience with the Great Gods — the last such audience ever held. One among them did "
             "not return the same. The records give no name. That name was removed from every ledger. "
             "What followed consumed the capital in a single night.'", Fore.CYAN)
        player.flags.add("read_ashen_tablet")

    elif name == "Charred Ledger":
        wrap("The surviving pages list names — hundreds — each crossed out in the same thick black ink. "
             "At the bottom of the last page, in a different hand: "
             "'The agreement was not with the Gods. It was with what stands behind them.'", Fore.CYAN)
        player.flags.add("read_charred_ledger")

    elif name == "Rolled Parchment":
        # Find the variant text — either stored in the item dict or pick randomly
        variant_text = item.get("_variant_text")
        variant_flag = item.get("_variant_flag")

        if not variant_text:
            # Fallback: pick a random unread variant
            v = random.choice([
                                  vv for vv in PARCHMENT_VARIANTS
                                  if vv["flag"] not in player.flags
                              ] or PARCHMENT_VARIANTS)
            variant_text = v["text"]
            variant_flag = v["flag"]

        hr(colour=Fore.CYAN)
        wrap(variant_text, Fore.CYAN)
        hr(colour=Fore.CYAN)
        if variant_flag:
            player.flags.add(variant_flag)
        pause()   # ← give player time to read before returning

    elif name == "Imperial Edict":
        wrap("The edict, in formal Eldrosian, declares: 'By order of Emperor Vaelan, Holder of the "
             "Godshards, Chosen of the Dragon-line, all records pertaining to the office of "
             "High Keeper are to be sealed pending investigation. Access restricted to the throne. "
             "This edict is permanent.' The date is three days before the Night of Collapse.", Fore.CYAN)
        player.flags.add("read_imperial_edict")

    elif name == "Priest's Journal":
        wrap("The first ink is careful, scholarly: notes on the wells, on the nature of the Thrys — "
             "the nine gods — on the relationship between Myrrakhel and the eight she created. "
             "The second ink begins mid-sentence, partway through the journal, and is erratic: "
             "'It is in the chamber. It has always been in the chamber. The Gods know. "
             "The Gods have always known and they said nothing because they did not know what to say. "
             "If they knew what I was going to — ' The entry ends.", Fore.CYAN)
        player.flags.add("read_priests_journal")

    elif name == "Talarion's Chronicle":
        wrap("The Chronicle opens to its final chapters — the rest is too damaged to read. "
             "What survives:", Fore.CYAN)
        wrap("'I was there when Maelvyr first began his searches. We all were. He was charming, "
             "brilliant, and furious — furious at the Gods for their silence. '", Fore.CYAN)
        wrap("'His friend Tolos tried to stop him. I tried to stop him. No one could stop him. '", Fore.CYAN)
        wrap("'What happened in the throne room — Tolos falling on the throne, Vaelan behind him, "
             "Maelvyr kneeling over his friend's body — I have told this story a hundred times. '", Fore.CYAN)
        wrap("'Each time I wonder if I am the only one who saw what I saw: that Maelvyr wept. '", Fore.CYAN)
        wrap("'Then he was gone. Injured. Diminished. But not dead. '", Fore.CYAN)
        wrap("'I proclaim the fall of an empire. I name the dead. I tell the story. '", Fore.CYAN)
        wrap("'Because someone must.'", Fore.CYAN)
        player.flags.add("read_talarion_chronicle")

    elif name == "Remnant Scholar's Notes":
        wrap("The notes are from someone who came here looking for answers. "
             "The handwriting starts neat and becomes less so.", Fore.CYAN)
        wrap("'Day 1: The ruins are extensive. Far larger than the surveys suggested. '", Fore.CYAN)
        wrap("'Day 4: Found inscriptions consistent with late-period Eldrosian. "
             "The Void-well may actually exist. '", Fore.CYAN)
        wrap("'Day 9: Something in the lower chambers is not ruins. It is occupied. '", Fore.CYAN)
        wrap("'Day 11: I have seen the cultists twice now. They are organised. "
             "They know where they are going. '", Fore.CYAN)
        wrap("'Day 12: I think they know about the '", Fore.CYAN)
        wrap("The entry ends.", Fore.CYAN)
        player.flags.add("read_scholar_notes")

    elif name == "Shard-Seeker's Map":
        wrap("The map is rough but legible. Three locations circled, all crossed out. "
             "Annotations in a mercenary hand:", Fore.CYAN)
        wrap("'Location 1: Nothing. Someone got here first. '", Fore.CYAN)
        wrap("'Location 2: Trap. Don't go back. '", Fore.CYAN)
        wrap("'Location 3: The throne room. There is something on the throne. "
             "I could not get close — there are cultists camped in the approach corridor. '", Fore.CYAN)
        wrap("On the back of the map, a note: 'If you find this, the throne room is real. "
             "Do not bring the shards together in one place. '", Fore.CYAN)
        wrap("'I don't know what happens. I don't want to know.'", Fore.CYAN)
        player.flags.add("read_shard_map")

    elif name == "The Last Warden's Log":
        wrap("The log is meticulous. Entry after entry: patrol routes, guard counts, "
             "gate inspections. The empire in careful maintenance.", Fore.CYAN)
        wrap("The final entries change:", Fore.CYAN)
        wrap("'Day -7: High Keeper has requested personal audience. "
             "I have filed objection. I do not trust this request. '", Fore.CYAN)
        wrap("'Day -3: Objection overruled. The audience will proceed. '", Fore.CYAN)
        wrap("'Day -1: Something is wrong. The city feels wrong. "
             "I cannot locate the High Keeper. '", Fore.CYAN)
        wrap("'Day 0: The bell. I should ring the bell. "
             "I am standing at the bell. "
             "If I ring it, the lockdown wakes everything we caged. "
             "I cannot ring it.'", Fore.CYAN + Style.BRIGHT)
        wrap("The entry ends mid-sentence.", Fore.CYAN)
        player.flags.add("read_warden_log")

    elif name == "A Field Guide to the Void-Touched":
        wrap("The handwriting is scholarly at the start. Less so by the end.", Fore.CYAN)
        wrap("'The Void-Touched are not corrupted in the usual sense. "
             "They are being completed — from their perspective. '", Fore.CYAN)
        wrap("'They believe contact with Atraxis is improvement. '", Fore.CYAN)
        wrap("'Stages of transformation: '", Fore.CYAN)
        wrap("'Stage 1: Direction. Subject becomes aware of a persistent pull. '", Fore.CYAN)
        wrap("'Stage 2: Deference. Subject begins to organise their life around the pull. '", Fore.CYAN)
        wrap("'Stage 3: Dissolution. Subject stops resisting. Name becomes optional. '", Fore.CYAN)
        wrap("'Stage 4: I don't — '", Fore.CYAN + Style.BRIGHT)
        wrap("The entry ends. The handwriting of the final note does not look like the first.", Fore.CYAN)
        player.flags.add("read_void_touched_guide")
        player.flags.add("atraxis_named")  # reading this teaches the name

    elif name == "Vaelan's Private Journal":
        wrap("The emperor's handwriting. Small, controlled, the handwriting of someone "
             "who writes carefully.", Fore.CYAN)
        wrap("'The High Keeper has requested a personal audience with the Gods. "
             "I have approved it against Serethan's advice. '", Fore.CYAN)
        wrap("'I approved it because Maelvyr is brilliant and I am running out of options. "
             "The empire is not what it was. The Gods do not speak. '", Fore.CYAN)
        wrap("'If anyone can get the Gods to speak, it is Maelvyr.'", Fore.CYAN)
        wrap("A later entry:", Fore.CYAN)
        wrap("'The audience was three days ago. Maelvyr has not been seen. "
             "I made a mistake. I do not know how large a mistake yet.'", Fore.CYAN + Style.BRIGHT)
        wrap("The journal ends there. The final pages are blank.", Fore.CYAN)
        player.flags.add("read_vaelan_journal")

    elif name == "Named's Grimoire":
        wrap("The text is in two languages simultaneously — "
             "one is Eldrosian, one is the language of the Void.", Fore.MAGENTA)
        wrap("The Eldrosian half reads like theology: careful, systematic, wrong. "
             "The Void half — which you can also read, somehow — "
             "is a correction of the Eldrosian half. "
             "Every error annotated.", Fore.MAGENTA)
        wrap("On the last page, in only Eldrosian: "
             "'I have learned the name. The name is changing me. '", Fore.MAGENTA + Style.BRIGHT)
        wrap("'I wanted power. This is not power. "
             "This is direction. I am becoming a direction. '", Fore.MAGENTA + Style.BRIGHT)
        wrap("'If you find this: do not learn the name unless you are prepared to become it.'", Fore.MAGENTA + Style.BRIGHT)
        player.flags.add("read_named_grimoire")
        player.flags.add("atraxis_named")  # reading this teaches the name
    pause()
    hr(colour=Fore.CYAN)

