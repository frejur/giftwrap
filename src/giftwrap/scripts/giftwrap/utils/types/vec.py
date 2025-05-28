from dataclasses import dataclass
from typing import Iterator

@dataclass
class Vec:
    x: float
    y: float
    z: float

    def __iter__(self) -> Iterator[float]:
        yield self.x
        yield self.y
        yield self.z