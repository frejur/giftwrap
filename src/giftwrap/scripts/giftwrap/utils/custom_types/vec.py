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

    def __eq__(self, other):
        return (self.x == other.x and
                self.y == other.y and
                self.z == other.z)

    def __hash__(self):
        return hash((self.x, self.y, self.z))
