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
