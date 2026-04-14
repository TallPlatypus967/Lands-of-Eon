

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
