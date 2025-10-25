from .schemas import DebateState
from typing import Optional

class MemoryStore:
    def __init__(self):
        self._db: dict[str, DebateState] = {}
    
    def get(self, k: str) -> Optional[DebateState]:
        return self._db.get(k)
    
    def set(self, k: str, v: DebateState):
        self._db[k] = v


class Store:
    def __init__(self):
        self.memory = MemoryStore()

    async def aget(self, k: str) -> Optional[DebateState]:
        return self.memory.get(k)

    async def aset(self, k: str, v: DebateState):
        self.memory.set(k, v)

store = Store()