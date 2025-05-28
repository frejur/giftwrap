from collections import namedtuple
from enum import Enum, auto

class BboxFacePair(Enum):
    TOP_BOTTOM = auto()
    LEFT_RIGHT = auto()
    FRONT_BACK = auto()

def determine_smallest_and_largest_bbox_side(width, height, depth):
    side_area = [
        (BboxFacePair.TOP_BOTTOM,   depth * width),
        (BboxFacePair.LEFT_RIGHT, depth * height),
        (BboxFacePair.FRONT_BACK, width * height)
    ]
    side_area.sort(key=lambda sArea: sArea[1])

    Side = namedtuple('Side', ['smallest', 'largest'])
    return Side(smallest= side_area[0][0], largest=side_area[2][0])
