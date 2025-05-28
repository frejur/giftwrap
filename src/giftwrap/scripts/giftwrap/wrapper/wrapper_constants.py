from enum import Enum, auto

"""
Various constants used for setting up the Wrapper class
"""

# ==============================================================================
# Wrapper class
# ==============================================================================

class WrapperMode(Enum):
    CREATE = auto()
    LOAD   = auto()

class RibbonType(Enum):
    FLAT   = auto()
    SQUARE = auto()
    ROUND  = auto()