class Tile:
    def __init__(
        self,
        id: str,
        solid: bool = True,
        kill: bool = False,
        boost: float = 0,
        finish: bool = False,
        checkpoint: bool = False,
        spawn: bool = False,
    ):
        self.id = id
        self.solid = solid
        self.kill = kill
        self.boost = boost
        self.finish = finish
        self.checkpoint = checkpoint
        self.spawn = spawn
