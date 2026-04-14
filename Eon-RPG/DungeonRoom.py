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