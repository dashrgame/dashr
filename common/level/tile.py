from typing import Optional


class Tile:
    def __init__(
        self,
        id: str,
        position: tuple[int, int] = (0, 0),
        is_solid: bool = True,
        is_kill: bool = False,
        boost: float = 0,
        is_finish: bool = False,
        is_checkpoint: bool = False,
        is_spawn: bool = False,
        spawn_entity: Optional[str] = None,
    ):
        self.id = id
        self.position = position
        self.is_solid = is_solid
        self.is_kill = is_kill
        self.boost = boost
        self.is_finish = is_finish
        self.is_checkpoint = is_checkpoint
        self.is_spawn = is_spawn
        self.spawn_entity = spawn_entity
